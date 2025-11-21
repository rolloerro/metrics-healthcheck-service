from fastapi import FastAPI
from .metrics import get_metrics

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metrics")
def metrics():
    return get_metrics()
