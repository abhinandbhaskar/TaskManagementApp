from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('SuperAdmin','SuperAdmin'),
        ('Admin','Admin'),
        ('User','User'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belogs to. A user will get all permissions granted to each of their groups. ',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permission for this user. ',
        verbose_name='user permissions',
    )


    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def is_superadmin(self):
        return self.role == 'SuperAdmin'
    
    @property
    def is_admin(self):
        return self.role == 'Admin'
    
    @property
    def is_user(self):
        return self.role == 'User'
    

class AdminUserMapping(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_users',
        limit_choices_to={'role':'Admin'}
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_admin',
        limit_choices_to={'role':'User'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} manages {self.user.username}"
    

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending','Pending'),
        ('In Progress','In Progress'),
        ('Completed','Completed'),
    ]

    title = models.CharField(max_length=255, verbose_name="Task Title")
    description = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tasks',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_tasks",
        on_delete=models.CASCADE
    )
    due_date = models.DateField(verbose_name="Due Date")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.FloatField(default=0.0,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        if self.due_date < date.today():
            raise ValidationError("The due date cannot be in the past. ")

        if self.status == 'Completed':
            if not self.completion_report:
                raise ValidationError("Please provide a completion report when marking a task as completed. ")
            if self.worked_hours is None or self.worked_hours <= 0:
                raise ValidationError("Please specify a positive number of hours worked when marking a task as completed. ")

