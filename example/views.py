from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from urllib.parse import urlparse
from .models import Pegawai, SubVariabel


# Create your views here.
def index(request):
    return render(request, "example/index.html")


def login(request):
    if request.method == "GET":
        return render(request, "example/login.html")
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        if username == password == "admin":
            return redirect("main")


def main(request):
    refferer_page = request.META.get("HTTP_REFERER", "")
    referrer_path = urlparse(refferer_page).path

    if referrer_path != "/example/login":
        return HttpResponseForbidden("Access Forbidden")

    pegawai_list = Pegawai.objects.all()
    subvar_list = SubVariabel.objects.all()

    return render(request, "example/main.html", {'pegawai_list': pegawai_list, 'subvar_list': subvar_list})
