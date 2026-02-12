import os
import uvicorn
from src.app.main import app

# Set the database URL
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///./todo_chatbot.db')

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info", reload=False)