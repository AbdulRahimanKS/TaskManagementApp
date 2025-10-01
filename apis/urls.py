from django.urls import path
from apis.views import *


urlpatterns = [
    path('Login/', LoginView.as_view(), name='Login'),
    path('tasks/', GetTasksView.as_view(), name='get_tasks'),
    path('tasks/<int:id>/', UpdateTaskStatusView.as_view(), name='update_task_status'),
    path('tasks/<int:id>/report/', TaskReportView.as_view(), name='task_report'),
]
