import time
import random
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from ..models import Node, Shard, ConsensusRound, Transaction

class LoadSensitivePBFT:
    """
    Load-sensitive Practical Byzantine Fault Tolerance consensus mechanism
    """
    
    def __init__(self):
        self.view_number = 0
        self.sequence_number = 0
        
    def process_transaction(self, transaction):
        """
        Process a transaction through PBFT consensus
        """
        shard = transaction.shard
        current_load = self.calculate_shard_load(shard)
        
        # Adjust consensus parameters based on load
        batch_size = self.adjust_batch_size(current_load)
        timeout = self.adjust_timeout(current_load)
        
        # Create consensus round
        round = ConsensusRound.objects.create(
            shard=shard,
            round_number=self.sequence_number,
            load_factor=current_load,
            batch_size=batch_size
        )
        
        # Select leader based on reputation
        leader = self.select_leader(shard)
        round.leader = leader
        round.save()
        
        # PBFT phases
        try:
            # Phase 1: Pre-prepare
            self.pre_prepare_phase(round, transaction)
            
            # Phase 2: Prepare
            if self.prepare_phase(round, transaction):
                # Phase 3: Commit
                if self.commit_phase(round, transaction):
                    # Phase 4: Reply
                    transaction.status = 'CONFIRMED'
                    transaction.confirmed_at = timezone.now()
                    transaction.consensus_rounds = round.round_number
                    transaction.save()
                    
                    round.status = 'DECIDED'
                    round.end_time = timezone.now()
                    round.save()
                    
                    return {'status': 'confirmed', 'round': round.round_number}
            
            # If consensus fails
            transaction.status = 'FAILED'
            transaction.save()
            
            round.status = 'COMMIT'
            round.end_time = timezone.now()
            round.save()
            
            return {'status': 'failed', 'round': round.round_number}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def calculate_shard_load(self, shard):
        """
        Calculate current load of a shard (0-1 scale)
        """
        # Calculate pending transactions
        pending_count = shard.transactions.filter(status='PENDING').count()
        
        # Calculate active nodes
        active_nodes = shard.members.filter(node__status='ACTIVE').count()
        
        # Calculate load factor
        if active_nodes == 0:
            return 1.0
        
        ideal_capacity = active_nodes * 10  # Assume 10 TX per node
        load = min(1.0, pending_count / ideal_capacity)
        
        return round(load, 2)
    
    def adjust_batch_size(self, load_factor):
        """
        Adjust batch size based on load
        """
        if load_factor < 0.3:
            return 20  # Low load, larger batches
        elif load_factor < 0.7:
            return 10  # Medium load, normal batches
        else:
            return 5   # High load, smaller batches
    
    def adjust_timeout(self, load_factor):
        """
        Adjust timeout based on load
        """
        base_timeout = 5  # seconds
        return base_timeout * (1 + load_factor)
    
    def select_leader(self, shard):
        """
        Select leader node for consensus round
        """
        # Get nodes in shard ordered by reputation
        members = shard.members.select_related('node').order_by('-reputation_in_shard')
        
        if not members.exists():
            return None
        
        # Select node with highest reputation as leader
        return members.first().node
    
    def pre_prepare_phase(self, round, transaction):
        """
        PBFT Pre-prepare phase
        """
        # Leader sends pre-prepare message
        # In real implementation, this would send messages to all replicas
        # For simulation, we'll just log it
        print(f"[Round {round.round_number}] Pre-prepare phase for transaction {transaction.id}")
        return True
    
    def prepare_phase(self, round, transaction):
        """
        PBFT Prepare phase
        """
        # Replicas send prepare messages
        # Need 2f+1 prepare messages (where f is number of faulty nodes)
        members = round.shard.members.filter(node__status='ACTIVE')
        total_members = members.count()
        
        # Calculate required quorum
        f = (total_members - 1) // 3  # Maximum faulty nodes
        required_prepares = 2 * f + 1
        
        print(f"[Round {round.round_number}] Prepare phase: need {required_prepares} prepares")
        
        # Simulate prepare messages (in real system, this would be actual messages)
        # Assume all honest nodes prepare
        honest_nodes = total_members - f
        return honest_nodes >= required_prepares
    
    def commit_phase(self, round, transaction):
        """
        PBFT Commit phase
        """
        # Similar to prepare phase
        members = round.shard.members.filter(node__status='ACTIVE')
        total_members = members.count()
        
        f = (total_members - 1) // 3
        required_commits = 2 * f + 1
        
        print(f"[Round {round.round_number}] Commit phase: need {required_commits} commits")
        
        honest_nodes = total_members - f
        return honest_nodes >= required_commits

# Global instance
load_sensitive_pbft = LoadSensitivePBFT()