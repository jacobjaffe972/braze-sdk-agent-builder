"""
LLM RAG Tools Agent - Consolidated implementation of Week 2 Parts 1, 2, and 3

This module provides a single agent class that can operate in three modes:
1. web_search: Live web search with Tavily and LLM summarization
2. document_rag: Traditional RAG with PDF documents and ChromaDB
3. corrective_rag: Hybrid approach with intelligent routing between documents and web search

The agent class follows the ChatInterface protocol and can be initialized with
different modes to handle various question-answering scenarios.
"""

import json
import time
import os
import os.path as osp
from typing import Dict, List, Optional, TypedDict, Literal

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import PyPDFLoader
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_tavily import TavilySearch
from opik.integrations.langchain import OpikTracer

from deep_research.core.chat_interface import ChatInterface
from deep_research.prompts.RAG_PROMPTS import (
    WEB_SEARCH_SUMMARIZER_PROMPT,
    DOCUMENT_RAG_PROMPT,
    DOCUMENT_RAG_MIXED_PROMPT,
    DOCUMENT_GRADING_PROMPT,
    DocumentGradingResponse,
    RagGenerationResponse
)


# Constants for document paths and storage
BASE_DIR = "/Users/Jacob.Jaffe/Documents/Maven/RAG Test Docs"
FILE_PATHS = [
    osp.join(BASE_DIR, "2019-annual-performance-report.pdf"),
    osp.join(BASE_DIR, "2020-annual-performance-report.pdf"),
    osp.join(BASE_DIR, "2021-annual-performance-report.pdf"),
    osp.join(BASE_DIR, "2022-annual-performance-report.pdf"),
]
CHROMA_PERSIST_DIRECTORY = "/Users/Jacob.Jaffe/chroma_db"


# State definitions for different modes

class WebSearchState(TypedDict):
    """State for web_search mode"""
    query: str
    search_results: str  # Formatted as JSON string
    answer: str


class DocumentRAGState(TypedDict):
    """State for document_rag mode"""
    question: str
    retrieved_docs: str  # Formatted as JSON string
    answer: str


class CorrectiveRAGState(TypedDict):
    """State for corrective_rag mode"""
    question: str
    history: str
    retrieved_docs: str  # Formatted as JSON string
    grade_result: str
    rewritten_query: str
    web_results: str  # Formatted as JSON string
    answer: str
    sources: List[str]


class LLMRAGToolsAgent(ChatInterface):
    """
    Consolidated RAG agent that supports three operational modes:
    - web_search: Web search with Tavily
    - document_rag: Document-based RAG with ChromaDB
    - corrective_rag: Hybrid approach with intelligent routing

    The mode determines which workflow graph is built and executed.
    """

    def __init__(self, mode: Literal["web_search", "document_rag", "corrective_rag"] = "corrective_rag"):
        """
        Initialize the LLM RAG Tools Agent with the specified mode.

        Args:
            mode: Operating mode - "web_search", "document_rag", or "corrective_rag"
        """
        self.mode = mode
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self.search_tool = None
        self.graph = None
        self.tracer = None

    def initialize(self) -> None:
        """
        Initialize all components needed for the selected mode.

        This includes:
        - LLM initialization (all modes)
        - Tavily search tool (web_search and corrective_rag modes)
        - OpenAI embeddings and ChromaDB (document_rag and corrective_rag modes)
        - LangGraph workflow construction
        - Opik tracer for observability
        """
        print(f"Initializing LLM RAG Tools Agent in '{self.mode}' mode...")

        # Initialize LLM (required for all modes)
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")

        # Initialize Tavily search tool for web_search and corrective_rag modes
        if self.mode in ["web_search", "corrective_rag"]:
            self.search_tool = TavilySearch(
                max_results=5,
                include_answer=True if self.mode == "web_search" else False,
                include_raw_content=False,
                include_images=False,
                search_depth="advanced",
            )
            print("Tavily search tool initialized.")

        # Initialize embeddings and vector store for document_rag and corrective_rag modes
        if self.mode in ["document_rag", "corrective_rag"]:
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                persist_directory=CHROMA_PERSIST_DIRECTORY,
                collection_name="opm_documents"
            )

            # Check if documents already exist in ChromaDB
            has_existing_documents = len(self.vector_store.get(limit=1)['ids']) > 0
            if has_existing_documents:
                print("ChromaDB found - reusing existing documents.")
            else:
                print("No existing ChromaDB found - processing and embedding documents...")
                docs = self._load_and_process_documents()
                print(f"Loaded and chunked {len(docs)} document pieces")
                self.vector_store.add_documents(docs)
                print("Embeddings processed and stored in ChromaDB.")

        # Build the appropriate graph based on mode
        if self.mode == "web_search":
            self.graph = self._build_web_search_graph()
            project_name = "rag-web-search"
        elif self.mode == "document_rag":
            self.graph = self._build_document_rag_graph()
            project_name = "rag-document"
        else:  # corrective_rag
            self.graph = self._build_corrective_rag_graph()
            project_name = "rag-corrective"

        # Initialize Opik tracer
        self.tracer = OpikTracer(
            graph=self.graph.get_graph(xray=True),
            project_name=project_name
        )

        print(f"Initialization complete. Ready to process messages in '{self.mode}' mode.")

    def _load_and_process_documents(self) -> List[Document]:
        """
        Load PDF documents and split them into chunks for embedding.

        Returns:
            List of Document objects with chunked content and metadata
        """
        docs = []
        for file_path in FILE_PATHS:
            print(f"Loading {osp.basename(file_path)}")
            loader = PyPDFLoader(file_path)
            page_docs = loader.load()

            combined_text = "\n".join([doc.page_content for doc in page_docs])

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(combined_text)

            docs.extend([
                Document(page_content=chunk, metadata={"source": file_path})
                for chunk in chunks
            ])
        return docs

    # ========== Web Search Graph ==========

    def _build_web_search_graph(self):
        """
        Build the LangGraph workflow for web_search mode.

        Graph structure: START → web_search → summarize_results → END

        Returns:
            Compiled LangGraph
        """
        graph = StateGraph(WebSearchState)
        graph.add_node("web_search", self._web_search_node)
        graph.add_node("summarize_results", self._summarize_web_results_node)
        graph.add_edge(START, "web_search")
        graph.add_edge("web_search", "summarize_results")
        graph.add_edge("summarize_results", END)
        return graph.compile()

    def _web_search_node(self, state: WebSearchState):
        """
        Execute web search using Tavily and format results as JSON.

        Args:
            state: Current graph state with query

        Returns:
            Updated state with search_results
        """
        results = self.search_tool.invoke({"query": state["query"]})

        # Extract and format relevant fields from each result
        formatted_results = []
        for result in results['results']:
            formatted_result = {
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "raw_content": result.get("raw_content", "")
            }
            formatted_results.append(formatted_result)

        # Convert to pretty JSON string with newlines between results
        formatted_json = "\n\n".join([
            json.dumps(result, indent=2)
            for result in formatted_results
        ])

        return {"search_results": formatted_json}

    def _summarize_web_results_node(self, state: WebSearchState):
        """
        Summarize web search results using the LLM.

        Args:
            state: Current graph state with search_results

        Returns:
            Updated state with answer
        """
        chain = WEB_SEARCH_SUMMARIZER_PROMPT | self.llm | StrOutputParser()
        answer = chain.invoke({
            "query": state["query"],
            "search_results": state["search_results"],
            "history": ""
        })
        return {"answer": answer}

    # ========== Document RAG Graph ==========

    def _build_document_rag_graph(self):
        """
        Build the LangGraph workflow for document_rag mode.

        Graph structure: START → retrieval → generation → END

        Returns:
            Compiled LangGraph
        """
        graph = StateGraph(DocumentRAGState)
        graph.add_node("retrieval", self._retrieval_node)
        graph.add_node("generation", self._generation_node)
        graph.add_edge(START, "retrieval")
        graph.add_edge("retrieval", "generation")
        graph.add_edge("generation", END)
        return graph.compile()

    def _retrieval_node(self, state: DocumentRAGState):
        """
        Retrieve relevant document chunks from ChromaDB.

        Args:
            state: Current graph state with question

        Returns:
            Updated state with retrieved_docs
        """
        docs = self.vector_store.similarity_search(state["question"], k=4)
        print(f"Retrieved {len(docs)} matching chunks")

        # Format retrieved documents as pretty JSON
        formatted_docs = []
        for idx, doc in enumerate(docs, 1):
            filename = osp.basename(doc.metadata.get("source", "unknown"))
            formatted_doc = {
                "id": idx,
                "filename": filename,
                "content": doc.page_content
            }
            formatted_docs.append(formatted_doc)

        # Convert to pretty JSON string with newlines between documents
        formatted_json = "\n\n".join([
            json.dumps(doc, indent=2)
            for doc in formatted_docs
        ])

        return {"retrieved_docs": formatted_json}

    def _generation_node(self, state: DocumentRAGState):
        """
        Generate answer from retrieved documents using structured output.

        Args:
            state: Current graph state with retrieved_docs and question

        Returns:
            Updated state with answer
        """
        prompt = DOCUMENT_RAG_PROMPT
        llm_structured = self.llm.with_structured_output(RagGenerationResponse)
        chain = prompt | llm_structured

        print(f"Generating answer for question: {state['question']}")
        response = chain.invoke({
            "retrieved_docs": state["retrieved_docs"],
            "question": state["question"],
            "history": ""
        })

        response_str = f"Answer: {response.answer}\n"
        if response.sources:
            clean_sources = [osp.basename(src) for src in response.sources]
            response_str += "\nSources:\n" + "\n".join(f"- {src}" for src in clean_sources)
        return {"answer": response_str}

    # ========== Corrective RAG Graph ==========

    def _build_corrective_rag_graph(self):
        """
        Build the LangGraph workflow for corrective_rag mode.

        Graph structure:
        START → retrieve → grade → [if sufficient] → generate → END
                                 → [if insufficient] → web_search → summarize_web → END

        Returns:
            Compiled LangGraph
        """
        graph = StateGraph(CorrectiveRAGState)
        graph.add_node("retrieve", self._corrective_retrieve_node)
        graph.add_node("grade", self._grade_documents_node)
        graph.add_node("generate", self._corrective_generate_node)
        graph.add_node("web_search", self._corrective_web_search_node)
        graph.add_node("summarize_web", self._corrective_summarize_web_node)

        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "grade")
        graph.add_conditional_edges(
            "grade",
            self._decide_route,
            {"generate": "generate", "web_search": "web_search"}
        )
        graph.add_edge("generate", END)
        graph.add_edge("web_search", "summarize_web")
        graph.add_edge("summarize_web", END)

        return graph.compile()

    def _corrective_retrieve_node(self, state: CorrectiveRAGState):
        """
        Retrieve relevant document chunks for corrective RAG.

        Args:
            state: Current graph state with question

        Returns:
            Updated state with retrieved_docs
        """
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 10})
        docs = retriever.invoke(state["question"])

        # Format retrieved documents as pretty JSON
        formatted_docs = []
        for idx, doc in enumerate(docs, 1):
            filename = osp.basename(doc.metadata.get("source", "unknown"))
            formatted_doc = {
                "id": idx,
                "filename": filename,
                "content": doc.page_content
            }
            formatted_docs.append(formatted_doc)

        # Convert to pretty JSON string with newlines between documents
        formatted_json = "\n\n".join([
            json.dumps(doc, indent=2)
            for doc in formatted_docs
        ])

        return {"retrieved_docs": formatted_json}

    def _grade_documents_node(self, state: CorrectiveRAGState):
        """
        Grade the relevance of retrieved documents using structured LLM output.

        Args:
            state: Current graph state with question and retrieved_docs

        Returns:
            Updated state with grade_result
        """
        prompt = DOCUMENT_GRADING_PROMPT
        llm_struct = self.llm.with_structured_output(DocumentGradingResponse)
        chain = prompt | llm_struct

        response = chain.invoke({
            "question": state["question"],
            "retrieved_docs": state["retrieved_docs"],
            "history": state.get("history", "")
        })
        print(f"Document grading response: {response}")

        # Store the grading result
        grade_result = "sufficient" if response.is_sufficient == 1 else "insufficient"
        return {"grade_result": grade_result}

    def _decide_route(self, state: CorrectiveRAGState) -> str:
        """
        Routing function to decide between generation and web search.

        Args:
            state: Current graph state with grade_result

        Returns:
            Next node name: "generate" or "web_search"
        """
        if state.get("grade_result") == "sufficient":
            return "generate"
        else:
            return "web_search"

    def _corrective_generate_node(self, state: CorrectiveRAGState):
        """
        Generate answer from documents in corrective RAG mode.

        Args:
            state: Current graph state with retrieved_docs and question

        Returns:
            Updated state with answer
        """
        prompt = DOCUMENT_RAG_PROMPT
        llm_struct = self.llm.with_structured_output(RagGenerationResponse)
        chain = prompt | llm_struct

        response = chain.invoke({
            "retrieved_docs": state["retrieved_docs"],
            "question": state["question"],
            "history": state.get("history", "")
        })

        text = f"Answer: {response.answer}\n"
        if response.sources:
            names = [osp.basename(src) for src in response.sources]
            text += "\nSources:\n" + "\n".join(f"- {s}" for s in names)
        return {"answer": text}

    def _corrective_web_search_node(self, state: CorrectiveRAGState):
        """
        Perform web search when documents are insufficient.

        Args:
            state: Current graph state with question

        Returns:
            Updated state with web_results
        """
        results = self.search_tool.invoke({"query": state["question"]})

        # Extract and format relevant fields from each result
        formatted_results = []
        for result in results['results']:
            formatted_result = {
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "raw_content": result.get("raw_content", "")
            }
            formatted_results.append(formatted_result)

        # Convert to pretty JSON string with newlines between results
        formatted_json = "\n\n".join([
            json.dumps(result, indent=2)
            for result in formatted_results
        ])

        return {"web_results": formatted_json}

    def _corrective_summarize_web_node(self, state: CorrectiveRAGState):
        """
        Summarize web search results in corrective RAG mode.

        Args:
            state: Current graph state with web_results and question

        Returns:
            Updated state with answer
        """
        chain = WEB_SEARCH_SUMMARIZER_PROMPT | self.llm | StrOutputParser()
        answer = chain.invoke({
            "query": state["question"],
            "search_results": state["web_results"],
            "history": state.get("history", "")
        })
        return {"answer": answer}

    # ========== ChatInterface Implementation ==========

    def process_message(self, message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Process a user message through the appropriate workflow based on the mode.

        Args:
            message: User's question or query
            chat_history: Optional list of previous messages for context

        Returns:
            Generated answer with sources (if applicable)
        """
        # Format chat history if provided
        history_str = ""
        if chat_history:
            history_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in chat_history
            ])

        # Initialize state based on mode
        if self.mode == "web_search":
            state = {"query": message}
        elif self.mode == "document_rag":
            state = {"question": message}
        else:  # corrective_rag
            state = {
                "question": message,
                "history": history_str
            }

        # Execute graph with Opik tracer
        config = {
            "configurable": {"thread_id": f"{self.mode}_session"},
            "callbacks": [self.tracer],
        }

        result = self.graph.invoke(state, config=config)
        print(f"Final Graph State: {result}")
        return result["answer"]
