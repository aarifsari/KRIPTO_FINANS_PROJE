from django.contrib import admin
from django.urls import path, include
from price_app import views # <--- Uygulamanızın views dosyasını çağırıyoruz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('price_app.urls')), # Veri akışı kanalı
    path('', views.index, name='home'),      # <--- ANASAYFA KANALI (Bunu ekledik)
]