import math
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count
from ..models import Node, Transaction, ReputationHistory

def calculate_node_reputation(node, shard=None):
    """
    Calculate reputation score for a node based on various factors
    """
    base_score = 5.0  # Neutral starting point
    
    # Hardware capability factor (0-2 points)
    hardware_factor = node.hardware_capability / 5.0
    
    # Uptime factor (check last 24 hours)
    day_ago = timezone.now() - timedelta(hours=24)
    recent_activity = node.last_seen >= day_ago
    uptime_factor = 1.0 if recent_activity else 0.5
    
    # Transaction success rate
    success_rate = calculate_transaction_success_rate(node, shard)
    
    # Consensus participation
    consensus_factor = calculate_consensus_participation(node, shard)
    
    # Penalties for recent failures
    penalty_factor = calculate_penalty_factor(node)
    
    # Calculate final score (0-10 scale)
    reputation = base_score + hardware_factor + uptime_factor
    reputation += success_rate * 2
    reputation += consensus_factor * 1.5
    reputation -= penalty_factor
    
    # Ensure score is within bounds
    reputation = max(0, min(10, reputation))
    
    # Save reputation history if changed significantly
    save_reputation_history(node, shard, reputation)
    
    return round(reputation, 2)

def calculate_transaction_success_rate(node, shard=None):
    """Calculate transaction success rate for a node"""
    transactions = Transaction.objects.filter(sender=node)
    if shard:
        transactions = transactions.filter(shard=shard)
    
    if not transactions.exists():
        return 0.5  # Neutral if no transactions
    
    successful = transactions.filter(status='CONFIRMED').count()
    total = transactions.count()
    
    return successful / total

def calculate_consensus_participation(node, shard=None):
    """Calculate consensus participation score"""
    # This would integrate with actual consensus participation data
    # For now, return a base value
    return 0.7

def calculate_penalty_factor(node):
    """Calculate penalties for bad behavior"""
    hour_ago = timezone.now() - timedelta(hours=1)
    recent_failures = Transaction.objects.filter(
        sender=node,
        status='FAILED',
        created_at__gte=hour_ago
    ).count()
    
    return recent_failures * 0.5

def save_reputation_history(node, shard, new_score):
    """Save reputation change to history"""
    if abs(node.reputation_score - new_score) > 0.1:  # Significant change
        ReputationHistory.objects.create(
            node=node,
            shard=shard,
            old_score=node.reputation_score,
            new_score=new_score,
            reason='Automatic recalculation'
        )

def evaluate_node_for_shard(node, shard):
    """
    Evaluate if a node is suitable for a shard based on requirements
    """
    reputation = node.reputation_score
    capability = node.hardware_capability
    
    # Check minimum requirements
    if reputation < shard.minimum_reputation:
        return False, f"Reputation {reputation} < required {shard.minimum_reputation}"
    
    if capability < shard.minimum_capability:
        return False, f"Capability {capability} < required {shard.minimum_capability}"
    
    # Check node type suitability
    node_type_suitability = {
        'URLLC': ['EDGE', 'CORE'],
        'EMBB': ['EDGE', 'CORE', 'USER'],
        'MIOT': ['IOT', 'EDGE'],
        'MEC': ['EDGE', 'CORE']
    }
    
    if node.node_type not in node_type_suitability.get(shard.service_type, []):
        return False, f"Node type {node.node_type} not suitable for {shard.service_type}"
    
    return True, "Node is suitable for shard"