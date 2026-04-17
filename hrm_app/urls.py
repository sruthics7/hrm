from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'), 
    path('login/admin/', views.auth_login, name='admin_login'), 
    path('', views.login_view, name='employee_login'),
    path('admin/', views.admin_index, name='admin_index'),
    path('employee/', views.employee_index, name='employee_index'),
    path('superadmin/', views.superadmin_index, name='superadmin_index'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:user_id>/', views.profile, name='profile'), 
    # path('employes/', views.employes, name='employes'),
    path('module/<int:module_id>/', views.module_view, name='module_url_name'),
    path('child/<int:child_id>/', views.child_view, name='child_url_name'),
    path('subchild/<int:sub_child_id>/', views.sub_child_view, name='sub_child_url_name'),
    path('subsubchild/<int:subsubchild_id>/', views.subsubchild_view, name='subsubchild_url_name'), 
    path('add_user/',views.add_user,name="add_user"),
    path('leavetracker/', views.leavetracker, name='leavetracker'),
    path('edit-leave/<int:leave_id>/', views.edit_leave, name='edit_leave'),
    path('delete-leave/<int:leave_id>/', views.delete_leave, name='delete_leave'),
    path('timesheet/', views.timesheet, name='timesheet'),
    path('timesheet/download/day/', views.download_timesheet_day, name='download_timesheet_day'),
    path('timesheet/download/month/', views.download_timesheet_month, name='download_timesheet_month'),
    # path('payrol/', views.payroll, name='payroll'), 
    path('payroll/', views.payroll, name='payroll'),     
    path('upcoming/', views.upcoming, name='upcoming'),
    path('schedule/',views.schedule,name='schedule'),
    path('birthdayanniversary/',views.birthdayanniversary,name='birthdayanniversary'),
    path('departments/',views.departments,name='departments'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/edit/<int:id>/', views.edit_department, name='edit_departments'),
    path('departments/delete/<int:dept_id>/', views.delete_department, name='delete_department'),
    path('passwordchange/', views.passwordchange, name='passwordchange'),
    path('notification/', views.send_notification, name='send_notification'),
    path('get-notifications/', views.get_notifications, name='get_notifications'),
    path('mark-notifications-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('terms/', views.termsandconditions, name='termsandconditions'),
    # employee
    path('employees/add/', views.add_employee, name='add_employee'),    
    path('registration/',views.registration,name='registration'),
    path('teammanagement/',views.teammanagement,name='teammanagement'),
    path('notification/',views.notification,name='notification'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('companyprofile/',views.companyprofile,name='companyprofile'),
    path('securitysettings/',views.securitysettings,name='securitysettings'),
    


    path('employes/', views.employes, name='employes'),
    path('user-management/edit/<int:user_id>/', views.edit_user, name='edit_user'),

    # path('employee/delete/<int:id>/', views.employee_delete, name='employee_delete'),


    path('add_user/<int:user_id>/', views.add_user, name='add_user'),
     path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('calendar-events/', views.calendar_events, name='calendar-events'),
    path('add-event/', views.add_event, name='add-event'),


    path('upcoming/', views.upcoming, name='upcoming_event'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit-event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete-event'),


    path('dashboard/birthdayanniversary/', views.birthday_anniversary_view, name='birthdayanniversary'),
    path('attendance/', views.attendance, name='attendance'),
    path('attendance/clock-in', views.attendance, name='clock_in'),
    path('attendance/clock-out', views.attendance, name='clock_out'),

    path('holidays/', views.manage_holidays, name='manage_holidays'),
    path('user_management/', views.user_management, name='user_management'),

   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
