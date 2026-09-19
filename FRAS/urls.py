"""
URL configuration for FRAS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from attendance import views as attndnce_views
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', attndnce_views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('mark_your_attendance', attndnce_views.mark_your_attendance,name='mark-your-attendance'),
    path('mark_your_attendance_out', attndnce_views.mark_your_attendance_out, name='mark-your-attendance-out'),

    
    path('logout/', auth_views.LogoutView.as_view(template_name='recognition/home.html'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),

    path('dashboard/', attndnce_views.dashboard2, name='dashboard'),
    path('view_attendance_home', attndnce_views.view_attendance_home, name='view-attendance-home'),
    path('register2/', users_views.register2, name='reg2'),
    path('add_photos/', attndnce_views.add_photos, name='add-photos'),
    path('train/', attndnce_views.train, name='train'),

    path('view_attendance_employee', attndnce_views.view_attendance_employee,name='view-attendance-employee'),
    path('view_attendance_date', attndnce_views.view_attendance_date,name='view-attendance-date'),

     path('view_my_attendance', attndnce_views.view_my_attendance_employee_login,name='view-my-attendance-employee-login'),
     path('view_my_employee_profile', attndnce_views.view_my_employee_profile,name='view-my-employee-profile'),
     path('edit_my_employee_profile/<int:id>/', attndnce_views.edit_my_employee_profile, name='employee-profile-edit'),
]



