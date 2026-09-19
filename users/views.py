from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from attendance.forms import Employee
from django.contrib.auth import  get_user_model

User = get_user_model()
# Create your views here.
@login_required
def register2(request):
	if request.user.username!='admin':
		return redirect('not-authorised')
	if request.method=='POST':
		all_users = User.objects.values()
		print(all_users[0]['email'])
		form=Employee(request.POST)
		if form.is_valid():
			form.save() ###add user to database
			messages.success(request, f'Employee registered successfully!')
			return redirect('dashboard')
		


	else:
		form=Employee()
	return render(request,'users/register2.html', {'form' : form})