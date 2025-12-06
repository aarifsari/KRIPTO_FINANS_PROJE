from django.db import models

class FinancialData(models.Model):
    # Temel Bilgiler
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=20) # CRYPTO, STOCK, FOREX, GOLD
    
    # Fiyat Bilgileri
    price = models.DecimalField(max_digits=20, decimal_places=4)
    
    # Değişim Oranları (4 Zaman Dilimi)
    change_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # Günlük
    change_week = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Haftalık
    change_month = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Aylık
    change_year = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Yıllık
    
    # Grafik Verisi (JSON formatında metin olarak saklayacağız)
    # Örn: [{"x": "2023-12-01", "y": 900}, ...]
    chart_data = models.TextField(blank=True, null=True) 

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name