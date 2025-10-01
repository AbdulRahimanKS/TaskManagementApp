from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from apis.constants import ADMIN, SUPER_ADMIN, USER, STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', SUPER_ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email, password, **extra_fields)
        return user    

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
        (SUPER_ADMIN, 'SuperAdmin'),
    ]
   
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    assigned_admin = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_users',
        limit_choices_to={'role': ADMIN}
    )
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date updated'), auto_now=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank=True,
        help_text='Specific permissions for this user',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'role']

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def is_superadmin(self):
        return self.role == SUPER_ADMIN

    def is_admin(self):
        return self.role == ADMIN
    
    def is_user(self):
        return self.role == USER
    
    @property
    def title(self):
        return f"{self.first_name} {self.last_name}"  if self.last_name else self.first_name
    

class Task(models.Model):
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', limit_choices_to={'role': USER})
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"
