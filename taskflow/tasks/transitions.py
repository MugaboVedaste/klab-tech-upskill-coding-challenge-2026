from .models import Task

# Transitions an employee may make, keyed by the task's current status.
EMPLOYEE_TRANSITIONS = {
    Task.Status.PENDING: {Task.Status.IN_PROGRESS},
    Task.Status.IN_PROGRESS: {Task.Status.DONE},
    Task.Status.REJECTED: {Task.Status.IN_PROGRESS, Task.Status.DONE},
}

# Decisions a manager may make once an employee has marked a task Done.
MANAGER_DECISIONS = {
    "reviewed": Task.Status.REVIEWED,
    "rejected": Task.Status.REJECTED,
}
