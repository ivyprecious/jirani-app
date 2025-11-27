from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Resident, Payment, Request, WorkOrder, Unit
from django.db.models import Count, Q
from datetime import date

@login_required
def dashboard_view(request):
    # Get current resident
    try:
        resident = Resident.objects.get(user=request.user)
    except Resident.DoesNotExist:
        messages.error(request, "Resident profile not found")
        return redirect('login')
    
    # Get payment summary
    current_month = date.today().month
    payments = Payment.objects.filter(
        resident=resident,
        due_date__month=current_month
    )
    
    payment_summary = {
        'rent': payments.filter(payment_type='rent').first(),
        'additional': payments.filter(payment_type='additional').first(),
        'maintenance': payments.filter(payment_type='maintenance').first(),
        'debt': payments.filter(payment_type='debt').first(),
    }
    
    # Get new requests
    new_requests = Request.objects.filter(
        status='pending'
    ).order_by('-created_at')[:3]
    
    # Get delayed work orders
    delayed_orders = WorkOrder.objects.filter(
        status='delayed'
    ).order_by('-days_late')[:3]
    
    # Get statistics
    stats = {
        'total_residents': Resident.objects.filter(is_active=True).count(),
        'total_units': Unit.objects.count(),
        'vacant_units': Unit.objects.filter(status='vacant').count(),
        'upcoming_units': Unit.objects.filter(status='upcoming').count(),
    }
    
    # Get work order statistics
    work_order_stats = {
        'new': WorkOrder.objects.filter(status='new').count(),
        'open': WorkOrder.objects.filter(status='open').count(),
        'in_progress': WorkOrder.objects.filter(status='in_progress').count(),
        'delayed': WorkOrder.objects.filter(status='delayed').count(),
    }
    
    # Get upcoming units
    upcoming_units = Unit.objects.filter(status='vacant')[:3]
    
    context = {
        'resident': resident,
        'payment_summary': payment_summary,
        'new_requests': new_requests,
        'delayed_orders': delayed_orders,
        'stats': stats,
        'work_order_stats': work_order_stats,
        'upcoming_units': upcoming_units,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'dashboard/login.html')

def signup_view(request):
    if request.method == 'POST':
        # Handle signup logic here
        pass
    return render(request, 'dashboard/signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')