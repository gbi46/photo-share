from src.routes import auth, post
from fastapi import FastAPI

import uvicorn

app = FastAPI()

app.include_router(auth.router)
app.include_router(post.router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
