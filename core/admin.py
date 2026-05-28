from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Node, Shard, ShardMembership, Transaction, 
    ConsensusRound, StorageRecord, ReputationHistory
)


# Customize User Admin to show more info
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Node Admin
class NodeAdmin(admin.ModelAdmin):
    list_display = ('node_id', 'node_type', 'ip_address', 'status', 'reputation_score', 'last_seen')
    list_filter = ('node_type', 'status', 'created_at')
    search_fields = ('node_id', 'ip_address', 'location')
    readonly_fields = ('id', 'created_at', 'last_seen')
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'node_id', 'node_type', 'ip_address', 'location')
        }),
        ('Capabilities', {
            'fields': ('hardware_capability', 'network_bandwidth')
        }),
        ('Status & Reputation', {
            'fields': ('status', 'reputation_score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_seen'),
            'classes': ('collapse',)
        }),
    )


# Shard Admin
class ShardAdmin(admin.ModelAdmin):
    list_display = ('shard_id', 'name', 'service_type', 'is_active', 'created_at')
    list_filter = ('service_type', 'is_active', 'created_at')
    search_fields = ('shard_id', 'name', 'description')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'shard_id', 'name', 'service_type')
        }),
        ('Requirements', {
            'fields': ('minimum_reputation', 'minimum_capability')
        }),
        ('Status', {
            'fields': ('is_active', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ShardMembership Admin
class ShardMembershipAdmin(admin.ModelAdmin):
    list_display = ('node', 'shard', 'role', 'reputation_in_shard', 'joined_at')
    list_filter = ('role', 'shard', 'joined_at')
    search_fields = ('node__node_id', 'shard__name')
    readonly_fields = ('joined_at',)


# Transaction Admin
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_hash', 'sender', 'receiver', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'shard', 'created_at')
    search_fields = ('transaction_hash', 'sender__node_id', 'receiver__node_id')
    readonly_fields = ('id', 'created_at', 'confirmed_at', 'transaction_hash')
    fieldsets = (
        ('Transaction Info', {
            'fields': ('id', 'transaction_hash', 'transaction_type', 'status')
        }),
        ('Participants', {
            'fields': ('sender', 'receiver', 'shard')
        }),
        ('Data', {
            'fields': ('data_size', 'payload_hash', 'offchain_storage_ref')
        }),
        ('Consensus', {
            'fields': ('consensus_rounds',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'confirmed_at'),
            'classes': ('collapse',)
        }),
    )


# ConsensusRound Admin
class ConsensusRoundAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'shard', 'leader', 'status', 'load_factor', 'start_time')
    list_filter = ('status', 'shard', 'start_time')
    search_fields = ('shard__name', 'leader__node_id')
    readonly_fields = ('start_time',)


# StorageRecord Admin
class StorageRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'storage_type', 'data_hash', 'size_bytes', 'timestamp')
    list_filter = ('storage_type', 'timestamp')
    search_fields = ('data_hash', 'transaction__transaction_hash', 'storage_location')
    readonly_fields = ('id', 'timestamp')


# ReputationHistory Admin
class ReputationHistoryAdmin(admin.ModelAdmin):
    list_display = ('node', 'old_score', 'new_score', 'reason', 'timestamp')
    list_filter = ('shard', 'timestamp')
    search_fields = ('node__node_id', 'reason')
    readonly_fields = ('timestamp',)


# Register all models
admin.site.register(Node, NodeAdmin)
admin.site.register(Shard, ShardAdmin)
admin.site.register(ShardMembership, ShardMembershipAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(ConsensusRound, ConsensusRoundAdmin)
admin.site.register(StorageRecord, StorageRecordAdmin)
admin.site.register(ReputationHistory, ReputationHistoryAdmin)
