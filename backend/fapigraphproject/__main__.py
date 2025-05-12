import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fapigraphproject.graphql_api.graphql_service import graphql_app
from fapigraphproject.ws_api.websocket_service import ws_router

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")
app.include_router(ws_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
