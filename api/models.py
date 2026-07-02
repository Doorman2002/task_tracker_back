from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class Admin(models.Model):
    Name=models.CharField(max_length=256,null=True)
    Email=models.EmailField(null=True)
    password=models.CharField(max_length=256, null=True)
    token=models.CharField(null=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Admin: {self.Name or 'Unnamed'}"

################################################## staff
class Staff(models.Model):
    Name=models.CharField(max_length=256,null=True)
    Email=models.EmailField(null=True)
    Unique_id=models.CharField(max_length=126,null=True)
    dpt=models.CharField(max_length=100,null=True)
    role=models.CharField(max_length=20, default='staff')
    token=models.CharField(null=True)
    def __str__(self):
        return f"{str(self.Name)} with the Email {str(self.Email)}"
        
class DirectorsTask(models.Model):
    staff=models.ForeignKey(Staff,on_delete=models.SET_NULL,related_name="director_tasks",null=True)
    task=models.TextField(null=True)
    date=models.DateField(null=True,auto_now=True)
    status=models.CharField(null=True,default="In progress")
                            
    def __str__(self):
    #
        if self.staff:
            return f"{str(self.staff.Name)} Task Done on {str(self.date)}"
        
    
        return f"Unassigned Task Done on {str(self.date)}"    
    
####################################################### task
    
class Task(models.Model):
    staff=models.ForeignKey(Staff,on_delete=models.SET_NULL,related_name="task",null=True)
    task=models.TextField(null=True)
    date=models.DateField(null=True,auto_now=True)
    status=models.CharField(null=True,default="In progress")
                            
    def __str__(self):
    #
        if self.staff:
            return f"{str(self.staff.Name)} Task Done on {str(self.date)}"
        
    
        return f"Unassigned Task Done on {str(self.date)}"

