from django.urls import path
from . import views

urlpatterns = [
    #  the auth signup  and login
    path("auth/signup/",views.Signup.as_view(),name="signup"),
    path("auth/login/",views.Login.as_view(), name="login"),
    # get the email of the whole staffs
    path("auth/login/emails/",views.Login.as_view(), name="login_emails"),
    
    path("task/",views.Task.as_view(),name="task"),
    path("history/",views.History.as_view(),name="history"),
        
    path("director/task/",views.DirectorTaskView.as_view(),name="director_task"),
    path("director/history/",views.DirectorHistoryView.as_view(),name="director_history"),
    path("director/tasks/",views.AllStaffTasksView.as_view(),name="all_staff_tasks"),

    path("admin/login/",views.AdminLogin.as_view(),name="admin_login"),
    path("admin/dashboard/",views.AdminDashboard.as_view(),name="admin_dashboard"),
    
]
