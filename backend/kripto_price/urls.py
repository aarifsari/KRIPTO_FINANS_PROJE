from django.contrib import admin
from django.urls import path, include
from price_app import views 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('price_app.urls')), 
    path('', views.index, name='home'),      
]