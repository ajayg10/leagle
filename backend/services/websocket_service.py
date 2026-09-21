import socketio
import logging

logger = logging.getLogger(__name__)

# Create a Socket.io server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=False  # Set to True for extra debug
)

# The ASGI application wrapper is now created in main.py to avoid circular imports

async def broadcast_alert(alert_data: dict):
    """
    Broadcast an alert to all connected clients.
    """
    try:
        await sio.emit('new_alert', alert_data)
        logger.info(f"📣 Broadcasted alert: {alert_data.get('message')}")
    except Exception as e:
        logger.error(f"❌ Failed to broadcast alert: {e}")

@sio.event
async def connect(sid, environ):
    """Client connected to Socket.IO"""
    logger.info(f"✅ Socket.IO client connected: {sid}")
    logger.debug(f"   Path: {environ.get('PATH_INFO')}")
    logger.debug(f"   Query: {environ.get('QUERY_STRING')}")

@sio.event
async def disconnect(sid):
    """Client disconnected from Socket.IO"""
    logger.info(f"❌ Socket.IO client disconnected: {sid}")

@sio.event
async def ping(sid):
    """Handle ping from client"""
    logger.debug(f"📍 Ping from {sid}")
    return "pong"
