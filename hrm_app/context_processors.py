from hrm_app.models import Profile,Module  # Adjust to your actual app name
from .models import Employee, Department


def global_user_profile(request):
    # Debugging: Log the current user being processed
    print(f"Processing user: {request.user}")

    if request.user.is_authenticated:
        try:
            # Fetch the profile associated with the logged-in user
            profile = Profile.objects.get(user=request.user)
            return {'global_user_profile': profile}
        except Profile.DoesNotExist:
            return {'global_user_profile': None}
    return {'global_user_profile': None}



def global_variables(request):
    modules = Module.objects.all()
    user_profile = None
    if request.user.is_authenticated:
        user_profile = Profile.objects.filter(user=request.user).first()
    return {
        'modules': modules,
        'global_user_profile': user_profile,
    }


def dashboard_stats(request):
    # Only calculate if user is authenticated (optional)
    if request.user.is_authenticated:
        return {
            'total_employees': Employee.objects.count(),
            'total_departments': Department.objects.count(),
            
        }
    return {}