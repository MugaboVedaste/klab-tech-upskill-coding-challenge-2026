from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        MANAGER = "manager", "Manager"
        EMPLOYEE = "employee", "Employee"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    email = models.EmailField("email address", blank=True, unique=True)

    # Optional department for managers; employees inherit their manager's department
    department = models.CharField(max_length=100, blank=True, default="")

    # The manager who created/owns this employee (unset for managers themselves)
    manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employees",
        limit_choices_to={"role": Role.MANAGER},
    )

    def __str__(self):
        return self.username