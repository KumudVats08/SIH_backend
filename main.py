import os

from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.courses import router as courses_router
from routers.gaps import router as gaps_router
from routers.routes import router


app = FastAPI(title="Skill Gap API")
app.include_router(router)
app.include_router(auth_router)
app.include_router(gaps_router)
app.include_router(courses_router)


@app.get("/")
def read_root():
	return {"message": "Skill Gap API is running"}


@app.get("/health")
def health_check():
	return {
		"status": "ok",
		"ai_configured": bool(os.getenv("GROQ_API_KEY")),
		"ai_model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
	}
