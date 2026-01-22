import json
import socket
from typing import Callable, Union, List, Dict

from loguru import logger
from pydantic import BaseModel
from websockets import ConnectionClosed
from websockets.sync.connection import Connection
from websockets.sync.server import serve, Server

from common.concurrent.abs_runnable import ThreadRunnable
from common.utils import web_util


############################
#  Json Web Socket Server  #
# Author: AkagawaTsurunaki #
############################

"""
    - 通用 Json Web Socket 服务器
    支持 JSON 格式的数据收发，支持子协议校验
"""
class JsonWsServer(ThreadRunnable):
    def __init__(self, host: str, port: int, subprotocols: List[str] = None):
        super().__init__()
        self.ws: Server | None = None
        self.host = host
        self.port = port
        # 重要！使用子协议用于校验！
        self.subprotocols = subprotocols

        # 监听器注册
        self.on_msg_handlers: List[Callable[[Connection, Union[Dict, List]], None]] = []
        self.on_open_handlers: List[Callable[[Connection], None]] = []
        self.on_close_handlers: List[Callable[[Connection, int, str], None]] = []
        self.on_err_handlers: List[Callable[[Connection, Exception], None]] = []

        # Connection 记录（关闭连接后不要使用 Connection 对象）
        self._connections: dict[Connection, str] = {}

    def name(self):
        return "JsonWsServer"

    # 基于websockets库创建 WebSocket 服务，自动识别 IPv4/IPv6，通过serve_forever()持续监听连接
    def start(self):
        super().start()
        is_ipv6 = web_util.is_ipv6(self.host)
        logger.info(f"This Websocket server will use {'IPv6' if is_ipv6 else 'IPv4'}.")
        with serve(handler=self._handle_json_recv, host=self.host, port=self.port,
                   subprotocols=self.subprotocols,
                   family=socket.AF_INET6 if is_ipv6 else socket.AF_INET) as ws:
            self.ws = ws
            logger.info(f"WebSocket server started at {self.host}:{self.port}")
            self.ws.serve_forever()

    # 停止服务
    def stop(self):
        super().stop()
        if self.ws is not None:
            self.ws.shutdown()

    @property
    def connections(self):
        return len(self._connections)
    # 每个客户端连接的核心处理循环：校验子协议 -> 记录新连接 -> 循环接收客户端消息，解析为 JSON 后触发所有on_msg_handlers
    def _handle_json_recv(self, ws: Connection):
        """处理每个 WebSocket 连接"""
        # 处理 Sec-WebSocket-Protocol 的 Header
        self._validate_subprotocols(ws)
        self._add_connection(ws)
        try:
            while True:
                try:
                    message = ws.recv()
                    data = json.loads(message)
                    # 注意：这里一旦抛出异常，那么并非所有的 Handler 都会被执行
                    # 例如说，有 10 个 Handler，如果第 5 个出错，那么后 5 个将不会被执行
                    for handler in self.on_msg_handlers:
                        handler(ws, data)
                except Exception as e:
                    if isinstance(e, ConnectionClosed):
                        raise e
                    if len(self.on_err_handlers) == 0:
                        logger.exception(e)
                    self._handle_exception(ws, e)

        except ConnectionClosed as e:
            self._remove_connection(ws, e)

    # 校验客户端使用的子协议是否在服务端允许的列表中，不匹配则抛出异常
    def _validate_subprotocols(self, ws: Connection):
        if ws.subprotocol is not None:
            if ws.subprotocol not in self.subprotocols:
                logger.warning(f"Not supported sub protocol: {ws.id} {ws.remote_address}")
                raise ValueError(f"Not supported sub protocol: {ws.id} {ws.remote_address}")

    # 维护活跃连接列表，触发连接建立的处理器，并打印日志
    def _add_connection(self, ws: Connection):
        self._connections[ws] = str(ws.id)
        for handler in self.on_open_handlers:
            handler(ws)
        logger.info(f"WebSocket client connected: {ws.id} {ws.remote_address}")

    # 维护活跃连接列表，触发连接关闭的处理器，并打印日志
    def _remove_connection(self, ws: Connection, e: ConnectionClosed):
        ws_id = self._connections.pop(ws)
        for handler in self.on_close_handlers:
            handler(ws, e.rcvd.code, e.rcvd.reason)
        logger.warning(f"WebSocket client disconnected: {ws_id}")

    # 触发所有异常处理器，并打印日志
    def _handle_exception(self, ws: Connection, e: Exception):
        for handler in self.on_err_handlers:
            handler(ws, e)

    # 发送 JSON 数据给所有连接的客户端
    def send_json(self, data: any):
        if isinstance(data, BaseModel):
            msg = data.model_dump_json(indent=4)
        else:
            msg = json.dumps(data, ensure_ascii=False, indent=4)

        for conn in self._connections:
            conn.send(msg)
