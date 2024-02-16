from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from urllib.parse import urlparse
from .models import Pegawai, SubVariabel, Skor


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
    if request.method == "GET":
        referer_page = request.META.get("HTTP_REFERER", "")
        referrer_path = urlparse(referer_page).path

        if referrer_path != "/example/login" and referrer_path != "/example/main":
            return HttpResponseForbidden("Access Forbidden")

        pegawai_list = Pegawai.objects.all()
        subvar_list = SubVariabel.objects.all()

        return render(request, "example/main.html", {'pegawai_list': pegawai_list, 'subvar_list': subvar_list})
    if request.method == "POST":
        pegawai = Pegawai.objects.get(pk=request.POST.get('pegawai', ''))
        subvars = SubVariabel.objects.all()
        values = request.POST.getlist('subvar[]')
        for i in range(len(values)):
            Skor.objects.update_or_create(pegawai=pegawai, sub_variabel=subvars[i], skor=values[i])
        return redirect("main")


def skor(request):
    if request.method == "GET":
        skors = []
        selisih = []
        pegawais = Pegawai.objects.all()
        for pegawai in pegawais:
            skors.append(Skor.objects.filter(pegawai=pegawai).select_related('sub_variabel'))
        for x in range(len(pegawais)):
            print(pegawais[x].nama)
            temp = []
            for angka in skors[x]:
                print(f"{angka.skor}: {angka.sub_variabel.standar}")
                temp.append(angka.skor - angka.sub_variabel.standar)
            selisih.append(temp)
        print(selisih)
        hasil = []
        for pegawai in selisih:
            temp = []
            for angka in pegawai:
                if angka == 0:
                    temp.append(6)
                elif angka == 1:
                    temp.append(5.5)
                elif angka == -1:
                    temp.append(5)
                else:
                    temp.append(4)
            hasil.append(temp)
        print(hasil)
        resp = dict()
        for i in range(len(pegawais)):
            resp.update({pegawais[i].nama: hasil[i]})
        print(resp)
        return render(request, "example/skor.html", context=resp)
