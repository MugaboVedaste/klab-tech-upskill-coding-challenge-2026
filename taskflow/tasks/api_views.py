from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsEmployee, IsManager
from .models import Task
from .serializers import TaskSerializer, TaskWriteSerializer
from .transitions import EMPLOYEE_TRANSITIONS, MANAGER_DECISIONS


class TaskViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.MANAGER:
            qs = Task.objects.filter(created_by=user)
        else:
            qs = Task.objects.filter(assigned_to=user)

        status_param = self.request.query_params.get("status")
        if status_param in Task.Status.values:
            qs = qs.filter(status=status_param)

        return qs.select_related("assigned_to", "created_by")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TaskWriteSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "review"):
            return [IsManager()]
        if self.action == "update_status":
            return [IsEmployee()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(created_by=request.user)
        return Response(TaskSerializer(task).data, status=201)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=["post"], url_path="status")
    def update_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get("status")
        allowed = EMPLOYEE_TRANSITIONS.get(task.status, set())

        if new_status not in allowed:
            return Response({"detail": "Invalid status transition."}, status=400)

        task.status = new_status
        task.save(update_fields=["status", "updated_at"])
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        task = self.get_object()
        new_status = MANAGER_DECISIONS.get(request.data.get("decision"))

        if not new_status or task.status != Task.Status.DONE:
            return Response({"detail": "Task must be Done before it can be reviewed."}, status=400)

        task.status = new_status
        task.save(update_fields=["status", "updated_at"])
        return Response(TaskSerializer(task).data)
