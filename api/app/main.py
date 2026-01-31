from fastapi import FastAPI
from api.app.api.routes import captcha

app = FastAPI(title="Captcha Solver API")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(captcha.router)
