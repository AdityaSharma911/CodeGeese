from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.utils.settings import settings
from src.service.vector_service import init_qdrant
from src.service.mongo_service import init_mongo
from src.controller.leetCodeProbListController import router as sync_problems

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting server and connecting to DBs...")
    init_mongo()
    init_qdrant()
    print("✅ Connections established.")
    yield
    print("🛑 Server shutdown — clean up if needed.")

app = FastAPI(lifespan=lifespan)

app.include_router(sync_problems)

@app.get("/")
def read_root():
    return {"status": "CodeGeese backend is running"}