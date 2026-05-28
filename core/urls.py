"""
Core application URL routing for 6G Blockchain System
"""

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin Management Views
    path('users/', views.user_management, name='user_management'),
    path('nodes/', views.node_management, name='node_management'),
    path('shards/', views.shard_management, name='shard_management'),
    path('transactions/', views.transaction_monitor, name='transaction_monitor'),
    path('consensus/', views.consensus_monitor, name='consensus_monitor'),
    path('storage/', views.storage_management, name='storage_management'),
    
    # Detail Views
    path('shard/<int:shard_id>/', views.shard_detail, name='shard_detail'),
    path('node/<int:node_id>/', views.node_detail, name='node_detail'),
    path('transaction/<int:tx_id>/', views.transaction_detail, name='transaction_detail'),
    
    # API endpoints

]