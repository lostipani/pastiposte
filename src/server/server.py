import asyncio
import json

import uvicorn
from fastapi import FastAPI, WebSocket, status
from fastapi.websockets import WebSocketDisconnect

from commons.configuration import Configuration
from commons.logger import logger
from server.data_generator import gauss_list, char_scalar

app = FastAPI()
config = Configuration()

LIST_LEN = 10


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = gauss_list(LIST_LEN)
        logger.debug(data)
        try:
            await websocket.send_json(data)
        except WebSocketDisconnect:
            break
        await asyncio.sleep(config["sleep"])


@app.get("/http", status_code=status.HTTP_200_OK)
async def http_endpoint():
    data = char_scalar()
    logger.debug(data)
    return json.dumps(data)


@app.get(
    "/healthcheck",
    status_code=status.HTTP_200_OK,
)
async def healthcheck():
    return True


if __name__ == "__main__":
    uvicorn.run(
        "server.server:app",
        host="0.0.0.0",
        port=int(config.get("WS_PORT", 12345)),
        log_level=str(config.get("LOG_LEVEL", "info")).lower(),
        ws="websockets",
    )
