from django.contrib import admin
# Register your models here.
from .models import Staff,Task,Admin,DirectorsTask

admin.site.register(Admin)


admin.site.register(Staff)


admin.site.register(Task)


admin.site.register(DirectorsTask)



