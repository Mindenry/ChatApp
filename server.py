from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict, Set, List
import json
from datetime import datetime
import asyncio

app = FastAPI()

class Room:
    def __init__(self, name: str, topic: str = ""):
        self.name = name
        self.topic = topic
        self.users: Dict[str, WebSocket] = {}
        self.messages: List[dict] = []

class ChatServer:
    def __init__(self):
        self.rooms: Dict[str, Room] = {
            "General": Room("General", "Welcome to the general discussion room"),
            "Random": Room("Random", "For random discussions"),
            "Work": Room("Work", "Work-related discussions"),
            "Social": Room("Social", "Social chat room")
        }
        self.user_status: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, username: str, room_name: str):
        # Create room if it doesn't exist (for DMs)
        if room_name not in self.rooms:
            self.rooms[room_name] = Room(room_name)
            
        room = self.rooms[room_name]
        
        await websocket.accept()
        room.users[username] = websocket
        self.user_status[username] = "🟢 Online"
        
        # Send room history
        for message in room.messages[-50:]:  # Last 50 messages
            await websocket.send_json(message)
        
        # Broadcast user list
        await self.broadcast_user_list(room)
        
        # Broadcast join message
        join_message = {
            'type': 'message',
            'username': 'System',
            'content': f'{username} has joined the room',
            'room': room_name,
            'timestamp': datetime.now().strftime('%H:%M')
        }
        await self.broadcast_message(join_message, room)

    async def disconnect(self, username: str, room_name: str):
        if room_name in self.rooms:
            room = self.rooms[room_name]
            if username in room.users:
                del room.users[username]
                if username in self.user_status:
                    del self.user_status[username]
                
                # Broadcast leave message
                leave_message = {
                    'type': 'message',
                    'username': 'System',
                    'content': f'{username} has left the room',
                    'room': room_name,
                    'timestamp': datetime.now().strftime('%H:%M')
                }
                await self.broadcast_message(leave_message, room)
                await self.broadcast_user_list(room)

    async def broadcast_message(self, message: dict, room: Room):
        room.messages.append(message)
        for connection in room.users.values():
            await connection.send_json(message)

    async def broadcast_user_list(self, room: Room):
        user_list = {
            'type': 'user_list',
            'users': list(room.users.keys()),
            'statuses': self.user_status
        }
        for connection in room.users.values():
            await connection.send_json(user_list)

    async def handle_status_change(self, username: str, status: str):
        self.user_status[username] = status
        # Broadcast to all rooms where user is present
        for room in self.rooms.values():
            if username in room.users:
                await self.broadcast_user_list(room)

chat_server = ChatServer()

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str,
    room: str = "General"
):
    await chat_server.connect(websocket, username, room)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'status':
                await chat_server.handle_status_change(
                    message['username'],
                    message['status']
                )
            else:
                await chat_server.broadcast_message(
                    message,
                    chat_server.rooms[room]
                )
                
    except WebSocketDisconnect:
        await chat_server.disconnect(username, room)

@app.get("/")
async def get():
    return HTMLResponse("<h1>Chat Server Running</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)