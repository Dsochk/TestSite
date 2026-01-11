from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('admin_panel/', views.admin_dashboard, name='dashboard'),
    path('admin_panel/diagnostics/', views.diagnostics, name='diagnostics'),
]

