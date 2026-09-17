from rest_framework import serializers

from .models import User


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "department",
            "is_active",
        ]
        read_only_fields = ["id", "department", "is_active"]


class AccountRegistrationFieldsMixin:
    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Username is required.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with that email already exists.")
        return value

    def validate_first_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("First name is required.")
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Last name is required.")
        return value


class EmployeeCreateSerializer(AccountRegistrationFieldsMixin, serializers.ModelSerializer):
    # Declared explicitly (not just via Meta.fields) because the model's
    # first_name/last_name are blank=True, which would otherwise make
    # DRF treat them as optional and skip validate_* on omission.
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=1)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password"]

    def create(self, validated_data):
        manager = self.context["request"].user
        return User.objects.create_user(
            role=User.Role.EMPLOYEE,
            department=manager.department,
            manager=manager,
            **validated_data,
        )


class ManagerRegisterSerializer(AccountRegistrationFieldsMixin, serializers.ModelSerializer):
    """Public manager self-registration. Accounts are created inactive and
    require superuser approval (activate via Django admin), same as the
    web UI's /accounts/register/.
    """

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=1)
    department = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password", "department"]

    def create(self, validated_data):
        return User.objects.create_user(
            role=User.Role.MANAGER,
            is_active=False,
            **validated_data,
        )
