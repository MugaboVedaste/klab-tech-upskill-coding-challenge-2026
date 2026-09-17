from django.urls import path

from . import views

urlpatterns = [
    path("", views.task_list, name="task_list"),
    path("create/", views.create_task, name="create_task"),
    path("my/", views.my_tasks, name="my_tasks"),
    path("<int:task_id>/status/", views.update_task_status, name="update_task_status"),
    path("<int:task_id>/review/", views.review_task, name="review_task"),
]
