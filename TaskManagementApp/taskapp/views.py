from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
# Create your views here.
from django.http import HttpResponse
from taskapp.models import CustomUser,AdminUserMapping,Task

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import Task
from taskapp.serializers import TaskSerializer
from datetime import date

def create_users(request):
    create_superadmin('superadmin','superadmin@gmail.com','superadminpassword')
    create_admin('admin','admin@gmail.com','adminpassword')
    # create_superadmin('superadmin','superadmin@gmail.com','Kanhangad_123')
    # create_admin('admin','admin@gmail.com','Kanhangad_123')
    return HttpResponse("Users created successfully!")



def create_superadmin(username,email,password):
    if not CustomUser.objects.filter(username=username).exists():
        CustomUser.objects.create_superuser(username=username,email=email,password=password,role='SuperAdmin')
        print(f"Superadmin '{username}' created successfully!")
    else:
        print(f"User with username '{username}' already exists.")


def create_admin(username,email,password):
    if not CustomUser.objects.filter(username=username).exists():
        user = CustomUser.objects.create_user(username=username,email=email,password=password,role='Admin')
        print(f"Admin '{username}' created successfully!")
    else:
        print(f"User with username '{username}' already exists.")







# user functions ----------------------------


class UserTasksView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        tasks=Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

class UpdateTaskStatusView(APIView):
    permission_classes=[IsAuthenticated]

    def put(self,request,id):
        try:
            task = Task.objects.get(id=id,assigned_to=request.user)
        except Task.DoesNotExist:
            return Response({"error":"Task not found or you are not authorized to update it."},status=status.HTTP_404_NOT_FOUND)
        status_update = request.data.get("status")
        completion_report=request.data.get("completion_report")
        worked_hours = request.data.get("worked_hours")

        if status_update == "Completed":
            if not completion_report or not worked_hours:
                return Response({"error":"Completion Report and Worked Hours are required to mark a task as Completed."},status=status.HTTP_400_BAD_REQUEST)
            task.completion_report = completion_report
            task.worked_hours = worked_hours
        task.status = status_update
        task.save()
        return Response({"message":"Task updated successfully."},status=status.HTTP_200_OK)
    


class TaskReportView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request, id):
        try:
            task = Task.objects.get(id=id,status="Completed")
        except Task.DoesNotExist:
            return Response({"error":"Task not found or not marked as Completed."},status=status.HTTP_404_NOT_FOUND)
        
        data = {
            "title":task.title,
            "description":task.description,
            "worked_hours":task.worked_hours,
            "completion_report":task.completion_report,
        }
        return Response(data,status=status.HTTP_200_OK)







#super admin functions ------------------------------------

def superadmin_login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request,username=username,password=password)
        if user is not None and user.is_superadmin:
            login(request, user)
            return redirect('superadmin_dashboard')
        else:
            return render(request, 'superadmin/loginpage.html',{'error':'Invalid credentials'})
    return render(request, 'superadmin/loginpage.html')

from django.contrib.auth import logout

def superadmin_logout_view(request):
    logout(request)
    return redirect('loginpage')


def loginpage(request):
    return render(request,'superadmin/loginpage.html')

def superadmin_dashboard(request):
    users_count=CustomUser.objects.filter(role="User").count()
    admin_count=CustomUser.objects.filter(role="Admin").count()
    tasks_count=Task.objects.all().count()
    tasks=Task.objects.filter(status="Completed")
    context={
        "users_count":users_count,
        "admin_count":admin_count,
        "tasks_count":tasks_count,
        "tasks":tasks
    }
    return render(request,'superadmin/homepage.html',context)

def manage_users(request):
    users=CustomUser.objects.filter(role='User')
    return render(request,'superadmin/UserSubpages/manage_users.html',{"users":users})

def add_user(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")
        status = request.POST.get("status")

        if not username or not email or not password or not confirm_password or not role:
            messages.error(request,"All fields are required.")
            return redirect('add_user')
        if password != confirm_password:
            messages.error(request, "password do not match.")
            return redirect('add_user')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request,"Username is already taken.")
            return redirect('add_user')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request,"Email is already taken.")
            return redirect('add_user')
        
        if status=="true":
            isactive=True
        else:
            isactive=False
        
        try:
            
            user=CustomUser.objects.create_user(username=username,email=email,password=password,role=role,is_active=isactive)
            messages.success(request,"User added successfully!")
        except Exception as e:
            messages.error(request,f"Error creating user {str(e)}")
            return redirect('add_user')
        
        return redirect('manage_users')
    return render(request, 'superadmin/UserSubpages/Add_users.html')


from django.shortcuts import get_object_or_404
def delete_user(request,id):
    user=get_object_or_404(CustomUser,id=id)
    user.delete()
    messages.success(request,"User deleted successfully.")
    return redirect('manage_users')

def edit_user(request,id):
    user=get_object_or_404(CustomUser, id=id)
    if request.method == 'POST':
        username = request.POST.get("username")
        email = request.POST.get("email")
        role = request.POST.get("role")
        status = request.POST.get("status")

        if status=="true":
            is_active=True
        else:
            is_active=False
        
        if not username or not email or not role:
            messages.error(request, "All fields are required.")
            return redirect('edit_user', id=id)
        
        if CustomUser.objects.filter(username=username).exclude(id=id).exists():
            messages.error(request, "Username is already taken.")
            return redirect('edit_user', id=id)
        
        if CustomUser.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, "Email is already taken.")
            return redirect('edit_user', id=id)
        
        try:
            user.username = username
            user.email = email
            user.role = role
            user.is_active = is_active
            user.save()
            messages.success(request, "User updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating user: {str(e)}")
            return redirect('edit_user', id=id)
        
        return redirect('manage_users')

    return render(request, 'superadmin/UserSubpages/Edit_users.html', {"user": user})



def manage_admins(request):
    admins=CustomUser.objects.filter(role='Admin')
    users=CustomUser.objects.filter(role="User",is_active=True)
    return render(request,'superadmin/AdminSubpages/Manage_admins.html',{"admins":admins,"users":users})




def add_admins(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")
        status = request.POST.get("status")

        if not username or not email or not password or not confirm_password or not role:
            messages.error(request,"All fields are required.")
            return redirect('add_admins')
        if password != confirm_password:
            messages.error(request, "password do not match.")
            return redirect('add_admins')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request,"Username is already taken.")
            return redirect('add_admins')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request,"Email is already taken.")
            return redirect('add_admins')
        
        if status=="true":
            isactive=True
        else:
            isactive=False
        
        try:
            
            user=CustomUser.objects.create_user(username=username,email=email,password=password,role=role,is_active=isactive,is_staff=True,is_superuser=False)

            messages.success(request,"Admin added successfully!")
        except Exception as e:
            messages.error(request,f"Error creating user {str(e)}")
            return redirect('add_admins')
        
        return redirect('manage_admins')
    return render(request, 'superadmin/AdminSubpages/Add_admins.html')


from django.shortcuts import get_object_or_404
def delete_admin(request,id):
    user=get_object_or_404(CustomUser,id=id)
    user.delete()
    messages.success(request,"Admin deleted successfully.")
    return redirect('manage_admins')


def assign_user_to_admin(request, admin_id):
    if request.method == 'POST':
        user_id = request.POST.get('userid')
        admin = get_object_or_404(CustomUser, id=admin_id, role='Admin')
        user = get_object_or_404(CustomUser, id=user_id, role='User')
        
        if not AdminUserMapping.objects.filter(admin=admin, user=user).exists():
            AdminUserMapping.objects.create(admin=admin, user=user)
            messages.success(request, f'Successfully assigned {user.username} to {admin.username}')
        else:
            messages.warning(request, f'{user.username} is already assigned to {admin.username}')
    
    return redirect('manage_admins') 

def remove_user_from_admin(request, admin_id, user_id):
    if request.method == 'POST':
        mapping = get_object_or_404(AdminUserMapping,admin__id=admin_id,user__id=user_id)
        mapping.delete()
        messages.success(request, 'User removed from admin successfully')
    return redirect('manage_admins')


def edit_admin(request,id):
    user=get_object_or_404(CustomUser, id=id)
    if request.method == 'POST':
        username = request.POST.get("username")
        email = request.POST.get("email")
        role = request.POST.get("role")
        status = request.POST.get("status")

        if status=="true":
            is_active=True
        else:
            is_active=False
        
        if not username or not email or not role:
            messages.error(request, "All fields are required.")
            return redirect('edit_admin', id=id)
        
        if CustomUser.objects.filter(username=username).exclude(id=id).exists():
            messages.error(request, "Username is already taken.")
            return redirect('edit_admin', id=id)
        
        if CustomUser.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, "Email is already taken.")
            return redirect('edit_admin', id=id)
        
        try:
            user.username = username
            user.email = email
            user.role = role
            user.is_active = is_active
            user.save()
            messages.success(request, "admin updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating user: {str(e)}")
            return redirect('edit_admin', id=id)
        
        return redirect('manage_admins')

    return render(request, 'superadmin/AdminSubpages/Edit_Admins.html', {"user": user})





def manage_tasks(request):
    tasks=Task.objects.all()
    return render(request,'superadmin/TasksSubpages/ManageTasks.html',{"tasks": tasks})

from datetime import datetime

def add_superadmin_task(request):
    if request.method == 'POST':
        title = request.POST.get("title")
        description = request.POST.get("description")
        assigned_to = request.POST.get("assigned_to")
        due_date_str = request.POST.get("due_date")
      

        if not title or not description or not assigned_to or not due_date_str:
            messages.error(request,"All fields are required.")
            return redirect('add_superadmin_task') 
        try:
            assigned_to_user = CustomUser.objects.get(id=assigned_to)
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            Task.objects.create(title=title,description=description,assigned_to=assigned_to_user,due_date=due_date,created_by=request.user)

            messages.success(request,"task added successfully!")
        except Exception as e:
            messages.error(request,f"Error creating task {str(e)}")
            return redirect('add_superadmin_task')
        
        return redirect('manage_tasks')
    users=CustomUser.objects.filter(role="User",is_active=True)
    return render(request, 'superadmin/TasksSubpages/CreateTask.html',{"users":users})






def view_task_details(request,id):
    task =  get_object_or_404(Task, id=id)

    if request.method == 'POST':
        title = request.POST.get("title")
        description = request.POST.get("description")
        due_date = request.POST.get("due_date")
        status = request.POST.get("status")

        if not title or not description or not due_date or not status:
            messages.error(request, "All fields are required.")
            return redirect('view_task_details', id=id)
                
        try:
            task.title = title
            task.description = description
            task.due_date = due_date
            task.status = status
            task.save()
            messages.success(request, "Task updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating user: {str(e)}")
            return redirect('view_task_details', id=id)
    
    return render(request, 'superadmin/TasksSubpages/ViewTaskDetail.html', {"tasks":task})



def view_all_tasks_report(request):
    tasks=Task.objects.filter(status="Completed")
    return render(request,'superadmin/TasksSubpages/ViewAllTaskReports.html',{"tasks":tasks})

def complete_task_report(request,id):
    tasks=Task.objects.get(id=id)
    return render(request,'superadmin/TasksSubpages/TaskReport.html',{"tasks":tasks})



    
#admin functions -----------------

def admin_login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request,username=username,password=password)
        if user is not None and user.is_admin:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin/adminloginpage.html',{'error':'Invalid credentials'})
    return render(request, 'admin/adminloginpage.html')

def admin_logout_view(request):
    logout(request)
    return redirect('adminloginpage')


def adminloginpage(request):
    return render(request,'admin/adminloginpage.html')

def admin_dashboard(request):
    user_count=CustomUser.objects.filter(role="User").count()
    pending_tasks=Task.objects.filter(status='Pending',created_by=request.user).count()
    completed_tasks=Task.objects.filter(status='Completed',created_by=request.user).count()
    inprogress_tasks=Task.objects.filter(status='In Progress',created_by=request.user).count()
    context = {
        'user_count': user_count,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'inprogress_tasks': inprogress_tasks,
        "username":request.user.username,
        "email":request.user.email
    }
    return render(request,'admin/adminhomepage.html',context)



def admin_manage_tasks(request):
    tasks=Task.objects.filter(created_by=request.user)
    return render(request,'admin/AdminTaskSubpages/AdminManageTasks.html',{"tasks": tasks})


from datetime import datetime

def add_admin_task(request):
    if request.method == 'POST':
        title = request.POST.get("title")
        description = request.POST.get("description")
        due_date_str = request.POST.get("due_date")
      

        if not title or not description or not due_date_str:
            messages.error(request,"All fields are required.")
            return redirect('add_admin_task') 
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            Task.objects.create(title=title,description=description,due_date=due_date,created_by=request.user,status='Pending')

            messages.success(request,"task added successfully!")
        except Exception as e:
            messages.error(request,f"Error creating task {str(e)}")
            return redirect('add_admin_task')
        
        return redirect('admin_manage_tasks')
    return render(request, 'admin/AdminTaskSubpages/AdminCreateTask.html')






def view_admintask_details(request,id):
    task =  get_object_or_404(Task, id=id)

    if request.method == 'POST':
        title = request.POST.get("title")
        description = request.POST.get("description")
        due_date = request.POST.get("due_date")
        userid = request.POST.get("userid")
        status = request.POST.get("status")

        if not title or not description or not due_date or not status or not userid:
            messages.error(request, "All fields are required.")
            return redirect('view_admintask_details', id=id)
                
        try:
            userobj=CustomUser.objects.get(id=userid)
            task.title = title
            task.description = description
            task.due_date = due_date
            task.status = status
            task.assigned_to =userobj
            task.save()
            messages.success(request, "Task updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating user: {str(e)}")
            return redirect('view_admintask_details', id=id)
        
    admin_mappings = AdminUserMapping.objects.filter(admin=request.user)
    managed_users = [mapping.user for mapping in admin_mappings]
    return render(request, 'admin/AdminTaskSubpages/AdminViewTaskDetails.html', {"task":task,"managed_users": managed_users})


def admin_view_tasks_reports(request):
    tasks=Task.objects.filter(status="Completed",created_by=request.user)
    return render(request,'admin/AdminTaskSubpages/AdminViewAllTaskReports.html',{"tasks":tasks})

def admin_complete_task_report(request,id):
    tasks=Task.objects.get(id=id)
    return render(request,'admin/AdminTaskSubpages/AdminCompleteTaskReport.html',{"tasks":tasks})