from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from hrm_app.models import LeaveRequest

class Command(BaseCommand):
    help = 'Send daily leave report to manager'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # Get employees on leave today
        on_leave_today = LeaveRequest.objects.filter(
            status='Approved',
            start_date__lte=today,
            end_date__gte=today
        ).select_related('user', 'user__profile')
        
        # Get pending leave requests
        pending_requests = LeaveRequest.objects.filter(
            status='Pending'
        ).select_related('user', 'user__profile')
        
        # Create the email report
        report = f"""Daily Leave Report - {today.strftime('%B %d, %Y')}
{'='*60}

📅 EMPLOYEES ON LEAVE TODAY ({on_leave_today.count()}):
"""
        
        if on_leave_today.exists():
            for leave in on_leave_today:
                name = leave.user.get_full_name() or leave.user.username
                designation = getattr(leave.user.profile, 'designation', 'N/A')
                report += f"""
  • {name} ({designation})
    Type: {leave.get_leave_type_display()}
    Duration: {leave.start_date.strftime('%b %d')} to {leave.end_date.strftime('%b %d')} ({leave.days} days)
    Reason: {leave.reason}
"""
        else:
            report += "\n  ✓ No employees on leave today.\n"
        
        report += f"""
⏳ PENDING APPROVALS ({pending_requests.count()}):
"""
        
        if pending_requests.exists():
            for leave in pending_requests:
                name = leave.user.get_full_name() or leave.user.username
                report += f"""
  • {name} - {leave.get_leave_type_display()}
    Dates: {leave.start_date.strftime('%b %d')} to {leave.end_date.strftime('%b %d')} ({leave.days} days)
    Reason: {leave.reason}
"""
        else:
            report += "\n  ✓ No pending requests.\n"
        
        # Send the email
        try:
            send_mail(
                subject=f'Daily Leave Report - {today.strftime("%b %d, %Y")}',
                message=report,
                from_email='noreply@yourcompany.com',
                recipient_list=['sruthics742001@gmail.com'],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('✓ Daily report sent successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {str(e)}'))