"""
URL configuration for TaskManagementApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from taskapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('create-users/', views.create_users, name='create_users'),


    #superadmin urls
    path('loginpage/',views.loginpage,name='loginpage'),
    path('superadmin_login_view/', views.superadmin_login_view, name='superadmin_login_view'),
    path('superadmin_dashboard/',views.superadmin_dashboard,name='superadmin_dashboard'),
    path('superadmin/logout/', views.superadmin_logout_view, name='superadmin_logout'),
    path('manage_users/',views.manage_users,name="manage_users"),
    path('add_user/',views.add_user,name="add_user"),
    path('delete_user/<int:id>/', views.delete_user, name="delete_user"),
    path('edit_user/<int:id>/', views.edit_user, name="edit_user"),

    #admin urls

    path('adminloginpage/',views.adminloginpage,name="adminloginpage"),
    path('admin_login_view/', views.admin_login_view, name='admin_login_view'),
    path('admin_dashboard/',views.admin_dashboard,name="admin_dashboard"),
    path('admin_logoutpage/',views.admin_logout_view,name="admin_logoutpage"),

    path('manage_admins/',views.manage_admins,name="manage_admins"),
    path('add_admins/',views.add_admins,name="add_admins"),
    path('delete_admin/<int:id>/', views.delete_admin, name="delete_admin"),
    path('assign-user-to-admin/<int:admin_id>/', views.assign_user_to_admin, name='assign_user_to_admin'),
    path('remove-user-from-admin/<int:admin_id>/<int:user_id>/', views.remove_user_from_admin, name='remove_user_from_admin'),
    path('edit_admin/<int:id>/',views.edit_admin,name="edit_admin"),

    path('manage_tasks',views.manage_tasks,name="manage_tasks"),
    path('add_superadmin_task',views.add_superadmin_task,name="add_superadmin_task"),
    path('view_task_details/<int:id>/', views.view_task_details, name="view_task_details"),
    








]
