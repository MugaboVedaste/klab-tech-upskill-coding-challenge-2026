from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test

User = get_user_model()
def manager_required(user):
    return user.is_authenticated and user.role == User.Role.MANAGER
@user_passes_test(manager_required)
def create_employee(request):

    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        employee = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=User.Role.EMPLOYEE,
        )

        return redirect("employee_list")

    return render(
        request,
        "accounts/create_employee.html",
    )
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        return render(
            request,
            "accounts/login.html",
            {"error": "Invalid username or password."},
        )

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")