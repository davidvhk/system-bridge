"""System Bridge Connector: WebSocket Client"""
from __future__ import annotations

from collections.abc import Callable
import json
import socket

import aiohttp

from systembridgeconnector.base import Base
from systembridgeconnector.const import (
    EVENT_API_KEY,
    EVENT_BASE,
    EVENT_DATA,
    EVENT_DIRECTORIES,
    EVENT_EVENT,
    EVENT_FILE,
    EVENT_FILES,
    EVENT_KEY,
    EVENT_MESSAGE,
    EVENT_MODULE,
    EVENT_MODULES,
    EVENT_PATH,
    EVENT_SUBTYPE,
    EVENT_TEXT,
    EVENT_TYPE,
    EVENT_URL,
    MODEL_MAP,
    MODEL_MEDIA_DIRECTORIES,
    MODEL_MEDIA_FILE,
    MODEL_MEDIA_FILES,
    SUBTYPE_BAD_API_KEY,
    SUBTYPE_LISTENER_ALREADY_REGISTERED,
    TYPE_DATA_UPDATE,
    TYPE_DIRECTORIES,
    TYPE_ERROR,
    TYPE_EXIT_APPLICATION,
    TYPE_FILE,
    TYPE_FILES,
    TYPE_GET_DATA,
    TYPE_GET_DIRECTORIES,
    TYPE_GET_FILE,
    TYPE_GET_FILES,
    TYPE_KEYBOARD_KEYPRESS,
    TYPE_KEYBOARD_TEXT,
    TYPE_OPEN,
    TYPE_REGISTER_DATA_LISTENER,
)
from systembridgeconnector.exceptions import (
    AuthenticationException,
    BadMessageException,
    ConnectionClosedException,
    ConnectionErrorException,
)
from systembridgeconnector.models.generic import Generic


class WebSocketClient(Base):
    """WebSocket Client"""

    def __init__(
        self,
        api_host: str,
        api_port: int,
        api_key: str,
    ) -> None:
        """Initialize"""
        super().__init__()
        self._api_host = api_host
        self._api_port = api_port
        self._api_key = api_key
        self._session: aiohttp.ClientSession | None = None
        self._websocket: aiohttp.ClientWebSocketResponse | None = None

    @property
    def connected(self) -> bool:
        """Get connection state."""
        return self._websocket is not None and not self._websocket.closed

    async def close(self) -> None:
        """Close connection"""
        self._logger.info("Closing WebSocket connection")
        if self._websocket is not None:
            await self._websocket.close()
        if self._session is not None:
            await self._session.close()

    async def connect(
        self,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Connect to server"""
        if session:
            self._session = session
        else:
            self._session = aiohttp.ClientSession()
        url = f"ws://{self._api_host}:{self._api_port}/api/websocket"
        self._logger.info("Connecting to WebSocket: %s", url)
        try:
            self._websocket = await self._session.ws_connect(url=url, heartbeat=30)
        except (
            aiohttp.WSServerHandshakeError,
            aiohttp.ClientConnectionError,
            socket.gaierror,
        ) as error:
            self._logger.error(
                "Failed to connect to WebSocket: %s - %s",
                error.__class__.__name__,
                error,
            )
            raise ConnectionErrorException from error
        self._logger.info("Connected to WebSocket")

    async def exit_backend(self) -> None:
        """Exit backend"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Exiting backend")
        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_EXIT_APPLICATION,
                        EVENT_API_KEY: self._api_key,
                    }
                )
            )

    async def get_data(
        self,
        modules: list[str],
    ) -> None:
        """Get data from server"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Getting data from server: %s", modules)

        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_GET_DATA,
                        EVENT_API_KEY: self._api_key,
                        EVENT_MODULES: modules,
                    }
                )
            )

    async def get_directories(self) -> None:
        """Get directories"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Getting directories:")

        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_GET_DIRECTORIES,
                        EVENT_API_KEY: self._api_key,
                    }
                )
            )

    async def get_files(
        self,
        base: str,
        path: str | None = None,
    ) -> None:
        """Get files"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Getting files: %s - %s", base, path)

        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_GET_FILES,
                        EVENT_API_KEY: self._api_key,
                        EVENT_BASE: base,
                        EVENT_PATH: path,
                    }
                )
            )

    async def get_file(
        self,
        base: str,
        path: str,
    ) -> None:
        """Get files"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Getting file: %s - %s", base, path)

        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_GET_FILE,
                        EVENT_API_KEY: self._api_key,
                        EVENT_BASE: base,
                        EVENT_PATH: path,
                    }
                )
            )

    async def register_data_listener(
        self,
        modules: list[str],
    ) -> None:
        """Register data listener"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Registering data listener: %s", modules)
        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_REGISTER_DATA_LISTENER,
                        EVENT_API_KEY: self._api_key,
                        EVENT_MODULES: modules,
                    }
                )
            )

    async def keyboard_keypress(
        self,
        key: str,
    ) -> None:
        """Keyboard keypress"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Press key: %s", key)
        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_KEYBOARD_KEYPRESS,
                        EVENT_API_KEY: self._api_key,
                        EVENT_KEY: key,
                    }
                )
            )

    async def keyboard_text(
        self,
        text: str,
    ) -> None:
        """Keyboard keypress"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Enter text: %s", text)
        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_KEYBOARD_TEXT,
                        EVENT_API_KEY: self._api_key,
                        EVENT_TEXT: text,
                    }
                )
            )

    async def open_path(
        self,
        path: str,
    ) -> None:
        """Open path"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Opening path: %s", path)
        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_OPEN,
                        EVENT_API_KEY: self._api_key,
                        EVENT_PATH: path,
                    }
                )
            )

    async def open_url(
        self,
        url: str,
    ) -> None:
        """Open url"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Opening URL: %s", url)
        if self._websocket is not None:
            await self._websocket.send_str(
                json.dumps(
                    {
                        EVENT_EVENT: TYPE_OPEN,
                        EVENT_API_KEY: self._api_key,
                        EVENT_URL: url,
                    }
                )
            )

    async def listen(
        self,
        callback: Callable,
    ) -> None:
        """Listen for messages and map to modules"""

        async def _callback_message(message: dict) -> None:
            """Message Callback"""
            self._logger.debug("New message: %s", message[EVENT_TYPE])
            if message[EVENT_TYPE] == TYPE_ERROR:
                if message[EVENT_SUBTYPE] == SUBTYPE_LISTENER_ALREADY_REGISTERED:
                    self._logger.debug(message)
                else:
                    self._logger.warning("Error message: %s", message)
            elif (
                message[EVENT_TYPE] == TYPE_DATA_UPDATE
                and message[EVENT_DATA] is not None
            ):
                self._logger.debug("New data for: %s", message[EVENT_MODULE])
                model = MODEL_MAP.get(message[EVENT_MODULE])
                if model is None:
                    self._logger.warning("Unknown model: %s", message[EVENT_MODULE])
                else:
                    await callback(
                        message[EVENT_MODULE],
                        model(**message[EVENT_DATA]),
                    )
            elif message[EVENT_TYPE] == TYPE_DIRECTORIES:
                self._logger.debug("New directories")
                model = MODEL_MAP[MODEL_MEDIA_DIRECTORIES]
                await callback(
                    MODEL_MEDIA_DIRECTORIES,
                    model(**message[EVENT_DIRECTORIES]),
                )
            elif message[EVENT_TYPE] == TYPE_FILES:
                self._logger.debug("New files")
                model = MODEL_MAP[MODEL_MEDIA_FILES]
                await callback(
                    MODEL_MEDIA_FILES,
                    model(**message[EVENT_FILES]),
                )
            elif message[EVENT_TYPE] == TYPE_FILE:
                self._logger.debug("New file")
                model = MODEL_MAP[MODEL_MEDIA_FILE]
                await callback(
                    MODEL_MEDIA_FILE,
                    model(**message[EVENT_FILE]),
                )

        await self.listen_for_messages(callback=_callback_message)

    async def listen_for_messages(
        self,
        callback: Callable,
    ) -> None:
        """Listen for messages"""
        if not self.connected:
            raise ConnectionClosedException("Connection is closed")

        self._logger.info("Listen for messages")
        if self._websocket is not None:
            while not self._websocket.closed:
                message = await self.receive_message()
                if isinstance(message, dict):
                    await callback(message)

    async def receive_message(self) -> dict | None:
        """Receive message"""
        if not self.connected or self._websocket is None:
            raise ConnectionClosedException("Connection is closed")

        try:
            message = await self._websocket.receive()
        except RuntimeError:
            return None

        if message.type == aiohttp.WSMsgType.ERROR:
            raise ConnectionErrorException(self._websocket.exception())

        if message.type in (
            aiohttp.WSMsgType.CLOSE,
            aiohttp.WSMsgType.CLOSED,
            aiohttp.WSMsgType.CLOSING,
        ):
            raise ConnectionClosedException("Connection closed to server")

        if message.type == aiohttp.WSMsgType.TEXT:
            message_json = message.json()

            if (
                message_json[EVENT_TYPE] == TYPE_ERROR
                and message_json[EVENT_SUBTYPE] == SUBTYPE_BAD_API_KEY
            ):
                raise AuthenticationException(message_json[EVENT_MESSAGE])

            return message_json

        raise BadMessageException(f"Unknown message type: {message.type}")
