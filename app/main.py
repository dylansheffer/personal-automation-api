from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from app.api import router as api_router
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal Automation API", description="API for personal automations")

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"

logger.info(f"Loaded API Key from environment: {API_KEY}")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    logger.info(f"Received API Key: {api_key_header}")
    logger.info(f"Expected API Key: {API_KEY}")
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")

app.include_router(api_router, dependencies=[Depends(get_api_key)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1621)