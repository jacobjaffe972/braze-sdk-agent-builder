# Quick Start Guide

## ✅ Virtual Environment Created!

A fresh virtual environment has been created at:
```
/Users/Jacob.Jaffe/deep_research_agent/code/.venv
```

## 🚀 Activation & Setup (Copy-Paste These Commands)

### Step 1: Deactivate Your Current Virtual Environment

```bash
deactivate
```

### Step 2: Activate the New Virtual Environment

```bash
cd /Users/Jacob.Jaffe/deep_research_agent/code
source .venv/bin/activate
```

You should now see `(.venv)` in your prompt instead of `(problem_first_ai_1)`.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- LangChain & LangGraph
- OpenAI & embeddings
- ChromaDB (vector store)
- Tavily (web search)
- Opik (observability)
- Gradio (UI)

### Step 4: Configure Environment Variables

Create a `.env` file:

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
OPIK_API_KEY=your_key_here
EOF
```

Then edit `.env` with your actual API keys.

### Step 5: Test the Installation

```bash
# Verify code structure
python verify_structure.py

# Run your first agent
python run.py --agent LLM_Chaining
```

## 📝 Daily Workflow

Every time you work on this project:

```bash
# Navigate to project
cd /Users/Jacob.Jaffe/deep_research_agent/code

# Activate venv
source .venv/bin/activate

# Start coding!
```

## 🎯 Available Agents

```bash
# LLM Chaining family
python run.py --agent llm_chaining_query
python run.py --agent llm_chaining_tools
python run.py --agent llm_chaining_memory
python run.py --agent LLM_Chaining          # Uses memory mode

# RAG Tools family
python run.py --agent rag_web_search
python run.py --agent rag_document
python run.py --agent rag_corrective
python run.py --agent LLM_RAG_Tools         # Uses corrective mode

# ReAct Multi-Agent family
python run.py --agent react_tool_using
python run.py --agent react_agentic_rag
python run.py --agent react_deep_research
python run.py --agent ReaAct_Multi_Agent    # Uses deep_research mode
```

## 🔧 Deactivating the Virtual Environment

When you're done:

```bash
deactivate
```

## ✨ What's Different from Before?

**Old setup:**
- Using `problem_first_ai_1` venv (located elsewhere)
- Had to navigate to a different directory

**New setup:**
- Dedicated `.venv` in this project directory
- Self-contained and portable
- Easier to manage dependencies

## 📂 Project Structure

```
code/
├── .venv/                    # ← Your new virtual environment
├── .env                      # ← API keys (create this)
├── .gitignore               # ← Keeps venv out of git
├── requirements.txt         # ← All dependencies
├── run.py                   # ← Main entry point
├── QUICKSTART.md           # ← This file
├── SETUP.md                # ← Detailed setup guide
└── deep_research/          # ← Agent code
```

## 🆘 Troubleshooting

**Issue:** `source .venv/bin/activate` doesn't work

**Solution:** Make sure you're in the correct directory:
```bash
cd /Users/Jacob.Jaffe/deep_research_agent/code
pwd  # Should show: /Users/Jacob.Jaffe/deep_research_agent/code
source .venv/bin/activate
```

**Issue:** Packages not found after installation

**Solution:** Make sure venv is activated (you should see `(.venv)` in prompt)

**Issue:** API key errors

**Solution:** Create `.env` file with your actual API keys (see Step 4)
