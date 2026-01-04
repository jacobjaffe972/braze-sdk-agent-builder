# Setup Guide

## Understanding Your Current Environment

Based on your terminal output:

```bash
(problem_first_ai_1) Jacob.Jaffe@BZJR6T3N9P37 code %
```

**Virtual Environment:** `problem_first_ai_1`
- Location: `/Users/Jacob.Jaffe/problem_first_ai_1/.venv/`
- This is **NOT** in your current project directory

## Installation Options

### Option 1: Use Your Existing Virtual Environment (Recommended)

Since you're already in the `problem_first_ai_1` virtual environment, just install the dependencies:

```bash
# You're already in the venv, just install requirements
pip install -r requirements.txt
```

### Option 2: Create a New Virtual Environment in This Project

If you want a dedicated venv for this project:

```bash
# Deactivate current venv
deactivate

# Create new venv in project directory
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Option 3: Quick Install (Without requirements.txt)

```bash
pip install langchain langchain-core langchain-community langgraph \
    langchain-openai langchain-tavily langchain-chroma \
    chromadb openai pypdf langchain-text-splitters \
    opik gradio python-dotenv pydantic tavily-python
```

## Environment Variables

Create a `.env` file in the `code/` directory:

```bash
# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
OPIK_API_KEY=your_opik_api_key_here
EOF
```

Or manually create `.env` with:

```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
OPIK_API_KEY=...
```

## Verify Installation

After installing dependencies, verify everything works:

```bash
python3 verify_structure.py
```

## Run Your First Agent

```bash
# LLM Chaining (no API keys needed for basic test)
python run.py --agent llm_chaining_query

# With API keys configured:
python run.py --agent LLM_Chaining
python run.py --agent rag_web_search
python run.py --agent react_deep_research
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:** Install the missing package:
```bash
pip install <package-name>
```

### Issue: "source .venv/bin/activate" fails

**Cause:** No `.venv` directory in current folder

**Solution:** Either:
1. Use your existing `problem_first_ai_1` venv (already active)
2. Create a new venv with `python3 -m venv .venv`

### Issue: Import errors with langgraph

**Fixed!** The `CompiledGraph` import error has been corrected.

### Issue: "OpenAI API key not found"

**Solution:** Create a `.env` file with your API keys (see above)

## What Was Fixed

1. ✅ Removed invalid `CompiledGraph` import from `llm_rag_tools.py`
2. ✅ Created `requirements.txt` for easy installation
3. ✅ All Python syntax verified

## Next Steps

1. Install dependencies (Option 1 recommended)
2. Configure `.env` file with API keys
3. Test with: `python run.py --agent LLM_Chaining`
