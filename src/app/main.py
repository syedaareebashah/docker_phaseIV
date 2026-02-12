from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints.chat import router as chat_router
from .api.endpoints.health import router as health_router
from .middleware.auth import get_current_user
from .database.session import get_session, init_db
from .mcp_server.server import mcp_server

app = FastAPI(
    title="Todo AI Chatbot API",
    description="AI-Powered Task Management API with MCP Integration",
    version="1.0.0"
)

# Initialize database
@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup."""
    init_db()
    
    # Start MCP server in a background thread
    import threading
    mcp_thread = threading.Thread(target=mcp_server.run, daemon=True)
    mcp_thread.start()

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://to-do-webapp-chrb.vercel.app",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)
app.include_router(health_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Todo AI Chatbot API",
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)