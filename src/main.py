from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.utils.settings import settings
from src.service.vector_service import init_qdrant
from src.service.mongo_service import init_mongo
from src.controller.problemsMetaController import router as sync_problems
from src.controller.problemDetailsController import router as scrape_problem_details
from src.controller.problemsSolutionController import router as solution_batch
from src.model.problemDetails import CodeSnippet

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
app.include_router(scrape_problem_details)
app.include_router(solution_batch)

@app.get("/")
def read_root():
    return {"status": "CodeGeese backend is running"}