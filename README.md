# 📋 AI-Powered Grant Proposal Assistant

An AI-driven grant writing tool using **Streamlit + Ollama**.  
No paid APIs. Fully local. Three specialized agents help you draft, budget, and refine proposals.

## 🤖 AI Agents

| Agent | Role |
|-------|------|
| **Outline Designer** | Creates a full section-by-section proposal outline tailored to the funding agency |
| **Budget Estimator** | Builds a detailed, OMB-compliant budget with line items and justification |
| **Reviewer Simulation** | Simulates expert peer review to find weaknesses before submission |

## 📁 Project Structure

```
grant_assistant/
├── app.py              # Main Streamlit UI (5 tabs)
├── agents.py           # 3 Ollama-powered AI agents
├── memory.py           # Topic-based versioning and persistent memory
├── requirements.txt    # Python dependencies
├── grant_memory/       # Auto-created: stores topic memory and versions
└── README.md
```

## ⚙️ Setup

### 1. Install Ollama
Download from [ollama.com](https://ollama.com)

### 2. Pull a Model
```bash
ollama pull llama3.2
```
> Also works with `mistral`, `gemma2`, `phi3`. Update `MODEL` in `agents.py`.

### 3. Start Ollama
```bash
ollama serve
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App
```bash
streamlit run app.py
```

## 🚀 How to Use

1. **Enter topic, goals, and funding agency** in the sidebar
2. **Tab 1 — Outline Designer**: Generate a complete proposal skeleton
3. **Tab 2 — Budget Estimator**: Get a line-item budget with justifications
4. **Tab 3 — Reviewer Simulation**: Choose a reviewer persona and get scored feedback
5. **Tab 4 — Version History**: View all versions with rationale and timestamps
6. **Tab 5 — Export**: Download a combined `.txt` proposal document

## 🧠 Memory & Versioning

- Each **topic** gets its own memory file in `grant_memory/`
- Every generated outline, budget, or review is **auto-versioned** with a rationale
- The Outline Designer **incorporates reviewer feedback** if a review exists in memory
- Memory persists across sessions — pick up where you left off

## 🔧 Customization

- **Change model**: Edit `MODEL = "llama3.2"` in `agents.py`
- **Add reviewer personas**: Extend the `reviewer_personas` dict in `agents.py`
- **Adjust indirect rate**: Set your institution's F&A rate in the Budget tab slider
