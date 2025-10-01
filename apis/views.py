from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apis.models import Task, User
from apis.serializers import LoginSerializer, TaskSerializer, UpdateTaskStatusSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from apis.constants import STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED
import logging

logger = logging.getLogger(__name__)


# Login API
@extend_schema(tags=["User Management"])
class LoginView(CreateAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            if not all([email, password]):
                return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(email=email)
            if not user.is_active:
                return Response({"error": "Account is not active, please contact admin"}, status=status.HTTP_400_BAD_REQUEST)  
            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            refresh["role"] = user.role
            refresh["id"] = user.id
            
            response_context = {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }

            return Response({"message": "Login successful", "data": response_context}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "No account found in this email"}, status=status.HTTP_400_BAD_REQUEST)  
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get Tasks API
@extend_schema(tags=["Task Management"])
class GetTasksView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)
    
    def list(self, request, *args, **kwargs):
        if not self.request.user.is_user():
            return Response({"error": "You are not a user"}, status=status.HTTP_403_FORBIDDEN)
        
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        
        return Response({"message": "Tasks retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    
    
# Update Task Status API
@extend_schema(
    tags=["Task Management"],
    request=UpdateTaskStatusSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="Task status updated successfully")
    }
)
class UpdateTaskStatusView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, *args, **kwargs):
        try:
            if not self.request.user.is_user():
                return Response({"error": "You are not a user"}, status=status.HTTP_403_FORBIDDEN)
        
            task_id = kwargs.get("id")
            task_status = request.data.get("status")
            if not task_status:
                return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            status_lower = task_status.lower()
            status_map = {
                'pending': STATUS_PENDING,
                'in_progress': STATUS_IN_PROGRESS,
                'completed': STATUS_COMPLETED
            }
            if status_lower not in status_map:
                return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
            
            status_value = status_map[status_lower]
            
            task = Task.objects.get(id=task_id)
            
            if task.status == STATUS_COMPLETED and status != STATUS_COMPLETED:
                return Response({"error": "A completed task cannot be reverted to previous status"}, status=status.HTTP_400_BAD_REQUEST)
            
            if status_value == STATUS_COMPLETED:
                completion_report = request.data.get("completion_report", "").strip()
                worked_hours = request.data.get("worked_hours")
                
                if not completion_report or worked_hours is None:
                    return Response({"error": "Completion report and worked hours are required when marking task as completed"}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    worked_hours_val = float(worked_hours)
                except ValueError:
                    return Response({"error": "Worked hours must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)
                
                if worked_hours_val <= 0:
                    return Response({"error": "Worked hours must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
                    
                task.completion_report = completion_report
                task.worked_hours = worked_hours_val
            else:
                task.completion_report = None
                task.worked_hours = None
                
            task.status = status_value
            task.save()
            
            return Response({"message": "Task status updated successfully"}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "No task found with this ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# Task Report API
@extend_schema(tags=["Task Management"])
class TaskReportView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = TaskSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            task_id = kwargs.get("id")
            
            if request.user.is_superadmin():
                task = Task.objects.get(id=task_id)
            elif request.user.is_admin():
                task = Task.objects.get(id=task_id, assigned_to__assigned_admin=request.user)
            else:
                return Response({"error": "You are not an admin"}, status=status.HTTP_403_FORBIDDEN)
            
            if task.status != STATUS_COMPLETED:
                return Response({"error": "Task is not completed"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(task)
            return Response({"message": "Task report retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "No task found with this ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)