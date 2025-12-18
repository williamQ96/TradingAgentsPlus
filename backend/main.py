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
                graph.save_markdown_report(request.analysis_date, full_state)
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
