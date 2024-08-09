from collections import defaultdict
import json

from django.http import HttpResponseBadRequest
from django.db.models import Exists, OuterRef
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from urllib.parse import urlparse

from .models import Pegawai, SubVariabel, Skor, Variabel
from .utils import get_skor


# Function to read data from JSON file
def read_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}


# Function to write data to JSON file
def write_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


# Function to append data to JSON file
def append_to_json(filename, username, password) -> bool:
    data = read_json(filename)
    if username not in data:
        data[username] = password
        write_json(data, filename)
        return True
    else:
        return False


# File name
file_name = "data.json"


# Create your views here.
def index(request):
    return render(request, "example/index.html")


@login_required
def main(request):
    if request.method == "GET":
        pegawai_list = Pegawai.objects.all()
        subvar_list = SubVariabel.objects.all()

        return render(request, "example/main.html", {'pegawai_list': pegawai_list, 'subvar_list': subvar_list})
    if request.method == "POST":
        pegawai = Pegawai.objects.get(pk=request.POST.get('pegawai', ''))
        subvars = SubVariabel.objects.all()

        values = request.POST.getlist('subvar[]')
        skors = Skor.objects.filter(pegawai=pegawai)
        if len(skors) != 0:
            for i in range(len(values)):
                # Skor.objects.update_or_create(pegawai=pegawai, sub_variabel=subvars[i], skor=values[i])
                skors[i].skor = values[i]
                skors[i].save()
        else:
            for i in range(len(values)):
                Skor.objects.update_or_create(pegawai=pegawai, sub_variabel=subvars[i], skor=values[i])

        return redirect("main")


@login_required
def skor(request):
    if request.method == "GET":
        class Data:
            def __init__(self, id_pegawai, nama, skor):
                self.id_pegawai = id_pegawai
                self.nama = nama
                self.skor = skor

        # Membuat variabel untuk menyimpan hasil akhir
        data = defaultdict(lambda: defaultdict(dict))

        # Ambil data semua pegawai dan semua variabel
        # pegawais = Pegawai.objects.all()
        variabel = Variabel.objects.all()
        pegawais = Pegawai.objects.filter(
            Exists(Skor.objects.filter(pegawai=OuterRef('pk')))
        )

        # Membuat variabel untuk menyimpan skor dari masing masing pegawai
        skors = []
        for pegawai in pegawais:
            # Ambil data pegawai
            skor = Skor.objects.filter(pegawai=pegawai).select_related('sub_variabel')

            # Lalu simpan di skors
            skors.append(skor)

        for x in range(len(pegawais)):
            # print(pegawais[x].nama)
            for angka in skors[x]:
                selisih = angka.skor - angka.sub_variabel.standar
                normal = 0
                if selisih == 0:
                    normal = 6
                elif selisih == -1:
                    normal = 5
                elif selisih == 1:
                    normal = 5.5
                elif selisih == -2:
                    normal = 4
                elif selisih == 2:
                    normal = 4.5
                elif selisih == -3:
                    normal = 3
                elif selisih == 3:
                    normal = 3.5
                elif selisih == -4:
                    normal = 2
                elif selisih == 4:
                    normal = 2.5

                try:
                    data[f'{angka.pegawai.id_pegawai}'][f'{angka.sub_variabel.variabel.nama}'][
                        f'{angka.sub_variabel.faktor}'].append(normal)
                except KeyError:
                    data[f'{angka.pegawai.id_pegawai}'][f'{angka.sub_variabel.variabel.nama}'][
                        f'{angka.sub_variabel.faktor}'] = [normal]

        # Ambil bobot porsi variabel
        portion = [var.persentase for var in variabel]

        # print(json.dumps(data, indent=4))

        # Membuat variabel wadah nilai akhir
        res = []
        for key, value in data.items():
            res.append(get_skor(value, portion))

        data = dict()
        for i in range(len(pegawais)):
            try:
                data[pegawais[i].nama] = res[i]
            except IndexError:
                pass

        baru = []
        for i in range(len(pegawais)):
            try:
                baru.append(Data(pegawais[i].id_pegawai, pegawais[i].nama, res[i]))
            except IndexError:
                pass

        # Sorting data hasil akhir
        sorted_data = sorted(baru, key=lambda item: item.skor, reverse=True)

        return render(request, "example/skor.html", {'length': len(sorted_data), 'data': sorted_data})


@login_required
def detail_skor(request, id_pegawai):
    if request.method == 'GET':
        data = defaultdict(dict)
        skor_pengelompokkan = defaultdict(dict)
        skor_per_variabel = defaultdict(dict)

        variabels = Variabel.objects.all()
        portion = [vari.persentase for vari in variabels]

        skor_pegawai = Skor.objects.filter(pegawai__id_pegawai=id_pegawai).select_related('sub_variabel')
        # sub_variabel = [skor.sub_variabel.kode for skor in skor_pegawai]

        # send
        skor_raw = {x.sub_variabel.kode: x.skor for x in skor_pegawai}

        for angka in skor_pegawai:
            selisih = angka.skor - angka.sub_variabel.standar
            normal = 0
            if selisih == 0:
                normal = 6
            elif selisih == -1:
                normal = 5
            elif selisih == 1:
                normal = 5.5
            elif selisih == -2:
                normal = 4
            elif selisih == 2:
                normal = 4.5
            elif selisih == -3:
                normal = 3
            elif selisih == 3:
                normal = 3.5
            elif selisih == -4:
                normal = 2
            elif selisih == 4:
                normal = 2.5

            try:
                data[f'{angka.sub_variabel.variabel.nama}'][
                    f'{angka.sub_variabel.faktor}'].append(normal)
            except KeyError:
                data[f'{angka.sub_variabel.variabel.nama}'][
                    f'{angka.sub_variabel.faktor}'] = [normal]

        # send
        skor_normalisasi = data

        for key, val in skor_normalisasi.items():
            for key_factor, val_factor in val.items():
                skor_pengelompokkan[key][key_factor] = sum(data[key][key_factor]) / len(data[key][key_factor])

        for key, val in skor_pengelompokkan.items():
            try:
                core = val['CORE']
            except KeyError:
                core = 0

            try:
                secondary = val['SECONDARY']
            except KeyError:
                secondary = 0
            skor_per_variabel[key] = 0.7 * core + 0.3 * secondary

        skor_per_variabel = dict(skor_per_variabel)
        res = []
        items = list(skor_per_variabel.items())
        for i in range(len(portion)):
            res.append(items[i][1] * (portion[i] / 100))

        for key, new_value in zip(skor_per_variabel.keys(), res):
            skor_per_variabel[key] = new_value
        # send
        skor_persentase = res

        return render(request, 'example/detail_skor.html',
                      {'skor_raw': skor_raw, 'skor_normalisasi': dict(skor_normalisasi),
                       'skor_pengelompokkan': dict(skor_pengelompokkan),
                       'skor_per_variabel': skor_per_variabel, 'skor_persentase': skor_persentase,
                       'skor_final': sum(skor_persentase)})


@login_required
def variabel(request):
    if request.method == 'GET':
        # Kalau ada ".objects.all()" berarti ambil data dari db
        try:
            message = request.session.pop('message')
        except KeyError:
            message = ''
        variabel_list = Variabel.objects.all()
        return render(request, 'example/variabel.html', {'data': variabel_list, 'message': message})


@login_required
def subvariabel(request):
    if request.method == 'GET':
        try:
            message = request.session.pop('message')
        except KeyError:
            message = ''
        subvariabel_list = SubVariabel.objects.all()
        return render(request, 'example/subvariabel.html', {'data': subvariabel_list, 'message': message})


@login_required
def employee(request):
    if request.method == 'GET':
        employee_list = Pegawai.objects.all()
        return render(request, 'example/employee.html', {'data': employee_list})


@login_required
def create_variabel(request):
    if request.method == 'GET':
        variabels = Variabel.objects.all()
        maximum_percentage = sum([var.persentase for var in variabels])
        if maximum_percentage == 100:
            request.session['message'] = 'Tidak bisa menambahkan variabel karena persentase sudah maksimal'
            return redirect(reverse('variabel'))
        return render(request, 'example/add_variabel.html', {'max': 100 - maximum_percentage})
    if request.method == 'POST':
        nama = request.POST.get('nama')
        faktor = request.POST.get('faktor')
        persentase = request.POST.get('persentase')

        record = Variabel.objects.filter(nama=nama)

        if record:
            request.session['message'] = 'Variabel sudah digunakan'
            return redirect(reverse('variabel'))
            # data = record.first()
            # data.faktor = faktor
            # data.persentase = persentase
            # data.save()
            # return redirect('update-variabel')
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
            if not request.POST.get('update'):
                request.session['message'] = 'Sub variabel sudah digunakan'
                return redirect(reverse('subvariabel'))
            data = record.first()
            data.variabel = variabel_sub
            data.nama = nama
            data.faktor = faktor
            data.standar = standar
            data.save()
            return redirect(reverse('subvariabel'))
            # data = record.first()
            # data.variabel = variabel_sub
            # data.nama = nama
            # data.faktor = faktor
            # data.standar = standar
            # data.save()
            # return redirect('update-subvariabel')
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
        # Ambil data dari db
        record = get_object_or_404(Variabel, nama=var_name)

        # Lalu dihapus
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
        try:
            message = request.session.pop('message')
        except KeyError:
            message = ''

        variabel_list = Variabel.objects.all()
        return render(request, 'example/update_variabel.html', {'data': variabel_list, 'message': message})
    elif request.method == 'POST':
        nama = request.POST.get('nama')
        faktor = request.POST.get('faktor')
        persentase = request.POST.get('persentase')

        total = 0
        all_variabel = Variabel.objects.exclude(nama=nama)
        for variabel in all_variabel:
            total += int(variabel.persentase)

        if int(persentase) + total > 100:
            request.session['message'] = 'Tidak bisa mengubah persentase variabel karena persentase sudah maksimal'
            return redirect(reverse('update-variabel'))

        record = Variabel.objects.filter(nama=nama)
        record = record.first()
        record.faktor = faktor
        record.persentase = int(persentase)
        record.save()

        # Variabel.objects.update_or_create(nama=nama, faktor=faktor, persentase=persentase)
        return redirect('update-variabel')


@login_required
def actual_update_variabel(request, var_name):
    if request.method == 'GET':
        record = Variabel.objects.filter(nama=var_name)
        try:
            message = request.session.pop('message')
        except KeyError:
            message = ''

        variabels = Variabel.objects.all()
        maximum_percentage = sum([var.persentase for var in variabels])

        return render(request, 'example/add_variabel.html',
                      {'data': record[0], 'message': message, 'var_name': var_name, 'max_val': maximum_percentage})


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


def login_view(request):
    if request.method == 'GET':
        try:
            message = request.session.pop('message')
        except KeyError:
            message = ''
        return render(request, 'example/login.html', {'message': message})
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            if read_json(file_name)[username] == password:
                user = authenticate(request, username='admin', password='admin')
                login(request, user)
                return redirect('index')
            else:
                request.session['message'] = 'Username & password tidak sesuai'
                return redirect('login')
        except KeyError:
            request.session['message'] = 'Username & password tidak sesuai'
            return redirect('login')


def add_user(request):
    if request.method == 'GET':
        return render(request, 'example/add_user.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if append_to_json(file_name, username, password):
            return redirect('login')
