from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

# Create your models here.

class Employee(AbstractUser):
    desigination = models.CharField(max_length=80)
    department = models.CharField(max_length=80)
    contactNumber = models.IntegerField(null=True)
    isAdmin =models.BooleanField(default=False)

class Attendance(models.Model):
    id =models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    isPresent=models.BooleanField(default=False)

class TimeTable(models.Model):
    id =models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    logtime=models.DateTimeField(null=True,blank=True)
    isLogin=models.BooleanField(default=False)


