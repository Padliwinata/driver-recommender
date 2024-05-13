from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', index, name='index'),
    # path('login', login, name='login'),
    path('main', main, name='main'),
    path('skor', skor, name='skor'),
    path('skor/<str:id_pegawai>', detail_skor, name='detail-skor'),
    path('variabel', variabel, name='variabel'),
    path('create-variabel', create_variabel, name='create-variabel'),
    path('update-variabel', update_variabel, name='update-variabel'),
    path('act-update-variabel/<str:var_name>', actual_update_variabel, name='actual-update-variabel'),
    path('delete-variabel/<str:var_name>', delete_variabel, name='delete-variabel'),
    path('delete-subvariabel/<str:kode>', delete_subvariabel, name='delete-subvariabel'),
    path('subvariabel', subvariabel, name='subvariabel'),
    path('create-subvariabel', create_subvariabel, name='create-subvariabel'),
    path('update-subvariabel', update_subvariabel, name='update-subvariabel'),
    path('act-update-subvariabel/<str:kode>', actual_update_subvariabel, name='actual-update-subvariabel'),
    path('employee', employee, name='employee'),
    path('create-employee', create_employee, name='create-employee'),
    path('update-employee', update_employee, name='update-employee'),
    path('act-update-employee/<str:id_pegawai>', actual_update_employee, name='actual-update-employee'),
    path('delete-employee/<str:id_pegawai>', delete_employee, name='delete-employee'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    # path('login', auth_views.LoginView.as_view(template_name='example/login.html'), name='login'),
    path('login', login_view, name='login'),
    path('add-user', add_user, name='add-user')
]
