from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from tasks.models import Task

User = get_user_model()


@login_required
def dashboard_view(request):
	# Render manager or employee dashboard based on user role
	role = getattr(request.user, "role", "employee")
	if role == "manager":
		# get employees this manager owns
		employees = User.objects.filter(role=User.Role.EMPLOYEE, manager=request.user)

		tasks = Task.objects.filter(created_by=request.user).select_related("assigned_to")
		stats = {
			"total": tasks.count(),
			"pending": tasks.filter(status=Task.Status.PENDING).count(),
			"in_progress": tasks.filter(status=Task.Status.IN_PROGRESS).count(),
			"done": tasks.filter(status=Task.Status.DONE).count(),
			"reviewed": tasks.filter(status=Task.Status.REVIEWED).count(),
			"rejected": tasks.filter(status=Task.Status.REJECTED).count(),
		}

		template = "dashboard/manager_dashboard.html"
		return render(
			request,
			template,
			{"employees": employees, "tasks": tasks[:5], "stats": stats},
		)
	else:
		tasks = Task.objects.filter(assigned_to=request.user)
		template = "dashboard/employee_dashboard.html"
		return render(request, template, {"tasks": tasks})
