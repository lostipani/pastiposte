import asyncio, time, aiohttp, json
from os import getenv
from commons.logger import logger
from binance.spot import Spot


class BinanceConnector:
    def __init__(self):
        self.base_url = getenv("BINANCE_BASE_URL", "https://api.binance.com")
        self.session = aiohttp.ClientSession()
        self.listen_key = None

    async def _get_listen_key(self):
        url = f"{self.base_url}/api/v3/userDataStream"
        headers = {"X-MBX-APIKEY": getenv("BINANCE_API_KEY")}
        async with self.session.post(url, headers=headers) as resp:
            data = await resp.json()
            self.listen_key = data["listenKey"]
            logger.info("Acquired listen key")
            return self.listen_key

    async def _keepalive(self):
        """Renew listen key every ~30 minutes."""
        while True:
            if self.listen_key:
                url = f"{self.base_url}/api/v3/userDataStream"
                headers = {"X-MBX-APIKEY": getenv("BINANCE_API_KEY")}
                async with self.session.put(url, headers=headers) as resp:
                    await resp.text()
                    logger.info("Listen key keepalive")
            await asyncio.sleep(30 * 60)

    async def listen_ws(self, callback):
        """Listen to user data WebSocket."""
        if not self.listen_key:
            await self._get_listen_key()
        ws_url = f"wss://stream.binance.com:9443/ws/{self.listen_key}"
        async with self.session.ws_connect(ws_url) as ws:
            logger.info("Connected to Binance WS")
            asyncio.create_task(self._keepalive())
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    event = json.loads(msg.data)
                    await callback(event)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error("WS error, reconnecting...")
                    break
            await asyncio.sleep(5)
            await self.listen_ws(callback)

    async def fetch_open_orders(self, symbol=None):
        """Poll open orders via signed REST call."""
        client = Spot(
            api_key=getenv("BINANCE_API_KEY"),
            api_secret=getenv("BINANCE_API_SECRET"),
            base_url=self.base_url,
        )
        return client.get_open_orders(symbol=symbol)  # signed automatically
