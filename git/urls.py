from django.urls import path

from git import views

urlpatterns = [
    path('get_commits/', views.get_commits, name='get_commits'),
    path('validate_repository/', views.validate_repository, name='validate_repository'),
    path('test/', views.test, name='test'),
]

