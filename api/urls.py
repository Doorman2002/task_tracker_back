from django.urls import path
from . import views

urlpatterns = [
    path("signup/",views.Signup.as_view(),name="signup"),
    path("login/",views.Login.as_view(), name="login"),
    path("task/",views.Task.as_view(),name="task"),
    path("admin/",views.Admin.as_view(),name="Admin"),
    path("admin/login/",views.AdminLogin.as_view(),name="admin_login"),
    path("admin/dashboard/",views.AdminDashboard.as_view(),name="admin_dashboard"),
    path("name/",views.Name.as_view(),name="name"),
    path("history/",views.History.as_view(),name="history"),
    path("director/task/",views.DirectorTaskView.as_view(),name="director_task"),
    path("director/history/",views.DirectorHistoryView.as_view(),name="director_history"),
    path("director/tasks/",views.AllStaffTasksView.as_view(),name="all_staff_tasks")

    
]
