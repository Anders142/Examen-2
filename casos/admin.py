from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Cliente, EstadoCaso, Caso, Expediente, Pago, PerfilAbogado


class PerfilAbogadoInline(admin.StackedInline):
    model = PerfilAbogado
    can_delete = False


class UsuarioAdmin(UserAdmin):
    inlines = [PerfilAbogadoInline]


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)


class ExpedienteInline(admin.TabularInline):
    model = Expediente
    extra = 1


class ExpedienteInline(admin.TabularInline):
    model = Expediente
    extra = 1


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'documento', 'telefono', 'correo')
    search_fields = ('nombres', 'documento', 'correo')
    list_filter = ('casos__estado',)


@admin.register(EstadoCaso)
class EstadoCasoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'permite_pagos')
    search_fields = ('nombre',)
    list_filter = ('permite_pagos',)


@admin.register(Caso)
class CasoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'cliente', 'estado', 'total_pagado', 'fecha_inicio')
    search_fields = ('codigo', 'titulo', 'cliente__nombres', 'cliente__documento')
    list_filter = ('estado', 'fecha_inicio')
    filter_horizontal = ('abogados',)
    inlines = [ExpedienteInline, PagoInline]


@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'juzgado', 'fecha_presentacion', 'caso')
    search_fields = ('numero', 'juzgado', 'caso__codigo')
    list_filter = ('juzgado', 'fecha_presentacion')