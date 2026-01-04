# Deep Research Agent

A production-ready AI agents framework demonstrating progressive enhancement of LLM capabilities through multiple agent architectures.

## Project Structure

```
code/
├── run.py                             # Main entry point
├── deep_research/
│   ├── agents/                        # Agent implementations
│   │   ├── llm_chaining.py            # Query understanding & basic tools
│   │   ├── llm_rag_tools.py           # Web search & document RAG
│   │   └── react_multi_agent.py       # ReAct agents & deep research
│   ├── core/
│   │   ├── chat_interface.py          # Base interface for all agents
│   │   └── factory.py                 # Agent factory with enum-based selection
│   ├── prompts/
│   │   ├── LLM_CHAINING_PROMPTS.py   # Query classification prompts
│   │   ├── RAG_PROMPTS.py            # Document & web search prompts
│   │   └── AGENT_PROMPTS.py          # ReAct & research agent prompts
│   ├── tools/
│   │   └── calculator.py              # Calculator tool
│   └── app.py                         # Gradio UI setup
└── verify_structure.py                # Structure verification script
```

## Quick Start

### Prerequisites
- Python 3.11.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Tavily API key ([Get one here](https://tavily.com/))
- Optional: Opik API key for observability ([Get one here](https://www.comet.com/site/products/opik/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/deep_research_agent.git
   cd deep_research_agent/code
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv

   # On macOS/Linux:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the `code/` directory:
   ```bash
   touch .env
   ```

   Add your API keys to `.env`:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   OPIK_API_KEY=your_opik_api_key_here  # Optional
   OPIK_WORKSPACE=your_workspace_name    # Optional
   ```

   **⚠️ Important**: Never commit your `.env` file to version control. It's already in `.gitignore`.

### Running Agents

```bash
# High-level agent types (use most advanced mode)
python run.py --agent LLM_Chaining
python run.py --agent LLM_RAG_Tools
python run.py --agent ReaAct_Multi_Agent

# Specific modes
python run.py --agent llm_chaining_query
python run.py --agent rag_web_search
python run.py --agent react_deep_research
```

## Agent Families

### 1. LLM Chaining Agents

**File:** [agents/llm_chaining.py](deep_research/agents/llm_chaining.py)

Progressive enhancement of basic LLM capabilities:

- **`llm_chaining_query`** - Query understanding with 5-category classification
  - Categories: factual, analytical, comparison, definition, default
  - Basic LangGraph workflow: classify → respond

- **`llm_chaining_tools`** - Adds calculator and datetime tools
  - 7 categories including calculation and datetime
  - Tool execution within LangGraph nodes

- **`llm_chaining_memory`** - Conversation history support
  - Full memory of chat history
  - Context-aware responses

**Example:**
```bash
python run.py --agent llm_chaining_tools
# Try: "What is 25 * 4 + 10?"
```

### 2. RAG (Retrieval Augmented Generation) Agents

**File:** [agents/llm_rag_tools.py](deep_research/agents/llm_rag_tools.py)

Information retrieval and synthesis:

- **`rag_web_search`** - Tavily web search integration
  - Real-time web search
  - Source citation
  - Opik tracing

- **`rag_document`** - Document RAG with ChromaDB
  - Vector embeddings (OpenAI text-embedding-3-small)
  - OPM annual reports (2019-2022)
  - Persistent vector store
  - Source citations

- **`rag_corrective`** - Hybrid corrective RAG
  - Document relevance grading
  - Conditional routing (document RAG → web search fallback)
  - Multiple knowledge source synthesis

**Example:**
```bash
python run.py --agent rag_corrective
# Try: "What were OPM's strategic objectives in 2021?"
```

### 3. ReAct Multi-Agent System

**File:** [agents/react_multi_agent.py](deep_research/agents/react_multi_agent.py)

Autonomous reasoning and action:

- **`react_tool_using`** - ReAct pattern with tools
  - Calculator, datetime, weather tools
  - Autonomous tool selection via `create_react_agent`
  - Thought → Action → Observation loop

- **`react_agentic_rag`** - Agent-driven information gathering
  - Custom evaluation loop (max 3 iterations)
  - Dynamic strategy: document search vs. web search
  - Query rewriting based on feedback

- **`react_deep_research`** - Multi-agent orchestration
  - **Research Manager**: Plans research structure (3-5 sections)
  - **Specialized Researchers**: Conduct thorough research per section
  - **Evaluator**: Quality control and iteration
  - **Report Finalizer**: Executive summary and synthesis
  - Output: Comprehensive markdown report (`~/final_report.md`)

**Example:**
```bash
python run.py --agent react_deep_research
# Try: "Research the impact of AI on employment in 2024-2025"
```

## Key Features

### LangGraph Workflows

All agents use LangGraph for state management and workflow orchestration:

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(StateType)
graph.add_node("process", process_function)
graph.add_edge(START, "process")
graph.add_edge("process", END)
compiled_graph = graph.compile()
```

### Opik Observability

RAG and ReAct agents include Opik tracing:

```python
from opik.integrations.langchain import OpikTracer

tracer = OpikTracer(
    graph=self.graph.get_graph(xray=True),
    project_name="rag-web-search"
)

result = self.graph.invoke(state, {"callbacks": [tracer]})
```

### ChromaDB Persistence

Document RAG modes use persistent vector storage:

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
)
```

## Architecture Patterns

### Factory Pattern

Central agent creation with enum-based selection:

```python
from deep_research.core.factory import AgentType, create_agent

agent = create_agent(AgentType.RAG_CORRECTIVE)
response = agent.process_message("Your query", chat_history)
```

### ChatInterface Base Class

All agents inherit from a common interface:

```python
from deep_research.core.chat_interface import ChatInterface

class MyAgent(ChatInterface):
    def initialize(self) -> None:
        # Set up LLM, tools, graphs
        pass

    def process_message(self, message: str, chat_history: List[Dict]) -> str:
        # Process message and return response
        return response
```

### Mode-Based Consolidation

Agents use mode parameters to switch behavior:

- **LLM Chaining**: Single class with conditional logic
- **RAG Tools**: Separate graph builders per mode
- **ReAct Multi-Agent**: Delegation pattern with internal agent classes

## Advanced Usage

### Custom Prompts

Modify prompts in the `prompts/` directory:

- [prompts/LLM_CHAINING_PROMPTS.py](deep_research/prompts/LLM_CHAINING_PROMPTS.py)
- [prompts/RAG_PROMPTS.py](deep_research/prompts/RAG_PROMPTS.py)
- [prompts/AGENT_PROMPTS.py](deep_research/prompts/AGENT_PROMPTS.py)

### Adding New Agents

1. Create `agents/new_agent.py` implementing `ChatInterface`
2. Add enum variant to `core/factory.py`
3. Add metadata to `app.py`
4. Run with `python run.py --agent new_agent`

### Structure Verification

Verify code structure without installing dependencies:

```bash
python verify_structure.py
```

This checks:
- File existence
- Python syntax
- Import structure
- Package naming consistency

## Available Modes

| Mode | Family | Description |
|------|--------|-------------|
| `llm_chaining_query` | LLM Chaining | Basic query classification |
| `llm_chaining_tools` | LLM Chaining | With calculator & datetime |
| `llm_chaining_memory` | LLM Chaining | With conversation history |
| `rag_web_search` | RAG Tools | Tavily web search |
| `rag_document` | RAG Tools | ChromaDB document retrieval |
| `rag_corrective` | RAG Tools | Hybrid RAG with grading |
| `react_tool_using` | ReAct | Basic ReAct with tools |
| `react_agentic_rag` | ReAct | Agent-driven RAG |
| `react_deep_research` | ReAct | Multi-agent research system |

## Example Queries

**LLM Chaining:**
- "What is the capital of France?" (factual)
- "Compare Python and Java" (comparison)
- "What is 25 * 4 + 10?" (calculation)

**RAG Tools:**
- "What were OPM's goals in 2020?" (document)
- "Latest AI developments in 2025" (web search)
- "OPM strategic objectives in 2021" (corrective)

**ReAct Multi-Agent:**
- "What day of the week is today?" (tool using)
- "OPM accomplishments in 2022" (agentic RAG)
- "Research AI impact on employment" (deep research)

## Technical Stack

- **LLM**: OpenAI GPT-4 / GPT-3.5
- **Framework**: LangChain + LangGraph
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector DB**: ChromaDB
- **Web Search**: Tavily
- **Observability**: Opik
- **UI**: Gradio
- **Language**: Python 3.11.8+

## Development

### Project Goals

This project demonstrates:
- LangChain/LangGraph agent patterns
- RAG implementation strategies
- Multi-agent orchestration
- ReAct (Reasoning + Acting) paradigm
- Production-ready code structure

### Code Quality

- All files use valid Python syntax
- Consistent import structure (`deep_research.*`)
- Type hints where applicable
- Comprehensive docstrings
- Modular, extensible design

## License

This is a personal project for learning and experimentation with AI agents.

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Opik Observability](https://www.comet.com/site/products/opik/)
- [Tavily Search API](https://tavily.com/)
