from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from .models import Staff, Task as TaskModel, Admin, DirectorsTask
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
          unique_id=str(uuid4())[:8]
          email=info.get("email")
          staff=Staff.objects.filter(Email=email).first()
          if staff:
              return Response({"info":"User exists"},status=status.HTTP_302_FOUND)
              
          role = info.get('role', 'staff')
          staff=Staff.objects.create(
              Name=info.get('name'),
              Email=info.get('email'),
              dpt=info.get('dept'),
              Unique_id=unique_id,
              role=role
              
          )
        
        
          return Response({
              "info":"Successful Signup",
              "unique_id": unique_id,
              "role": role
          },status=status.HTTP_201_CREATED)
        else:
            return Response({"info":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            
        
class Login(APIView):
 
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            info=serializer.validated_data
            name=info["name"]
            
            unique_id=info["unique_id"].lower()
            staff=Staff.objects.filter(Name=name).first()
            if not staff:
                return Response({"info":"No staff Available"},status=status.HTTP_200_OK)
            else:
                if staff.Unique_id.lower() == unique_id:
                    token=secrets.token_hex(32)
                    staff.token=token
                    staff.save()
                    response= Response({
                        "info":"Login successful",
                        "role": staff.role
                    },status=status.HTTP_200_OK)
                    response.set_cookie(
                        key="refresh_cookie",
                        value=token,
                        max_age=60*60*24,
                        samesite=None,
                        httponly=False,
                        secure=False
                    )
                  
                    return response
                else:
                    return Response({"info":"Your Unique id is wrong"},status=status.HTTP_404_NOT_FOUND)
                
        else:
            return Response({"info":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        
        
class Name(APIView):
    def get(self,request):
        
        staff=Staff.objects.all()
        print(staff)
        names=[]
        for s in staff:
            staff_name=s.Name
            names.append(staff_name)
        return Response({"info":names},status=status.HTTP_200_OK)  
    
      
class History(APIView):
      def get(self,request):
        cookie=request.COOKIES.get("refresh_cookie")
        # print(cookie)
        
        
        if not cookie:
            return Response({"info":"Unable to Authenticate"},status=status.HTTP_400_BAD_REQUEST)
        
        # cookie=cookie.lower()
        # print(cookie)
        staff=Staff.objects.filter(token=cookie).first()
        if not staff:
            return Response({"info":"Unable to get staff"},status=status.HTTP_404_NOT_FOUND)
        
        # print(cookie)
        task=TaskModel.objects.filter(staff=staff)
        
        serializer=TaskSerializer(task,many=True)
        print(serializer.data)
        return Response({"info":serializer.data, "staff_name": staff.Name},status=status.HTTP_200_OK)
    
        
class Task(APIView):
    
    # def get(self,request):
    #     tasks=Task.objects.select_related('staff').all()
    #     data=[]
    #     for t in tasks:
    #         data.append({
    #             "id":t.id,
    #             "staff_name":t.staff.Name if t.staff else None,
    #             "task":t.task,
    #             "date":t.date,
    #         })
    #     return Response(data,status=status.HTTP_200_OK)
    def post(self, request):
        cookie = request.COOKIES.get("refresh_cookie")
        if not cookie:
            return Response({"info": "Unable to get cookie"}, status=status.HTTP_400_BAD_REQUEST)

        staff = Staff.objects.filter(token=cookie).first()
        if not staff:
            return Response({"info": "Invalid or missing token"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(staff=staff)  
            return Response({"info": "Task Added successfully"}, status=status.HTTP_201_CREATED)
        
        return Response({"info": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DirectorTaskView(APIView):
    def post(self, request):
        cookie = request.COOKIES.get("refresh_cookie")
        if not cookie:
            return Response({"info": "Unable to get cookie"}, status=status.HTTP_400_BAD_REQUEST)
        staff = Staff.objects.filter(token=cookie).first()
        if not staff:
            return Response({"info": "Invalid or missing token"}, status=status.HTTP_401_UNAUTHORIZED)
        if staff.role != 'director':
            return Response({"info": "Access denied. Director only."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            DirectorsTask.objects.create(
                staff=staff,
                task=serializer.validated_data.get('task'),
                status=serializer.validated_data.get('status', 'In progress')
            )
            return Response({"info": "Director task added successfully"}, status=status.HTTP_201_CREATED)
        return Response({"info": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DirectorHistoryView(APIView):
    def get(self, request):
        cookie = request.COOKIES.get("refresh_cookie")
        if not cookie:
            return Response({"info": "Unable to Authenticate"}, status=status.HTTP_400_BAD_REQUEST)
        staff = Staff.objects.filter(token=cookie).first()
        if not staff:
            return Response({"info": "Unable to get staff"}, status=status.HTTP_404_NOT_FOUND)
        if staff.role != 'director':
            return Response({"info": "Access denied. Director only."}, status=status.HTTP_403_FORBIDDEN)
        tasks = DirectorsTask.objects.filter(staff=staff)
        serializer = DirectorsTaskSerializer(tasks, many=True)
        return Response({"info": serializer.data}, status=status.HTTP_200_OK)

class AllStaffTasksView(APIView):
    def get(self, request):
        cookie = request.COOKIES.get("refresh_cookie")
        if not cookie:
            return Response({"info": "Unable to Authenticate"}, status=status.HTTP_400_BAD_REQUEST)
        staff = Staff.objects.filter(token=cookie).first()
        if not staff:
            return Response({"info": "Unable to get staff"}, status=status.HTTP_404_NOT_FOUND)
        if staff.role != 'director':
            return Response({"info": "Access denied. Director only."}, status=status.HTTP_403_FORBIDDEN)
        all_tasks = TaskModel.objects.select_related('staff').all().order_by('-date')
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
                admin.token=token
                admin.save()
                response=Response({"info":"Admin login successful"},status=status.HTTP_200_OK)
                response.set_cookie(
                    key="admin_cookie",
                    value=token,
                    max_age=60*60*24*7,
                    samesite=None,
                    httponly=False,
                    secure=False
                )
                return response
            return Response({"info":"Invalid credentials"},status=status.HTTP_401_UNAUTHORIZED)
        return Response({"info":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


class AdminDashboard(APIView):

    def get(self,request):
        cookie=request.COOKIES.get("admin_cookie")
        if not cookie:
            return Response({"info":"Authentication required"},status=status.HTTP_401_UNAUTHORIZED)
        admin=Admin.objects.filter(token=cookie).first()
        if not admin:
            return Response({"info":"Invalid admin session"},status=status.HTTP_401_UNAUTHORIZED)

        total_staff=Staff.objects.count()
        total_tasks=TaskModel.objects.count()
        staff_list=StaffSerializer(Staff.objects.all(),many=True).data
        tasks_by_status=TaskModel.objects.values("status").annotate(count=Count("id"))
        staff_task_counts=Staff.objects.annotate(task_count=Count("task")).values("Name","task_count")

        return Response({
            "admin":admin.Name,
            "total_staff":total_staff,
            "total_tasks":total_tasks,
            "tasks_by_status":list(tasks_by_status),
            "staff_task_counts":list(staff_task_counts),
            "staff_list":staff_list
        },status=status.HTTP_200_OK)


class Admin(APIView):

    def _check_auth(self,request):
        cookie=request.COOKIES.get("admin_cookie")
        if not cookie:
            return None
        return Admin.objects.filter(token=cookie).first()
    
    def get(self,request):
        if not self._check_auth(request):
            return Response({"info":"Authentication required"},status=status.HTTP_401_UNAUTHORIZED)
        staff=Staff.objects.all()
        serializer=StaffSerializer(staff,many=True)
        return Response({"info":serializer.data},status=status.HTTP_200_OK)
    
    def post(self,request):
        if not self._check_auth(request):
            return Response({"info":"Authentication required"},status=status.HTTP_401_UNAUTHORIZED)
        serializer=StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"info":"Staff created"},status=status.HTTP_201_CREATED)
        return Response({"info":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request):
        if not self._check_auth(request):
            return Response({"info":"Authentication required"},status=status.HTTP_401_UNAUTHORIZED)
        unique_id=request.data.get('unique_id')
        if not unique_id:
            return Response({"info":"unique_id required"},status=status.HTTP_400_BAD_REQUEST)
        staff=Staff.objects.filter(Unique_id=unique_id).first()
        if not staff:
            return Response({"info":"Staff not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=StaffSerializer(staff,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"info":"Staff updated"},status=status.HTTP_200_OK)
        return Response({"info":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        if not self._check_auth(request):
            return Response({"info":"Authentication required"},status=status.HTTP_401_UNAUTHORIZED)
        unique_id=request.data.get('unique_id')
        if not unique_id:
            return Response({"info":"unique_id required"},status=status.HTTP_400_BAD_REQUEST)
        staff=Staff.objects.filter(Unique_id=unique_id).first()
        if not staff:
            return Response({"info":"Staff not found"},status=status.HTTP_404_NOT_FOUND)
        staff.delete()
        return Response({"info":"Staff deleted"},status=status.HTTP_200_OK)





