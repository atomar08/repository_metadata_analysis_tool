from django.urls import path

from git import views

urlpatterns = [
    path('validate_repository/', views.validate_repository, name='validate_repository'),
    path('get_commits/', views.get_commits, name='get_commits'),
    path('get_commits_page/', views.get_commits_page, name='get_commits_page'),
    path('read_commits_page/', views.read_commits_page, name='read_commits_page'),
    path('get_commits_id/', views.get_commits_id, name='get_commits_id'),
    path('get_repo_issues/', views.get_repo_issues, name='get_repo_issues'),
    path('test/', views.test, name='test'),
]

