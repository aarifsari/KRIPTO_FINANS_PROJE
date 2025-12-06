from django.db import models

class FinancialData(models.Model):
    
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=20) 
    
    price = models.DecimalField(max_digits=20, decimal_places=4)
  
    change_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)   
    change_week = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    change_month = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    change_year = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    

    chart_data = models.TextField(blank=True, null=True) 

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name