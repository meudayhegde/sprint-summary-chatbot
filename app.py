"""
Sprint Summary Chatbot - FastAPI Application
An interactive AI-powered chatbot for analyzing sprint data with visualizations.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os

from config import settings
from data_analyzer import SprintDataAnalyzer
from agent import SprintAnalysisAgent
from dashboard_analyzer import DashboardAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sprint Summary Chatbot",
    description="AI-powered chatbot for sprint data analysis with interactive visualizations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize data analyzer and agent
data_analyzer = None
agent = None
dashboard_analyzer = None

@app.on_event("startup")
async def startup_event():
    """Initialize the data analyzer and agent on startup."""
    global data_analyzer, agent, dashboard_analyzer
    
    try:
        logger.info(f"Loading data from {settings.data_file}")
        data_analyzer = SprintDataAnalyzer(settings.data_file)
        
        logger.info(f"Initializing LangChain agent with {settings.llm_provider} provider")
        agent = SprintAnalysisAgent(data_analyzer)
        
        logger.info("Initializing dashboard analyzer")
        dashboard_analyzer = DashboardAnalyzer(data_analyzer.df)
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raiser.error(f"Error during startup: {str(e)}")
        raise


# Pydantic models
class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    charts: Optional[List[Dict[str, Any]]] = []
    timestamp: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    data_loaded: bool
    total_tickets: int


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        llm_provider=settings.llm_provider,
        data_loaded=data_analyzer is not None,
        total_tickets=len(data_analyzer.df) if data_analyzer and data_analyzer.df is not None else 0
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message and return AI response with optional charts.
    """
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        logger.info(f"Processing message: {message.message}")
        
        result = agent.query(message.message)
        
        return ChatResponse(
            response=result["answer"],
            charts=result["charts"]
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary")
async def get_summary():
    """Get overall data summary."""
    if not data_analyzer:
        raise HTTPException(status_code=500, detail="Data analyzer not initialized")
    
    return data_analyzer.get_data_summary()


@app.get("/api/sprint/{sprint_id}")
async def get_sprint(sprint_id: str):
    """Get specific sprint summary."""
    if not data_analyzer:
        raise HTTPException(status_code=500, detail="Data analyzer not initialized")
    
    return data_analyzer.get_sprint_summary(sprint_id)


@app.get("/api/team-performance")
async def get_team_performance():
    """Get team performance metrics."""
    if not data_analyzer:
        raise HTTPException(status_code=500, detail="Data analyzer not initialized")
    
@app.get("/api/bugs")
async def get_bugs():
    """Get bug analysis."""
    if not data_analyzer:
        raise HTTPException(status_code=500, detail="Data analyzer not initialized")
    
    return data_analyzer.get_bug_analysis()


# Dashboard API endpoints
@app.get("/api/dashboard/kpis")
async def get_dashboard_kpis():
    """Get KPIs for dashboard."""
    if not dashboard_analyzer:
        raise HTTPException(status_code=500, detail="Dashboard analyzer not initialized")
    
    return dashboard_analyzer.get_kpis()


@app.get("/api/dashboard/state-distribution")
async def get_state_distribution():
    """Get state distribution data."""
    if not dashboard_analyzer:
        raise HTTPException(status_code=500, detail="Dashboard analyzer not initialized")
    
    return dashboard_analyzer.get_state_distribution()


@app.get("/api/dashboard/velocity")
async def get_velocity_chart():
    """Get velocity chart data."""
    if not dashboard_analyzer:
        raise HTTPException(status_code=500, detail="Dashboard analyzer not initialized")
    
    return dashboard_analyzer.get_velocity_chart()


@app.get("/api/dashboard/cycle-time")
async def get_cycle_time():
    """Get cycle time analysis data."""
    if not dashboard_analyzer:
        raise HTTPException(status_code=500, detail="Dashboard analyzer not initialized")
    
    return dashboard_analyzer.get_cycle_time_analysis()


@app.get("/api/dashboard/bugs")
async def get_bugs_breakdown():
    """Get bugs breakdown data."""
    if not dashboard_analyzer:
        raise HTTPException(status_code=500, detail="Dashboard analyzer not initialized")
    
    return dashboard_analyzer.get_bugs_breakdown()


@app.get("/api/dashboard/workload")
async def get_workload_distribution():
    """Get workload distribution data."""
    if not dashboard_analyzer:
        raise HTTPException(status_code=500, detail="Dashboard analyzer not initialized")
    
    return dashboard_analyzer.get_workload_distribution()


@app.get("/api/dashboard/spillover")
async def get_spillover_overview():
    """Get spillover overview data."""
    if not dashboard_analyzer:
        raise HTTPException(status_code=500, detail="Dashboard analyzer not initialized")
    
    return dashboard_analyzer.get_spillover_overview()


@app.get("/api/dashboard/raw-data")
async def get_raw_data():
    """Get raw data summary."""
    if not dashboard_analyzer:
        raise HTTPException(status_code=500, detail="Dashboard analyzer not initialized")
    
    return dashboard_analyzer.get_raw_data()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
