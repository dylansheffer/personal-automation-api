from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(title="Personal Automation API", description="API for personal automations")

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)