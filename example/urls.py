from django.urls import path
from django.contrib.auth import views as auth_views
from .views import index, main, skor, variabel, create_variabel, delete_variabel, subvariabel, \
    delete_subvariabel, create_subvariabel, employee, create_employee, delete_employee

urlpatterns = [
    path('', index, name='index'),
    # path('login', login, name='login'),
    path('main', main, name='main'),
    path('skor', skor, name='skor'),
    path('variabel', variabel, name='variabel'),
    path('create-variabel', create_variabel, name='create-variabel'),
    path('delete-variabel/<str:var_name>', delete_variabel, name='delete-variabel'),
    path('delete-subvariabel/<str:kode>', delete_subvariabel, name='delete-subvariabel'),
    path('subvariabel', subvariabel, name='subvariabel'),
    path('create-subvariabel', create_subvariabel, name='create-subvariabel'),
    path('employee', employee, name='employee'),
    path('create-employee', create_employee, name='create-employee'),
    path('delete-employee/<str:id_pegawai>', delete_employee, name='delete-employee'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('login', auth_views.LoginView.as_view(template_name='example/login.html'), name='login')
]
