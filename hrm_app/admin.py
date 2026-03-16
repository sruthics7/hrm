from django.contrib import admin
from .models import UserGroup, Module, Permission, Child, Profile,SubChild,SubSubChild
from .models import Employee
from .models import Department
from .models import LeaveRequest, Holiday, Attendance



# Inline permission under UserGroup
class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 0

class UserGroupAdmin(admin.ModelAdmin):
    inlines = [PermissionInline]

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'usergroup', 'name','image')
    search_fields = ('user__username', 'name')
    
    # This is important for models with a custom primary key
    def get_object(self, request, object_id, from_field=None):
        # Custom handling for getting the object by user_id instead of id
        queryset = self.get_queryset(request)
        model = queryset.model
        try:
            # Use pk lookup directly since user is the primary key
            object_id = model._meta.pk.to_python(object_id)
            return queryset.get(pk=object_id)
        except (model.DoesNotExist, ValueError, TypeError):
            return None

admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(Profile, ProfileAdmin)
# Inline child under Module
class ChildInline(admin.TabularInline):
    model = Child
    extra = 1

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ChildInline]

class SubChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'child', 'url_name')
    search_fields = ('name',)

class SubSubChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'subchild', 'url_name')
    search_fields = ('name',)




class DepartmentAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('name', 'head', 'budget', 'num_employees', 'open_positions')
    
    # Make the department list searchable by name
    search_fields = ('name',)
    
    # Add filters for head and budget
    list_filter = ('head',)
    
    # Fields to use in the edit/create form
    fields = ('name', 'head', 'budget', 'num_employees', 'open_positions')
    
    # If you want to automatically calculate num_employees based on related employees
    # you might want to make this field read-only
    readonly_fields = ('num_employees',)  # Optional
    
    # If you want to customize how the head field is displayed in the admin
    raw_id_fields = ('head',)  # Shows a search widget instead of a dropdown
    autocomplete_fields = ('head',)
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'designation', 'department', 'joining_date')
    search_fields = ('full_name', 'email', 'phone', 'designation', 'department')
    list_filter = ('department', 'joining_date', 'blood_group')
    ordering = ('-joining_date',)


admin.site.register(Module, ModuleAdmin)
admin.site.register(Child)  # Optional: only if you want to manage Child separately too
admin.site.register(SubChild, SubChildAdmin)
admin.site.register(SubSubChild, SubSubChildAdmin)
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'date',
        'clock_in',
        'clock_out',
        'formatted_hours',
        'status',
    )

    list_filter = (
        'status',
        'date',
    )

    search_fields = (
        'user__username',
    )

    ordering = (
        '-date',
        'user__username',
    )

    readonly_fields = (
        'hours_worked',
        'formatted_hours',
    )

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'leave_type',
        'start_date',
        'end_date',
        'days',
        'status',
        'is_compensated',
        'applied_on',
    )

    list_filter = (
        'leave_type',
        'status',
        'is_compensated',
        'applied_on',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
    )

    ordering = ('-applied_on',)

    readonly_fields = (
        'user',
        'days',
        'applied_on',
    )

    fieldsets = (
        ('Employee Info', {
            'fields': ('user',)
        }),
        ('Leave Details', {
            'fields': (
                'leave_type',
                'start_date',
                'end_date',
                'days',
                'reason',
                'medical_proof',
            )
        }),
        ('Status & Approval', {
            'fields': (
                'status',
                'is_compensated',
            )
        }),
        ('System Info', {
            'fields': ('applied_on',)
        }),
    )
@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    ordering = ('date',)
from django.contrib import admin
from .models import Payroll

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'basic_salary', 'hra', 'bonus', 'deductions', 'net_salary', 'month', 'year', 'created_at']
    list_filter = ['month', 'year']
    search_fields = ['employee__full_name']