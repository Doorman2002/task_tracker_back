from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password,make_password
from .models import Staff, Task as TaskModel, Admin, DirectorsTask
from django.utils import timezone
from datetime import datetime, timedelta
from .serializer import (
    SignupSerializer, StaffSerializer, LoginSerializer, TaskSerializer,
    AdminSerializer, AdminLoginSerializer, DirectorsTaskSerializer
)
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from uuid import uuid4
import secrets



class Signup(APIView):

    def post(self,request):
        serializer=SignupSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
          info=serializer.validated_data
        
          email=info.get("email")
          password=info.get("password")
          role = info.get('role')
          staff=Staff.objects.filter(Email=email).first()
          if staff:
              return Response({"info":"User exists"},status=status.HTTP_302_FOUND)
              
        #   role = info.get('role')
          staff=Staff.objects.create(
              Name=info.get('name'),
              Email=info.get('email'),
              dpt=info.get('dept'),
              password=make_password(password),
              role=role
              
          )
        
        
          return Response({"info":"Successful Signup","status":"You can navigate to the login page"},status=status.HTTP_201_CREATED)
        else:
            return Response({"info":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            
            
            
        
class Login(APIView):
    
    
    def get(self,request):
        #  get all the email with this company
        staff=Staff.objects.all()
        # unable to the staff
        if not staff:
            return Response({"info":"Unable to get the staffs"},status=status.HTTP_404_NOT_FOUND)
        
        staff_email=[]
        for i in staff:
            staff_email.append(i.Email)
        return Response({"info":staff_email},status=status.HTTP_200_OK)
        
        
        
 
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"info":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        info=serializer.validated_data
        email=info.get("email")
        password=info.get("password")
        staff=Staff.objects.filter(Email=email).first()
        if not staff:
            return Response({"info":"Staff not found"},status=status.HTTP_404_NOT_FOUND)
        if not check_password(password,staff.password):
            return Response({"info":"Password Unable to be Authenticated"},status=status.HTTP_401_UNAUTHORIZED)
        auth_token=secrets.token_hex(32)
        refresh=secrets.token_hex(64)
        staff.auth=auth_token
        staff.refresh=refresh
        staff.auth_created_at=timezone.now()
        staff.auth_expire_at=timezone.now()+timedelta(minutes=10)
        staff.refresh_created_at=timezone.now()
        staff.refresh_expire_at=timezone.now()+timedelta(hours=2)
        staff.save()
        response=Response({"info":"User Authenticated","role":staff.role,"dpt":staff.dpt},headers={"Authorization":auth_token},status=status.HTTP_201_CREATED)
        response.set_cookie(
            key="refresh_cookie",
            value=refresh,
            httponly=True,
            samesite='None',
            secure=False,)
        return response

        

    
      
class History(APIView):
    def get(self,request):
        auth=request.headers.get("Authorization")
        cookie=request.COOKIES.get("refresh_cookie")
        if not auth:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        auth_db=Staff.objects.filter(auth=auth).first()
        if not auth_db:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        if auth_db.expire_auth():
            if not cookie:
                return Response({"info":"Unable to get cookie"},status=status.HTTP_400_BAD_REQUEST)
            refresh_token=Staff.objects.filter(refresh=cookie).first()
            if not refresh_token:
                return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
            if refresh_token.expire_refresh():
                return Response({"info":"Login Cookie expired, Login again"},status=status.HTTP_400_BAD_REQUEST)
            staff=refresh_token
        else:
            staff=auth_db.staff
        task=TaskModel.objects.filter(staff=staff)
        serializer=TaskSerializer(task,many=True)
        return Response({"info":serializer.data, "staff_name": staff.Name},status=status.HTTP_200_OK)

            
class Task(APIView):
    

    def post(self, request):
        serializer=TaskSerializer(data=request.data)
        auth=request.headers.get("Authorization")
        cookie=request.COOKIES.get("refresh_cookie")
        if not auth:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        auth_db=Staff.objects.filter(auth=auth).first()
        if not auth_db:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        if auth_db.expire_auth():
            if not cookie:
                return Response({"info":"Unable to get cookie"},status=status.HTTP_400_BAD_REQUEST)
            refresh_token=Staff.objects.filter(refresh=cookie).first()
            if not refresh_token:
                return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
            if refresh_token.expire_refresh():
                return Response({"info":"Login Cookie expired, Login again"},status=status.HTTP_400_BAD_REQUEST)
            staff=refresh_token
        else:
            staff=auth_db
        if serializer.is_valid():
            serializer.save(staff=staff)
            return Response({"info": "Task Added successfully"}, status=status.HTTP_201_CREATED)
        return Response({"info": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DirectorTaskView(APIView):
    def post(self, request):
        serializer=DirectorsTaskSerializer(data=request.data)
        auth=request.headers.get("Authorization")
        cookie=request.COOKIES.get("refresh_cookie")
        if not auth:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        auth_db=Staff.objects.filter(auth=auth).first()
        if not auth_db:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        if auth_db.expire_auth():
            if not cookie:
                return Response({"info":"Unable to get cookie"},status=status.HTTP_400_BAD_REQUEST)
            refresh_token=Staff.objects.filter(refresh=cookie).first()
            if not refresh_token:
                return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
            if refresh_token.expire_refresh():
                return Response({"info":"Login Cookie expired, Login again"},status=status.HTTP_400_BAD_REQUEST)
            staff=refresh_token
        else:
            staff=auth_db
        if not serializer.is_valid():
            return Response({"info": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        DirectorsTask.objects.create(
            staff=staff,
            task=serializer.validated_data.get('task'),
            status=serializer.validated_data.get('status', 'In progress')
        )
        return Response({"info": "Director task added successfully"}, status=status.HTTP_201_CREATED)

class DirectorHistoryView(APIView):
    def get(self, request):
        auth=request.headers.get("Authorization")
        cookie=request.COOKIES.get("refresh_cookie")
        if not auth:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        auth_db=Staff.objects.filter(auth=auth).first()
        if not auth_db:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        if auth_db.expire_auth():
            if not cookie:
                return Response({"info":"Unable to get cookie"},status=status.HTTP_400_BAD_REQUEST)
            refresh_token=Staff.objects.filter(refresh=cookie).first()
            if not refresh_token:
                return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
            if refresh_token.expire_refresh():
                return Response({"info":"Login Cookie expired, Login again"},status=status.HTTP_400_BAD_REQUEST)
            director=refresh_token
        else:
            director=auth_db
        if director.role == 'director':
            serializer = DirectorsTaskSerializer(director.director_tasks.all(), many=True)
            return Response({"info": serializer.data}, status=status.HTTP_200_OK)
        return Response({"info":"Access denied"}, status=status.HTTP_403_FORBIDDEN)

class AllStaffTasksView(APIView):
    def get(self, request):
        auth=request.headers.get("Authorization")
        cookie=request.COOKIES.get("refresh_cookie")
        if not auth:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        auth_db=Staff.objects.filter(auth=auth).first()
        if not auth_db:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        if auth_db.expire_auth():
            if not cookie:
                return Response({"info":"Unable to get cookie"},status=status.HTTP_400_BAD_REQUEST)
            refresh_token=Staff.objects.filter(refresh=cookie).first()
            if not refresh_token:
                return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
            if refresh_token.expire_refresh():
                return Response({"info":"Login Cookie expired, Login again"},status=status.HTTP_400_BAD_REQUEST)
            staff=refresh_token
        else:
            staff=auth_db
        if staff.role != 'director':
            return Response({"info": "Access denied. Director only."}, status=status.HTTP_403_FORBIDDEN)
        all_tasks = TaskModel.objects.select_related('staff').all()
        data = []
        for t in all_tasks:
            data.append({
                "id": t.id,
                "staff_name": t.staff.Name if t.staff else "Unknown",
                "staff_dpt": t.staff.dpt if t.staff else "Unknown",
                "task": t.task,
                "date": t.date,
                "status": t.status,
            })
        return Response({"info": data}, status=status.HTTP_200_OK)


    
 
                    
                
        
        
class AdminLogin(APIView):

    def post(self,request):
        serializer=AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            info=serializer.validated_data
            email=info.get("email")
            password=info.get("password")
            admin=Admin.objects.filter(Email=email).first()
            if not admin:
                return Response({"info":"No admin found"},status=status.HTTP_404_NOT_FOUND)
            if check_password(password, admin.password):
                token=secrets.token_hex(32)
                admin.auth=token
                admin.save()
                return Response({"info":"Admin login successful"},headers={"Authorization":token},status=status.HTTP_200_OK)
            return Response({"info":"Invalid credentials"},status=status.HTTP_401_UNAUTHORIZED)
        return Response({"info":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


class AdminDashboard(APIView):

    def get(self,request):
        auth=request.headers.get("Authorization")
        if not auth:
            return Response({"info":"Authentication required"},status=status.HTTP_401_UNAUTHORIZED)
        admin=Admin.objects.filter(auth=auth).first()
        if not admin:
            return Response({"info":"Invalid admin session"},status=status.HTTP_401_UNAUTHORIZED)
        
        dir_staff=[]
        normal_staff=[]
        staffs=Staff.objects.all()
        for i in staffs:
            if i.role=="director":
                dir_tasks=i.director_tasks.all()
                dir_staff.append({
                    "dir_count":dir_tasks.count(),
                    "dir":i.Name,
                    "tasks":[t.task for t in dir_tasks],
                    "status":[t.status for t in dir_tasks]
                })
            else:
                staff_tasks=i.task.all()
                normal_staff.append({
                    "staff_count":staff_tasks.count(),
                    "staff_name":i.Name,
                    "staff_tasks":[t.task for t in staff_tasks],
                    "status":[t.status for t in staff_tasks]
                })
                
                
            
        total_staff=Staff.objects.count()
        dir_staffs=dir_staff
        other_staff=normal_staff
        
        total_tasks=TaskModel.objects.count()
        staff_list=StaffSerializer(Staff.objects.all(),many=True).data
        tasks_by_status=TaskModel.objects.values("status").annotate(count=Count("id"))
        staff_task_counts=Staff.objects.annotate(task_count=Count("task")).values("Name","task_count")

        return Response({
            "admin":admin.Name,
            "dir_staffs":dir_staffs,
            "other_staff":other_staff,
            "total_staff":total_staff,
            "total_tasks":total_tasks,
            "tasks_by_status":list(tasks_by_status),
            "staff_task_counts":list(staff_task_counts),
            "staff_list":staff_list
        },status=status.HTTP_200_OK)

