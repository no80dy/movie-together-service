import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from services.client_id import ClientIDService, get_client_id_service
from services.websocket import WebSocketService, get_websocket_service

router = APIRouter()


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = "92e68168c3bb73c5b9297f7bfd688313b25683efbc6a59c63371355c5a8c2ce2";
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost/waiting_party/api/v1/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    websocket_service: WebSocketService = Depends(get_websocket_service),
    client_id_service: ClientIDService = Depends(get_client_id_service),
):
    await websocket_service.connect(client_id, websocket)
    # film_id = '1530ac24-8123-4db8-85ef-ccce5a3a37f1'
    film_id = client_id_service.get_film_id_from_client_id(client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_service.broadcast(
                film_id, f"Client #{client_id} says: {data}"
            )
    except WebSocketDisconnect:
        websocket_service.disconnect(client_id)
        await websocket_service.broadcast(
            film_id, f"Client #{client_id} left the chat"
        )


@router.get("/")
async def get():
    return HTMLResponse(html)
