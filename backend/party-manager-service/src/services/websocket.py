from fastapi import Depends, WebSocket

from integration.websocket import

class WebsocketReceiverService:
    def __init__(self, websocket_route_table: ):