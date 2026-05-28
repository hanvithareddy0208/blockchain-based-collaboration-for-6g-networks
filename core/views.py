from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib import messages
import json
from datetime import datetime, timedelta

from .models import (
    Node, Shard, ShardMembership, Transaction, ConsensusRound, 
    StorageRecord, ReputationHistory
)
from .forms import UserRegistrationForm
from .utils.reputation import calculate_node_reputation
from .utils.consensus import load_sensitive_pbft

# ============================================
# DECORATORS
# ============================================

def admin_required(view_func):
    """Decorator to restrict access to admin/superuser only"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

# ============================================
# AUTHENTICATION VIEWS
# ============================================

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Login - 6G Blockchain System'
        return context

class CustomLogoutView(LogoutView):
    next_page = 'login'
    
    def dispatch(self, request, *args, **kwargs):
        # Clear all session data on logout
        response = super().dispatch(request, *args, **kwargs)
        request.session.flush()
        return response

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 
                f'Account created successfully! Welcome {user.username}. Please login.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'page_title': 'Register - 6G Blockchain System'
    })

# ============================================
# DASHBOARD VIEWS
# ============================================

@login_required
def dashboard(request):
    """Dashboard - User dashboard or Admin dashboard based on role"""
    
    # Common data
    user_count = User.objects.count()
    
    # Statistics
    total_nodes = Node.objects.count()
    active_nodes = Node.objects.filter(status='ACTIVE').count()
    total_shards = Shard.objects.filter(is_active=True).count()
    pending_transactions = Transaction.objects.filter(status='PENDING').count()
    
    # Recent activity
    recent_transactions = Transaction.objects.all().order_by('-created_at')[:10]
    recent_nodes = Node.objects.all().order_by('-last_seen')[:5]
    
    # Performance metrics
    hour_ago = datetime.now() - timedelta(hours=1)
    recent_tx_count = Transaction.objects.filter(created_at__gte=hour_ago).count()
    
    # All users (for admin)
    all_users = User.objects.all().order_by('-date_joined')
    staff_users = all_users.filter(is_staff=True).count()
    
    # Determine if admin
    is_admin = request.user.is_staff or request.user.is_superuser
    
    context = {
        'is_admin': is_admin,
        'total_nodes': total_nodes,
        'active_nodes': active_nodes,
        'total_shards': total_shards,
        'pending_transactions': pending_transactions,
        'recent_transactions': recent_transactions,
        'recent_nodes': recent_nodes,
        'recent_tx_count': recent_tx_count,
        'all_users': all_users if is_admin else None,
        'total_users': user_count,
        'staff_users': staff_users,
        'page_title': '6G Blockchain Dashboard',
    }
    
    # Use different template based on role
    if is_admin:
        return render(request, 'dashboard.html', context)
    else:
        return render(request, 'user_dashboard.html', context)

# ============================================
# ADMIN MANAGEMENT VIEWS
# ============================================

@login_required
@admin_required
def user_management(request):
    """Admin user management view"""
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'staff_users': users.filter(is_staff=True).count(),
        'page_title': 'User Management',
    }
    return render(request, 'admin/user_management.html', context)

@login_required
def node_management(request):
    """Node management view"""
    nodes = Node.objects.all().prefetch_related('shard_memberships__shard')
    
    node_type = request.GET.get('node_type', '')
    if node_type:
        nodes = nodes.filter(node_type=node_type)
    
    status = request.GET.get('status', '')
    if status:
        nodes = nodes.filter(status=status)
    
    context = {
        'nodes': nodes,
        'node_types': Node.NODE_TYPES if hasattr(Node, 'NODE_TYPES') else [],
        'status_choices': Node.STATUS_CHOICES if hasattr(Node, 'STATUS_CHOICES') else [],
        'page_title': 'Node Management',
    }
    return render(request, 'nodes.html', context)

@login_required
def shard_management(request):
    """Shard management view"""
    shards = Shard.objects.all().prefetch_related('members')
    
    for shard in shards:
        shard.member_count = shard.members.count()
        shard.avg_reputation = shard.members.aggregate(
            avg=Avg('reputation_in_shard')
        )['avg'] or 0
        shard.recent_tx_count = shard.transactions.filter(
            created_at__gte=datetime.now() - timedelta(hours=1)
        ).count()
    
    context = {
        'shards': shards,
        'page_title': 'Shard Management',
    }
    return render(request, 'shards.html', context)

@login_required
def transaction_monitor(request):
    """Transaction monitoring view"""
    transactions = Transaction.objects.all().select_related(
        'sender', 'receiver', 'shard'
    ).order_by('-created_at')
    
    tx_type = request.GET.get('tx_type', '')
    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)
    
    status = request.GET.get('status', '')
    if status:
        transactions = transactions.filter(status=status)
    
    shard_id = request.GET.get('shard', '')
    if shard_id:
        transactions = transactions.filter(shard_id=shard_id)
    
    transactions = transactions[:100]
    
    context = {
        'transactions': transactions,
        'transaction_types': Transaction.TRANSACTION_TYPES if hasattr(Transaction, 'TRANSACTION_TYPES') else [],
        'status_choices': Transaction.STATUS_CHOICES if hasattr(Transaction, 'STATUS_CHOICES') else [],
        'shards': Shard.objects.filter(is_active=True),
        'page_title': 'Transaction Monitor',
    }
    return render(request, 'transactions.html', context)

@login_required
def consensus_monitor(request):
    """Consensus monitoring view"""
    try:
        active_rounds = ConsensusRound.objects.filter(
            end_time__isnull=True
        ).select_related('shard', 'leader').order_by('-start_time')[:10]
        
        recent_rounds = ConsensusRound.objects.all().select_related(
            'shard', 'leader'
        ).order_by('-start_time')[:50]
        
        context = {
            'active_rounds': list(active_rounds),
            'consensus_rounds': list(recent_rounds),
            'page_title': 'Consensus Monitor',
        }
        return render(request, 'consensus.html', context)
        
    except Exception as e:
        context = {
            'active_rounds': [],
            'consensus_rounds': [],
            'page_title': 'Consensus Monitor',
            'error': str(e)
        }
        return render(request, 'consensus.html', context)

@login_required
def storage_management(request):
    """Storage management view"""
    storage_records = StorageRecord.objects.all().select_related(
        'transaction'
    ).order_by('-timestamp')[:100]
    
    onchain_size = StorageRecord.objects.filter(
        storage_type='ON_CHAIN'
    ).aggregate(total=Sum('size_bytes'))['total'] or 0
    
    offchain_size = StorageRecord.objects.filter(
        storage_type='OFF_CHAIN'
    ).aggregate(total=Sum('size_bytes'))['total'] or 0
    
    context = {
        'storage_records': storage_records,
        'onchain_size': onchain_size,
        'offchain_size': offchain_size,
        'page_title': 'Storage Management',
    }
    return render(request, 'storage.html', context)

# ============================================
# DETAIL VIEWS
# ============================================

@login_required
def shard_detail(request, shard_id):
    """Shard details view"""
    shard = get_object_or_404(Shard, id=shard_id)
    nodes = shard.members.select_related('node')
    transactions = shard.transactions.all().order_by('-created_at')[:50]
    
    context = {
        'shard': shard,
        'nodes': nodes,
        'transactions': transactions,
        'page_title': f'{shard.name} Details',
    }
    return render(request, 'shard_detail.html', context)

@login_required
def node_detail(request, node_id):
    """Node details view"""
    node = get_object_or_404(Node, id=node_id)
    shard_memberships = node.shard_memberships.select_related('shard')
    reputation_history = node.reputation_history.all()[:20]
    
    context = {
        'node': node,
        'shard_memberships': shard_memberships,
        'reputation_history': reputation_history,
        'page_title': f'Node {node.node_id}',
    }
    return render(request, 'node_detail.html', context)

@login_required
def transaction_detail(request, tx_id):
    """Transaction details view"""
    transaction = get_object_or_404(Transaction, id=tx_id)
    storage_records = transaction.storage_records.all()
    
    context = {
        'transaction': transaction,
        'storage_records': storage_records,
        'page_title': f'Transaction {transaction.transaction_hash[:16]}...',
    }
    return render(request, 'transaction_detail.html', context)

# ============================================
# API ENDPOINTS
# ============================================

@login_required
def api_node_join(request):
    """API: Node join network"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            node = Node.objects.create(
                node_id=data['node_id'],
                node_type=data['node_type'],
                ip_address=data['ip_address'],
                hardware_capability=data.get('hardware_capability', 1),
                network_bandwidth=data.get('network_bandwidth', 100.0),
            )
            
            reputation = calculate_node_reputation(node)
            node.reputation_score = reputation
            node.save()
            
            return JsonResponse({
                'status': 'success',
                'node_id': str(node.id),
                'reputation_score': reputation
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required
def api_create_transaction(request):
    """API: Create transaction"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            transaction = Transaction.objects.create(
                sender_id=data['sender_id'],
                receiver_id=data.get('receiver_id'),
                shard_id=data['shard_id'],
                transaction_type=data['transaction_type'],
                data_size=data.get('data_size', 0),
                payload_hash=data['payload_hash'],
                offchain_storage_ref=data.get('offchain_storage_ref', ''),
            )
            
            result = load_sensitive_pbft.process_transaction(transaction)
            
            return JsonResponse({
                'status': 'success',
                'transaction_id': str(transaction.id),
                'transaction_hash': transaction.transaction_hash,
                'consensus_result': result
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 
                f'Account created successfully! Welcome {user.username}. Please login.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'page_title': 'Register - 6G Blockchain System'
    })


# Custom login view override for duplicate class
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Login - 6G Blockchain System'
        return context


@login_required
def system_config(request):
    context = {
        'page_title': 'System Configuration',
        'config_sections': [
            {'name': 'Sharding', 'url': 'sharding_config', 'icon': 'fa-sitemap'},
            {'name': 'Consensus', 'url': 'consensus_config', 'icon': 'fa-sync-alt'},
            {'name': 'Reputation', 'url': 'reputation_config', 'icon': 'fa-star'},
            {'name': 'Storage', 'url': 'storage_config', 'icon': 'fa-database'},
            {'name': 'Network', 'url': 'network_config', 'icon': 'fa-network-wired'},
            {'name': 'Security', 'url': 'security_config', 'icon': 'fa-shield-alt'},
        ]
    }
    return render(request, 'system_config.html', context)

@login_required
def network_visualization(request):
    shards = Shard.objects.filter(is_active=True).prefetch_related('members__node')
    nodes = Node.objects.filter(status='ACTIVE')
    
    context = {
        'page_title': 'Network Visualization',
        'shards': shards,
        'nodes': nodes,
    }
    return render(request, 'network_viz.html', context)

@login_required
def system_reports(request):
    context = {
        'page_title': 'System Reports',
        'reports': [
            {'name': 'Performance Report', 'url': 'performance_report', 'icon': 'fa-chart-line'},
            {'name': 'Security Report', 'url': 'security_report', 'icon': 'fa-shield-alt'},
            {'name': 'Usage Report', 'url': 'usage_report', 'icon': 'fa-chart-pie'},
            {'name': 'Node Activity', 'url': 'node_activity_report', 'icon': 'fa-server'},
            {'name': 'Transaction Analysis', 'url': 'transaction_analysis', 'icon': 'fa-exchange-alt'},
            {'name': 'Consensus Statistics', 'url': 'consensus_statistics', 'icon': 'fa-sync-alt'},
        ]
    }
    return render(request, 'reports.html', context)

@login_required
def system_alerts(request):
    alerts = [
        {'type': 'warning', 'message': 'Shard URLLC-1 load exceeded 80%', 'time': '5 minutes ago'},
        {'type': 'info', 'message': 'Node N-2345 joined network', 'time': '10 minutes ago'},
        {'type': 'success', 'message': 'Transaction batch confirmed', 'time': '15 minutes ago'},
    ]
    
    context = {
        'page_title': 'System Alerts',
        'alerts': alerts,
    }
    return render(request, 'alerts.html', context)


