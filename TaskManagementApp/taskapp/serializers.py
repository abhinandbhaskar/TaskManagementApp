from rest_framework import serializers
from taskapp.models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id','title','description','status','due_date','assigned_to','created_by']