from fastapi import FastAPI

from src.routes import router_todo, auth_router

app = FastAPI()

app.include_router(router_todo)
app.include_router(auth_router)


@app.get("/hello")
async def test():
    return "Hello word!"
