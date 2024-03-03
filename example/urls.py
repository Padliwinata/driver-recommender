from django.urls import path
from .views import index, main, login, skor, variabel

urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('main', main, name='main'),
    path('skor', skor, name='skor'),
    path('variabel', variabel, name='variabel')
]
