from django.contrib import admin
from .models import Attendance,TimeTable,Employee
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(Attendance)
admin.site.register(TimeTable)
admin.site.register(Employee, UserAdmin)