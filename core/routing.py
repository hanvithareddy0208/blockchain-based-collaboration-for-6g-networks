"""
WebSocket routing for real-time updates
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Blockchain updates
    re_path(r'ws/blockchain/$', consumers.BlockchainConsumer.as_asgi()),
    
    # Node updates
    re_path(r'ws/nodes/$', consumers.NodeConsumer.as_asgi()),
    
    # Transaction updates
    re_path(r'ws/transactions/$', consumers.TransactionConsumer.as_asgi()),
    
    # System alerts
    re_path(r'ws/alerts/$', consumers.AlertConsumer.as_asgi()),
]