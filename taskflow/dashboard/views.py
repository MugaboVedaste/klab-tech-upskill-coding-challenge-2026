from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def dashboard_view(request):
	# Render manager or employee dashboard based on user role
	role = getattr(request.user, "role", "employee")
	if role == "manager":
		# get employees list
		employees = User.objects.filter(role=User.Role.EMPLOYEE)

		# try to import Task model if present
		tasks = []
		try:
			from tasks.models import Task

			tasks = Task.objects.all()
		except Exception:
			tasks = []

		template = "dashboard/manager_dashboard.html"
		return render(request, template, {"employees": employees, "tasks": tasks})
	else:
		template = "dashboard/employee_dashboard.html"
		return render(request, template)
