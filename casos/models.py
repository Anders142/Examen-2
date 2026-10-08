from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class Cliente(models.Model):
    nombres = models.CharField(max_length=150)
    documento = models.CharField(max_length=11, unique=True)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()

    def __str__(self):
        return f'{self.nombres} ({self.documento})'


class EstadoCaso(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    permite_pagos = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class Caso(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='casos')
    estado = models.ForeignKey(EstadoCaso, on_delete=models.PROTECT, related_name='casos')
    abogados = models.ManyToManyField(User, related_name='casos_revisados')

    def __str__(self):
        return f'{self.codigo} - {self.titulo}'

    def total_pagado(self):
        return self.pagos.aggregate(total=Sum('monto'))['total'] or 0


class Expediente(models.Model):
    numero = models.CharField(max_length=30, unique=True)
    juzgado = models.CharField(max_length=150)
    fecha_presentacion = models.DateField()
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='expedientes')

    def __str__(self):
        return f'Exp. {self.numero}'


class Pago(models.Model):
    caso = models.ForeignKey(Caso, on_delete=models.PROTECT, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.caso.codigo} - S/ {self.monto}'

    def clean(self):
        if self.caso_id and not self.caso.estado.permite_pagos:
            raise ValidationError('El estado del caso no permite registrar pagos.')


class PerfilAbogado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    colegiatura = models.CharField(max_length=20)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.usuario.username} - CAL {self.colegiatura}'

class Expediente(models.Model):
    numero = models.CharField(max_length=30, unique=True)
    juzgado = models.CharField(max_length=150)
    fecha_presentacion = models.DateField()
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='expedientes')
    documento = models.FileField(upload_to='expedientes/', blank=True, null=True)

    def __str__(self):
        return f'Exp. {self.numero}'