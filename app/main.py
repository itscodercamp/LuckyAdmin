from fastapi import FastAPI
from .database import engine, Base
from .routers import auth, wallet, rewards, content, admin
from fastapi.middleware.cors import CORSMiddleware

import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lucky Lubricant Reward System API")

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(wallet.router)
app.include_router(rewards.router)
app.include_router(content.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Lucky Lubricant Reward System API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
