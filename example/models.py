from enum import Enum

from django.db import models


class Faktor(Enum):
    CORE = "Core"
    SECONDARY = "Secondary"


# Create your models here.
class Variabel(models.Model):
    nama = models.CharField(max_length=50)
    faktor = models.CharField(
        max_length=10,
        choices=[(choice.name, choice.value) for choice in Faktor],
        default=Faktor.CORE.name,
    )
    persentase = models.IntegerField()

    def __str__(self) -> str:
        return self.nama


class SubVariabel(models.Model):
    kode = models.CharField(max_length=10)
    nama = models.CharField(max_length=10)
    faktor = models.CharField(
        max_length=10,
        choices=[(choice.name, choice.value) for choice in Faktor],
        default=Faktor.CORE.name,
    )
    standar = models.IntegerField()

    def __str__(self) -> str:
        return self.nama


class Pegawai(models.Model):
    id_pegawai = models.CharField(max_length=100, primary_key=True)
    nama = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.nama


class Skor(models.Model):
    pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE)
    sub_variabel = models.ForeignKey(SubVariabel, on_delete=models.CASCADE)
    skor = models.IntegerField()

    def __str__(self) -> str:
        return self.pegawai.nama
