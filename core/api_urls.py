"""
API endpoints for 6G Blockchain System
"""

from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard and system stats
    path('dashboard-stats/', api_views.dashboard_stats, name='api_dashboard_stats'),
    
    # Node management APIs
    path('nodes/', api_views.node_list, name='api_node_list'),
    path('nodes/<uuid:node_id>/status/', api_views.update_node_status, name='api_update_node_status'),
    
    # Transaction APIs
    path('transactions/', api_views.transaction_list, name='api_transaction_list'),
    
    # Storage APIs
    path('storage/statistics/', api_views.storage_statistics, name='api_storage_stats'),

    path('consensus/active-rounds/', api_views.consensus_active_rounds, name='api_consensus_active_rounds'),
    path('consensus/history/', api_views.consensus_history, name='api_consensus_history'),
    # Node join and shard creation
    path('node-join/', api_views.node_join, name='api_node_join'),
    # Temporary GET fallback for quick node creation (no JS required)
    path('node-join-via-get/', api_views.node_join_via_get, name='api_node_join_via_get'),
    path('shard-create/', api_views.shard_create, name='api_shard_create'),
    # Debug/test endpoints (development only)
    path('debug/shard-test/', api_views.debug_shard_create, name='api_debug_shard_create'),
]