from django.urls import path
from . import views

urlpatterns = [
    # Adresimiz: /api/data/ olacak
    path('data/', views.get_latest_data, name='get_data'),
]