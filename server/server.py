import os
from typing import Dict
import random
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, status
from fastapi.websockets import WebSocketDisconnect

from commons.parser import get_server_period
from commons.logger import logger

app = FastAPI()


def producer() -> Dict[str, float]:
    return {"value": random.gauss(0, 1)}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = producer()
        logger.info(data)
        try:
            await websocket.send_json(data)
        except WebSocketDisconnect:
            break
        await asyncio.sleep(get_server_period())


@app.get("/http")
async def http_endpoint():
    return producer()


@app.get(
    "/healthcheck",
    status_code=status.HTTP_200_OK,
)
async def healthcheck():
    return {"value": 0}


if __name__ == "__main__":
    uvicorn.run(
        "server.server:app",
        host="0.0.0.0",
        port=int(os.getenv("WS_PORT", 12345)),
        log_level=str(os.getenv("LOGLEVEL", "info")).lower(),
        ws="websockets",
    )
