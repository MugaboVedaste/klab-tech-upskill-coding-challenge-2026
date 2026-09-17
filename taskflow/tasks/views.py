from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from accounts.views import manager_required
from .models import Task
from .transitions import EMPLOYEE_TRANSITIONS, MANAGER_DECISIONS

User = get_user_model()


def employee_required(user):
    return user.is_authenticated and user.role == User.Role.EMPLOYEE


@user_passes_test(manager_required)
def create_task(request):
    employees = User.objects.filter(
        role=User.Role.EMPLOYEE, manager=request.user, is_active=True
    )
    error = None

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        priority = request.POST.get("priority", Task.Priority.MEDIUM)
        assigned_to_id = request.POST.get("assigned_to")

        assignee = employees.filter(id=assigned_to_id).first()

        if not title or not assignee:
            error = "A title and a valid employee are required."
        elif priority not in Task.Priority.values:
            error = "Invalid priority."
        else:
            Task.objects.create(
                title=title,
                description=description,
                priority=priority,
                created_by=request.user,
                assigned_to=assignee,
            )
            return redirect("task_list")

    return render(
        request,
        "tasks/create_task.html",
        {"employees": employees, "error": error},
    )


@user_passes_test(manager_required)
def task_list(request):
    tasks = Task.objects.filter(created_by=request.user).select_related("assigned_to")

    status = request.GET.get("status")
    if status in Task.Status.values:
        tasks = tasks.filter(status=status)

    all_tasks = Task.objects.filter(created_by=request.user)
    stats = {
        "total": all_tasks.count(),
        "pending": all_tasks.filter(status=Task.Status.PENDING).count(),
        "in_progress": all_tasks.filter(status=Task.Status.IN_PROGRESS).count(),
        "done": all_tasks.filter(status=Task.Status.DONE).count(),
        "reviewed": all_tasks.filter(status=Task.Status.REVIEWED).count(),
        "rejected": all_tasks.filter(status=Task.Status.REJECTED).count(),
    }

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": tasks,
            "stats": stats,
            "status": status,
            "statuses": Task.Status,
        },
    )


@user_passes_test(manager_required)
def review_task(request, task_id):
    if request.method != "POST":
        return redirect("task_list")

    try:
        task = Task.objects.get(id=task_id, created_by=request.user)
    except Task.DoesNotExist:
        return redirect("task_list")

    new_status = MANAGER_DECISIONS.get(request.POST.get("decision"))

    if new_status and task.status == Task.Status.DONE:
        task.status = new_status
        task.save(update_fields=["status", "updated_at"])

    return redirect("task_list")


@user_passes_test(employee_required)
def my_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, "tasks/my_tasks.html", {"tasks": tasks})


@user_passes_test(employee_required)
def update_task_status(request, task_id):
    if request.method != "POST":
        return redirect("my_tasks")

    try:
        task = Task.objects.get(id=task_id, assigned_to=request.user)
    except Task.DoesNotExist:
        return redirect("my_tasks")

    new_status = request.POST.get("status")
    allowed = EMPLOYEE_TRANSITIONS.get(task.status, set())

    if new_status in allowed:
        task.status = new_status
        task.save(update_fields=["status", "updated_at"])

    return redirect("my_tasks")
