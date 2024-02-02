from django.urls import path
from .views import index, main, login


urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('main', main, name='main')
]
