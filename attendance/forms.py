from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
#from django.contrib.admin.widgets import AdminDateWidget
from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import UpdateView
from django.shortcuts import render,redirect, get_object_or_404
from users.models import Employee as emp



class usernameForm(forms.Form):
    username=forms.CharField(max_length=30)


class MyDateInput(forms.widgets.DateInput):
    input_type = 'date'
   


    

class DateForm(forms.Form):
    date = forms.DateField(widget=MyDateInput())
    


class UsernameAndDateForm(forms.Form):
    username=forms.CharField(max_length=30)
    date_from=forms.DateField(widget=MyDateInput() )
    date_to=forms.DateField(widget=MyDateInput())

class DateForm_2(forms.Form):
    date_from=forms.DateField(widget=MyDateInput() )
    date_to=forms.DateField(widget=MyDateInput())
      
DEPARTMENT_CHOICES =( 
    ("Finance", "Finance"), 
    ("Marketing", "Marketing"), 
    ("Sales", "Sales"), 
) 
DESIGNATION_CHOICES =(
    ("Senior Manager", "Senior Manager"), 
    ("Junior Manager", "Junior Manager"), 
    ("SENIOR Employee", "SENIOR Employee"), 
    ("Junior Employee", "Junior Employee"),
) 

class Employee(UserCreationForm):

    desigination= forms.ChoiceField(choices = DESIGNATION_CHOICES, label="Desigination")
    department= forms.ChoiceField(choices = DEPARTMENT_CHOICES, label="Department") 
    contactNumber= forms.CharField(label = "Contact Number",max_length=10)
    isAdmin =forms.BooleanField(label = "Is Admin", required=False)

    class Meta:
        model=  get_user_model()
        fields=(
            'username',
            'first_name',
            'last_name',
            'email',
            'isAdmin',
            'contactNumber',
            'desigination',
            'department'
        )
    def save(self,commit=True):
        user=super(Employee,self).save(commit=False)
        user.username1=self.cleaned_data['username']
        
        

        if commit:
            user.save()

        return user
    
class edit_my_employee_profile(ModelForm):
      desigination= forms.ChoiceField(choices = DESIGNATION_CHOICES, label="Desigination")
      department= forms.ChoiceField(choices = DEPARTMENT_CHOICES, label="Department")
      contactNumber= forms.CharField(label = "Contact Number",max_length=10)
      def update(self,commit=True):
          user=super(Employee,self).save(commit=False)
          user.username1=self.cleaned_data['username']
          if commit:
            user.save(update_fields=['desigination'])

          return user
   
      class Meta:
            model = emp
            fields=(
              'email',
              'contactNumber',
              'desigination',
              'department'
        )
    