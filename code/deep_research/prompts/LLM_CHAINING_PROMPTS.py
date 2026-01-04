"""Prompts for LLM Chaining Agent (Week 1).

Contains all prompts for query classification and response generation,
both with and without conversation history support.
"""

from langchain_core.prompts import ChatPromptTemplate

# Classifier prompt (without history - for Part 1 & Part 2)
CLASSIFIER_PROMPT = ChatPromptTemplate.from_template("""
Classify the given user question into one of the specified categories based on its nature.

- Factual Questions: Questions starting with phrases like "What is...?" or "Who invented...?" should be classified as 'factual'.
- Analytical Questions: Questions starting with phrases like "How does...?" or "Why do...?" should be classified as 'analytical'.
- Comparison Questions: Questions starting with phrases like "What's the difference between...?" should be classified as 'comparison'.
- Definition Requests: Questions starting with phrases like "Define..." or "Explain..." should be classified as 'definition'.

If the question does not fit into any of these categories, return 'default'.

# Steps

1. Analyze the user question.
2. Determine which category the question fits into based on its structure and keywords.
3. Return the corresponding category or 'default' if none apply.

# Output Format

- Return only the category word: 'factual', 'analytical', 'comparison', 'definition', or 'default'.
- Do not include any extra text or quotes in the output.

# Examples

- **Example 1**
* Question: What is the highest mountain in the world?
* Response: factual

- **Example 2**
* Question: What's the difference between OpenAI and Anthropic?
* Response: comparison

User question: {question}
""")

# Classifier prompt with calculation and datetime (Part 2)
CLASSIFIER_PROMPT_WITH_TOOLS = ChatPromptTemplate.from_template("""
Classify the given user question into one of the specified categories based on its nature, including all defined categories.

- Factual Questions: Questions starting with phrases like "What is...?" or "Who invented...?" should be classified as 'factual'.
- Analytical Questions: Questions starting with phrases like "How does...?" or "Why do...?" should be classified as 'analytical'.
- Comparison Questions: Questions starting with phrases like "What's the difference between...?" should be classified as 'comparison'.
- Definition Requests: Questions starting with phrases like "Define..." or "Explain..." should be classified as 'definition'.
- Datetime Questions: Questions related to date or time computation should be classified as 'datetime'.
- Calculation Questions: Questions requiring mathematical computation, not associated with date or time, should be classified as 'calculation'.

If the question does not fit into any of these categories, return 'default'.

# Steps

1. Analyze the user question.
2. Determine which category the question fits into based on its structure and keywords.
3. Return the corresponding category or 'default' if none apply.

# Output Format

- Return only the category word: 'factual', 'analytical', 'comparison', 'definition', 'datetime', 'calculation', or 'default'.
- Do not include any extra text or quotes in the output.

# Examples

- **Example 1**
  * Question: What is the highest mountain in the world?
  * Response: factual

- **Example 2**
  * Question: What's the difference between OpenAI and Anthropic?
  * Response: comparison

- **Example 3**
  * Question: What's an 18% tip of a $105 bill?
  * Response: calculation

- **Example 4**
  * Question: What day is it today?
  * Response: datetime

User question: {question}
""")

# Classifier prompt with history (Part 3)
CLASSIFIER_PROMPT_WITH_HISTORY = ChatPromptTemplate.from_template("""
Classify the given user question into one of the specified categories based on its nature, including all defined categories.

- Factual Questions: Questions starting with phrases like "What is...?" or "Who invented...?" should be classified as 'factual'.
- Analytical Questions: Questions starting with phrases like "How does...?" or "Why do...?" should be classified as 'analytical'.
- Comparison Questions: Questions starting with phrases like "What's the difference between...?" should be classified as 'comparison'.
- Definition Requests: Questions starting with phrases like "Define..." or "Explain..." should be classified as 'definition'.
- Datetime Questions: Questions related to date or time computation should be classified as 'datetime'.
- Calculation Questions: Questions requiring mathematical computation, not associated with date or time, should be classified as 'calculation'.

If the question does not fit into any of these categories, return 'default'.

# Steps

1. Analyze the user question.
2. Determine which category the question fits into based on its structure and keywords.
3. Return the corresponding category or 'default' if none apply.

# Output Format

- Return only the category word: 'factual', 'analytical', 'comparison', 'definition', 'datetime', 'calculation', or 'default'.
- Do not include any extra text or quotes in the output.

# Examples

- **Example 1**
  * Question: What is the highest mountain in the world?
  * Response: factual

- **Example 2**
  * Question: What's the difference between OpenAI and Anthropic?
  * Response: comparison

- **Example 3**
  * Question: What's an 18% tip of a $105 bill?
  * Response: calculation

- **Example 4**
  * Question: What day is it today?
  * Response: datetime

Use information from the conversation history only if relevant to the above user query, otherwise ignore the history.
Conversation history with the user:
{history}

User question: {question}

""")

# Response prompts (without history - for Part 1 & Part 2)
RESPONSE_PROMPTS = {
    "factual": ChatPromptTemplate.from_template(
        """
        Answer the following question concisely with a direct fact. Avoid unnecessary details.

        User question: "{question}"
        Answer:
        """
    ),
    "analytical": ChatPromptTemplate.from_template(
        """
        Provide a detailed explanation with reasoning for the following question. Break down the response into logical steps.

        User question: "{question}"
        Explanation:
        """
    ),
    "comparison": ChatPromptTemplate.from_template(
        """
        Compare the following concepts. Present the answer in a structured format using bullet points or a table for clarity.

        User question: "{question}"
        Comparison:
        """
    ),
    "definition": ChatPromptTemplate.from_template(
        """
        Define the following term and provide relevant examples and use cases for better understanding.

        User question: "{question}"
        Definition:
        Examples:
        Use Cases:
        """
    ),
    "calculation": ChatPromptTemplate.from_template(
        """
        You are a smart AI model but cannot do any complex calculations. You are very good at
        translating a math question to a simple equation which can be solved by a calculator.

        Convert the user question below to a math calculation.
        Remember that the calculator can only use +, -, *, /, //, % operators,
        so only use those operators and output the final math equation.

        Examples:
        Question: What is 5 times 20?
        Answer: 5 * 20

        Question: What is the split of each person for a 4 person dinner of $100 with 20% tip?
        Answer: (100 + 0.2*100) / 4

        Question: Round 100.5 to the nearest integer.
        Answer: 100.5 // 1

        User Query: "{question}"

        The final output should ONLY contain the valid math equation, no words or any other text.
        Otherwise the calculator tool will error out.
        """
    ),
    "datetime": ChatPromptTemplate.from_template(
        """You are a smart AI which is very good at translating a question in english
        to a simple python code to output the result. You'll only be given queries related
        to date and time, for which generate the python code required to get the answer.
        Your code will be sent to a Python interpreter and the expectation is to print the output on the final line.

        These are the ONLY python libraries you have access to - math, datetime, time.

        Examples:
        Question: What day is it today?
        Answer: print(datetime.now().strftime("%A"))

        Question: What is the date of 30 days from now?
        Answer: print(datetime.now() + timedelta(days=30))

        User Query: "{question}"

        The final output should ONLY contain valid Python code, no words or any other text.
        Otherwise the Python interpreter tool will error out. Avoid returning ``` or python
        in the output, just return the code directly.
        """
    ),
    "default": ChatPromptTemplate.from_template(
        """
        Respond your best to answer the following question but keep it very brief.

        User question: "{question}"
        Answer:
        """
    )
}

# Response prompts with history (Part 3)
RESPONSE_PROMPTS_WITH_HISTORY = {
    "factual": ChatPromptTemplate.from_template(
        """
        Answer the following question concisely with a direct fact. Avoid unnecessary details.

        Use information from the conversation history only if relevant to the above user query, otherwise ignore the history.
        Conversation history with the user:
        {history}

        User question: "{question}"
        Answer:
        """
    ),
    "analytical": ChatPromptTemplate.from_template(
        """
        Provide a detailed explanation with reasoning for the following question. Break down the response into logical steps.

        Use information from the conversation history only if relevant to the above user query, otherwise ignore the history.
        Conversation history with the user:
        {history}

        User question: "{question}"
        Explanation:
        """
    ),
    "comparison": ChatPromptTemplate.from_template(
        """
        Compare the following concepts. Present the answer in a structured format using bullet points or a table for clarity.

        Use information from the conversation history only if relevant to the above user query, otherwise ignore the history.
        Conversation history with the user:
        {history}

        User question: "{question}"
        Comparison:
        """
    ),
    "definition": ChatPromptTemplate.from_template(
        """
        Define the following term and provide relevant examples and use cases for better understanding.

        Use information from the conversation history only if relevant to the above user query, otherwise ignore the history.
        Conversation history with the user:
        {history}

        User question: "{question}"
        Definition:
        Examples:
        Use Cases:
        """
    ),
    "calculation": ChatPromptTemplate.from_template(
        """
        You are a smart AI model but cannot do any complex calculations. You are very good at
        translating a math question to a simple equation which can be solved by a calculator.

        Convert the user question below to a math calculation.
        Remember that the calculator can only use +, -, *, /, //, % operators,
        so only use those operators and output the final math equation.

        Examples:
        Question: What is 5 times 20?
        Answer: 5 * 20

        Question: What is the split of each person for a 4 person dinner of $100 with 20% tip?
        Answer: (100 + 0.2*100) / 4

        Question: Round 100.5 to the nearest integer.
        Answer: 100.5 // 1

        Use information from the conversation history only if relevant to the above user query, otherwise ignore the history.
        Conversation history with the user:
        {history}

        User Query: "{question}"

        The final output should ONLY contain the valid math equation, no words or any other text.
        Otherwise the calculator tool will error out.
        """
    ),
    "datetime": ChatPromptTemplate.from_template(
        """You are a smart AI which is very good at translating a question in english
        to a simple python code to output the result. You'll only be given queries related
        to date and time, for which generate the python code required to get the answer.
        Your code will be sent to a Python interpreter and the expectation is to print the output on the final line.

        These are the ONLY python libraries you have access to - math, datetime, time.

        Examples:
        Question: What day is it today?
        Answer: print(datetime.now().strftime("%A"))

        Question: What is the date of 30 days from now?
        Answer: print(datetime.now() + timedelta(days=30))

        Use information from the conversation history only if relevant to the above user query, otherwise ignore the history.
        Conversation history with the user:
        {history}

        User Query: "{question}"

        The final output should ONLY contain valid Python code, no words or any other text.
        Otherwise the Python interpreter tool will error out. Avoid returning ``` or python
        in the output, just return the code directly.
        """
    ),
    "default": ChatPromptTemplate.from_template(
        """
        Respond your best to answer the following question but keep it very brief.

        Use information from the conversation history only if relevant to the above user query, otherwise ignore the history.
        Conversation history with the user:
        {history}

        User question: "{question}"
        Answer:
        """
    )
}
