from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsManager
from .serializers import EmployeeCreateSerializer, EmployeeSerializer, ManagerRegisterSerializer


class RegisterManagerView(APIView):
    """Public manager self-registration. Mirrors the web UI's
    /accounts/register/ — the account is created inactive and needs
    superuser approval before it can log in.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ManagerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        manager = serializer.save()
        return Response(
            {
                "detail": "Registration submitted. An administrator must approve "
                "your account before you can log in.",
                "username": manager.username,
            },
            status=201,
        )


class EmployeeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsManager]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.EMPLOYEE, manager=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return EmployeeCreateSerializer
        return EmployeeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        return Response(EmployeeSerializer(employee).data, status=201)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        employee = self.get_object()
        if employee == request.user:
            return Response({"detail": "Cannot pause your own account."}, status=400)
        employee.is_active = False
        employee.save(update_fields=["is_active"])
        return Response(EmployeeSerializer(employee).data)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        employee = self.get_object()
        employee.is_active = True
        employee.save(update_fields=["is_active"])
        return Response(EmployeeSerializer(employee).data)
