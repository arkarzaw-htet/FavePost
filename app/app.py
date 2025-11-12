from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def basic():
    return {"a" : "ab"}