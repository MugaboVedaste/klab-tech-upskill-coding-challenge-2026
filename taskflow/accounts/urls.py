from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_manager, name="register"),
    path(
        "employees/create/",
        views.create_employee,
        name="create_employee",
    ),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/<int:user_id>/pause/", views.pause_employee, name="pause_employee"),
    path("employees/<int:user_id>/resume/", views.resume_employee, name="resume_employee"),
]