from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError

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

        # basic validation to avoid IntegrityError on unique username/email
        error = None
        if User.objects.filter(username=username).exists():
            error = "Username already taken."
        elif User.objects.filter(email=email).exists():
            error = "An account with that email already exists."
        else:
            try:
                employee = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    role=User.Role.EMPLOYEE,
                )
            except IntegrityError:
                error = "Could not create employee — username may already exist."

        if not error:
            return redirect("employee_list")
        else:
            return render(request, "accounts/create_employee.html", {"error": error})

    return render(
        request,
        "accounts/create_employee.html",
    )


@user_passes_test(manager_required)
def employee_list(request):
    # Show all employees to managers
    employees = User.objects.filter(role=User.Role.EMPLOYEE)
    return render(request, "accounts/employee_list.html", {"employees": employees})


@user_passes_test(manager_required)
def pause_employee(request, user_id):
    # Pause (deactivate) an employee account
    if request.method != "POST":
        return redirect("employee_list")

    try:
        emp = User.objects.get(id=user_id, role=User.Role.EMPLOYEE)
    except User.DoesNotExist:
        return redirect("employee_list")

    # Prevent manager from pausing their own account
    if emp == request.user:
        return redirect("employee_list")

    emp.is_active = False
    emp.save(update_fields=["is_active"])
    return redirect("employee_list")
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


def register_manager(request):
    """Public manager registration. Accounts created as inactive and require
    superuser approval (activate via Django admin).
    """
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        department = request.POST.get("department")

        # Basic validation: unique username and email
        if User.objects.filter(username=username).exists():
            error = "Username already taken."
        elif User.objects.filter(email=email).exists():
            error = "An account with that email already exists."
        else:
            # Create manager user but keep inactive until approved by superuser
            employee = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                role=User.Role.MANAGER,
                is_active=False,
            )

            if department:
                employee.department = department
                employee.save(update_fields=["department"])

            return render(request, "accounts/registration_submitted.html", {"username": username})

    return render(request, "accounts/register_manager.html", {"error": error})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")