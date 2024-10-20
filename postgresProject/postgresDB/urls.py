from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('dashboard', views.dashboard, name='dashboard'),    
    # path('error', views.error, name='error'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
]