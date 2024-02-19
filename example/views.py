from collections import defaultdict
import json

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from urllib.parse import urlparse
from .models import Pegawai, SubVariabel, Skor, Variabel
from .utils import get_skor


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
        data = defaultdict(lambda: defaultdict(dict))
        pegawais = Pegawai.objects.all()

        variabel = Variabel.objects.all()

        nama = None
        for pegawai in pegawais:
            skors.append(Skor.objects.filter(pegawai=pegawai).select_related('sub_variabel'))
        # print(skors)
        for x in range(len(pegawais)):
            # print(pegawais[x].nama)
            for angka in skors[x]:
                selisih = angka.skor - angka.sub_variabel.standar
                normal = 6 - abs(selisih) * 0.5
                if selisih < 0:
                    normal -= 0.5
                try:
                    data[f'{angka.pegawai.nama}'][f'{angka.sub_variabel.variabel.nama}'][
                        f'{angka.sub_variabel.faktor}'].append(normal)
                except KeyError:
                    data[f'{angka.pegawai.nama}'][f'{angka.sub_variabel.variabel.nama}'][
                        f'{angka.sub_variabel.faktor}'] = [normal]

        portion = [var.persentase for var in variabel]

        res = []
        for key, value in data.items():
            res.append(get_skor(value, portion))

        data = dict()
        for i in range(len(pegawais)):
            data[pegawais[i].nama] = res[i]
        return render(request, "example/skor.html", {'data': data})
