"""
API views for 6G Blockchain System
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, timedelta

from .models import Node, Shard, Transaction, StorageRecord
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import logging
import traceback

logger = logging.getLogger(__name__)
from django.views.decorators.http import require_http_methods
from django.db.models import Avg
import math

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_stats(request):
    """Get dashboard statistics"""
    try:
        total_nodes = Node.objects.count()
        active_nodes = Node.objects.filter(status='ACTIVE').count()
        total_shards = Shard.objects.filter(is_active=True).count()
        pending_transactions = Transaction.objects.filter(status='PENDING').count()
        
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_tx_count = Transaction.objects.filter(created_at__gte=hour_ago).count()
        
        return JsonResponse({
            'status': 'success',
            'total_nodes': total_nodes,
            'active_nodes': active_nodes,
            'total_shards': total_shards,
            'pending_transactions': pending_transactions,
            'recent_tx_count': recent_tx_count,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def node_list(request):
    """Get list of nodes"""
    try:
        # pagination params
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1
        try:
            per_page = int(request.GET.get('per_page', 25))
        except ValueError:
            per_page = 25

        total_nodes = Node.objects.count()
        total_pages = max(1, math.ceil(total_nodes / per_page)) if per_page > 0 else 1
        page = max(1, min(page, total_pages))

        offset = (page - 1) * per_page
        nodes_qs = Node.objects.all()[offset:offset + per_page]

        nodes_data = []
        for node in nodes_qs:
            membership = node.shard_memberships.first()

            nodes_data.append({
                'id': str(node.id),
                'node_id': node.node_id,
                'node_type': node.node_type,
                'ip_address': node.ip_address,
                'reputation_score': node.reputation_score,
                'hardware_capability': node.hardware_capability,
                'status': node.status,
                'last_seen': node.last_seen.isoformat() if node.last_seen else None,
                'shard': membership.shard.name if membership else None,
                })


        # basic stats expected by frontend
        high_reputation = Node.objects.filter(reputation_score__gte=8).count()
        edge_nodes = Node.objects.filter(node_type='EDGE').count()
        avg_rep = Node.objects.aggregate(avg=Avg('reputation_score'))['avg'] or 0.0
        active = Node.objects.filter(status='ACTIVE').count()
        inactive = Node.objects.filter(status='INACTIVE').count()

        return JsonResponse({
            'status': 'success',
            'nodes': nodes_data,
            'stats': {
                'total': total_nodes,
                'high_reputation': high_reputation,
                'edge_nodes': edge_nodes,
                'avg_reputation': float(avg_rep),
                'active': active,
                'inactive': inactive,
            },
            'total_pages': total_pages,
            'current_page': page,
            'total_nodes': total_nodes,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ---------------- NODE JOIN (POST) ----------------

@csrf_exempt
@require_http_methods(["POST"])
def node_join(request):
    """Create or update a node safely (no duplicate error)"""
    try:
        data = json.loads(request.body or "{}")

        node_id = data.get('node_id')
        if not node_id:
            return JsonResponse({'status': 'error', 'message': 'node_id required'}, status=400)

        node, created = Node.objects.update_or_create(
            node_id=node_id,
            defaults={
                'node_type': data.get('node_type', 'EDGE'),
                'ip_address': data.get('ip_address', '127.0.0.1'),
                'location': data.get('location', ''),
                'hardware_capability': int(data.get('hardware_capability', 1)),
                'reputation_score': float(data.get('reputation_score', 5.0)),
                'status': 'ACTIVE'
            }
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Node created' if created else 'Node updated',
            'node': {
                'id': str(node.id),
                'node_id': node.node_id,
                'node_type': node.node_type,
                'status': node.status
            }
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ---------------- NODE JOIN VIA GET ----------------

@csrf_exempt
@require_http_methods(["GET"])
def node_join_via_get(request):
    """Create or update node via GET (for testing)"""
    try:
        node_id = request.GET.get('node_id')
        if not node_id:
            return JsonResponse({'status': 'error', 'message': 'node_id required'}, status=400)

        node, created = Node.objects.update_or_create(
            node_id=node_id,
            defaults={
                'node_type': request.GET.get('node_type', 'EDGE'),
                'ip_address': request.GET.get('ip_address', '127.0.0.1'),
                'location': request.GET.get('location', ''),
                'hardware_capability': int(request.GET.get('hardware_capability', 1)),
                'reputation_score': float(request.GET.get('reputation_score', 5.0)),
                'status': 'ACTIVE'
            }
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Node created via GET' if created else 'Node updated via GET'
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ---------------- UPDATE NODE STATUS (REAL UPDATE) ----------------

@csrf_exempt
@require_http_methods(["POST"])
def update_node_status(request, node_id):
    """Update node status in database (was mock earlier)"""
    try:
        data = json.loads(request.body or "{}")

        node = Node.objects.filter(id=node_id).first()
        if not node:
            return JsonResponse({'status': 'error', 'message': 'Node not found'}, status=404)

        new_status = data.get('status', 'ACTIVE')
        node.status = new_status
        node.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Node {node.node_id} status updated',
            'new_status': new_status
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)



@csrf_exempt
@require_http_methods(["POST"])
def shard_create(request):
    """Create a new shard from an API request"""
    try:
        data = json.loads(request.body)
        # Basic validation
        shard_id = (data.get('shard_id') or '').strip()
        if not shard_id:
            return JsonResponse({'status': 'error', 'message': 'shard_id is required'}, status=400)

        name = data.get('name') or shard_id or 'New Shard'

        # Normalize service type to allowed choices (case-insensitive)
        requested_type = (data.get('service_type') or 'URLLC').upper()
        allowed_types = [t for t, _ in getattr(Shard, 'SERVICE_TYPES', [])]
        service_type = requested_type if requested_type in allowed_types else 'URLLC'

        if Shard.objects.filter(shard_id=shard_id).exists():
            msg = f"Shard with id '{shard_id}' already exists"
            logger.info(msg)
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        try:
            shard = Shard.objects.create(
                shard_id=shard_id,
                name=name,
                service_type=service_type,
                description=data.get('description', ''),
                minimum_reputation=float(data.get('minimum_reputation', 3.0)),
                minimum_capability=int(data.get('minimum_capability', 3)),
            )
        except (IntegrityError, ValidationError) as e:
            tb = traceback.format_exc()
            logger.error('Error creating shard: %s\n%s', e, tb)
            return JsonResponse({'status': 'error', 'message': str(e), 'trace': tb}, status=400)
        except Exception as e:
            tb = traceback.format_exc()
            logger.error('Unexpected error creating shard: %s\n%s', e, tb)
            return JsonResponse({'status': 'error', 'message': str(e), 'trace': tb}, status=500)

        return JsonResponse({
            'status': 'success',
            'message': 'Shard created',
            'shard': {
                'id': str(shard.id),
                'shard_id': shard.shard_id,
                'name': shard.name,
                'service_type': shard.service_type,
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def update_node_status(request, node_id):
    """Update node status"""
    try:
        data = json.loads(request.body)
        
        # In a real implementation, you would update the node status
        # For now, return a mock response
        return JsonResponse({
            'status': 'success',
            'message': f'Node {node_id} status updated',
            'new_status': data.get('status', 'ACTIVE')
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def transaction_list(request):
    """Get list of transactions"""
    try:
        transactions = Transaction.objects.all().order_by('-created_at')[:50]
        
        transactions_data = []
        for tx in transactions:
            transactions_data.append({
                'id': str(tx.id),
                'transaction_hash': tx.transaction_hash,
                'transaction_type': tx.transaction_type,
                'sender': tx.sender.node_id if tx.sender else None,
                'receiver': tx.receiver.node_id if tx.receiver else None,
                'shard': tx.shard.name if tx.shard else None,
                'status': tx.status,
                'created_at': tx.created_at.isoformat() if tx.created_at else None,
            })
        
        return JsonResponse({
            'status': 'success',
            'transactions': transactions_data,
            'total_transactions': Transaction.objects.count(),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def storage_statistics(request):
    """Get storage statistics"""
    try:
        # Mock data for now
        return JsonResponse({
            'status': 'success',
            'onchain_size': 1024 * 1024 * 10,  # 10MB
            'offchain_size': 1024 * 1024 * 100,  # 100MB
            'total_records': 1500,
            'storage_efficiency': '85%',
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)



@csrf_exempt
@require_http_methods(["POST"])
def start_consensus_round(request):
    """Start a new consensus round"""
    try:
        # In a real implementation, this would start a new consensus round
        # For now, return a mock response
        return JsonResponse({
            'status': 'success',
            'message': 'Consensus round started',
            'round_id': 1001,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def consensus_active_rounds(request):
    """Get active consensus rounds"""
    try:
        # Try to get real data
        from .models import ConsensusRound
        active_rounds = ConsensusRound.objects.filter(
            end_time__isnull=True
        ).order_by('-start_time')[:10]
        
        rounds_data = []
        for round in active_rounds:
            rounds_data.append({
                'id': round.id,
                'round_number': round.round_number,
                'shard_name': round.shard.name if round.shard else 'Unknown',
                'leader': round.leader.node_id if round.leader else 'Electing...',
                'status': round.status,
                'load_factor': round.load_factor,
                'batch_size': round.batch_size,
                'start_time': round.start_time.isoformat() if round.start_time else None,
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(rounds_data),
            'rounds': rounds_data,
        })
        
    except Exception as e:
        # Return mock data if there's an error
        return JsonResponse({
            'status': 'success',
            'count': 2,
            'rounds': [
                {
                    'id': 1,
                    'round_number': 1001,
                    'shard_name': 'URLLC',
                    'leader': 'Node-EDGE-001',
                    'status': 'PRE_PREPARE',
                    'load_factor': 0.65,
                    'batch_size': 10,
                    'start_time': datetime.now().isoformat(),
                },
                {
                    'id': 2,
                    'round_number': 1002,
                    'shard_name': 'eMBB',
                    'leader': 'Node-CORE-005',
                    'status': 'PREPARE',
                    'load_factor': 0.85,
                    'batch_size': 5,
                    'start_time': (datetime.now() - timedelta(seconds=30)).isoformat(),
                }
            ],
        })

@csrf_exempt
@require_http_methods(["GET"])
def consensus_history(request):
    """Get consensus history"""
    try:
        # Try to get real data
        from .models import ConsensusRound
        history = ConsensusRound.objects.filter(
            end_time__isnull=False
        ).order_by('-start_time')[:20]
        
        history_data = []
        for round in history:
            history_data.append({
                'id': round.id,
                'round_number': round.round_number,
                'shard_name': round.shard.name if round.shard else 'Unknown',
                'leader': round.leader.node_id if round.leader else 'N/A',
                'status': round.status,
                'load_factor': round.load_factor,
                'batch_size': round.batch_size,
                'start_time': round.start_time.isoformat() if round.start_time else None,
                'end_time': round.end_time.isoformat() if round.end_time else None,
                'duration': str(round.end_time - round.start_time).split('.')[0] if round.end_time and round.start_time else 'N/A',
            })
        
        return JsonResponse({
            'status': 'success',
            'history': history_data,
        })
        
    except Exception as e:
        # Return mock data
        now = datetime.now()
        mock_history = []
        
        for i in range(10):
            mock_history.append({
                'id': i + 1,
                'round_number': 1000 - i,
                'shard_name': ['URLLC', 'eMBB', 'mIoT', 'MEC'][i % 4],
                'leader': f"Node-{['EDGE', 'CORE', 'IOT', 'USER'][i % 4]}-{str(i+1).zfill(3)}",
                'status': 'DECIDED',
                'load_factor': 0.3 + (i * 0.06),
                'batch_size': [20, 10, 5, 15][i % 4],
                'start_time': (now - timedelta(minutes=i)).isoformat(),
                'end_time': (now - timedelta(minutes=i) + timedelta(seconds=5)).isoformat(),
                'duration': '5s',
            })
        
        return JsonResponse({
            'status': 'success',
            'history': mock_history,
        })


@csrf_exempt
@require_http_methods(["POST"])
def debug_shard_create(request):
    """Debug endpoint: create a test shard and return detailed result (development only)."""
    try:
        import time, uuid, traceback

        shard_id = f"DBG-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        name = f"DebugShard-{shard_id}"
        shard = Shard.objects.create(
            shard_id=shard_id,
            name=name,
            service_type='URLLC',
            description='Debug shard created by debug_shard_create',
            minimum_reputation=1.0,
            minimum_capability=1,
        )

        logger.info('debug_shard_create created shard %s', shard_id)

        return JsonResponse({
            'status': 'success',
            'message': 'Debug shard created',
            'shard': {
                'id': str(shard.id),
                'shard_id': shard.shard_id,
                'name': shard.name,
                'service_type': shard.service_type,
            }
        })
    except Exception as e:
        tb = traceback.format_exc()
        logger.error('debug_shard_create failed: %s\n%s', e, tb)
        return JsonResponse({'status': 'error', 'message': str(e), 'trace': tb}, status=500)