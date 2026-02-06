# TradingAgents Plus (TA+)

> **An enhanced, interactive GUI version of the [TradingAgents](https://github.com/TauricResearch/TradingAgents) framework.**

TradingAgents Plus transforms the powerful multi-agent financial framework into a modern, user-friendly desktop application. It adds a real-time visualization layer, local AI support, and a flexible configuration system.

![TA+ Interface](assets/ta_plus_preview.png)

## ✨ Key Enhancements

### 🖥️ Modern Vue.js GUI
- **Real-Time Feed**: Watch agents think, debate, and analyze in real-time.
- **Collapsible Cards**: Drill down into specific agent outputs or keep the feed clean.
- **Markdown Report Viewer**: Read beautifully formatted financial reports with tables and charts.

### 🔒 Local & Private AI
- **Ollama Integration**: Run the entire stack locally using models like Llama 3 or Mistral.
- **Cost Effective**: Save on API costs by offloading "Quick Thinking" tasks to local models.

### 🔌 Multi-Provider Support
configure the system with your preferred AI providers:
- **OpenAI** (GPT-4o)
- **Anthropic** (Claude 3.5 Sonnet)
- **Google** (Gemini 1.5 Pro)
- **Groq** (Llama 3 70B - Fast!)
- **Deepseek / Qwen**

## 🚀 Quick Start

For detailed setup instructions, see [howto.md](howto.md).

### 1. Requirements
- Python 3.10+
- Node.js & npm

### 2. Setup (Summary)
```bash
# Backend
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload

# Frontend (New Terminal)
cd frontend
npm install
npm run dev
```

## 🏗️ Architecture

TA+ preserves the core logic of the original TradingAgents graph:

1.  **Analyst Team**: Market, News, Fundamentals, Sentiment.
2.  **Investment Debate**: Bull vs. Bear researchers.
3.  **Risk Management**: Trader proposes plan -> Risk/Safe/Neutral Analysts critique -> Judge decides.

See [strategys.md](strategys.md) for a deep dive into the agent flow.

## 📄 Original Documentation

This project is built upon the incredible work of the Tauric Research team.
For the original scientific paper and cli documentation, please refer to:
- [README_original.md](README_original.md)
- [Original Repository](https://github.com/TauricResearch/TradingAgents)

---
*TradingAgent Plus is a community enhancement and is not affiliated with Tauric Research.*
