from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Resident, Payment, Request, WorkOrder, Unit, ParkingSlot, Subcontractor
from django.db.models import Count, Q, Max, Sum
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta
from decimal import Decimal

@login_required
def dashboard_view(request):
    from datetime import date, timedelta
    from django.db.models import Sum, Count, Q, Max
    from decimal import Decimal
    
    # Helper function for formatting currency
    def format_currency(amount):
        return "{:,.0f}".format(float(amount))
    
    # Helper function for time ago
    def time_ago(dt):
        if not dt:
            return "Recently"
        
        from django.utils import timezone
        now = timezone.now()
        
        # Convert to datetime if it's a date
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())
        
        # Make datetime timezone-aware if it's naive
        if dt.tzinfo is None:
            dt = timezone.make_aware(dt)
        
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"
    
    # Get current month data
    today = date.today()
    current_month_start = today.replace(day=1)
    
    # ========================================
    # KEY METRICS
    # ========================================
    
    total_units = Unit.objects.count()
    total_residents = Resident.objects.filter(is_active=True, status='active').count()
    occupied_units = Unit.objects.filter(status='occupied').count()
    
    occupancy_rate = 0
    if total_units > 0:
        occupancy_rate = round((occupied_units / total_units) * 100, 1)
    
    # New tenants this month
    new_this_month = Resident.objects.filter(
        move_in_date__gte=current_month_start,
        status='active'
    ).count()
    
    # Monthly revenue
    current_month_payments = Payment.objects.filter(
        due_date__gte=current_month_start,
        payment_type='rent'
    )
    
    monthly_revenue = current_month_payments.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    collected = current_month_payments.filter(status='paid').aggregate(
        total=Sum('amount_paid')
    )['total'] or Decimal('0')
    
    collection_rate = 0
    if monthly_revenue > 0:
        collection_rate = round((collected / monthly_revenue) * 100, 1)
    
    # Pending issues (work orders)
    pending_issues = WorkOrder.objects.filter(
        status__in=['new', 'open', 'in_progress', 'delayed']
    ).count()
    
    urgent_count = WorkOrder.objects.filter(
        priority='urgent',
        status__in=['new', 'open', 'in_progress', 'delayed']
    ).count()
    
    # Parking utilization
    total_parking = ParkingSlot.objects.count()
    assigned_parking = ParkingSlot.objects.filter(status='assigned').count()
    
    parking_utilization = 0
    if total_parking > 0:
        parking_utilization = round((assigned_parking / total_parking) * 100, 1)
    
    available_parking = total_parking - assigned_parking
    
    dashboard_stats = {
        'total_units': total_units,
        'total_residents': total_residents,
        'occupancy_rate': occupancy_rate,
        'new_this_month': new_this_month,
        'monthly_revenue': format_currency(monthly_revenue),
        'collection_rate': collection_rate,
        'pending_issues': pending_issues,
        'urgent_count': urgent_count,
        'parking_utilization': parking_utilization,
        'available_parking': available_parking,
    }
    
    # ========================================
    # FINANCIAL SUMMARY
    # ========================================
    
    outstanding = current_month_payments.filter(
        status__in=['pending', 'partial']
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    overdue = current_month_payments.filter(
        status='overdue'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    collection_percentage = collection_rate
    
    financial_summary = {
        'expected': format_currency(monthly_revenue),
        'collected': format_currency(collected),
        'outstanding': format_currency(outstanding),
        'overdue': format_currency(overdue),
        'collection_percentage': collection_percentage,
    }
    
    # ========================================
    # DELAYED WORK ORDERS
    # ========================================
    
    delayed_orders = WorkOrder.objects.filter(
        status='delayed'
    ).select_related('assigned_to', 'resident').order_by('-days_late')[:5]
    
    # ========================================
    # RECENT TENANT REQUESTS (Simulated from work orders)
    # ========================================
    
    recent_requests_qs = WorkOrder.objects.filter(
        status__in=['new', 'open']
    ).select_related('resident__user', 'assigned_to').order_by('-created_at')[:5]
    
    recent_requests = []
    for wo in recent_requests_qs:
        if wo.resident:
            tenant_name = wo.resident.user.get_full_name()
            tenant_initials = tenant_name[0] + (tenant_name.split()[-1][0] if len(tenant_name.split()) > 1 else '')
        else:
            tenant_name = "Unknown Tenant"
            tenant_initials = "?"
        
        recent_requests.append({
            'tenant_name': tenant_name,
            'tenant_initials': tenant_initials,
            'unit_number': wo.unit_number,
            'description': wo.title,
            'time_ago': time_ago(wo.created_at),
            'priority': wo.priority,
            'get_priority_display': wo.get_priority_display(),
        })
    
    # ========================================
    # WORK ORDER STATS
    # ========================================
    
    wo_total = WorkOrder.objects.count() or 1  # Avoid division by zero
    
    wo_new = WorkOrder.objects.filter(status='new').count()
    wo_open = WorkOrder.objects.filter(status='open').count()
    wo_in_progress = WorkOrder.objects.filter(status='in_progress').count()
    wo_delayed = WorkOrder.objects.filter(status='delayed').count()
    wo_completed = WorkOrder.objects.filter(status='completed').count()
    
    work_order_stats = {
        'new': wo_new,
        'open': wo_open,
        'in_progress': wo_in_progress,
        'delayed': wo_delayed,
        'completed': wo_completed,
        'new_percent': round((wo_new / wo_total) * 100, 0),
        'open_percent': round((wo_open / wo_total) * 100, 0),
        'in_progress_percent': round((wo_in_progress / wo_total) * 100, 0),
        'delayed_percent': round((wo_delayed / wo_total) * 100, 0),
        'completed_percent': round((wo_completed / wo_total) * 100, 0),
    }
    
    # ========================================
    # VACANT UNITS
    # ========================================
    
    vacant_units = Unit.objects.filter(status='vacant').order_by('unit_number')[:6]
    
    # Format rent amounts
    for unit in vacant_units:
        unit.rent_amount = format_currency(unit.rent_amount)
    
    # ========================================
    # TOP CONTRACTORS
    # ========================================
    
    top_contractors_qs = Subcontractor.objects.filter(
        status='active'
    ).annotate(
        completed_jobs=Count('work_orders', filter=Q(work_orders__status='completed'))
    ).order_by('-rating', '-completed_jobs')[:5]
    
    top_contractors = []
    for contractor in top_contractors_qs:
        name_parts = contractor.name.split()
        initials = name_parts[0][0] + (name_parts[-1][0] if len(name_parts) > 1 else '')
        
        top_contractors.append({
            'name': contractor.name,
            'initials': initials,
            'category': contractor.category,
            'get_category_display': contractor.get_category_display(),
            'rating': contractor.rating,
        })
    
    # ========================================
    # RECENT MESSAGES (Simulated)
    # ========================================
    
    # Simulate recent messages from tenants
    recent_messages = [
        {
            'sender_name': 'Grace Mwangi',
            'sender_initials': 'GM',
            'preview': 'Thank you for fixing the AC so quickly!',
            'time_ago': '2h ago',
        },
        {
            'sender_name': 'David Kimani',
            'sender_initials': 'DK',
            'preview': 'When can I expect the plumber to visit?',
            'time_ago': '5h ago',
        },
        {
            'sender_name': 'Aisha Hassan',
            'sender_initials': 'AH',
            'preview': 'Payment confirmation for December rent',
            'time_ago': '1d ago',
        },
    ]
    recent_messages_count = len(recent_messages)
    
    # ========================================
    # CONTEXT
    # ========================================
    
    context = {
        'dashboard_stats': dashboard_stats,
        'financial_summary': financial_summary,
        'delayed_orders': delayed_orders,
        'recent_requests': recent_requests,
        'work_order_stats': work_order_stats,
        'vacant_units': vacant_units,
        'top_contractors': top_contractors,
        'recent_messages': recent_messages,
        'recent_messages_count': recent_messages_count,
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

@login_required
def tenants_view(request):
    # Get all residents
    all_residents = Resident.objects.select_related('user').order_by('-id')
    
    # Get filter from query params
    filter_status = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Filter by status
    if filter_status == 'active':
        residents = all_residents.filter(status='active')
    elif filter_status == 'pending':
        residents = all_residents.filter(status='pending')
    elif filter_status == 'moved_out':
        residents = all_residents.filter(status='moved_out')
    else:
        residents = all_residents
    
    # Search functionality
    if search_query:
        residents = residents.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(unit_number__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Calculate stats
    stats = {
        'total': all_residents.count(),
        'active': all_residents.filter(status='active').count(),
        'pending': all_residents.filter(status='pending').count(),
        'moved_out': all_residents.filter(status='moved_out').count(),
    }
    
    # Get overdue payments count
    from datetime import date
    current_month = date.today().month
    overdue = Payment.objects.filter(
        due_date__month__lt=current_month,
        paid=False
    ).values('resident').distinct().count()
    
    context = {
        'residents': residents,
        'stats': stats,
        'overdue': overdue,
        'filter_status': filter_status,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/tenants.html', context)

@login_required
def add_tenant_view(request):
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            unit_number = request.POST.get('unit_number')
            monthly_rent = request.POST.get('monthly_rent')
            move_in_date = request.POST.get('move_in_date')
            status = request.POST.get('status', 'active')
            
            # Create username from name
            username = f"{first_name.lower()}.{last_name.lower()}"
            
            # Check if username exists, add number if needed
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='password123'  # Default password, should be changed
            )
            
            # Create resident
            resident = Resident.objects.create(
                user=user,
                unit_number=unit_number,
                phone=phone,
                move_in_date=move_in_date,
                monthly_rent=monthly_rent,
                status=status
            )
            
            messages.success(request, f'Successfully added {first_name} {last_name} as a tenant!')
            return redirect('tenants')
            
        except Exception as e:
            messages.error(request, f'Error adding tenant: {str(e)}')
            return redirect('tenants')
    
    return redirect('tenants')

@login_required
def edit_tenant_view(request, resident_id):
    if request.method == 'POST':
        try:
            resident = Resident.objects.get(id=resident_id)
            
            # Update user info
            resident.user.first_name = request.POST.get('first_name')
            resident.user.last_name = request.POST.get('last_name')
            resident.user.email = request.POST.get('email')
            resident.user.save()
            
           # Update resident info
            old_status = resident.status
            resident.phone = request.POST.get('phone')
            resident.unit_number = request.POST.get('unit_number')
            resident.monthly_rent = request.POST.get('monthly_rent')
            resident.move_in_date = request.POST.get('move_in_date')
            resident.status = request.POST.get('status')
            resident.save()

            # Auto-unassign parking if tenant moved out
            if old_status != 'moved_out' and resident.status == 'moved_out':
            # Unassign all parking slots for this resident
                ParkingSlot.objects.filter(resident=resident).update(
                    resident=None,
                    status='available',
                    assigned_date=None
    )
            
            messages.success(request, f'Successfully updated {resident.user.get_full_name()}!')
            return redirect('tenants')
            
        except Resident.DoesNotExist:
            messages.error(request, 'Tenant not found')
            return redirect('tenants')
        except Exception as e:
            messages.error(request, f'Error updating tenant: {str(e)}')
            return redirect('tenants')
    
    return redirect('tenants')

@login_required
def delete_tenant_view(request, resident_id):
    try:
        resident = Resident.objects.get(id=resident_id)
        tenant_name = resident.user.get_full_name()
        
        # Delete the user (this will cascade delete the resident)
        resident.user.delete()
        
        messages.success(request, f'Successfully deleted {tenant_name}')
        return redirect('tenants')
        
    except Resident.DoesNotExist:
        messages.error(request, 'Tenant not found')
        return redirect('tenants')
    except Exception as e:
        messages.error(request, f'Error deleting tenant: {str(e)}')
        return redirect('tenants')
    
@login_required
def parking_view(request):
    # Get all parking slots
    all_slots = ParkingSlot.objects.select_related('resident__user').order_by('-assigned_date', 'slot_number')
    
    # Get filter and search
    filter_status = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Filter by status
    if filter_status == 'assigned':
        slots = all_slots.filter(status='assigned')
    elif filter_status == 'available':
        slots = all_slots.filter(status='available')
    else:
        slots = all_slots
    
    # Search
    if search_query:
        slots = slots.filter(
            Q(slot_number__icontains=search_query) |
            Q(resident__unit_number__icontains=search_query)
        )
    
    # Calculate stats
    stats = {
        'total': all_slots.count(),
        'assigned': all_slots.filter(status='assigned').count(),
        'available': all_slots.filter(status='available').count(),
    }
    
    # Parking rules
    parking_rules = [
        "Park only in your assigned slot (Unit 101 → P-101A & P-101B)",
        "Do not block other vehicles or access ways",
        "Visitors must use designated visitor parking slots",
        "Report any unauthorized vehicles to management immediately",
        "Maintain a maximum speed of 10 km/h within the parking area",
        "No parking in fire lanes or emergency access areas",
        "Each unit is assigned 2 parking slots - contact management for additional slots",
        "Vehicles must display valid parking permits at all times",
    ]
    
    # Get active residents for assignment dropdown
    active_residents = Resident.objects.filter(status='active').select_related('user').order_by('unit_number')
    
    # Get available slots for assignment dropdown
    available_slots = all_slots.filter(status='available').order_by('slot_number')
    
    context = {
        'slots': slots,
        'stats': stats,
        'filter_status': filter_status,
        'search_query': search_query,
        'parking_rules': parking_rules,
        'active_residents': active_residents,
        'available_slots': available_slots,
    }
    
    return render(request, 'dashboard/parking.html', context) 

@login_required
def assign_parking_view(request):
    if request.method == 'POST':
        try:
            slot_number = request.POST.get('slot_number')
            resident_id = request.POST.get('resident_id')
            
            # Get the slot and resident
            slot = ParkingSlot.objects.get(slot_number=slot_number)
            resident = Resident.objects.get(id=resident_id)
            
            # Assign parking
            slot.resident = resident
            slot.status = 'assigned'
            slot.assigned_date = date.today()
            slot.save()
            
            messages.success(request, f'Successfully assigned {slot_number} to {resident.user.get_full_name()} (Unit {resident.unit_number})')
            return redirect('parking')
            
        except ParkingSlot.DoesNotExist:
            messages.error(request, 'Parking slot not found')
            return redirect('parking')
        except Resident.DoesNotExist:
            messages.error(request, 'Tenant not found')
            return redirect('parking')
        except Exception as e:
            messages.error(request, f'Error assigning parking: {str(e)}')
            return redirect('parking')
    
    return redirect('parking')


@login_required
def unassign_parking_view(request, slot_id):
    try:
        slot = ParkingSlot.objects.get(id=slot_id)
        tenant_name = slot.tenant_name if slot.resident else 'Unknown'
        
        # Unassign parking
        slot.resident = None
        slot.status = 'available'
        slot.assigned_date = None
        slot.save()
        
        messages.success(request, f'Successfully unassigned parking slot {slot.slot_number}')
        return redirect('parking')
        
    except ParkingSlot.DoesNotExist:
        messages.error(request, 'Parking slot not found')
        return redirect('parking')
    except Exception as e:
        messages.error(request, f'Error unassigning parking: {str(e)}')
        return redirect('parking')
    
@login_required
def subcontractors_view(request):
    # Get all subcontractors
    all_subcontractors = Subcontractor.objects.order_by('-id')
    
    # Get filter and search
    filter_category = request.GET.get('category', 'all')
    filter_status = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Filter by category
    if filter_category != 'all':
        subcontractors = all_subcontractors.filter(category=filter_category)
    else:
        subcontractors = all_subcontractors
    
    # Filter by status
    if filter_status == 'active':
        subcontractors = subcontractors.filter(status='active')
    elif filter_status == 'inactive':
        subcontractors = subcontractors.filter(status='inactive')
    
    # Search functionality
    if search_query:
        subcontractors = subcontractors.filter(
            Q(name__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Calculate stats
    stats = {
        'total': all_subcontractors.count(),
        'active': all_subcontractors.filter(status='active').count(),
        'inactive': all_subcontractors.filter(status='inactive').count(),
        'work_orders': sum([s.active_work_orders_count() for s in all_subcontractors]),
    }
    
    # Order by name
    subcontractors = subcontractors.order_by('name')
    
    context = {
        'subcontractors': subcontractors,
        'stats': stats,
        'filter_category': filter_category,
        'filter_status': filter_status,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/subcontractors.html', context)


@login_required
def add_subcontractor_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            company_name = request.POST.get('company_name')
            category = request.POST.get('category')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            status = request.POST.get('status', 'active')
            notes = request.POST.get('notes', '')
            
            # Create subcontractor
            Subcontractor.objects.create(
                name=name,
                company_name=company_name,
                category=category,
                phone=phone,
                email=email,
                status=status,
                notes=notes
            )
            
            messages.success(request, f'Successfully added {name} to subcontractors!')
            return redirect('subcontractors')
            
        except Exception as e:
            messages.error(request, f'Error adding subcontractor: {str(e)}')
            return redirect('subcontractors')
    
    return redirect('subcontractors')


@login_required
def edit_subcontractor_view(request, subcontractor_id):
    if request.method == 'POST':
        try:
            subcontractor = Subcontractor.objects.get(id=subcontractor_id)
            
            # Update info
            subcontractor.name = request.POST.get('name')
            subcontractor.company_name = request.POST.get('company_name')
            subcontractor.category = request.POST.get('category')
            subcontractor.phone = request.POST.get('phone')
            subcontractor.email = request.POST.get('email')
            subcontractor.status = request.POST.get('status')
            subcontractor.notes = request.POST.get('notes', '')
            subcontractor.save()
            
            messages.success(request, f'Successfully updated {subcontractor.name}!')
            return redirect('subcontractors')
            
        except Subcontractor.DoesNotExist:
            messages.error(request, 'Subcontractor not found')
            return redirect('subcontractors')
        except Exception as e:
            messages.error(request, f'Error updating subcontractor: {str(e)}')
            return redirect('subcontractors')
    
    return redirect('subcontractors')


@login_required
def delete_subcontractor_view(request, subcontractor_id):
    try:
        subcontractor = Subcontractor.objects.get(id=subcontractor_id)
        name = subcontractor.name
        subcontractor.delete()
        
        messages.success(request, f'Successfully deleted {name}')
        return redirect('subcontractors')
        
    except Subcontractor.DoesNotExist:
        messages.error(request, 'Subcontractor not found')
        return redirect('subcontractors')
    except Exception as e:
        messages.error(request, f'Error deleting subcontractor: {str(e)}')
        return redirect('subcontractors')
    
@login_required
def rent_collection_view(request):
    # Get all rent payments
    all_payments = Payment.objects.filter(payment_type='rent').select_related('resident__user')
    
    # Get current month for stats
    current_month = date.today().strftime('%B %Y')
    current_month_payments = all_payments.filter(month=current_month)
    
    # Get filter parameters
    filter_status = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    payments = all_payments
    
    if filter_status != 'all':
        payments = payments.filter(status=filter_status)
    
    if search_query:
        payments = payments.filter(
            Q(resident__user__first_name__icontains=search_query) |
            Q(resident__user__last_name__icontains=search_query) |
            Q(resident__unit_number__icontains=search_query) |
            Q(transaction_code__icontains=search_query)
        )
    
    # Calculate statistics
    total_expected = current_month_payments.aggregate(Sum('amount'))['amount__sum'] or 0
    total_collected = current_month_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    stats = {
        'total_expected': total_expected,
        'total_collected': total_collected,
        'total_balance': total_expected - total_collected,
        'paid_count': current_month_payments.filter(status='paid').count(),
        'pending_count': current_month_payments.filter(status='pending').count(),
        'overdue_count': current_month_payments.filter(status='overdue').count(),
        'partial_count': current_month_payments.filter(status='partial').count(),
    }
    
    # Calculate collection rate
    if stats['total_expected'] > 0:
        stats['collection_rate'] = round((stats['total_collected'] / stats['total_expected']) * 100, 1)
    else:
        stats['collection_rate'] = 0
    
    context = {
        'payments': payments.order_by('-due_date', 'resident__unit_number'),
        'stats': stats,
        'filter_status': filter_status,
        'search_query': search_query,
        'current_month': current_month,
    }
    
    return render(request, 'dashboard/rent_collection.html', context)


@login_required
def record_payment_view(request, payment_id):
    if request.method == 'POST':
        try:
            payment = Payment.objects.get(id=payment_id)
            
            amount_paid = Decimal(request.POST.get('amount_paid'))
            payment_method = request.POST.get('payment_method')
            transaction_code = request.POST.get('transaction_code', '')
            payment_date = request.POST.get('payment_date')
            notes = request.POST.get('notes', '')
            
            # Update payment
            payment.amount_paid += amount_paid
            payment.payment_method = payment_method
            payment.transaction_code = transaction_code
            payment.paid_date = payment_date
            payment.notes = notes
            payment.save()  # This will auto-update status
            
            messages.success(request, f'Payment of Ksh.{amount_paid} recorded successfully!')
            return redirect('rent_collection')
            
        except Payment.DoesNotExist:
            messages.error(request, 'Payment record not found')
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
    
    return redirect('rent_collection')


@login_required
def generate_invoices_view(request):
    """Generate payment records for all active tenants"""
    if request.method == 'POST':
        try:
            # Get next month
            from datetime import datetime
            from dateutil.relativedelta import relativedelta
            
            next_month_date = date.today() + relativedelta(months=1)
            month_str = next_month_date.strftime('%B %Y')
            due_date = next_month_date.replace(day=5)
            
            # Get all active residents
            active_residents = Resident.objects.filter(status='active')
            
            created_count = 0
            for resident in active_residents:
                # Check if payment already exists for this month
                if not Payment.objects.filter(
                    resident=resident, 
                    month=month_str,
                    payment_type='rent'
                ).exists():
                    Payment.objects.create(
                        resident=resident,
                        month=month_str,
                        amount=resident.monthly_rent,
                        amount_paid=0,
                        payment_type='rent',
                        due_date=due_date,
                        status='pending'
                    )
                    created_count += 1
            
            messages.success(request, f'Successfully generated {created_count} invoices for {month_str}')
            return redirect('rent_collection')
            
        except Exception as e:
            messages.error(request, f'Error generating invoices: {str(e)}')
    
    return redirect('rent_collection')

@login_required
def services_view(request):
    # Get all work orders
    all_orders = WorkOrder.objects.select_related('assigned_to', 'resident').all()
    
    # Get filter parameters
    filter_status = request.GET.get('status', 'all')
    filter_priority = request.GET.get('priority', 'all')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    orders = all_orders
    
    if filter_status != 'all':
        orders = orders.filter(status=filter_status)
    
    if filter_priority != 'all':
        orders = orders.filter(priority=filter_priority)
    
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(unit_number__icontains=search_query) |
            Q(assigned_to__name__icontains=search_query)
        )
    
    # Calculate statistics
    stats = {
        'total': all_orders.count(),
        'new': all_orders.filter(status='new').count(),
        'open': all_orders.filter(status='open').count(),
        'in_progress': all_orders.filter(status='in_progress').count(),
        'completed': all_orders.filter(status='completed').count(),
        'urgent': all_orders.filter(priority='urgent').count(),
    }
    
    # Get residents and contractors for create form
    residents = Resident.objects.filter(status='active')
    contractors = Subcontractor.objects.filter(status='active')
    
    context = {
        'work_orders': orders.order_by('-created_at'),
        'stats': stats,
        'filter_status': filter_status,
        'filter_priority': filter_priority,
        'search_query': search_query,
        'residents': residents,
        'contractors': contractors,
    }
    
    return render(request, 'dashboard/services.html', context)

@login_required
def create_work_order_view(request):
    if request.method == 'POST':
        try:
            # Generate unique order ID
            import random
            order_id = f"WO-{random.randint(1000, 9999)}"
            while WorkOrder.objects.filter(order_id=order_id).exists():
                order_id = f"WO-{random.randint(1000, 9999)}"
            
            title = request.POST.get('title')
            description = request.POST.get('description')
            unit_number = request.POST.get('unit_number')
            category = request.POST.get('category')
            priority = request.POST.get('priority')
            contractor_id = request.POST.get('contractor_id')
            due_date = request.POST.get('due_date')
            
            # Get contractor and resident
            contractor = None
            if contractor_id:
                contractor = Subcontractor.objects.get(id=contractor_id)
            
            resident = Resident.objects.filter(unit_number=unit_number).first()
            
            # Create work order
            work_order = WorkOrder.objects.create(
                order_id=order_id,
                title=title,
                description=description,
                unit_number=unit_number,
                category=category,
                priority=priority,
                assigned_to=contractor,
                resident=resident,
                due_date=due_date if due_date else None,
                status='new'
            )
            
            messages.success(request, f'Work order {order_id} created successfully!')
            return redirect('services')
            
        except Exception as e:
            messages.error(request, f'Error creating work order: {str(e)}')
    
    return redirect('services')


@login_required
def update_work_order_view(request, order_id):
    if request.method == 'POST':
        try:
            work_order = WorkOrder.objects.get(id=order_id)
            
            work_order.title = request.POST.get('title')
            work_order.description = request.POST.get('description')
            work_order.category = request.POST.get('category')
            work_order.priority = request.POST.get('priority')
            work_order.status = request.POST.get('status')
            
            contractor_id = request.POST.get('contractor_id')
            if contractor_id:
                work_order.assigned_to = Subcontractor.objects.get(id=contractor_id)
            
            due_date = request.POST.get('due_date')
            work_order.due_date = due_date if due_date else None
            
            cost = request.POST.get('cost')
            if cost:
                work_order.cost = cost
            
            # If status is completed, set completed_date
            if work_order.status == 'completed' and not work_order.completed_date:
                work_order.completed_date = date.today()
            
            work_order.save()
            
            messages.success(request, f'Work order {work_order.order_id} updated successfully!')
            return redirect('services')
            
        except WorkOrder.DoesNotExist:
            messages.error(request, 'Work order not found')
        except Exception as e:
            messages.error(request, f'Error updating work order: {str(e)}')
    
    return redirect('services')


@login_required
def delete_work_order_view(request, order_id):
    try:
        work_order = WorkOrder.objects.get(id=order_id)
        order_number = work_order.order_id
        work_order.delete()
        
        messages.success(request, f'Work order {order_number} deleted successfully')
        return redirect('services')
        
    except WorkOrder.DoesNotExist:
        messages.error(request, 'Work order not found')
    except Exception as e:
        messages.error(request, f'Error deleting work order: {str(e)}')
    
    return redirect('services')

@login_required
def building_view(request):
    # Get all units
    all_units = Unit.objects.select_related('resident__user').all()
    
    # Get filter parameters
    filter_status = request.GET.get('status', 'all')
    filter_type = request.GET.get('type', 'all')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    units = all_units
    
    if filter_status != 'all':
        units = units.filter(status=filter_status)
    
    if filter_type != 'all':
        units = units.filter(unit_type=filter_type)
    
    if search_query:
        units = units.filter(
            Q(unit_number__icontains=search_query) |
            Q(resident__user__first_name__icontains=search_query) |
            Q(resident__user__last_name__icontains=search_query)
        )
    
    # Calculate statistics
    total_units = all_units.count()
    occupied_units = all_units.filter(status='occupied').count()
    vacant_units = all_units.filter(status='vacant').count()
    maintenance_units = all_units.filter(status='maintenance').count()
    
    # Calculate occupancy rate
    occupancy_rate = 0
    if total_units > 0:
        occupancy_rate = round((occupied_units / total_units) * 100, 1)
    
    # Get total floors
    total_floors = all_units.aggregate(Max('floor'))['floor__max'] or 0
    
    # Get available residents for assignment
    available_residents = Resident.objects.filter(
    is_active=True,  # or status='active' if that's your field
    unit_number__in=['', None]  # tenants with no unit assigned
).select_related('user')
    
    stats = {
        'total_units': total_units,
        'occupied': occupied_units,
        'vacant': vacant_units,
        'maintenance': maintenance_units,
        'occupancy_rate': occupancy_rate,
        'total_floors': total_floors,
    }
    
    context = {
        'units': units.order_by('unit_number'),
        'stats': stats,
        'filter_status': filter_status,
        'filter_type': filter_type,
        'search_query': search_query,
        'available_residents': available_residents,
    }
    
    return render(request, 'dashboard/building.html', context)


@login_required
def create_unit_view(request):
    if request.method == 'POST':
        try:
            unit_number = request.POST.get('unit_number')
            unit_type = request.POST.get('unit_type')
            floor = request.POST.get('floor')
            size_sqm = request.POST.get('size_sqm')
            rent_amount = request.POST.get('rent_amount')
            status = request.POST.get('status')
            description = request.POST.get('description', '')
            
            # Create unit
            Unit.objects.create(
                unit_number=unit_number,
                unit_type=unit_type,
                floor=floor,
                size_sqm=size_sqm,
                rent_amount=rent_amount,
                status=status,
                description=description
            )
            
            messages.success(request, f'Unit {unit_number} created successfully!')
            return redirect('building')
            
        except Exception as e:
            messages.error(request, f'Error creating unit: {str(e)}')
    
    return redirect('building')


@login_required
def update_unit_view(request, unit_id):
    if request.method == 'POST':
        try:
            unit = Unit.objects.get(id=unit_id)
            
            unit.unit_number = request.POST.get('unit_number')
            unit.unit_type = request.POST.get('unit_type')
            unit.floor = request.POST.get('floor')
            unit.size_sqm = request.POST.get('size_sqm')
            unit.rent_amount = request.POST.get('rent_amount')
            unit.status = request.POST.get('status')
            unit.description = request.POST.get('description', '')
            
            unit.save()
            
            messages.success(request, f'Unit {unit.unit_number} updated successfully!')
            return redirect('building')
            
        except Unit.DoesNotExist:
            messages.error(request, 'Unit not found')
        except Exception as e:
            messages.error(request, f'Error updating unit: {str(e)}')
    
    return redirect('building')


@login_required
def assign_tenant_to_unit_view(request, unit_id):
    if request.method == 'POST':
        try:
            unit = Unit.objects.get(id=unit_id)
            resident_id = request.POST.get('resident_id')
            
            if resident_id:
                resident = Resident.objects.get(id=resident_id)
                
                # Unassign any previous unit for this resident
                if hasattr(resident, 'assigned_unit') and resident.assigned_unit:
                    old_unit = resident.assigned_unit
                    old_unit.resident = None
                    old_unit.status = 'vacant'
                    old_unit.save()
                
                # Assign to new unit
                unit.resident = resident
                unit.status = 'occupied'
                
                # Update resident's unit_number
                resident.unit_number = unit.unit_number
                resident.monthly_rent = unit.rent_amount
                resident.save()
                
                unit.save()
                
                messages.success(request, f'{resident.user.get_full_name()} assigned to Unit {unit.unit_number}!')
            else:
                # Unassign tenant
                if unit.resident:
                    unit.resident = None
                    unit.status = 'vacant'
                    unit.save()
                    messages.success(request, f'Unit {unit.unit_number} is now vacant')
            
            return redirect('building')
            
        except Unit.DoesNotExist:
            messages.error(request, 'Unit not found')
        except Resident.DoesNotExist:
            messages.error(request, 'Resident not found')
        except Exception as e:
            messages.error(request, f'Error assigning tenant: {str(e)}')
    
    return redirect('building')


@login_required
def delete_unit_view(request, unit_id):
    try:
        unit = Unit.objects.get(id=unit_id)
        unit_number = unit.unit_number
        unit.delete()
        
        messages.success(request, f'Unit {unit_number} deleted successfully')
        return redirect('building')
        
    except Unit.DoesNotExist:
        messages.error(request, 'Unit not found')
    except Exception as e:
        messages.error(request, f'Error deleting unit: {str(e)}')
    
    return redirect('building')

@login_required
def reports(request):
   
    # Get period filter (default to current month)
    period = request.GET.get('period', 'current_month')
    
    # Calculate date ranges
    today = datetime.now().date()
    if period == 'current_month':
        start_date = today.replace(day=1)
        end_date = today
    elif period == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = last_month
    elif period == 'last_3_months':
        start_date = today - timedelta(days=90)
        end_date = today
    elif period == 'last_6_months':
        start_date = today - timedelta(days=180)
        end_date = today
    elif period == 'year_to_date':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date = today.replace(day=1)
        end_date = today
    
    # ========================================
    # FINANCIAL DATA
    # ========================================
    
    payments = Payment.objects.filter(
        due_date__range=[start_date, end_date]
    )
    
    total_collected = payments.filter(status='paid').aggregate(
        total=Sum('amount_paid')
    )['total'] or Decimal('0')
    
    # Get overdue AMOUNT (not count)
    overdue = payments.filter(status='overdue').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    total_expected = payments.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    collection_rate = 0
    if total_expected > 0:
        collection_rate = round((total_collected / total_expected) * 100, 1)
    
    # Format numbers with commas
    def format_currency(amount):
        return "{:,.0f}".format(float(amount))
    
    financial_data = {
        'total_collected': format_currency(total_collected),
        'total_expected': format_currency(total_expected),
        'overdue': format_currency(overdue),
        'collection_rate': collection_rate,
    }
    
    # Recent payments for table
    recent_payments = Payment.objects.filter(
        paid=True,
        paid_date__isnull=False
    ).select_related('resident__user').order_by('-paid_date')[:10]
    
    # Format payment amounts with commas
    for payment in recent_payments:
        payment.amount_paid_formatted = "{:,.0f}".format(float(payment.amount_paid))
    
    # ========================================
    # OCCUPANCY DATA
    # ========================================
    
    total_units = Unit.objects.count()
    occupied_units = Unit.objects.filter(status='occupied').count()
    vacant_units = Unit.objects.filter(status='vacant').count()
    
    occupancy_rate = 0
    if total_units > 0:
        occupancy_rate = round((occupied_units / total_units) * 100, 1)
    
    occupancy_data = {
        'total_units': total_units,
        'occupied': occupied_units,
        'vacant': vacant_units,
        'occupancy_rate': occupancy_rate,
    }
    
    # ========================================
    # MAINTENANCE DATA
    # ========================================
    
    total_orders = WorkOrder.objects.count()
    completed_orders = WorkOrder.objects.filter(status='completed').count()
    in_progress_orders = WorkOrder.objects.filter(status='in_progress').count()
    
    # Calculate average response time (simplified - in real app, track actual times)
    avg_response_time = 24  # Placeholder - implement actual calculation
    
    maintenance_data = {
        'total_orders': total_orders,
        'completed': completed_orders,
        'in_progress': in_progress_orders,
        'avg_response_time': avg_response_time,
    }
    
    # Top contractors
    top_contractors = Subcontractor.objects.filter(
        status='active'
    ).annotate(
        completed_jobs=Count('work_orders', filter=Q(work_orders__status='completed'))
    ).order_by('-rating', '-completed_jobs')[:5]
    
    # Add avg response time to contractors (placeholder)
    for contractor in top_contractors:
        contractor.avg_response_time = 18  # Placeholder
    
    # ========================================
    # TENANT REPORTS
    # ========================================
    
    tenant_reports = []
    residents = Resident.objects.filter(
        is_active=True
    ).select_related('user')
    
    for resident in residents:
        # Calculate payment statistics
        resident_payments = Payment.objects.filter(resident=resident)
        payment_count = resident_payments.filter(paid=True).count()
        
        outstanding_amount = resident_payments.filter(
            status__in=['pending', 'partial', 'overdue']
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        # Create tenant report data
        tenant_data = {
            'user': resident.user,
            'unit_number': resident.unit_number,
            'move_in_date': resident.move_in_date,
            'monthly_rent': "{:,.0f}".format(float(resident.monthly_rent)),
            'payment_count': payment_count,
            'outstanding': "{:,.0f}".format(float(outstanding_amount)),
            'outstanding_raw': outstanding_amount,  # For comparison
            'status': resident.status,
            'get_status_display': resident.get_status_display,
        }
        tenant_reports.append(type('obj', (object,), tenant_data))
    
    # ========================================
    # CONTEXT
    # ========================================
    
    context = {
        'financial_data': financial_data,
        'recent_payments': recent_payments,
        'occupancy_data': occupancy_data,
        'maintenance_data': maintenance_data,
        'top_contractors': top_contractors,
        'tenant_reports': tenant_reports,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'dashboard/reports.html', context)


@login_required
def export_report(request, report_type, file_format):
    
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.{file_format}"'
    
    # TODO: Generate actual report file
    response.write(b'Report export coming soon...')
    
    return response