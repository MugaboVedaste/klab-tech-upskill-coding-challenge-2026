from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path(
        "employees/create/",
        views.create_employee,
        name="create_employee",
    ),
]