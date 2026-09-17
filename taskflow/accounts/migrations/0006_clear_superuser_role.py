from django.db import migrations


def clear_superuser_role(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(is_superuser=True).update(role="")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_managers_alter_user_role'),
    ]

    operations = [
        migrations.RunPython(clear_superuser_role, noop_reverse),
    ]
