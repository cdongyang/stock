import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

log = logging.getLogger(__name__)


class WSManager:
    def __init__(self):
        self._conns: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._conns.append(ws)

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            try:
                self._conns.remove(ws)
            except ValueError:
                pass

    async def broadcast(self, data: Any):
        msg = json.dumps(data, ensure_ascii=False)
        async with self._lock:
            dead: list[WebSocket] = []
            for conn in self._conns:
                try:
                    await conn.send_text(msg)
                except Exception:
                    dead.append(conn)
            for conn in dead:
                try:
                    self._conns.remove(conn)
                except ValueError:
                    pass
