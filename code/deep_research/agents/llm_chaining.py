"""LLM Chaining Agent - Consolidated Week 1 Implementation.

Modes:
- query_understanding: Basic 5-category classification (factual, analytical, comparison, definition, default)
- basic_tools: Adds calculation and datetime tools (7 categories total)
- memory: Adds conversation history support with tools
"""

from typing import Dict, List, Optional, TypedDict, Literal
import contextlib
import io
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END

from deep_research.core.chat_interface import ChatInterface
from deep_research.tools.calculator import Calculator
from deep_research.prompts.LLM_CHAINING_PROMPTS import (
    CLASSIFIER_PROMPT,
    CLASSIFIER_PROMPT_WITH_TOOLS,
    CLASSIFIER_PROMPT_WITH_HISTORY,
    RESPONSE_PROMPTS,
    RESPONSE_PROMPTS_WITH_HISTORY
)


# Tool decorators for calculator and datetime
@tool
def calculator_tool(expression: str) -> str:
    """Evaluate a math expression and return the result as a string.

    Supports only basic arithmetic operations (+, -, *, /, //, %) and parentheses.

    Args:
        expression: The math expression to evaluate.

    Returns:
        The result of the math expression as a string formatted as "The answer is: {result}"
    """
    print(f"Evaluating expression: {expression}")
    result = str(Calculator.evaluate_expression(expression))
    return f"The answer is: {result}"


@tool
def datetime_tool(code: str) -> str:
    """Execute Python code to answer date or time related questions.

    NOTE: We are using exec here to execute the code, which is not a good practice for production
    as this can lead to security vulnerabilities. For the purpose of the assignment, we are assuming
    the model will only return valid and safe python code.

    Args:
        code: The python code to execute.

    Returns:
        The output of the python code as a string.
    """
    print(f"Executing code: {code}")
    output_buffer = io.StringIO()
    code = f"import datetime\nimport time\nfrom datetime import timedelta\n{code}"
    with contextlib.redirect_stdout(output_buffer):
        exec(code)
    return output_buffer.getvalue().strip()


# State definitions for different modes
class QueryState(TypedDict):
    """State for query_understanding mode."""
    question: str
    category: str
    response: str


class ToolState(TypedDict):
    """State for basic_tools mode."""
    question: str
    category: str
    response: str


class MemoryState(TypedDict):
    """State for memory mode."""
    question: str
    history: str
    category: str
    response: str


class LLMChainingAgent(ChatInterface):
    """Consolidated LLM Chaining Agent supporting multiple modes.

    This agent can operate in three modes:
    - query_understanding: Basic query classification with 5 categories
    - basic_tools: Adds calculator and datetime tools (7 categories)
    - memory: Adds conversation history support
    """

    def __init__(self, mode: Literal["query_understanding", "basic_tools", "memory"] = "memory"):
        """Initialize the LLM Chaining Agent.

        Args:
            mode: The operational mode for the agent
        """
        self.mode = mode

        # Initialize the LLM
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")

        # Build the graph based on mode
        self.graph = None
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph with conditional routing based on mode."""
        # Select the appropriate state class based on mode
        if self.mode == "query_understanding":
            state_class = QueryState
        elif self.mode == "basic_tools":
            state_class = ToolState
        else:  # memory mode
            state_class = MemoryState

        # Create the graph
        workflow = StateGraph(state_class)

        # Add classifier node
        workflow.add_node("classifier", self._classify_query)

        # Add response nodes for all modes (5 basic categories)
        workflow.add_node("factual_response", self._factual_response)
        workflow.add_node("analytical_response", self._analytical_response)
        workflow.add_node("comparison_response", self._comparison_response)
        workflow.add_node("definition_response", self._definition_response)
        workflow.add_node("default_response", self._default_response)

        # Add tool-based response nodes for basic_tools and memory modes
        if self.mode in ["basic_tools", "memory"]:
            workflow.add_node("calculation_response", self._calculation_response)
            workflow.add_node("datetime_response", self._datetime_response)

        # Set entry point
        workflow.set_entry_point("classifier")

        # Add conditional edges from classifier
        route_map = {
            "factual": "factual_response",
            "analytical": "analytical_response",
            "comparison": "comparison_response",
            "definition": "definition_response",
            "default": "default_response"
        }

        # Add tool routes for basic_tools and memory modes
        if self.mode in ["basic_tools", "memory"]:
            route_map["calculation"] = "calculation_response"
            route_map["datetime"] = "datetime_response"

        workflow.add_conditional_edges(
            "classifier",
            self._route_query,
            route_map
        )

        # Add edges from response nodes to END
        workflow.add_edge("factual_response", END)
        workflow.add_edge("analytical_response", END)
        workflow.add_edge("comparison_response", END)
        workflow.add_edge("definition_response", END)
        workflow.add_edge("default_response", END)

        if self.mode in ["basic_tools", "memory"]:
            workflow.add_edge("calculation_response", END)
            workflow.add_edge("datetime_response", END)

        # Compile the graph
        self.graph = workflow.compile()

    def _classify_query(self, state: Dict) -> Dict:
        """Classify the query into a category.

        Args:
            state: Current state containing the question (and history for memory mode)

        Returns:
            Updated state with category
        """
        # Select appropriate classifier prompt based on mode
        if self.mode == "query_understanding":
            classifier_prompt = CLASSIFIER_PROMPT
            valid_categories = ["factual", "analytical", "comparison", "definition", "default"]
        elif self.mode == "basic_tools":
            classifier_prompt = CLASSIFIER_PROMPT_WITH_TOOLS
            valid_categories = ["factual", "analytical", "comparison", "definition", "calculation", "datetime", "default"]
        else:  # memory mode
            classifier_prompt = CLASSIFIER_PROMPT_WITH_HISTORY
            valid_categories = ["factual", "analytical", "comparison", "definition", "calculation", "datetime", "default"]

        # Build classifier chain
        classifier_chain = classifier_prompt | self.llm | StrOutputParser()

        # Invoke with appropriate parameters
        if self.mode == "memory":
            category = classifier_chain.invoke({
                "question": state["question"],
                "history": state["history"]
            }).strip().lower()
        else:
            category = classifier_chain.invoke({"question": state["question"]}).strip().lower()

        # Ensure category is valid
        if category not in valid_categories:
            category = "default"

        print(f"Question: {state['question']}, Category: {category}")

        return {
            **state,
            "category": category
        }

    def _route_query(self, state: Dict) -> str:
        """Route to the appropriate response node based on category.

        Args:
            state: Current state containing the category

        Returns:
            Category name to route to
        """
        return state["category"]

    def _factual_response(self, state: Dict) -> Dict:
        """Generate factual response.

        Args:
            state: Current state

        Returns:
            Updated state with response
        """
        # Select appropriate prompts based on mode
        if self.mode == "memory":
            prompts = RESPONSE_PROMPTS_WITH_HISTORY
            response = (prompts["factual"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"],
                "history": state["history"]
            })
        else:
            prompts = RESPONSE_PROMPTS
            response = (prompts["factual"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"]
            })

        return {**state, "response": response}

    def _analytical_response(self, state: Dict) -> Dict:
        """Generate analytical response.

        Args:
            state: Current state

        Returns:
            Updated state with response
        """
        if self.mode == "memory":
            prompts = RESPONSE_PROMPTS_WITH_HISTORY
            response = (prompts["analytical"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"],
                "history": state["history"]
            })
        else:
            prompts = RESPONSE_PROMPTS
            response = (prompts["analytical"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"]
            })

        return {**state, "response": response}

    def _comparison_response(self, state: Dict) -> Dict:
        """Generate comparison response.

        Args:
            state: Current state

        Returns:
            Updated state with response
        """
        if self.mode == "memory":
            prompts = RESPONSE_PROMPTS_WITH_HISTORY
            response = (prompts["comparison"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"],
                "history": state["history"]
            })
        else:
            prompts = RESPONSE_PROMPTS
            response = (prompts["comparison"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"]
            })

        return {**state, "response": response}

    def _definition_response(self, state: Dict) -> Dict:
        """Generate definition response.

        Args:
            state: Current state

        Returns:
            Updated state with response
        """
        if self.mode == "memory":
            prompts = RESPONSE_PROMPTS_WITH_HISTORY
            response = (prompts["definition"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"],
                "history": state["history"]
            })
        else:
            prompts = RESPONSE_PROMPTS
            response = (prompts["definition"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"]
            })

        return {**state, "response": response}

    def _default_response(self, state: Dict) -> Dict:
        """Generate default response.

        Args:
            state: Current state

        Returns:
            Updated state with response
        """
        if self.mode == "memory":
            prompts = RESPONSE_PROMPTS_WITH_HISTORY
            response = (prompts["default"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"],
                "history": state["history"]
            })
        else:
            prompts = RESPONSE_PROMPTS
            response = (prompts["default"] | self.llm | StrOutputParser()).invoke({
                "question": state["question"]
            })

        return {**state, "response": response}

    def _calculation_response(self, state: Dict) -> Dict:
        """Generate math expression and execute calculator using chained tools.

        Only available in basic_tools and memory modes.

        Args:
            state: Current state

        Returns:
            Updated state with response
        """
        if self.mode == "memory":
            prompts = RESPONSE_PROMPTS_WITH_HISTORY
            chain = prompts["calculation"] | self.llm | StrOutputParser() | calculator_tool
            response = chain.invoke({
                "question": state["question"],
                "history": state["history"]
            })
        else:  # basic_tools mode
            prompts = RESPONSE_PROMPTS
            chain = prompts["calculation"] | self.llm | StrOutputParser() | calculator_tool
            response = chain.invoke({
                "question": state["question"]
            })

        return {**state, "response": response}

    def _datetime_response(self, state: Dict) -> Dict:
        """Generate Python code and execute it using chained tools.

        Only available in basic_tools and memory modes.

        Args:
            state: Current state

        Returns:
            Updated state with response
        """
        if self.mode == "memory":
            prompts = RESPONSE_PROMPTS_WITH_HISTORY
            chain = prompts["datetime"] | self.llm | StrOutputParser() | datetime_tool
            response = chain.invoke({
                "question": state["question"],
                "history": state["history"]
            })
        else:  # basic_tools mode
            prompts = RESPONSE_PROMPTS
            chain = prompts["datetime"] | self.llm | StrOutputParser() | datetime_tool
            response = chain.invoke({
                "question": state["question"]
            })

        return {**state, "response": response}

    def process_message(self, message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Process a message using the LLM chaining agent.

        Args:
            message: The user's input message
            chat_history: List of previous chat messages with 'role' and 'content' keys
                         (only used in memory mode)

        Returns:
            str: The assistant's response
        """
        # Initialize state based on mode
        if self.mode == "memory":
            # Format chat history as a string
            if chat_history:
                history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
            else:
                history = ""

            initial_state = {
                "question": message,
                "history": history,
                "category": "",
                "response": ""
            }
        else:
            # query_understanding and basic_tools modes
            initial_state = {
                "question": message,
                "category": "",
                "response": ""
            }

        # Run the graph
        result = self.graph.invoke(initial_state)

        # Return the response
        return result["response"]
