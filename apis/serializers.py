from rest_framework import serializers
from apis.models import Task, User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'role']    
    
    
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
        
class UpdateTaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES, required=True)
    completion_report = serializers.CharField(required=False)
    worked_hours = serializers.IntegerField(required=False)