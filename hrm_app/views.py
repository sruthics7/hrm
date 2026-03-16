from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile,User,Child,SubChild
from .models import Module
from django.shortcuts import render, get_object_or_404, redirect
from datetime import date
from .forms import EmployeeForm,Employee,RegistrationForm
from .models import Department,Employee,SubSubChild
from decimal import Decimal, InvalidOperation
from .forms import LeaveRequestForm
from .models import LeaveRequest
from django.http import JsonResponse
from .models import Event  
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive, now, localtime
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash
from .models import Attendance
from datetime import date, time, timedelta 
from .models import Holiday
from .models import Employee, Payroll
from django.http import HttpResponse
import csv
import pytz
IST = pytz.timezone("Asia/Kolkata")
from .models import Notification, NotificationRecipient
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from .models import Profile, Module 
from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, Q
from django.core.mail import send_mail
from django.conf import settings


@csrf_protect
@never_cache
def login_view(request):
    # If user already logged in → redirect based on user group
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.usergroup == 'Super Admin':
                return redirect('superadmin_index')
            elif profile.usergroup == 'Admin':
                return redirect('admin_index')
            elif profile.usergroup == 'Employee':
                return redirect('employee_index')
        except Profile.DoesNotExist:
            messages.error(request, "User profile not found.")
            auth_logout(request)
            return redirect('login')

    # Handle login POST
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            try:
                profile = user.profile
                request.session['usergroup'] = profile.usergroup

                if profile.usergroup == 'Super Admin':
                    return redirect('superadmin_index')
                elif profile.usergroup == 'Admin':
                    return redirect('admin_index')
                elif profile.usergroup == 'Employee':
                    return redirect('employee_index')
                else:
                    messages.error(request, "User group not recognized.")
                    return redirect('login')
            except Profile.DoesNotExist:
                messages.error(request, "User profile not found.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'dashboard/login.html', {'form': form})


@login_required
def index(request):
    try:
        profile = request.user.profile
        usergroup = profile.usergroup

        # Calculate total employees here — this is what the card needs
        total_employees = Employee.objects.count()

        context = {
            'total_employees': total_employees,  # ← This is what your card needs
        }

        if usergroup == 'Super Admin':
            return render(request, 'dashboard/superadmin_index.html', context)

        elif usergroup == 'Admin':
            return render(request, 'dashboard/admin_index.html', context)

        elif usergroup == 'Employee':
            return render(request, 'dashboard/employee_index.html', context)

        else:
            messages.error(request, "Invalid user group.")
            return redirect('login')

    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('login')

@login_required
def admin_index(request):
    return render(request, 'dashboard/index.html')


@login_required
def employee_index(request):
    return render(request, 'employee/index.html')


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')



def index(request):
    """
    Generic landing page for logged-in users - redirects to proper dashboard.
    """
    try:
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.usergroup == 'Admin':
            return redirect('admin_index')
        elif user_profile.usergroup == 'Employee':
            return redirect('employee_index')
        else:
            messages.error(request, "Invalid user group.")
            return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "User profile not assigned.")
        auth_logout(request)
        return redirect('login')

@login_required
def superadmin_index(request):
    try:
        profile = request.user.profile
        if profile.usergroup != 'Super Admin':
            messages.error(request, "Access denied. You are not authorized to access Super Admin dashboard.")
            return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "User profile not assigned.")
        return redirect('login')

    modules = Module.objects.all()
    return render(request, 'dashboard/index.html', {
        'modules': modules,
        'global_user_profile': profile,
    })

@login_required
def admin_index(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
        # Only users with usergroup='Admin' can access admin dashboard
        if user_profile.usergroup != 'Admin':
            messages.error(request, "Access denied. You are not authorized to access Admin dashboard.")
            return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "User profile not assigned.")
        return redirect('login')

    modules = Module.objects.all()
    return render(request, 'dashboard/index.html', {
        'modules': modules,
        'global_user_profile': user_profile,
    })

@login_required
def employee_index(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.usergroup != 'Employee':
            messages.error(request, "You are not authorized to access Employee dashboard.")
            return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "User profile not assigned.")
        return redirect('login')

    modules = Module.objects.all()
    return render(request, 'employee/index.html', {
        'modules': modules,
        'global_user_profile': user_profile,
    })

def logout_view(request):
    username = request.user.username if request.user.is_authenticated else "User"
    auth_logout(request)
    messages.success(request, f"Goodbye {username}! You have successfully logged out.")
    return redirect('login')


# @login_required
# def index(request):
#     modules = Module.objects.all()
#     user_profile = Profile.objects.filter(user=request.user).first()
#     return render(request, 'dashboard/index.html', {
#         'modules': modules,
#         'global_user_profile': user_profile,
#     })


@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    
    errors = {}

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password1', '')
        image = request.FILES.get('image')
        usergroup = request.POST.get('usergroup', '').strip()  # ADDED THIS LINE

        # Validate inputs
        if not name:
            errors['name'] = ['Name is required.']
        if not email:
            errors['email'] = ['Email is required.']
        if not username:
            errors['username'] = ['Username is required.']
        elif User.objects.exclude(id=user.id).filter(username=username).exists():
            errors['username'] = ['Username already exists.']
        elif User.objects.exclude(id=user.id).filter(email=email).exists():
            errors['email'] = ['Email already exists.']
        
        if not errors:
            # Update User model
            user.username = username
            user.email = email
            user.save()

            # Update Profile model
            profile.name = name
            profile.usergroup = usergroup  # ADDED THIS LINE
            if image:
                profile.image = image
            profile.save()

            # Update password if provided
            if password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password updated. You may need to log in again.')

            messages.success(request, 'Profile updated successfully.')
            return redirect('profile', user_id=user.id)

        # If there are validation errors, fall through to re-render form

        form_data = {
            'name': name,
            'email': email,
            'username': username,
            'usergroup': usergroup,  # CHANGED FROM profile.usergroup TO usergroup
            'password1': password,
            'image': profile.image,
        }
        # Attach error lists to the corresponding fields
        for field in ['name', 'email', 'username', 'password1']:
            if field not in errors:
                errors[field] = []
        form_data = {**form_data, **errors}
    else:
        # GET method
        form_data = {
            'name': profile.name,
            'email': user.email,
            'username': user.username,
            'usergroup': profile.usergroup,
            'image': profile.image,
        }

    return render(request, 'dashboard/profile.html', {
        'profile': profile,
        'form_data': form_data,
        'user': user
    })    

def add_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Create the related Profile
            Profile.objects.create(
                user=user,
                usergroup=form.cleaned_data['usergroup'],
                name=form.cleaned_data['name'],
                image=form.cleaned_data.get('image')
            )

            return redirect('teammanagement')
    else:
        form = RegistrationForm()

    return render(request, 'dashboard/add_user.html', {'form': form})


def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)

    if user_to_delete.is_superuser:
        messages.error(request, "You cannot delete another admin.")
    else:
        user_to_delete.delete()
        messages.success(request, "User removed successfully.")

    return redirect('teammanagement')  # Update this with the correct name for your user list view







def module_view(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    
    # Determine the template dynamically
    if module.url_name:
        template_name = f'dashboard/{module.url_name}.html'
    else:
        template_name = 'dashboard/index.html'
    
    return render(request, template_name, {'module': module})

def child_view(request, child_id):
   
    child = get_object_or_404(Child, id=child_id)

    # Decide which template to render based on the child's url_name
    if child.url_name:
        template_path = f'dashboard/{child.url_name}'
    else:
        template_path = 'dashboard/add_usergroup.html'  # fallback

    return render(request, template_path, {'child': child})

# views.py

def sub_child_view(request, sub_child_id):
    sub_child = get_object_or_404(SubChild, id=sub_child_id)

    # Determine the template dynamically
    if sub_child.url_name:
        template_path = f'dashboard/{sub_child.url_name}'
    else:
        template_path = 'dashboard/default_sub_child.html'  # Fallback template

    return render(request, template_path, {'sub_child': sub_child})


def subsubchild_view(request, subsubchild_id):
    subsubchild = get_object_or_404(SubSubChild, id=subsubchild_id)

    # Decide which template to render based on subsubchild's url_name
    if subsubchild.url_name:
        template_path = f'dashboard/{subsubchild.url_name}'
    else:
        template_path = 'dashboard/default_subsubchild.html'  # Fallback template

    return render(request, template_path, {'subsubchild': subsubchild})

# @login_required
# def employes(request):
#     """
#     Show all employees created by Super Admin (usergroup = 'Employee').
#     """
#     if not hasattr(request.user, 'profile'):
#         messages.error(request, "Profile not found.")
#         return redirect('index')

#     # Get all employees that have a linked user with Employee usergroup
#     employees = Employee.objects.select_related('department', 'user__profile').filter(
#         user__profile__usergroup='Employee'
#     ).order_by('id')

#     return render(request, 'dashboard/employes.html', {
#         'employees': employees,
#     })

# attendance

def attendance(request):
    
    return render(request, 'employee/attendance.html')



@login_required
def leavetracker(request):
    profile = request.user.profile
    leave_type_choices = LeaveRequest.LEAVE_TYPE_CHOICES
    total_leaves = 12  # Total Casual Leave allocation

    
    # Taken leaves: Only Approved non-Emergency leaves count towards balance
    taken_leaves = (
        LeaveRequest.objects.filter(
            user=request.user,
            status='Approved'
        )
        .exclude(leave_type__in=['EL', 'ML'])
        .aggregate(total_days=models.Sum('days'))['total_days'] or 0
    )

    remaining_leaves = total_leaves - taken_leaves
    today = timezone.now().date()
    holidays = Holiday.objects.filter(date__gte=today)

    # === Medical Leave Statistics ===
    approved_medical_days = LeaveRequest.objects.filter(
    user=request.user,
    leave_type='ML',
    status='Approved'
    ).aggregate(total=models.Sum('days'))['total'] or 0

    pending_medical_count = LeaveRequest.objects.filter(
        user=request.user,
        leave_type='ML',
        status='Pending'
    ).count()

    remaining_medical_leaves = 2 - approved_medical_days  # Only approved count

    # === Compensated (Emergency) Leaves ===
    compensated_leaves_data = LeaveRequest.objects.filter(
        user=request.user,
        status='Approved',
        leave_type='EL'
    ).aggregate(total_days=models.Sum('days'))
    compensated_leaves = compensated_leaves_data['total_days'] or 0

    # === Leave History ===
    if profile.usergroup in ['Admin', 'Super Admin']:
        leave_history = LeaveRequest.objects.select_related('user').all().order_by('-applied_on')
    else:
        leave_history = LeaveRequest.objects.filter(user=request.user).order_by('-applied_on')

    # === Handle POST Requests ===
    if request.method == 'POST':

        # ── Employee applying for leave ──────────────────────────────────────
        if profile.usergroup == 'Employee':
            form = LeaveRequestForm(request.POST, request.FILES)
            if form.is_valid():
                leave = form.save(commit=False)

                # Normalize dates
                start_date = leave.start_date.date() if hasattr(leave.start_date, 'date') else leave.start_date
                end_date = leave.end_date.date() if hasattr(leave.end_date, 'date') else leave.end_date

                if end_date < start_date:
                    messages.error(request, "End date cannot be before start date.")
                    return redirect('leavetracker')

                leave_days = (end_date - start_date).days + 1
                leave_type = leave.leave_type

                # Backdating rules: ML and EL allowed (within 30 days)
                if leave_type in ['ML', 'EL']:
                    max_backdate = today - timedelta(days=30)
                    if start_date < max_backdate:
                        messages.error(request, f"{leave.get_leave_type_display()} can only be applied within the last 30 days.")
                        return redirect('leavetracker')
                    if start_date > today:
                        messages.warning(request, f"{leave.get_leave_type_display()} is typically for past or current dates. Please confirm.")
                # Casual Leave: must be future

                elif leave_type == 'CL':
                    two_days_later = today + timedelta(days=2)
                
                    if start_date <= two_days_later:
                        messages.error(
                            request,
                            "Casual Leave must be applied at least 2 days in advance."
                        )
                        return redirect('leavetracker')
                    # Check if CL is before/after holiday or weekend
                    previous_day = start_date - timedelta(days=1)
                    next_day = start_date + timedelta(days=1)
                
                    is_holiday_before = Holiday.objects.filter(date=previous_day).exists()
                    is_holiday_after = Holiday.objects.filter(date=next_day).exists()
                
                    is_weekend_before = previous_day.weekday() in [5, 6]  # Saturday or Sunday
                    is_weekend_after = next_day.weekday() in [5, 6]
                
                    if is_holiday_before or is_holiday_after or is_weekend_before or is_weekend_after:
                        leave.is_paid = False
                        messages.warning(
                            request,
                            "Casual Leave attached to a holiday/weekend will be treated as Unpaid Leave or must be compensated."
                        )
                    else:
                        leave.is_paid = True
                
                    # Monthly CL rule
                    existing_cl = LeaveRequest.objects.filter(
                        user=request.user,
                        leave_type='CL',
                        start_date__year=start_date.year,
                        start_date__month=start_date.month
                    ).count()
                
                    if existing_cl >= 1:
                        leave.is_paid = False
                        messages.warning(request, "This leave will be marked as Unpaid Casual Leave.")
                    existing_cl = LeaveRequest.objects.filter(
                        user=request.user,
                        leave_type='CL',
                        start_date__year=start_date.year,
                        start_date__month=start_date.month
                    ).count()
                
                    # First CL → Paid
                    if existing_cl >= 1:
                        leave.is_paid = False   # mark as unpaid
                        messages.warning(request, "This leave will be marked as Unpaid Casual Leave.")
                    else:
                        leave.is_paid = True

                # Medical Leave: Max 2, proof required
                if leave_type == 'ML':
                    if approved_medical_days >= 2:
                        messages.error(request, "You have already used your maximum of 2 Medical Leaves.")
                        return redirect('leavetracker')
                    if not leave.medical_proof:
                        messages.error(request, "Medical proof (file upload) is required for Medical Leave.")
                        return redirect('leavetracker')
                 # Check only one CL per month
                

                # Overlapping leaves check
                overlapping = LeaveRequest.objects.filter(
                    user=request.user,
                    status__in=['Pending', 'Approved']
                ).exclude(end_date__lt=start_date).exclude(start_date__gt=end_date)

                if overlapping.exists():
                    messages.error(request, "You already have a leave request overlapping these dates.")
                    return redirect('leavetracker')

                # Holiday overlap warning
                holiday_conflicts = Holiday.objects.filter(date__range=[start_date, end_date])
                if holiday_conflicts.exists():
                    names = ", ".join([h.name for h in holiday_conflicts])
                    messages.warning(request, f"Selected dates include holidays: {names}")

                # Save the request
                leave.user = request.user
                leave.status = 'Pending'
                # NOTE: Emergency Leave is_compensated stays False by default.
                # Admin must explicitly mark it as compensated after the employee works back the day.

                try:
                    leave.save()

                    if leave_type == 'ML':
                        messages.success(
                            request,
                            f"Medical Leave request ({leave.days} day(s)) submitted. "
                            f"You have {remaining_medical_leaves - 1} Medical Leave(s) remaining after approval. "
                            "Pending admin approval."
                        )
                    elif leave_type == 'EL':
                        messages.success(
                            request,
                            f"Emergency Leave request ({leave.days} day(s)) submitted. "
                            "Salary will be deducted until admin marks it as compensated."
                        )
                    else:
                        messages.success(
                            request,
                            f"Casual Leave request ({leave.days} day(s)) submitted successfully. "
                            "Will be deducted from balance once approved."
                        )
                    return redirect('leavetracker')
                except ValidationError as e:
                    for error in e.messages:
                        messages.error(request, error)

            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label if field != '__all__' else ''}: {error}".strip())

            return redirect('leavetracker')

        # ── Admin / Super Admin actions ──────────────────────────────────────
        elif profile.usergroup in ['Admin', 'Super Admin']:
            leave_id = request.POST.get('leave_id')
            action = request.POST.get('action')

            if leave_id and action:
                leave = get_object_or_404(LeaveRequest, id=leave_id)

                # ── APPROVE ──────────────────────────────────────────────────
                if action == 'approve':
                    # Check Medical Leave limit
                    if leave.leave_type == 'ML':
                        current_approved_ml = LeaveRequest.objects.filter(
                            user=leave.user,
                            leave_type='ML',
                            status='Approved'
                        ).count()
                        if current_approved_ml >= 2:
                            messages.error(
                                request,
                                f"Cannot approve: {leave.user.get_full_name() or leave.user.username} "
                                "has already used 2 Medical Leaves."
                            )
                            return redirect('leavetracker')

                    # ── FIX: For Emergency Leave, bypass the model's clean() validation
                    # by setting is_compensated temporarily or using update() instead of save()
                    if leave.leave_type == 'EL':
                        # Use update() to skip full_clean() — Emergency Leave approved but NOT compensated yet
                        LeaveRequest.objects.filter(id=leave.id).update(status='Approved')
                        leave.refresh_from_db()
                    else:
                        leave.status = 'Approved'
                        try:
                            leave.save()
                        except ValidationError as e:
                            for error in e.messages:
                                messages.error(request, error)
                            return redirect('leavetracker')

                    # === Send Email Notification ===
                    try:
                        employee_name = leave.user.get_full_name() or leave.user.username
                        employee_email = leave.user.email
                        leave_type_display = leave.get_leave_type_display()

                        employee_designation = getattr(leave.user.profile, 'designation', 'Employee')
                        employee_id = getattr(leave.user.profile, 'employee_id', 'N/A')

                        start_date = leave.start_date.date() if hasattr(leave.start_date, 'date') else leave.start_date
                        end_date = leave.end_date.date() if hasattr(leave.end_date, 'date') else leave.end_date

                        if leave.leave_type == 'CL':
                            employee_taken_leaves = (
                                LeaveRequest.objects.filter(
                                    user=leave.user,
                                    status='Approved'
                                )
                                .exclude(leave_type__in=['EL', 'ML'])
                                .aggregate(total_days=models.Sum('days'))['total_days'] or 0
                            )
                            employee_remaining_leaves = total_leaves - employee_taken_leaves - leave.days
                            remaining_text = f"Remaining Casual Leaves: {employee_remaining_leaves}"

                        elif leave.leave_type == 'ML':
                            employee_approved_ml = LeaveRequest.objects.filter(
                                user=leave.user,
                                leave_type='ML',
                                status='Approved'
                            ).count()
                            employee_remaining_ml = 2 - employee_approved_ml - 1
                            remaining_text = f"Remaining Medical Leaves: {employee_remaining_ml}"

                        elif leave.leave_type == 'EL':
                            remaining_text = "Note: Salary will be deducted until this leave is marked as compensated by admin."

                        else:
                            remaining_text = "Remaining Leaves: N/A"

                        subject = f'Leave Approved - {employee_name} ({start_date.strftime("%b %d")} to {end_date.strftime("%b %d, %Y")})'

                        message = f"""Dear Sir,

I am writing to formally inform you that my leave request has been approved from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} due to {leave.reason}.

Thank you.

Best regards,
{employee_name}
{employee_designation}

---
Leave Type: {leave_type_display}
Total Days: {leave.days}
{remaining_text}
Status: Approved
"""

                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=employee_email,
                            recipient_list=['sruthics742001@gmail.com'],
                            fail_silently=False,
                        )
                    except Exception as e:
                        print(f"Email sending failed: {str(e)}")
                        messages.warning(request, "Leave approved but email notification failed.")

                    if leave.leave_type == 'ML':
                        remaining_after = 2 - (current_approved_ml + 1)
                        messages.success(
                            request,
                            f"Medical Leave for {leave.user} approved ({leave.days} days). "
                            f"They now have {remaining_after} Medical Leave(s) remaining."
                        )
                    elif leave.leave_type == 'EL':
                        messages.success(
                            request,
                            f"Emergency Leave for {leave.user} approved ({leave.days} days). "
                            "Salary will be deducted until marked as compensated."
                        )
                    else:
                        messages.success(request, f"Leave for {leave.user} approved ({leave.days} days).")

                # ── REJECT ───────────────────────────────────────────────────
                elif action == 'reject':
                    leave.status = 'Rejected'
                    leave.save()
                    messages.warning(request, f"Leave request for {leave.user} rejected ({leave.days} days).")

                # ── COMPENSATE ───────────────────────────────────────────────
                elif action == 'compensate':
                    if leave.leave_type == 'EL' and leave.status == 'Approved':
                        if leave.is_compensated:
                            messages.warning(request, f"This Emergency Leave for {leave.user} is already compensated.")
                        else:
                            compensation_date_str = request.POST.get('compensation_date')
                            if not compensation_date_str:
                                messages.error(request, "Please select a compensation date.")
                                return redirect('leavetracker')
                            try:
                                from datetime import date
                                compensation_date = date.fromisoformat(compensation_date_str)
                            except ValueError:
                                messages.error(request, "Invalid compensation date format.")
                                return redirect('leavetracker')

                            leave.is_compensated = True
                            leave.compensation_date = compensation_date  # Date admin manually entered
                            leave.save()
                            messages.success(
                                request,
                                f"Emergency Leave for {leave.user} ({leave.days} days) marked as compensated. "
                                f"Compensation date: {compensation_date}. Salary deduction removed."
                            )
                    else:
                        messages.error(request, "Only approved Emergency Leaves can be marked as compensated.")

                return redirect('leavetracker')

    else:
        form = LeaveRequestForm()

    context = {
        'form': form,
        'leave_type_choices': leave_type_choices,
        'total_leaves': total_leaves,
        'taken_leaves': taken_leaves,
        'remaining_leaves': remaining_leaves,
        'compensated_leaves': compensated_leaves,
        'approved_medical_days': approved_medical_days,
        'pending_medical_count': pending_medical_count,
        'remaining_medical_leaves': remaining_medical_leaves,
        'leave_history': leave_history,
        'usergroup': profile.usergroup,
        'today': today,
        'holidays': holidays,
    }

    return render(request, 'dashboard/leavetracker.html', context)

def termsandconditions(request):
    
    return render(request, 'dashboard/termsconditions.html')


def timesheet(request):
    
    return render(request, 'dashboard/timesheet.html')


# def upcoming(request):
    
#     return render(request, 'dashboard/upcoming.html')


def schedule(request):
    
    return render(request, 'dashboard/schedule.html')

def birthdayanniversary(request):
    
    return render(request, 'dashboard/birthdayanniversary.html')




@login_required
def passwordchange(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        elif len(new_password) < 6:
            messages.error(request, "New password must be at least 6 characters.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Important to prevent logout
            messages.success(request, "Password changed successfully.")
            return redirect('index')

    return render(request, 'dashboard/passwordchange.html')







def departments(request):
    
    return render(request, 'dashboard/departments.html')

def registration(request):
    

    # Always fetch departments before handling the request
    departments = Department.objects.all()
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee registered successfully!")
            return redirect('employes')  # Ensure this URL name exists
    else:
        form = EmployeeForm()

    return render(request, 'dashboard/registration.html', {
        'form': form,
        'today': date.today().isoformat(),
        'departments': departments  # Pass departments here as well
    })
@login_required()
def teammanagement(request):
    users = Profile.objects.select_related('user').all()  # optimize DB access
    return render(request, 'dashboard/teammanagement.html', {'users': users})


def notification(request):
    
    return render(request, 'dashboard/notification.html')

def dashboard(request):
    
    return render(request, 'dashboard/dashboard.html')

def companyprofile(request):
    
    return render(request, 'dashboard/companyprofile.html')

def securitysettings(request):
    
    return render(request, 'dashboard/securitysettings.html')








@login_required

def departments(request):
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')
    departments = Department.objects.select_related('head').all()

    context = {
        'total_departments': departments.count(),
        'new_departments': 2,  # Replace with dynamic logic if needed
        'total_employees': sum(dept.num_employees for dept in departments),
        'new_employees': 15,  # Replace with dynamic logic if needed
        'open_positions': sum(dept.open_positions for dept in departments),
        'urgent_positions': 3,  # Replace with dynamic logic if needed
        'avg_tenure': 3.2,  # Placeholder
        'tenure_growth': 10,  # Placeholder
        'departments': departments  # Now passing the actual queryset
    }

    return render(request, 'dashboard/departments.html', context)


def add_department(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        head_username = request.POST.get('head')
        try:
            num_employees = int(request.POST.get('num_employees'))
            open_positions = int(request.POST.get('open_positions'))
            budget = Decimal(request.POST.get('budget'))
        except (ValueError, InvalidOperation):
            return render(request, 'dashboard/add_department.html', {
                'error': 'Please enter valid numeric values.',
                'users': User.objects.all()
            })

        # Optional: Check range if you're using PositiveSmallIntegerField
        if open_positions > 65535 or num_employees > 65535:
            return render(request, 'dashboard/add_department.html', {
                'error': 'Value too large for open positions or number of employees.',
                'users': User.objects.all()
            })

        try:
            head_user = User.objects.get(username=head_username)
        except User.DoesNotExist:
            return render(request, 'dashboard/add_department.html', {
                'error': 'Selected department head does not exist.',
                'users': User.objects.all()
            })

        Department.objects.create(
            name=name,
            head=head_user,
            num_employees=num_employees,
            open_positions=open_positions,
            budget=budget
        )
        return redirect('departments')

    users = User.objects.all()
    return render(request, 'dashboard/add_department.html', {'users': users})


# Edit Department

def edit_department(request, id):
    department = get_object_or_404(Department, id=id)

    if request.method == 'POST':
        department.name = request.POST.get('name')
        head_input = request.POST.get('head')

        # ✅ Fetch User by username (from dropdown value)
        try:
            department.head = User.objects.get(username=head_input)
        except User.DoesNotExist:
            department.head = None  # Optionally handle this more gracefully

        department.num_employees = request.POST.get('num_employees')
        department.open_positions = request.POST.get('open_positions')
        department.budget = request.POST.get('budget')
        department.save()
        return redirect('departments')

    # ✅ Pass all users to template for dropdown
    users = User.objects.all()
    return render(request, 'dashboard/edit_departments.html', {
        'department': department,
        'users': users,
    })

# Delete Department

# views.py
def delete_department(request, dept_id):  # Change parameter name to match URL
    department = get_object_or_404(Department, pk=dept_id)
    
    # Your deletion logic here
    try:
        department.delete()
        messages.success(request, "Department deleted successfully")
    except Exception as e:
        messages.error(request, f"Error deleting department: {str(e)}")
    
    return redirect('departments')  # Replace with your actual redirect target




def calendar_events(request):
    events = Event.objects.all()
    data = []
    for event in events:
        data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start_time.isoformat(),
            "end": event.end_time.isoformat() if event.end_time else None,
        })
    return JsonResponse(data, safe=False)




def add_event(request):
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        raw_start = request.POST.get('start_time')
        raw_end = request.POST.get('end_time')

        start_time = parse_datetime(raw_start)
        end_time = parse_datetime(raw_end) if raw_end else None

        if start_time is not None:
            if start_time.tzinfo is None:
                start_time = make_aware(start_time)

            if end_time and end_time.tzinfo is None:
                end_time = make_aware(end_time)

        # Validation
        if not title:
            return JsonResponse({'status': 'error', 'message': 'Title cannot be empty.'}, status=400)

        if not start_time:
            return JsonResponse({'status': 'error', 'message': 'Invalid start time.'}, status=400)

        if start_time < now():
            return JsonResponse({'status': 'error', 'message': 'Start time must be in the future.'}, status=400)

        if end_time and end_time < start_time:
            return JsonResponse({'status': 'error', 'message': 'End time must be after start time.'}, status=400)

        # Save
        Event.objects.create(title=title, start_time=start_time, end_time=end_time)
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)



def upcoming(request):
    events = Event.objects.all().order_by('start_time')
    return render(request, 'dashboard/upcoming.html', {'events': events})
 


def edit_event(request, event_id):
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        start_time = parse_datetime(request.POST.get('start_time'))
        end_time = parse_datetime(request.POST.get('end_time')) if request.POST.get('end_time') else None

        if not title.strip():
            messages.error(request, 'Title cannot be empty or just spaces.')
            return redirect('upcoming')

        if is_naive(start_time):
            start_time = make_aware(start_time)

        if start_time < now():
            messages.error(request, 'Start time cannot be in the past.')
            return redirect('upcoming')

        event.title = title
        event.start_time = start_time
        event.end_time = end_time
        event.save()

        messages.success(request, 'Event updated successfully.')
        return redirect('upcoming')

    # Handle GET request (show edit form)
    return render(request, 'dashboard/edit_event.html', {'event': event})


def delete_event(request, event_id):
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('upcoming')



def birthday_anniversary_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')
    today = date.today()

    # =========================
    # 🔹 WHEN BUTTON IS CLICKED
    # =========================
    if request.method == "POST":
        emp_id = request.POST.get("employee_id")
        wish_type = request.POST.get("wish_type")

        employee = get_object_or_404(Employee, id=emp_id)

        # 🎂 Birthday Mail
        if wish_type == "birthday":
            if (
                employee.date_of_birth.month == today.month and
                employee.date_of_birth.day == today.day
            ):
                send_mail(
                    subject="Happy Birthday 🎉",
                    message=(
                        f"Dear {employee.full_name},\n\n"
                        "Wishing you a very Happy Birthday 🎂🎉\n"
                        "Have a wonderful year ahead!\n\n"
                        "Best Regards,\nHR Team"
                    ),
                    from_email=None,  # Uses EMAIL_HOST_USER
                    recipient_list=[employee.email],
                    fail_silently=False,
                )
                messages.success(request, "Birthday wishes sent successfully!")
            else:
                messages.warning(request, "Today is not the employee's birthday.")

        # 🎊 Anniversary Mail
        elif wish_type == "anniversary":
            if (
                employee.joining_date.month == today.month and
                employee.joining_date.day == today.day
            ):
                send_mail(
                    subject="Happy Work Anniversary 🎊",
                    message=(
                        f"Dear {employee.full_name},\n\n"
                        "Happy Work Anniversary 🎉🎊\n"
                        "Thank you for your dedication and contribution.\n\n"
                        "Best Regards,\nHR Team"
                    ),
                    from_email=None,
                    recipient_list=[employee.email],
                    fail_silently=False,
                )
                messages.success(request, "Anniversary wishes sent successfully!")
            else:
                messages.error(request, "Today is not the employee's anniversary.")

        return redirect("birthdayanniversary")

    # =========================
    # 🔹 PAGE LOAD (GET REQUEST)
    # =========================
    birthdays = Employee.objects.all()
    anniversaries = Employee.objects.all()

    # 🎂 Birthday calculations
    for emp in birthdays:
        age = today.year - emp.date_of_birth.year
        if (today.month, today.day) < (emp.date_of_birth.month, emp.date_of_birth.day):
            age -= 1

        emp.age = age
        emp.birthday_in = emp.date_of_birth.strftime('%d %B')

        # ✅ Birthday today flag
        emp.is_birthday_today = (
            emp.date_of_birth.month == today.month and
            emp.date_of_birth.day == today.day
        )

    # 🎊 Anniversary calculations
    for emp in anniversaries:
        years = today.year - emp.joining_date.year
        if (today.month, today.day) < (emp.joining_date.month, emp.joining_date.day):
            years -= 1

        emp.years = years
        emp.anniversary_in = emp.joining_date.strftime('%d %B')

        # ✅ Anniversary today flag
        emp.is_anniversary_today = (
            emp.joining_date.month == today.month and
            emp.joining_date.day == today.day
        )

    return render(request, 'dashboard/birthdayanniversary.html', {
        'birthdays': birthdays,
        'anniversaries': anniversaries,
    })

# attendance

@login_required
def attendance(request):
    from datetime import timedelta, datetime
    from django.db import IntegrityError

    profile = getattr(request.user, "profile", None)
    today = timezone.localdate()
    IST = pytz.timezone("Asia/Kolkata")
    ist_now = timezone.now().astimezone(IST)

    is_admin = request.user.is_superuser or (profile and profile.usergroup in ["Admin", "Super Admin"])

    # ============================================================
    # HELPER FUNCTIONS
    # ============================================================
    def is_second_saturday(date):
        if date.weekday() != 5:
            return False
        return 8 <= date.day <= 14

    def is_working_day(date):
        if date.weekday() == 6:  # Sunday
            return False
        if is_second_saturday(date):
            return False
        if Holiday.objects.filter(date=date).exists():
            return False
        return True

    def auto_mark_absent(date):
        if not is_working_day(date):
            return

        all_employees = User.objects.filter(
            is_active=True,
            is_superuser=False
        ).exclude(profile__usergroup__in=['Admin', 'Super Admin'])

        for employee in all_employees:
            # Skip if record already exists
            if Attendance.objects.filter(user=employee, date=date).exists():
                continue

            on_leave = LeaveRequest.objects.filter(
                user=employee,
                status='Approved',
                start_date__lte=date,
                end_date__gte=date
            ).exists()

            status = 'On Leave' if on_leave else 'Absent'

            try:
                Attendance.objects.create(
                    user=employee,
                    date=date,
                    status=status
                )
            except IntegrityError:
                # Another process already created it, safe to skip
                pass

    # Run auto-mark for today and last 30 days
    for i in range(30):
        check_date = today - timedelta(days=i)
        auto_mark_absent(check_date)

    # ============================================================
    # ADMIN VIEW
    # ============================================================
    if is_admin:
        selected_date_str = request.GET.get("date", str(today))
        selected_user = request.GET.get("user", None)

        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            selected_date = today

        if selected_user:
            records = Attendance.objects.filter(
                user__username=selected_user,
                date=selected_date
            ).select_related('user')
        else:
            records = Attendance.objects.filter(
                date=selected_date
            ).select_related('user').order_by('user__username')

        all_employees = User.objects.filter(
            is_active=True,
            is_superuser=False
        ).exclude(profile__usergroup__in=['Admin', 'Super Admin'])

        employee_attendance = {
            emp.username: Attendance.objects.filter(
                user=emp
            ).order_by("-date")[:7]
            for emp in all_employees
        }

        summary = {
            'present': records.filter(status='Present').count(),
            'late': records.filter(status='Late').count(),
            'half_day': records.filter(status='Half Day').count(),
            'absent': records.filter(status='Absent').count(),
            'on_leave': records.filter(status='On Leave').count(),
        }

        return render(request, "employee/attendance.html", {
            "records": records,
            "today": today,
            "selected_date": selected_date,
            "employee_attendance": employee_attendance,
            "is_admin": True,
            "summary": summary,
            "is_working_day": is_working_day(selected_date),
        })

    # ============================================================
    # EMPLOYEE VIEW
    # ============================================================

    # auto_mark_absent already created today's record if needed
    # so we just fetch it safely here
    try:
        record, created = Attendance.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'status': 'Absent'}
        )
    except IntegrityError:
        record = Attendance.objects.get(user=request.user, date=today)

    if request.method == "POST":
        action = request.POST.get("action")
        now_time = ist_now.time()

        clock_in_start = time(8, 45)
        clock_in_end = time(10, 0)
        clock_out_start = time(13, 0)
        clock_out_end = time(22, 0)

        if action == "clock_in":
            if not record.clock_in_datetime:
                if clock_in_start <= now_time <= clock_in_end:
                    record.clock_in_datetime = ist_now
                    record.clock_in = ist_now.time()
                    messages.success(request, "Clock-in successful at %s" % ist_now.strftime("%H:%M"))
                else:
                    messages.error(request, "You can only clock in between 08:45 and 10:00 AM.")
            else:
                messages.warning(request, "Already clocked in today.")

        elif action == "clock_out":
            if record.clock_in_datetime and not record.clock_out_datetime:
                if clock_out_start <= now_time <= clock_out_end:
                    record.clock_out_datetime = ist_now
                    record.clock_out = ist_now.time()
                    messages.success(request, "Clock-out successful at %s" % ist_now.strftime("%H:%M"))
                else:
                    messages.error(request, "You can only clock out between 1:00 PM and 10:00 PM.")
            elif not record.clock_in_datetime:
                messages.error(request, "You must clock in before clocking out.")
            else:
                messages.warning(request, "Already clocked out today.")

        record.save()
        return redirect("attendance")

    history = Attendance.objects.filter(user=request.user).order_by("-date")[:10]

    return render(request, "employee/attendance.html", {
        "record": record,
        "today": today,
        "history": history,
        "is_admin": False,
        "is_working_day": is_working_day(today),
    })
        
# holiday

@login_required
def manage_holidays(request):
    
    # Only allow superusers
    

    today = now().date()

    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'delete':
            Holiday.objects.filter(id=request.POST.get('holiday_id')).delete()
        else:
            name = request.POST.get('name')
            date = request.POST.get('date')
            holiday_type = request.POST.get('holiday_type')
            if date >= str(today):
                Holiday.objects.create(name=name, date=date, holiday_type=holiday_type)
        return redirect('manage_holidays')

    holidays = Holiday.objects.all()
    return render(request, 'dashboard/holidays.html', {'holidays': holidays, 'today': today})



# user management

@login_required
def user_management(request):
    """
    Super Admin can:
    - Create new Admin/Employee users
    - Automatically add Employee details when usergroup = Employee
    - Update roles
    - Activate/Deactivate users
    """
    # Only Super Admin can access
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')

    # Exclude Super Admin themselves
    users = Profile.objects.select_related('user').exclude(user=request.user)
    departments = Department.objects.all()

    if request.method == 'POST':


        
        action = None
        if 'create_user' in request.POST:
            action = 'create_user'
        elif 'update_role' in request.POST:
            action = 'update_role'
        elif 'toggle_status' in request.POST:
            action = 'toggle_status'

        try:
            # 1️⃣ Create User + Employee
            if action == 'create_user':
                name = request.POST.get('name', '').strip()
                email = request.POST.get('email', '').strip()
                username = request.POST.get('username', '').strip()
                password = request.POST.get('password1', '').strip()
                usergroup = request.POST.get('usergroup', '').strip()
                image = request.FILES.get('image')

                # Employee fields
                employee_id = request.POST.get('employee_id', '').strip()
                date_of_birth = request.POST.get('date_of_birth') or None
                joining_date = request.POST.get('joining_date') or None
                designation = request.POST.get('designation', '').strip()
                department_id = request.POST.get('department')
                salary = request.POST.get('salary') or 0
                phone = request.POST.get('phone', '').strip()
                emergency_number = request.POST.get('emergency_number', '').strip()
                blood_group = request.POST.get('blood_group', '').strip()

                # Validate mandatory fields
                if not all([name, email, username, password, usergroup]):
                    messages.error(request, "All required fields must be filled.")
                    return redirect('user_management')

                if User.objects.filter(username=username).exists():
                    messages.error(request, "Username already exists.")
                    return redirect('user_management')

                if User.objects.filter(email=email).exists():
                    messages.error(request, "Email already exists.")
                    return redirect('user_management')

                # Create User and Profile
                user = User.objects.create_user(username=username, email=email, password=password)
                Profile.objects.create(user=user, name=name, usergroup=usergroup, image=image)

                # If Employee → also create Employee record
                if usergroup == "Employee":
                    Employee.objects.create(
                        full_name=name,
                        email=email,
                        date_of_birth=date_of_birth,
                        joining_date=joining_date,
                        designation=designation or "Not specified",
                        department_id=department_id if department_id else None,
                        salary=salary or 0,
                        phone=phone,
                        emergency_number=emergency_number,
                        blood_group=blood_group or "N/A"
                    )

                messages.success(request, f"{usergroup} '{username}' created successfully.")

            # 2️⃣ Update Role
            elif action == 'update_role':
                user_id = request.POST.get('user_id')
                usergroup = request.POST.get('usergroup')
                profile = get_object_or_404(Profile, user_id=user_id)
                old_role = profile.usergroup
                profile.usergroup = usergroup
                profile.save()
                messages.success(request, f"Updated role for '{profile.user.username}' from {old_role} → {usergroup}.")

            # 3️⃣ Activate/Deactivate User
            elif action == 'toggle_status':
                user_id = request.POST.get('user_id')
                user = get_object_or_404(User, id=user_id)
                user.is_active = not user.is_active
                user.save()
                messages.info(request, f"User '{user.username}' is now {'Active' if user.is_active else 'Inactive'}.")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('user_management')

    return render(request, 'dashboard/user_management.html', {
        'users': users,
        'departments': departments,
    })

@login_required
def add_employee(request):
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup not in ['Admin', 'Super Admin']:
        messages.error(request, "You don't have permission to add employees.")
        return redirect('employes')

    departments = Department.objects.all()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                name = request.POST.get('name', '').strip()
                username = request.POST.get('username', '').strip().lower()
                email = request.POST.get('email', '').strip().lower()
                password1 = request.POST.get('password1')
                joining_date = request.POST.get('joining_date')
                designation = request.POST.get('designation', '').strip()
                department_id = request.POST.get('department')
                salary = request.POST.get('salary', '0').strip()
                phone = request.POST.get('phone', '').strip()
                emergency_number = request.POST.get('emergency_number', '').strip()
                blood_group = request.POST.get('blood_group', '').strip()
                image = request.FILES.get('image')

                if image:
                    #  Check MIME type
                    if not image.content_type.startswith('image/'):
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Only image files are allowed'
                        }, status=400)
                
                    #  Check file extension
                    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
                    if not image.name.lower().endswith(tuple(allowed_extensions)):
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Invalid image format'
                        }, status=400)


                # Required field validation
                if not all([name, username, email, password1, joining_date, phone, emergency_number]):
                    messages.error(request, "Please fill all required fields: Name, Username, Email, Password, Joining Date, Phone, Emergency Number.")
                    return redirect('add_employee')

                # Uniqueness checks
                if User.objects.filter(username__iexact=username).exists():
                    messages.error(request, "Username already exists.")
                    return redirect('add_employee')
                if User.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already in use.")
                    return redirect('add_employee')

                # Create User and Profile
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.is_active = True
                user.save()

                Profile.objects.create(
                    user=user,
                    name=name,
                    usergroup='Employee',
                    image=image
                )

                # Safe salary
                try:
                    salary_val = Decimal(salary) if salary else Decimal('0.00')
                except:
                    salary_val = Decimal('0.00')

                # Create Employee with SAFE values for required fields
                Employee.objects.create(
                    full_name=name,
                    email=email,
                    joining_date=joining_date,
                    designation=designation or "Employee",
                    department_id=department_id or None,
                    salary=salary_val,
                    phone=phone,  # Required — user must enter
                    emergency_number=emergency_number,  # Required — user must enter
                    blood_group=blood_group or "O+",  # Safe default
                    date_of_birth=request.POST.get('date_of_birth') or None 
                    # If you add date_of_birth to form later, use: date_of_birth=request.POST.get('date_of_birth') or '1990-01-01'
                )

                messages.success(request, f"Employee '{name}' added successfully with login access!")
                return redirect('employes')

        except Exception as e:
            # Now show real error in console for debugging
            import traceback
            traceback.print_exc()
            messages.error(request, f"Failed to add employee: {str(e)}")
            return redirect('add_employee')

    # GET request — show form
    return render(request, 'dashboard/addingform.html', {
        'departments': departments,
    })
    
@login_required
def edit_user(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    departments = Department.objects.all()
    try:
        employee = Employee.objects.get(email=user.email)
    except Employee.DoesNotExist:
        employee = None

    if request.method == 'POST':
        # Update User info
        profile.name = request.POST.get('name', profile.name)
        profile.usergroup = request.POST.get('usergroup', profile.usergroup)
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        profile.save()
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        if request.POST.get('password1'):
            user.set_password(request.POST.get('password1'))
        user.save()

        if employee:
            employee.full_name = request.POST.get('name', employee.full_name)
            employee.email = request.POST.get('email', employee.email)
            employee.date_of_birth = request.POST.get('date_of_birth') or employee.date_of_birth
            employee.joining_date = request.POST.get('joining_date') or employee.joining_date
            employee.designation = request.POST.get('designation', employee.designation)
            employee.department_id = request.POST.get('department') or employee.department_id
            employee.salary = request.POST.get('salary') or employee.salary
            employee.phone = request.POST.get('phone', employee.phone)
            employee.emergency_number = request.POST.get('emergency_number', employee.emergency_number)
            employee.blood_group = request.POST.get('blood_group', employee.blood_group)
            employee.save()

        messages.success(request, f"User '{user.username}' updated successfully.")
        return redirect('user_management')

    return render(request, 'dashboard/edit_user.html', {
        'user': user,
        'profile': profile,
        'employee': employee,
        'departments': departments,
    })


#employess


@login_required
def employes(request):
    if not hasattr(request.user, 'profile'):
        messages.error(request, "Profile not found.")
        return redirect('index')

    # Show ALL employees — no inner join that can hide records
    employees = Employee.objects.select_related('department').all().order_by('-joining_date')

    # Optional debug (remove later if you want)
    print(f"DEBUG: Found {employees.count()} employees in database")

    return render(request, 'dashboard/employes.html', {
        'employees': employees,
        'debug_count': employees.count(),  # Remove this line later if not needed
    })
    
    
    
# timesheet


@login_required
def timesheet(request):
    """Show timesheet — all employees if admin/superuser, else only user's own."""
    today = timezone.localdate()
    selected_date = request.GET.get('date', '')
    selected_month = request.GET.get('month', '')
    selected_user = request.GET.get('user')

    # Check role
    is_admin = request.user.is_superuser or getattr(request.user, "profile", None) and getattr(request.user.profile, "usergroup", "") == "Admin"

    if is_admin:
        # Admin can pick any employee or see all
        if selected_user:
            records = Attendance.objects.filter(user__username=selected_user)
            # Apply date/month filter if provided
            if selected_date:
                records = records.filter(date=selected_date)
            elif selected_month:
                year, month = map(int, selected_month.split('-'))
                records = records.filter(date__year=year, date__month=month)
        else:
            # No specific user selected
            if selected_date:
                records = Attendance.objects.filter(date=selected_date)
            elif selected_month:
                year, month = map(int, selected_month.split('-'))
                records = Attendance.objects.filter(date__year=year, date__month=month)
            else:
                # No filters - show nothing or recent records
                records = Attendance.objects.none()
        employees = User.objects.all()
    else:
        # Regular employee — only their records
        records = Attendance.objects.filter(user=request.user)
        if selected_date:
            records = records.filter(date=selected_date)
        elif selected_month:
            year, month = map(int, selected_month.split('-'))
            records = records.filter(date__year=year, date__month=month)
        else:
            # No filters - show nothing or recent records
            records = Attendance.objects.none()
        employees = None

    # Convert datetime fields to time fields if time fields are empty
    IST = pytz.timezone("Asia/Kolkata")
    for record in records:
        if record.clock_in_datetime and not record.clock_in:
            record.clock_in = record.clock_in_datetime.astimezone(IST).time()
        if record.clock_out_datetime and not record.clock_out:
            record.clock_out = record.clock_out_datetime.astimezone(IST).time()

    return render(request, "dashboard/timesheet.html", {
        "records": records,
        "selected_date": selected_date,
        "selected_month": selected_month,
        "selected_user": selected_user,
        "employees": employees,
        "is_admin": is_admin,
        "today": today,
    })


@login_required
def download_timesheet_day(request):
    """Download day report (admin can pick user; employee sees own)."""
    date_str = request.GET.get("date") or timezone.localdate()
    selected_user = request.GET.get("user")

    is_admin = request.user.is_superuser or getattr(request.user, "profile", None) and getattr(request.user.profile, "usergroup", "") == "Admin"

    IST = pytz.timezone("Asia/Kolkata")

    if is_admin and selected_user:
        records = Attendance.objects.filter(user__username=selected_user, date=date_str)
        filename = f"timesheet_{selected_user}_{date_str}.csv"
    else:
        records = Attendance.objects.filter(user=request.user, date=date_str)
        filename = f"timesheet_{request.user.username}_{date_str}.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(["Employee", "Date", "Clock In", "Clock Out", "Hours", "Status"])

    for r in records:
        # Get time from TimeField, fallback to DateTimeField
        clock_in_time = r.clock_in or (r.clock_in_datetime.astimezone(IST).time() if r.clock_in_datetime else None)
        clock_out_time = r.clock_out or (r.clock_out_datetime.astimezone(IST).time() if r.clock_out_datetime else None)
        
        writer.writerow([
            r.user.username,
            r.date,
            clock_in_time.strftime("%H:%M:%S") if clock_in_time else "--",
            clock_out_time.strftime("%H:%M:%S") if clock_out_time else "--",
            r.formatted_hours or "--:--",
            r.status,
        ])
    return response


@login_required
def download_timesheet_month(request):
    """Download monthly report (admin sees all or selected user)."""
    month_str = request.GET.get("month") or timezone.localdate().strftime("%Y-%m")
    year, month = map(int, month_str.split('-'))
    selected_user = request.GET.get("user")

    is_admin = request.user.is_superuser or getattr(request.user, "profile", None) and getattr(request.user.profile, "usergroup", "") == "Admin"

    IST = pytz.timezone("Asia/Kolkata")

    if is_admin and selected_user:
        records = Attendance.objects.filter(user__username=selected_user, date__year=year, date__month=month)
        filename = f"timesheet_{selected_user}_{month_str}.csv"
    elif is_admin:
        records = Attendance.objects.filter(date__year=year, date__month=month)
        filename = f"timesheet_all_{month_str}.csv"
    else:
        records = Attendance.objects.filter(user=request.user, date__year=year, date__month=month)
        filename = f"timesheet_{request.user.username}_{month_str}.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(["Employee", "Date", "Clock In", "Clock Out", "Hours", "Status"])

    for r in records:
        # Get time from TimeField, fallback to DateTimeField
        clock_in_time = r.clock_in or (r.clock_in_datetime.astimezone(IST).time() if r.clock_in_datetime else None)
        clock_out_time = r.clock_out or (r.clock_out_datetime.astimezone(IST).time() if r.clock_out_datetime else None)
        
        writer.writerow([
            r.user.username,
            r.date,
            clock_in_time.strftime("%H:%M:%S") if clock_in_time else "--",
            clock_out_time.strftime("%H:%M:%S") if clock_out_time else "--",
            r.formatted_hours or "--:--",
            r.status,
        ])
    return response

def payroll(request):

    # Permission check
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')

    employees_with_payroll = []

    today = timezone.now()

    first_day = today.replace(day=1)

    if today.month == 12:
        last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    TOTAL_WORKING_DAYS = 26
    PAID_LEAVE_LIMIT = 12
    LATE_FREE_LIMIT = 3

    # -------- Find 2nd Saturday --------
    second_saturday = None
    saturday_count = 0
    current_day = first_day.date()

    while current_day <= last_day.date():
        if current_day.weekday() == 5:
            saturday_count += 1
            if saturday_count == 2:
                second_saturday = current_day
                break
        current_day += timedelta(days=1)

    # -------- Loop Employees --------
    for employee in Employee.objects.all():

        latest_payroll = Payroll.objects.filter(
            employee=employee
        ).order_by('-created_at').first()

        try:
            user = User.objects.get(email=employee.email)

            # -------- Attendance --------
            present_days = Attendance.objects.filter(
                user=user,
                date__range=[first_day, last_day],
                status='Present'
            ).count()

            late_days = Attendance.objects.filter(
                user=user,
                date__range=[first_day, last_day],
                status='Late'
            ).count()

            half_days = Attendance.objects.filter(
                user=user,
                date__range=[first_day, last_day],
                status='Half Day'
            ).count()

            # -------- Approved Leave Dates --------
            approved_leaves = LeaveRequest.objects.filter(
                user=user,
                status='Approved',
                start_date__lte=last_day,
                end_date__gte=first_day
            )

            leave_dates = []

            for leave in approved_leaves:
                current = leave.start_date
                while current <= leave.end_date:
                    leave_dates.append(current)
                    current += timedelta(days=1)

            # -------- Absence excluding Leave --------
            absent_qs = Attendance.objects.filter(
                user=user,
                date__range=[first_day, last_day],
                status='Absent'
            ).exclude(date__in=leave_dates)

            if second_saturday:
                absent_qs = absent_qs.exclude(date=second_saturday)

            absent_days = absent_qs.count()

            # -------- Second Saturday Work --------
            worked_second_saturday = 0

            if second_saturday:
                worked_second_saturday = Attendance.objects.filter(
                    user=user,
                    date=second_saturday,
                    status__in=['Present', 'Late']
                ).count()

            # -------- Leave Calculation --------

            def count_leave_days_excluding_saturdays(leave_qs):
                total = 0
                for leave in leave_qs:

                    start = leave.start_date
                    end = leave.end_date

                    current = start

                    while current <= end:
                        if current.weekday() != 5:
                            total += 1
                        current += timedelta(days=1)

                return total

            # -------- Paid Leave (CL + ML) --------
            paid_leave_qs = LeaveRequest.objects.filter(
                user=user,
                status='Approved',
                leave_type__in=['CL', 'ML'],
                start_date__lte=last_day,
                end_date__gte=first_day
            )

            paid_leaves = count_leave_days_excluding_saturdays(paid_leave_qs)

            excess_paid_leaves = max(0, paid_leaves - PAID_LEAVE_LIMIT)

            # -------- Emergency Leave --------
            emergency_leave_qs = LeaveRequest.objects.filter(
                user=user,
                leave_type='EL',
                status='Approved',
                start_date__lte=last_day,
                end_date__gte=first_day
            )
            # -------- Unpaid Casual Leave (more than 1 CL in month) --------
            casual_leave_qs = LeaveRequest.objects.filter(
                user=user,
                leave_type='CL',
                status='Approved',
                start_date__range=[first_day, last_day]
            )
            
            unpaid_casual_leaves = max(0, casual_leave_qs.count() - 1)

            unpaid_emergency_leaves = 0
          
            for leave in emergency_leave_qs:

                start = leave.start_date
                end = leave.end_date

                current = start

                while current <= end:

                    if current.weekday() != 5:

                        if not leave.is_compensated:
                            unpaid_emergency_leaves += 1

                    current += timedelta(days=1)

        except User.DoesNotExist:

            present_days = 0
            late_days = 0
            half_days = 0
            absent_days = 0
            excess_paid_leaves = 0
            unpaid_emergency_leaves = 0
            worked_second_saturday = 0

        # -------- Salary Calculation --------
        
        basic_salary = (
            latest_payroll.basic_salary
            if latest_payroll else (employee.salary or 0)
        )

        per_day_salary = float(basic_salary) / TOTAL_WORKING_DAYS

        absence_deduction = absent_days * per_day_salary
        half_day_deduction = half_days * (per_day_salary * 0.5)

        chargeable_late_days = max(0, late_days - LATE_FREE_LIMIT)
        late_deduction = chargeable_late_days * (per_day_salary * 0.1)

        excess_paid_leave_deduction = excess_paid_leaves * per_day_salary
        unpaid_emergency_leave_deduction = unpaid_emergency_leaves * per_day_salary

        payroll_deductions = float(latest_payroll.deductions) if latest_payroll else 0
        bonus = float(latest_payroll.bonus) if latest_payroll else 0

        # -------- Second Saturday Bonus --------
        second_saturday_bonus = worked_second_saturday * per_day_salary
        bonus += second_saturday_bonus

        unpaid_casual_leave_deduction = unpaid_casual_leaves * per_day_salary
          
        total_deductions = (
            payroll_deductions +
            absence_deduction +
            half_day_deduction +
            late_deduction +
            excess_paid_leave_deduction +
            unpaid_emergency_leave_deduction +
            unpaid_casual_leave_deduction
        )

        net_salary = float(basic_salary) + bonus - total_deductions

        employees_with_payroll.append({

            'id': employee.id,
            'full_name': employee.full_name,
            'designation': employee.designation,
            'department': employee.department.name if employee.department else '',

            'basic_salary': basic_salary,
            'bonus': bonus,
            'deductions': total_deductions,
            'total_salary': net_salary,

            'late_days': late_days,
            'chargeable_late_days': chargeable_late_days,
            'excess_paid_leaves': excess_paid_leaves,
            'unpaid_emergency_leaves': unpaid_emergency_leaves,
        })

    context = {
        'employees': employees_with_payroll,
        'current_month': today.strftime('%B %Y'),
    }

    return render(request, 'dashboard/payroll.html', context)
def payroll_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.usergroup != 'Super Admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('index')
    payrolls = Payroll.objects.all().order_by('-created_at')
    return render(request, 'dashboard/payroll.html', {'payrolls': payrolls})

# notification



@login_required
def send_notification(request):
    usergroup = request.user.profile.usergroup  # 'Super Admin', 'Admin', or 'Employee'

    # Determine recipients automatically based on sender's role
    if usergroup == 'Super Admin':
        recipients = User.objects.filter(
            profile__usergroup__in=['Admin', 'Employee']
        ).exclude(id=request.user.id)
    elif usergroup == 'Admin':
        recipients = User.objects.filter(
            profile__usergroup__in=['Admin', 'Employee']
        ).exclude(id=request.user.id)
    else:
        messages.error(request, "You are not authorized to send notifications.")
        return redirect('index')  # update to your dashboard home URL

    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')

        if not title or not message:
            messages.error(request, "Please fill in all fields.")
        else:
            # Create the notification
            notification = Notification.objects.create(
                title=title,
                message=message,
                sender=request.user
            )

            # Send to all eligible users
            for user in recipients:
                NotificationRecipient.objects.create(notification=notification, recipient=user)

            messages.success(request, f"Notification sent to {recipients.count()} users successfully!")
            return redirect('send_notification')

    return render(request, 'dashboard/notification.html', {
        'role': usergroup,
    })
    
    
@login_required
def get_notifications(request):
    """Return the latest notifications for the logged-in user (only from last 2 days)."""
    user = request.user
    
    # Get notifications from the last 2 days only
    two_days_ago = timezone.now() - timedelta(days=2)
    
    notifications = (
        NotificationRecipient.objects
        .filter(recipient=user, notification__created_at__gte=two_days_ago)
        .select_related('notification')
        .order_by('-notification__created_at')[:10]
    )

    # Count unread notifications
    unread_count = NotificationRecipient.objects.filter(
        recipient=user, 
        read=False,
        notification__created_at__gte=two_days_ago
    ).count()

    data = [
        {
            'title': n.notification.title,
            'message': n.notification.message,
            'created_at': n.notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'read': n.read,
        }
        for n in notifications
    ]
    
    return JsonResponse({
        'notifications': data,
        'unread_count': unread_count  # Include unread count in response
    })


@require_POST
@login_required
def mark_notifications_read(request):
    """Mark all notifications for this user as read."""
    NotificationRecipient.objects.filter(recipient=request.user, read=False).update(read=True)
    return JsonResponse({'status': 'ok'})


# Optional: Add a cleanup task to delete old notifications
# You can run this periodically via cron job or celery
def cleanup_old_notifications():
    """Delete notifications older than 2 days."""
    two_days_ago = timezone.now() - timedelta(days=2)
    old_notifications = Notification.objects.filter(created_at__lt=two_days_ago)
    count = old_notifications.count()
    old_notifications.delete()
    return f"Deleted {count} old notifications"

