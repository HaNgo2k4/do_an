from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.route import router
app = FastAPI(title="Đồ Án Trợ Lí Ảo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host = "127.0.0.1", port = 9999, reload = True)