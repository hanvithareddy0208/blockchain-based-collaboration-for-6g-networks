from django.db import models
import uuid


# ------------------ NODE MODEL ------------------

class Node(models.Model):
    NODE_TYPES = [
        ('EDGE', 'Edge Computing Node'),
        ('CORE', 'Core Network Node'),
        ('IOT', 'IoT Device'),
        ('USER', 'User Equipment'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Allow flexible node ids from API
    node_id = models.CharField(max_length=100, unique=True)

    node_type = models.CharField(max_length=20, choices=NODE_TYPES)
    ip_address = models.GenericIPAddressField()

    # Important fix: allow empty location (prevents 400 error)
    location = models.CharField(max_length=200, blank=True, null=True)

    hardware_capability = models.IntegerField(default=1)
    network_bandwidth = models.FloatField(default=100.0)
    reputation_score = models.FloatField(default=5.0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.node_id} ({self.node_type})"


# ------------------ SHARD MODEL ------------------

class Shard(models.Model):
    SERVICE_TYPES = [
        ('URLLC', 'Ultra-Reliable Low Latency'),
        ('EMBB', 'Enhanced Mobile Broadband'),
        ('MIOT', 'Massive IoT'),
        ('MEC', 'Multi-access Edge Computing'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shard_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)

    description = models.TextField(blank=True, null=True)

    minimum_reputation = models.FloatField(default=3.0)
    minimum_capability = models.IntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.service_type})"


# ------------------ SHARD MEMBERSHIP ------------------

class ShardMembership(models.Model):
    ROLE_CHOICES = [
        ('LEADER', 'Shard Leader'),
        ('VALIDATOR', 'Validator'),
        ('OBSERVER', 'Observer'),
    ]

    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='shard_memberships')
    shard = models.ForeignKey(Shard, on_delete=models.CASCADE, related_name='members')

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VALIDATOR')
    joined_at = models.DateTimeField(auto_now_add=True)
    reputation_in_shard = models.FloatField(default=5.0)

    class Meta:
        unique_together = ['node', 'shard']


# ------------------ TRANSACTION ------------------

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DATA_SHARE', 'Data Sharing'),
        ('RESOURCE_ALLOC', 'Resource Allocation'),
        ('SERVICE_REQ', 'Service Request'),
        ('CONSENSUS', 'Consensus Message'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_hash = models.CharField(max_length=64, unique=True)

    sender = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='received_transactions',
        null=True,
        blank=True
    )

    shard = models.ForeignKey(Shard, on_delete=models.CASCADE, related_name='transactions')

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    data_size = models.IntegerField(default=0)
    payload_hash = models.CharField(max_length=64)

    offchain_storage_ref = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    consensus_rounds = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.transaction_hash[:16]


# ------------------ CONSENSUS ------------------

class ConsensusRound(models.Model):
    STATUS_CHOICES = [
        ('PRE_PREPARE', 'Pre-prepare'),
        ('PREPARE', 'Prepare'),
        ('COMMIT', 'Commit'),
        ('DECIDED', 'Decided'),
    ]

    shard = models.ForeignKey(Shard, on_delete=models.CASCADE, related_name='consensus_rounds', null=True, blank=True)
    round_number = models.IntegerField(default=1)
    leader = models.ForeignKey(Node, on_delete=models.SET_NULL, null=True, blank=True)

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRE_PREPARE')

    load_factor = models.FloatField(default=0.5)
    batch_size = models.IntegerField(default=10)

    def __str__(self):
        return f"Round {self.round_number}"


# ------------------ STORAGE ------------------

class StorageRecord(models.Model):
    STORAGE_TYPES = [
        ('ON_CHAIN', 'On-chain'),
        ('OFF_CHAIN', 'Off-chain'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='storage_records')

    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPES)
    data_hash = models.CharField(max_length=64)
    storage_location = models.CharField(max_length=500)

    metadata = models.JSONField(default=dict)

    timestamp = models.DateTimeField(auto_now_add=True)
    size_bytes = models.IntegerField(default=0)


# ------------------ REPUTATION ------------------

class ReputationHistory(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='reputation_history')
    shard = models.ForeignKey(Shard, on_delete=models.CASCADE, null=True, blank=True)

    old_score = models.FloatField()
    new_score = models.FloatField()

    reason = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
