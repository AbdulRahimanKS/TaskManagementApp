from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from admin_interface.permissions_mixin import RoleRequiredMixin
from apis.constants import *
from apis.models import Task, User
from datetime import datetime


# Admin Login
class AdminLoginView(TemplateView):
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get('email')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Username and Password are required')
            return self.get(request, *args, **kwargs)
        
        user = authenticate(request, username=username, password=password)
        
        if user and user.is_authenticated:
            login(request, user)

            if user.is_superadmin():
                return redirect('manage_users')
            elif user.is_admin():
                return redirect('assigned_users')
            else:
                messages.error(request, f"Account is not an admin account")
                return self.get(request, *args, **kwargs)
        else:
            messages.error(request, 'Invalid credentials or inactive account')
            return self.get(request, *args, **kwargs)
        
        
# Admin Logout
class AdminLogoutView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return redirect('admin_login')


# Manage Users
class ManageUsersView(RoleRequiredMixin, TemplateView):
    template_name = "manage_users.html"
    allowed_roles = [SUPER_ADMIN]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_users = User.objects.exclude(is_superuser=True, id=self.request.user.id)
        admin_users = User.objects.filter(role=ADMIN)
        user_role_choices = [(USER, 'User'), (ADMIN, 'Admin')]

        context['all_users'] = all_users
        context['choices'] = user_role_choices
        context['admin_users'] = admin_users
        
        return context
    
    
# Add User
class AddUserView(RoleRequiredMixin, View):
    allowed_roles = [SUPER_ADMIN]
    
    def post(self, request, *args, **kwargs):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")
        assigned_admin_id = request.POST.get("assigned_admin")
        
        if not all([first_name, email, password, confirm_password, role]):
            messages.error(request, "Fill all the required fields")
            return redirect("manage_users")

        if password != confirm_password:
            messages.error(request, "Passwords are not matching")
            return redirect("manage_users")

        if User.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists")
            return redirect("manage_users")

        user = User.objects.create_user(email=email, first_name=first_name,
            last_name=last_name, password=password, role=role)

        if role == USER and assigned_admin_id:
            try:
                assigned_admin = User.objects.get(id=assigned_admin_id, role=ADMIN)
                user.assigned_admin = assigned_admin
                user.save()
            except User.DoesNotExist:
                messages.warning(request, "Selected admin not found. User created without assigned admin")

        messages.success(request, f"User created successfully")
        return redirect("manage_users")
    
    
# Update User
class UpdateUserView(RoleRequiredMixin, View):
    allowed_roles = [SUPER_ADMIN]
    
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        role = request.POST.get("role")
        assigned_admin_id = request.POST.get("assigned_admin")
        
        if not user_id:
            messages.error(request, "User ID not provided")
            return redirect("manage_users")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect("manage_users")
        
        if email and User.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, "A user with this email already exists")
            return redirect("manage_users")
        
        previous_role = user.role
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.role = role
        
        if user.role == USER:
            if assigned_admin_id:
                try:
                    assigned_admin = User.objects.get(id=assigned_admin_id, role=ADMIN)
                    user.assigned_admin = assigned_admin
                except User.DoesNotExist:
                    messages.warning(request, "Selected admin not found. User updated without assigned admin")
            else:
                user.assigned_admin = None
        else:
            user.assigned_admin = None
            
        if previous_role == ADMIN and role != ADMIN:
            User.objects.filter(assigned_admin=user).update(assigned_admin=None)
        
        user.save()
        messages.success(request, f"User updated successfully")
        return redirect("manage_users")
    
    
# Delete User
class DeleteUserView(RoleRequiredMixin, View):
    allowed_roles = [SUPER_ADMIN]
    
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        
        if not user_id:
            messages.error(request, "User ID not provided")
            return redirect("manage_users")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect("manage_users")
        
        user.delete()
        messages.success(request, f"User deleted successfully")
        return redirect("manage_users")

    
# Assigned Users
class AssignedUsersView(RoleRequiredMixin, TemplateView):
    template_name = "assigned_users.html"
    allowed_roles = [ADMIN]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assigned_users = User.objects.filter(assigned_admin=self.request.user)
        
        context['assigned_users'] = assigned_users
        return context
    
    
# Manage Tasks
class ManageTasksView(RoleRequiredMixin, TemplateView):
    template_name = "manage_tasks.html"
    allowed_roles = [SUPER_ADMIN, ADMIN]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        users = User.objects.filter(role=USER)
        tasks = Task.objects.select_related("assigned_to__assigned_admin").all()
        
        if self.request.user.is_admin():
            users = users.filter(assigned_admin=self.request.user)
            tasks = tasks.filter(assigned_to__in=users)
            
        
        context['tasks'] = tasks
        context['users'] = users
        context['task_status'] = [(STATUS_PENDING, 'Pending'), (STATUS_IN_PROGRESS, 'In Progress'), (STATUS_COMPLETED, 'Completed')]
        
        return context
    
    
# Add Task
class AddTaskView(RoleRequiredMixin, View):
    allowed_roles = [SUPER_ADMIN, ADMIN]
    
    def post(self, request, *args, **kwargs):
        title = request.POST.get("title")
        description = request.POST.get("description")
        assigned_to = request.POST.get("assigned_to")
        due_date = request.POST.get("due_date")
        status = request.POST.get("status")
        
        if not all([title, description, assigned_to, due_date, status]):
            messages.error(request, "Fill all the required fields")
            return redirect("manage_tasks")
        
        if Task.objects.filter(title__iexact=title).exists():
            messages.error(request, "Task with this title already exists. Please use a different title")
            return redirect("manage_tasks")
        
        if due_date and datetime.now().date() > datetime.strptime(due_date, "%Y-%m-%d").date():
            messages.error(request, "Due date cannot be in the past")
            return redirect("manage_tasks")
        
        Task.objects.create(title=title, description=description,
            assigned_to_id=assigned_to, due_date=due_date, status=status)
        
        messages.success(request, f"Task created successfully")
        return redirect("manage_tasks")
    
    
# Update Task
class UpdateTaskView(RoleRequiredMixin, View):
    allowed_roles = [SUPER_ADMIN, ADMIN]
    
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get("task_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        assigned_to = request.POST.get("assigned_to")
        due_date = request.POST.get("due_date")
        status = request.POST.get("status")
        
        if not all([task_id, title, description, assigned_to, due_date, status]):
            messages.error(request, "Fill all the required fields")
            return redirect("manage_tasks")
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            messages.error(request, "Task not found")
            return redirect("manage_tasks")
        
        try:
            assigned_to_user = User.objects.get(id=assigned_to)
        except User.DoesNotExist:
            messages.error(request, "Assigning user not found")
            return redirect("manage_tasks")
        
        if due_date and datetime.now().date() > datetime.strptime(due_date, "%Y-%m-%d").date():
            messages.error(request, "Due date cannot be in the past")
            return redirect("manage_tasks")
        
        if task.status == STATUS_COMPLETED and status != STATUS_COMPLETED:
            messages.error(request, "A completed task cannot be reverted to previous status")
            return redirect("manage_tasks")
                
        if status == STATUS_COMPLETED:
            completion_report = request.POST.get("completion_report", "").strip()
            worked_hours = request.POST.get("worked_hours")

            if not completion_report or not worked_hours:
                messages.error(request, "Completion report and worked hours are required when marking task as completed")
                return redirect("manage_tasks")

            try:
                worked_hours_val = float(worked_hours)
            except ValueError:
                messages.error(request, "Worked hours must be a valid number")
                return redirect("manage_tasks")

            if worked_hours_val <= 0:
                messages.error(request, "Worked hours must be greater than 0")
                return redirect("manage_tasks")

            task.completion_report = completion_report
            task.worked_hours = worked_hours_val
        else:
            task.completion_report = None
            task.worked_hours = None
        
        task.title = title
        task.description = description
        task.assigned_to = assigned_to_user
        task.due_date = due_date
        task.status = status
        task.save()
        
        messages.success(request, f"Task updated successfully")
        return redirect("manage_tasks")
    
    
# Delete Task
class DeleteTaskView(RoleRequiredMixin, View):
    allowed_roles = [SUPER_ADMIN, ADMIN]
    
    def post(self, request, *args, **kwargs):
        task_id = request.POST.get("task_id")
        
        if not task_id:
            messages.error(request, "Task ID not provided")
            return redirect("manage_tasks")
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            messages.error(request, "Task not found")
            return redirect("manage_tasks")
        
        task.delete()
        messages.success(request, f"Task deleted successfully")
        return redirect("manage_tasks")
        
    
# Task Reports
class TaskReportsView(RoleRequiredMixin, TemplateView):
    template_name = "task_reports.html"
    allowed_roles = [SUPER_ADMIN, ADMIN]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        users = User.objects.filter(role=USER)
        tasks = Task.objects.select_related("assigned_to__assigned_admin").filter(status=STATUS_COMPLETED).all()
        
        if self.request.user.is_admin():
            users = users.filter(assigned_admin=self.request.user)
            tasks = tasks.filter(assigned_to__in=users)
        
        context['tasks'] = tasks.order_by('-updated_at') 
        return context