from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone

from tasks.models import Task

User = get_user_model()

TREND_DAYS = 7

CHART_WIDTH = 560
CHART_HEIGHT = 160
CHART_PAD_LEFT = 28
CHART_PAD_RIGHT = 10
CHART_PAD_TOP = 12
CHART_PAD_BOTTOM = 24
PLOT_WIDTH = CHART_WIDTH - CHART_PAD_LEFT - CHART_PAD_RIGHT
PLOT_HEIGHT = CHART_HEIGHT - CHART_PAD_TOP - CHART_PAD_BOTTOM


def _task_trend(tasks):
	today = timezone.localdate()
	days = [today - timedelta(days=offset) for offset in range(TREND_DAYS - 1, -1, -1)]

	counts = []
	for day in days:
		counts.append({
			"date": day,
			"label": day.strftime("%a"),
			"created": tasks.filter(created_at__date=day).count(),
			"completed": tasks.filter(status=Task.Status.REVIEWED, updated_at__date=day).count(),
		})

	peak = max((max(d["created"], d["completed"]) for d in counts), default=0)
	step = PLOT_WIDTH / (len(counts) - 1) if len(counts) > 1 else 0

	def y_for(value):
		if not peak:
			return CHART_PAD_TOP + PLOT_HEIGHT
		return CHART_PAD_TOP + PLOT_HEIGHT - (value / peak * PLOT_HEIGHT)

	points = []
	for i, d in enumerate(counts):
		x = CHART_PAD_LEFT + i * step
		points.append({
			"x": round(x, 1),
			"label": d["label"],
			"created": d["created"],
			"completed": d["completed"],
			"y_created": round(y_for(d["created"]), 1),
			"y_completed": round(y_for(d["completed"]), 1),
		})

	return {
		"width": CHART_WIDTH,
		"height": CHART_HEIGHT,
		"baseline_y": CHART_PAD_TOP + PLOT_HEIGHT,
		"peak": peak,
		"peak_y": CHART_PAD_TOP,
		"points": points,
		"created_line": " ".join(f"{p['x']},{p['y_created']}" for p in points),
		"completed_line": " ".join(f"{p['x']},{p['y_completed']}" for p in points),
	}


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
		trend = _task_trend(tasks)

		template = "dashboard/manager_dashboard.html"
		return render(
			request,
			template,
			{
				"employees": employees,
				"tasks": tasks[:5],
				"stats": stats,
				"trend": trend,
			},
		)
	else:
		tasks = Task.objects.filter(assigned_to=request.user)
		template = "dashboard/employee_dashboard.html"
		return render(request, template, {"tasks": tasks})
