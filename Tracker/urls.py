from django.contrib import admin
from django.urls import path, include
from api.views import admin_dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('api/', include('api.urls')),
]
