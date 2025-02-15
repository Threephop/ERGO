import socketio

# Create an AsyncServer instance
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:8000"],
    logger=True,
    engineio_logger=True
)

sio_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f'{sid}: Client connected')

@sio.event
async def disconnect(sid):
    print(f'{sid}: Client disconnected')

@sio.event
async def send_message(sid, data):
    print(f'Received message from {sid}: {data}')
    await sio.emit("new_message", data)
