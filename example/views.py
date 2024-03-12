from collections import defaultdict
import json

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from urllib.parse import urlparse

from .models import Pegawai, SubVariabel, Skor, Variabel
from .utils import get_skor


# Create your views here.
def index(request):
    return render(request, "example/index.html")


# def mapping(request):
#     if request.method == "GET":
#         return render(request, "example/login.html")
#     if request.method == "POST":
#         username = request.POST.get("username", "")
#         password = request.POST.get("password", "")
#
#         if username == password == "admin":
#             return redirect("main")


@login_required
def main(request):
    if request.method == "GET":
        # referer_page = request.META.get("HTTP_REFERER", "")
        # referrer_path = urlparse(referer_page).path
        #
        # if referrer_path != "/example/login" and referrer_path != "/example/main":
        #     return HttpResponseForbidden("Access Forbidden")

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


@login_required
def skor(request):
    if request.method == "GET":
        skors = []
        data = defaultdict(lambda: defaultdict(dict))
        pegawais = Pegawai.objects.all()
        variabel = Variabel.objects.all()
        subvars = SubVariabel.objects.all()

        skors = []
        for pegawai in pegawais:
            skor = Skor.objects.filter(pegawai=pegawai).select_related('sub_variabel')
            skors.append(skor)

        # return render(request, 'example/skor.html', {'length': length, 'data': []})
        # else:
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
            data[pegawais[i].id_pegawai] = res[i]

        sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

        return render(request, "example/skor.html", {'length': len(sorted_data), 'data': sorted_data})


@login_required
def variabel(request):
    if request.method == 'GET':
        variabel_list = Variabel.objects.all()
        return render(request, 'example/variabel.html', {'data': variabel_list})


@login_required
def subvariabel(request):
    if request.method == 'GET':
        subvariabel_list = SubVariabel.objects.all()
        return render(request, 'example/subvariabel.html', {'data': subvariabel_list})


@login_required
def employee(request):
    if request.method == 'GET':
        employee_list = Pegawai.objects.all()
        return render(request, 'example/employee.html', {'data': employee_list})


@login_required
def create_variabel(request):
    if request.method == 'GET':
        return render(request, 'example/add_variabel.html')
    if request.method == 'POST':
        nama = request.POST.get('nama')
        faktor = request.POST.get('faktor')
        persentase = request.POST.get('persentase')

        record = Variabel.objects.filter(nama=nama)

        if record:
            data = record.first()
            data.faktor = faktor
            data.persentase = persentase
            data.save()
            return redirect('update-variabel')
        else:
            Variabel.objects.update_or_create(nama=nama, faktor=faktor, persentase=persentase)
            return redirect('variabel')


@login_required
def create_subvariabel(request):
    if request.method == 'GET':
        variabels = Variabel.objects.all()
        return render(request, 'example/add_subvariabel.html', {'variabels': variabels})
    if request.method == 'POST':
        kode = request.POST.get('kode')
        variabel = request.POST.get('variabel')
        nama = request.POST.get('nama')
        faktor = request.POST.get('faktor')
        standar = request.POST.get('standar')

        variabel_sub = Variabel.objects.filter(nama=variabel)
        variabel_sub = variabel_sub[0]

        record = SubVariabel.objects.filter(kode=kode)

        if record:
            data = record.first()
            data.variabel = variabel_sub
            data.nama = nama
            data.faktor = faktor
            data.standar = standar
            data.save()
            return redirect('update-subvariabel')
        else:
            SubVariabel.objects.update_or_create(kode=kode, variabel=variabel_sub, nama=nama, faktor=faktor,
                                                 standar=standar)
            return redirect('subvariabel')


@login_required
def create_employee(request):
    if request.method == 'GET':
        return render(request, 'example/add_employee.html')
    if request.method == 'POST':
        id_pegawai = request.POST.get('id_pegawai')
        nama = request.POST.get('nama')

        record = Pegawai.objects.filter(id_pegawai=id_pegawai)

        if record:
            data = record.first()
            data.nama = nama
            data.save()
            return redirect('update-employee')
        else:
            Pegawai.objects.update_or_create(id_pegawai=id_pegawai, nama=nama)
            return redirect('employee')


@login_required
def delete_variabel(request, var_name):
    if request.method == 'GET':
        record = get_object_or_404(Variabel, nama=var_name)
        record.delete()

        return redirect('variabel')


@login_required
def delete_subvariabel(request, kode):
    if request.method == 'GET':
        record = get_object_or_404(SubVariabel, kode=kode)
        record.delete()

        return redirect('subvariabel')


@login_required
def delete_employee(request, id_pegawai):
    if request.method == 'GET':
        record = get_object_or_404(Pegawai, id_pegawai=id_pegawai)
        record.delete()

        return redirect('employee')


@login_required
def update_variabel(request):
    if request.method == 'GET':
        variabel_list = Variabel.objects.all()
        return render(request, 'example/update_variabel.html', {'data': variabel_list})


@login_required
def actual_update_variabel(request, var_name):
    if request.method == 'GET':
        record = Variabel.objects.filter(nama=var_name)
        return render(request, 'example/add_variabel.html', {'data': record[0]})


@login_required
def update_subvariabel(request):
    if request.method == 'GET':
        subvariabel_list = SubVariabel.objects.all()
        variabel_list = Variabel.objects.all()
        return render(request, 'example/update_subvariabel.html',
                      {'data': subvariabel_list, 'variabels': variabel_list})


@login_required
def actual_update_subvariabel(request, kode):
    if request.method == 'GET':
        record = SubVariabel.objects.filter(kode=kode)
        variabel_list = Variabel.objects.all()
        return render(request, 'example/add_subvariabel.html', {'data': record[0], 'variabels': variabel_list})


@login_required
def update_employee(request):
    if request.method == 'GET':
        employee_list = Pegawai.objects.all()
        return render(request, 'example/update_employee.html', {'data': employee_list})


@login_required
def actual_update_employee(request, id_pegawai):
    if request.method == 'GET':
        record = Pegawai.objects.filter(id_pegawai=id_pegawai)
        return render(request, 'example/add_employee.html', {'data': record[0]})
