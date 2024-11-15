from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('dashboard', views.dashboard, name='dashboard'),    
    # path('error', views.error, name='error'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('update_categories', views.update_categories, name='update_categories'),
    path('summary', views.summary, name = 'summary'),
    path('summary_build/', views.summary_execute, name = 'summary_execute')
]