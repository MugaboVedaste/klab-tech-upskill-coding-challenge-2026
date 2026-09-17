from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from accounts.api_views import EmployeeViewSet, RegisterManagerView
from tasks.api_views import TaskViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="api-task")
router.register("employees", EmployeeViewSet, basename="api-employee")

urlpatterns = [
    path("auth/register/", RegisterManagerView.as_view(), name="api_register"),
    path("auth/login/", obtain_auth_token, name="api_login"),
    path("auth/token/", obtain_auth_token, name="api_token_auth"),  # alias of login/
    path("", include(router.urls)),
]
