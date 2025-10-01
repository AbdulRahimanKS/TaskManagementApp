from django.urls import path
from admin_interface.views import *


urlpatterns = [
    path('', AdminLoginView.as_view(), name='admin_login'),
    path('admin_logout/', AdminLogoutView.as_view(), name='admin_logout'),
    
    path('manage_users/', ManageUsersView.as_view(), name='manage_users'),
    path('add_user/', AddUserView.as_view(), name='add_user'),
    path('update_user/', UpdateUserView.as_view(), name='update_user'),
    path('delete_user/', DeleteUserView.as_view(), name='delete_user'),
    path('assigned_users/', AssignedUsersView.as_view(), name='assigned_users'),
    
    path('manage_tasks/', ManageTasksView.as_view(), name='manage_tasks'),
    path('add_task/', AddTaskView.as_view(), name='add_task'),
    path('update_task/', UpdateTaskView.as_view(), name='update_task'),
    path('delete_task/', DeleteTaskView.as_view(), name='delete_task'),
    
    path('task_reports/', TaskReportsView.as_view(), name='task_reports'),
]
