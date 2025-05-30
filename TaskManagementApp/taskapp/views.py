from django.shortcuts import render

# Create your views here.

#super admin functions
def loginpage(request):
    return render(request,'superadmin/loginpage.html')

def homepage(request):
    return render(request,'superadmin/homepage.html')

#admin functions
def adminloginpage(request):
    return render(request,'admin/adminloginpage.html')

def adminhomepage(request):
    return render(request,'admin/adminhomepage.html')


