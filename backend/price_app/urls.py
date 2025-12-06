from django.urls import path
from . import views

urlpatterns = [

    path('data/', views.get_latest_data, name='get_data'),
]