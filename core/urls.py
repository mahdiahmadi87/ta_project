from django.urls import path
from . import views

urlpatterns = [
    # User-facing pages
    path('', views.home, name='home'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    
    # API endpoints
    path('api/topic/<int:topic_id>/submit/', views.submit_drawing, name='submit_drawing'),
    
    # Admin pages
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/group/<int:group_id>/', views.group_detail_admin, name='group_detail_admin'),
    path('dashboard/create-user/', views.create_user, name='create_user'),
    path('dashboard/create-group/', views.create_group, name='create_group'),
    path('dashboard/create-topic/', views.create_topic, name='create_topic'),
]