# How to Use Ollama with TradingAgent Plus

Ollama allows you to run powerful LLMs (like Llama 3) locally on your own computer. This is completely **free** and avoids the "Rate Limit" errors you might see with cloud providers like Groq or OpenAI.

## 1. Install Ollama
Download and install Ollama from the official website:
- **Website**: [https://ollama.com](https://ollama.com)
- Available for Windows, macOS, and Linux.

## 2. Pull the Models
Once installed, open your terminal (Command Prompt or PowerShell) and run the following command to download the Llama 3 model (approx. 4.7GB):

```powershell
ollama pull llama3
ollama pull nomic-embed-text
```

> **Note**: `nomic-embed-text` is required for the agent's memory/RAG features. `llama3` is the default reasoning model.

## 3. Verify Ollama is Running
Ollama typically runs in the background. You can check if it's active by visiting this URL in your browser:
[http://localhost:11434](http://localhost:11434)
You should see the text: `Ollama is running`.

## 4. Configure TradingAgent Plus
1.  Open **TradingAgent Plus**.
2.  Click the **Settings (Gear Icon)**.
3.  Scroll down to **Local LLM (Ollama) URL**.
4.  Ensure it is set to: `http://localhost:11434/v1` (Note the `/v1` at the end is important for compatibility).
5.  **API Key**: You do **NOT** need an API key for Ollama. The app handles this automatically.
6.  Click **Save Configuration**.

## 5. Start Analysis
1.  In the main dashboard, select **Ollama** from the "Model Provider" dropdown.
2.  Enter your Ticker (e.g., NVDA).
3.  Click **Start Research Operation**.

---

### Troubleshooting
- **"Connection Refused"**: Make sure the Ollama app is actually running in your system tray.
- **"Model not found"**: Run `ollama list` in your terminal to see which models you have. If you don't have `llama3`, run `ollama pull llama3`.
- **System Slowness**: running local models requires RAM and GPU power. If your computer is slow, try a smaller model like `llama3:8b` or stick to cloud providers.
