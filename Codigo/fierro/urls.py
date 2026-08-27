"""
URL configuration for fierro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from hotelghino import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='password_reset'),
    path('recuperar-contrasena/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('recuperar-contrasena/restablecer/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete'),
    ), name='password_reset_confirm'),
    path('recuperar-contrasena/completado/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('configuracion/modificar-usuario/', views.modificarUsuario, name='modificar_usuario'),
    path("admin/", admin.site.urls),
    path("alojamientos/", views.registroAlojamiento, name="alojamientos"),
    path("registro.hoteles.html", views.registroAlojamiento, name="registro_hoteles"),
    path("mis-hoteles/", views.misHoteles, name="mis_hoteles"),
    path("mis-hoteles/<int:alojamiento_id>/modificar/", views.modificarAlojamiento, name="modificar_hotel"),
    path("mis-hoteles/<int:alojamiento_id>/eliminar/", views.eliminarAlojamiento, name="eliminar_hotel"),
    path("mis-hoteles/<int:alojamiento_id>/habitaciones/registrar/", views.registroHabitacion, name="registrar_habitacion"),
    path("habitaciones/<int:habitacion_id>/modificar/", views.modificarHabitacion, name="modificar_habitacion"),
    path("habitaciones/<int:habitacion_id>/eliminar/", views.eliminarHabitacion, name="eliminar_habitacion"),
    path("propietario/", views.solicitudPropietario, name="propietario"),
    path("hoteles/<int:alojamiento_id>/", views.detalleHotel, name="detalle_hotel"),
    path("mis-reservas/", views.misReservas, name="mis_reservas"),
    path("mis-reservas/<int:reserva_id>/cancelar/", views.cancelarReserva, name="cancelar_reserva"),
]

