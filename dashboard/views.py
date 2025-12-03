from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Resident, Payment, Request, WorkOrder, Unit, ParkingSlot, Subcontractor
from django.db.models import Count, Q
from datetime import date, datetime
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q, Sum
from dateutil.relativedelta import relativedelta
from decimal import Decimal

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
    all_work_orders = WorkOrder.objects.select_related('assigned_to', 'resident').all()
    
    # Get filter parameters
    filter_status = request.GET.get('status', 'all')
    filter_priority = request.GET.get('priority', 'all')
    filter_category = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    work_orders = all_work_orders
    
    if filter_status != 'all':
        work_orders = work_orders.filter(status=filter_status)
    
    if filter_priority != 'all':
        work_orders = work_orders.filter(priority=filter_priority)
    
    if filter_category != 'all':
        work_orders = work_orders.filter(category=filter_category)
    
    if search_query:
        work_orders = work_orders.filter(
            Q(order_id__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(unit_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Calculate statistics
    stats = {
        'total': all_work_orders.count(),
        'new': all_work_orders.filter(status='new').count(),
        'open': all_work_orders.filter(status='open').count(),
        'in_progress': all_work_orders.filter(status='in_progress').count(),
        'completed': all_work_orders.filter(status='completed').count(),
        'delayed': all_work_orders.filter(status='delayed').count(),
        'urgent': all_work_orders.filter(priority='urgent').count(),
    }
    
    # Get available contractors
    contractors = Subcontractor.objects.filter(status='active')
    
    # Get available units
    residents = Resident.objects.filter(status='active')
    
    context = {
        'work_orders': work_orders.order_by('-created_at'),
        'stats': stats,
        'filter_status': filter_status,
        'filter_priority': filter_priority,
        'filter_category': filter_category,
        'search_query': search_query,
        'contractors': contractors,
        'residents': residents,
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