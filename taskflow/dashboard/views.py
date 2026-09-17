from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
	# Render manager or employee dashboard based on user role
	role = getattr(request.user, "role", "employee")
	if role == "manager":
		template = "dashboard/manager_dashboard.html"
	else:
		template = "dashboard/employee_dashboard.html"

	return render(request, template)
