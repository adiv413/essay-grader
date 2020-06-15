from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("create", views.create, name="create"),
    path("setup", views.setup, name="setup"),
    path("home", views.index, name="home"),
    path("<int:pk>/", views.detail, name="detail"),
    path("submit", views.submit, name="submit"),
    path("dark_mode/", views.dark, name="dark_mode"),
    path('ajax/load-assignments/', views.load_assignments, name='ajax_load_assignments'),
    path('ajax/load-essay/', views.load_essay, name="ajax_load_essay"),
    path('ajax/validate/', views.validate_due_date, name="ajax_validate"),
    path('ajax/User/email', views.validate_user_email, name="ajax_user_email"),
    path('ajax/User/password', views.validate_user_password, name="ajax_user_password"),
    path('teacher/ajax/comment/', views.comment, name="ajax_comment"),
    path("teacher/home", views.teacher, name="teacher"),
    path("teacher/assignment", views.assignment, name="assignment"),
    path("teacher/<int:pk>/graded", views.teacher_graded, name="teacher_graded"),
    path("teacher/<int:pk>/not_graded", views.teacher_not_graded, name="teacher_not_graded"),
    path("teacher/<int:pk>/grade", views.grade, name="grade"),
    path("teacher/<int:pk>/grade_essay", views.grade_essay, name="grade_essay"),
    path("settings/info", views.settings_changeInfo, name="settings_info"),
    path("settings/password", views.settings_changePassword, name="settings_password"),
    path("settings/teachers", views.settings_changeTeachers, name="settings_teachers"),
]
