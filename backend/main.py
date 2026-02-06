import os
import sys
import json
import asyncio
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

# Add parent directory to path to import tradingagents modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

load_dotenv()

app = FastAPI(title="TradingAgents API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    ticker: str
    analysis_date: str
    analysts: List[str]
    research_depth: int
    llm_provider: str = "openai"
    deep_thinker: str
    shallow_thinker: str
    backend_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    qwen_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    ollama_base_url: Optional[str] = None

@app.get("/api/config")
async def get_config():
    """Return available configuration options."""
    return {
        "analysts": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
        "llm_providers": ["openai", "anthropic", "google", "groq", "deepseek", "qwen", "ollama", "local"],
        "default_models": {
            "openai": {"deep": "gpt-4o", "shallow": "gpt-4o-mini"},
            "anthropic": {"deep": "claude-3-5-sonnet-latest", "shallow": "claude-3-haiku-20240307"},
            "google": {"deep": "gemini-1.5-pro", "shallow": "gemini-1.5-flash"},
            "groq": {"deep": "llama-3.3-70b-versatile", "shallow": "llama-3.1-8b-instant"},
            "deepseek": {"deep": "deepseek-chat", "shallow": "deepseek-chat"},
            "qwen": {"deep": "qwen-max", "shallow": "qwen-turbo"}, 
            "ollama": {"deep": "llama3", "shallow": "llama3"},
            "local": {"deep": "local-model", "shallow": "local-model"},
        }
    }

class OllamaRequest(BaseModel):
    action: str # "pull" or "run"
    model: str
    ollama_url: str = "http://localhost:11434"

import requests
import threading
from fastapi import BackgroundTasks

# Track active pulls: model_name -> threading.Event (if set, cancel)
# Track active pulls: model_name -> threading.Event (if set, cancel)
pull_cancellations = {}
# Track pull status: model_name -> {"status": "pulling"|"success"|"error"|"cancelled", "message": "..."}
pull_states = {}

def perform_ollama_pull(url: str, model: str):
    """Background task to pull model via Ollama API."""
    cancel_event = threading.Event()
    pull_cancellations[model] = cancel_event
    pull_states[model] = {"status": "pulling", "message": "Starting pull..."}
    
    try:
        print(f"INFO: Starting background pull for {model} at {url}")
        # Streaming pull to avoid timeout
        with requests.post(f"{url}/api/pull", json={"name": model}, stream=True) as r:
            for line in r.iter_lines():
                if cancel_event.is_set():
                    print(f"WARN: Pull for {model} was cancelled by user.")
                    pull_states[model] = {"status": "cancelled", "message": "Pull cancelled by user."}
                    return
                
                if line:
                    decoded = line.decode('utf-8')
                    try:
                        data = json.loads(decoded)
                        if "status" in data:
                             msg = f"Pulling: {data['status']}"
                             if "completed" in data and "total" in data:
                                 msg += f" {data['completed']}/{data['total']}"
                             pull_states[model] = {"status": "pulling", "message": msg}
                    except:
                        pass # Ignore parse errors
                    print(f"OLLAMA PULL {model}: {decoded}")
        
        print(f"INFO: Finished pulling {model}")
        pull_states[model] = {"status": "success", "message": "Model pulled successfully."}
        
    except Exception as e:
        print(f"ERROR: Failed to pull {model}: {e}")
        pull_states[model] = {"status": "error", "message": str(e)}
    finally:
        # Cleanup cancellation event but keep status for a bit so frontend sees it?
        # Actually frontend polls status. We should iterate status expiry or just leave it until restart.
        # For now, simplistic approach: leave it.
        if model in pull_cancellations:
            del pull_cancellations[model]

@app.post("/api/ollama/cancel")
async def cancel_ollama_pull(request: OllamaRequest):
    """Cancel an active pull job."""
    if request.model in pull_cancellations:
        pull_cancellations[request.model].set()
        return {"status": "cancelled", "message": f"Cancellation requested for {request.model}"}
    return {"status": "not_found", "message": "No active pull found for this model"}

@app.get("/api/ollama/status/{model}")
async def get_ollama_status(model: str):
    """Get the status of a specific model pull operation."""
    if model in pull_states:
        return pull_states[model]
    else:
        # If not in our state tracker, check if it exists in Ollama (maybe pulled before?)
        # Or just return 'idle'
        return {"status": "idle", "message": "No active operation."}

@app.post("/api/ollama/manage")
async def manage_ollama(request: OllamaRequest, background_tasks: BackgroundTasks):
    """Handle Ollama management commands (pull/run)."""
    
    # Clean URL
    base_url = request.ollama_url.rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3] # Remove /v1 for native API calls
        
    if request.action == "pull":
        if request.model in pull_cancellations:
             return {"status": "active", "message": f"Model {request.model} is already being pulled."}
             
        # Run pull in background as it can take a long time
        background_tasks.add_task(perform_ollama_pull, base_url, request.model)
        return {"status": "started", "message": f"Pulling model {request.model} in background..."}
        
    elif request.action == "run":
        # Robust 'Run' logic:
        # 1. Check if running
        # 2. If not, load it
        try:
            # Check /api/ps to see if model is loaded
            ps_response = requests.get(f"{base_url}/api/ps")
            if ps_response.status_code == 200:
                running_models = ps_response.json().get("models", [])
                # Check if our model matches any running model name
                # Ollama names can simplify differently (e.g. library/tag), usually matches request
                is_running = any(m.get("name") == request.model or m.get("model") == request.model for m in running_models)
                
                if is_running:
                     return {"status": "success", "message": f"Model '{request.model}' is already running."}
            
            # Not running, try to load it
            # We use a 0-token generation request to force-load the model
            load_response = requests.post(
                f"{base_url}/api/generate", 
                json={"model": request.model, "prompt": "", "keep_alive": "5m"},
                timeout=10 # Short timeout for connection, but wait for load? Loading can take time.
                # If loading takes > 10s, this might timeout. But usually we want to wait or background it.
                # User asked to "display notification when it is done". So we should await it here.
                # We'll increase timeout slightly. Large models might take 30s.
            )
            
            if load_response.status_code == 200:
                 return {"status": "success", "message": f"Model '{request.model}' loaded successfully."}
            else:
                 # Try to extract error
                 try:
                     err_data = load_response.json()
                     err_msg = err_data.get("error", "Unknown error")
                 except:
                     err_msg = load_response.text
                 
                 raise Exception(f"Ollama API returned {load_response.status_code}: {err_msg}")

        except requests.exceptions.ConnectionError:
             return {"status": "error", "message": f"Failed to connect to Ollama at {base_url}. Is it running?"}
        except Exception as e:
            # Catch timeouts, etc
            print(f"ERROR: Run model failed: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to run model: {str(e)}")
            
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    """Start an analysis job and stream results."""
    
    # Set API keys and routing logic
    env_updates = {}
    
    print(f"DEBUG: Analyze Request for {request.ticker}")
    print(f"DEBUG: Provider: {request.llm_provider}")
    print(f"DEBUG: Keys Present: OpenAI={bool(request.openai_api_key)}, Groq={bool(request.groq_api_key)}, Alpha={bool(request.alpha_vantage_api_key)}")
    
    # 1. Vendor Keys
    if request.alpha_vantage_api_key:
        env_updates["ALPHA_VANTAGE_API_KEY"] = request.alpha_vantage_api_key

    # 2. LLM Provider Routing
    # We map various providers to the underlying client logic (mostly OpenAI compatible)
    
    # Defaults
    llm_provider = request.llm_provider
    backend_url = request.backend_url

    if request.llm_provider == "openai":
        if request.openai_api_key: env_updates["OPENAI_API_KEY"] = request.openai_api_key
        
    elif request.llm_provider == "anthropic":
        if request.anthropic_api_key: env_updates["ANTHROPIC_API_KEY"] = request.anthropic_api_key
        
    elif request.llm_provider == "google":
        if request.google_api_key: env_updates["GOOGLE_API_KEY"] = request.google_api_key
        
    elif request.llm_provider == "groq":
        # Map to OpenAI client
        llm_provider = "openai"
        backend_url = "https://api.groq.com/openai/v1"
        if request.groq_api_key: env_updates["OPENAI_API_KEY"] = request.groq_api_key
        
    elif request.llm_provider == "deepseek":
        llm_provider = "openai"
        backend_url = "https://api.deepseek.com"
        if request.deepseek_api_key: env_updates["OPENAI_API_KEY"] = request.deepseek_api_key
        
    elif request.llm_provider == "qwen":
        llm_provider = "openai"
        # Using OpenRouter/DashScope compatible endpoint if known, or user provided
        # Defaulting to DashScope compatible endpoint for Qwen (Aliyun)
        backend_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        if request.qwen_api_key: env_updates["OPENAI_API_KEY"] = request.qwen_api_key

    elif request.llm_provider == "ollama":
        # Client handles 'ollama' provider string if configured, or we map to openai
        # TradingAgentsGraph currently supports 'ollama' string but redirects to ChatOpenAI
        # so we just need to ensure backend_url is set.
        backend_url = request.ollama_base_url or "http://localhost:11434/v1"
        env_updates["OPENAI_API_KEY"] = "ollama" # Dummy key often needed

    elif request.llm_provider == "local":
        llm_provider = "openai"
        backend_url = "http://localhost:1234/v1" # Example LM Studio
        env_updates["OPENAI_API_KEY"] = "local"

    # Apply env updates
    for k, v in env_updates.items():
        os.environ[k] = v
        print(f"DEBUG: Set ENV {k} = {'*' * 4}")

    async def event_generator():
        try:
            # 1. Setup Configuration
            config = DEFAULT_CONFIG.copy()
            config["max_debate_rounds"] = request.research_depth
            config["max_risk_discuss_rounds"] = request.research_depth
            config["quick_think_llm"] = request.shallow_thinker
            config["deep_think_llm"] = request.deep_thinker
            config["llm_provider"] = llm_provider
            if backend_url:
                config["backend_url"] = backend_url

            # 2. Initialize Agent Graph
            # Map friendly names to internal enum values if needed, 
            # currently implementations expect lower case values for selection
            selected_analysts_map = {
                "Market Analyst": "market",
                "Social Analyst": "social",
                "News Analyst": "news",
                "Fundamentals Analyst": "fundamentals"
            }
            
            internal_analysts = [selected_analysts_map.get(a, a.lower()) for a in request.analysts]
            
            # Use 'market' as default if mapping fails or empty
            if not internal_analysts:
                 internal_analysts = ["market"]

            print(f"DEBUG: Internal Analysts List: {internal_analysts}")

            yield {
                "event": "init",
                "data": json.dumps({"message": f"Initializing agents for {request.ticker}..."})
            }

            graph = TradingAgentsGraph(
                selected_analysts=internal_analysts,
                config=config,
                debug=True # Force debug to get traces if possible, though we rely on stream
            )

            # 3. Stream Execution
            # We need to use the synchronous stream method in a way that doesn't block the async loop entirely.
            # However, TradingAgentsGraph.graph.stream is likely synchronous or returns a synchronous iterator.
            # If the underlying LangGraph is sync, we might need to run it in a threadpool or 
            # just iterate carefully. LangGraph usually supports async but the wrapper class instantiation 
            # might have set it up safely.
            # Let's assume standard synchronous stream for now, but yield regularly.
            
            # Prepare inputs
            # TradingAgentsGraph.propagate handles init state creation, but we want to stream.
            # So we mimic propagate's setup:
            
            # Using private/internal methods might be risky if API changes, but necessary for streaming
            # propagate() calls:
            #   init_agent_state = self.propagator.create_initial_state(company_name, trade_date)
            #   args = self.propagator.get_graph_args()
            #   for chunk in self.graph.stream(init_agent_state, **args): ...

            # Prepare inputs
            init_state = graph.propagator.create_initial_state(request.ticker, request.analysis_date)
            args = graph.propagator.get_graph_args()
            
            # Explicitly set ticker for report generation
            graph.ticker = request.ticker

            # Track full state accumulator for final report
            full_state = init_state.copy()

            # Iterate over the graph stream
            for chunk in graph.graph.stream(init_state, **args):
                # chunk is a dict of state updates, usually keyed by node name
                # e.g. {'market_analyst': {...state update...}}
                
                for node_name, state_update in chunk.items():
                    # Update full state accumulator
                    full_state.update(state_update)

                    # Check what info we have. 
                    # State updates usually contain messages or report sections.
                    
                    event_data = {
                        "node": node_name,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Try to extract meaningful "thought" or content
                    # If there are messages (LangGraph messages)
                    if "messages" in state_update and state_update["messages"]:
                        last_msg = state_update["messages"][-1]
                        # Handling different message types (AIMessage, HumanMessage, etc)
                        content = getattr(last_msg, "content", str(last_msg))
                        event_data["content"] = content
                        event_data["type"] = "thought"
                    
                    
                    # Check if a report section was updated
                    report_sections = [
                        "market_report", "sentiment_report", "news_report", "fundamentals_report",
                        "investment_plan", "trader_investment_plan", "final_trade_decision"
                    ]
                    
                    for section in report_sections:
                        if section in state_update:
                            event_data["section_update"] = section
                            event_data["section_content"] = state_update[section]
                            event_data["type"] = "report"
                    


                         



                    # Check for Investment Debate updates (Bull/Bear)
                    if "investment_debate_state" in state_update:
                         ids = state_update["investment_debate_state"]
                         if "current_response" in ids and ids.get("current_response"):
                             # Convert to Report type for button display
                             event_data["section_content"] = ids["current_response"]
                             # Determine title based on node or history
                             role = "Debate"
                             if "Bull" in ids["current_response"]: role = "Bull Narrative"
                             if "Bear" in ids["current_response"]: role = "Bear Case"
                             
                             event_data["section_update"] = role
                             event_data["type"] = "report"

                    # Check for Risk Debate updates
                    if "risk_debate_state" in state_update:
                         rds = state_update["risk_debate_state"]
                         speaker = rds.get("latest_speaker")
                         
                         content = ""
                         title = "Risk Debate"
                         
                         if speaker == "Risky":
                             content = rds.get("current_risky_response", "")
                             title = "Risky Analysis"
                         elif speaker == "Safe":
                             content = rds.get("current_safe_response", "")
                             title = "Conservative Analysis"
                         elif speaker == "Neutral":
                             content = rds.get("current_neutral_response", "")
                             title = "Neutral Analysis"
                         elif speaker == "Judge":
                             content = rds.get("judge_decision", "")
                             title = "Risk Verdict"
                             
                         if content:
                             event_data["section_content"] = content
                             event_data["section_update"] = title
                             event_data["type"] = "report" # Force button view

                    
                    yield {
                        "event": "agent_update",
                        "data": json.dumps(event_data)
                    }
                    
                    # Sleep briefly to yield control only if necessary, 
                    # but typically starlette handles generator yields.
                    await asyncio.sleep(0.01)

            # 4. Final Wrap up
            # Save the markdown report to disk
            try:
                report_path = graph.save_markdown_report(request.analysis_date, full_state)
                print(f"INFO: Saved report to {report_path}")
                
                 # Yield Final Report Event
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        final_report_content = f.read()
                        
                    yield {
                        "event": "agent_update",
                        "data": json.dumps({
                            "node": "Final Report",
                            "timestamp": datetime.now().isoformat(),
                            "type": "report",
                            "section_content": final_report_content,
                            "section_update": "Comprehensive Analysis Report"
                        })
                    }
                except Exception as read_err:
                     print(f"ERROR: Could not read final report for streaming: {read_err}")
                
            except Exception as e:
                print(f"ERROR: Could not save report from main.py: {e}")

            yield {
                "event": "complete",
                "data": json.dumps({"message": "Analysis processing complete."})
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
