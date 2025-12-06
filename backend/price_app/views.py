import yfinance as yf
import json
import datetime
from django.shortcuts import render
from django.http import JsonResponse
from .models import FinancialData
from django.db import transaction
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

@transaction.atomic
def fetch_and_save_data():
    # LİSTE: (Yahoo Kodu, Ekranda Görünecek İsim, Tür)
    assets = [
        ("BTC-USD", "BTC", "CRYPTO"),         # Kripto
        ("XU100.IS", "XU100", "STOCK"),       # Borsa
        ("GC=F", "GRAM-ALTIN", "COMMODITY"),  # Emtia (Ons -> Gram çevireceğiz)
        ("TRY=X", "USD/TRY", "FOREX"),        # Döviz
        ("EURTRY=X", "EUR/TRY", "FOREX"),     # Döviz
        ("SI=F", "GÜMÜŞ", "COMMODITY"),       # Gümüş
    ]

    # Önce Dolar kurunu al (Çeviriler için şart)
    try:
        usd_t = yf.Ticker("TRY=X")
        # Son 1 haftayı çekip ffill yapıyoruz ki boş gelmesin
        hist_usd = usd_t.history(period="5d").ffill()
        usd_price = hist_usd['Close'].iloc[-1]
    except:
        usd_price = 36.00 # Acil durum yedeği

    for yf_code, symbol_name, dtype in assets:
        try:
            ticker = yf.Ticker(yf_code)
            # 1.5 Yıllık veri çekiyoruz (Yıllık değişim hesabı garanti olsun diye)
            hist = ticker.history(period="2y")
            
            if hist.empty:
                print(f"Veri yok: {symbol_name}")
                continue

            # --- KRİTİK DÜZELTME: BOŞLUKLARI DOLDUR ---
            # Hafta sonu boşluklarını önceki günün fiyatıyla doldurur
            hist = hist.ffill() 

            # Şimdiki Fiyat
            current_price = hist['Close'].iloc[-1]

            # --- ESNEK TARİH SEÇİCİ (Helper) ---
            # Tam o gün yoksa, verideki en yakın geçmiş günü bulur
            def get_past_price(days_ago):
                try:
                    # İstenen tarihe git
                    target_date = hist.index[-1] - datetime.timedelta(days=days_ago)
                    # O tarihe en yakın indexi bul (method='pad' geçmişe bakar)
                    idx = hist.index.get_indexer([target_date], method='pad')[0]
                    if idx < 0: return current_price # Çok eski tarihse şimdiki fiyatı dön
                    return hist['Close'].iloc[idx]
                except:
                    return current_price

            # Geçmiş Fiyatları Al
            price_1d = hist['Close'].iloc[-2] # Dün (Garantili çünkü ffill yaptık)
            price_1w = get_past_price(7)      # 1 Hafta
            price_1m = get_past_price(30)     # 1 Ay
            price_1y = get_past_price(365)    # 1 Yıl

            # Yüzdeleri Hesapla
            chg_d = ((current_price - price_1d) / price_1d) * 100
            chg_w = ((current_price - price_1w) / price_1w) * 100
            chg_m = ((current_price - price_1m) / price_1m) * 100
            chg_y = ((current_price - price_1y) / price_1y) * 100

            # --- GRAFİK VERİSİ (SON 30 GÜN) ---
            chart_history = []
            # Son 30 veriyi al
            recent_data = hist.tail(45) # Biraz fazla alalım
            
            for date, row in recent_data.iterrows():
                val = row['Close']
                
                # ONS ALTIN -> GRAM ALTIN Çevirisi
                if yf_code == "GC=F":
                    # Altın hesabı: (Ons * Dolar) / 31.10
                    # Tarihsel verideki doları bilmediğimiz için kabaca güncel kurla çarpıyoruz 
                    # (Profesyonel sistemde tarihsel kur verisi de tutulur ama bu yeterli)
                    val = (val * usd_price) / 31.1035
                
                # BTC -> TRY Çevirisi
                elif yf_code == "BTC-USD":
                    val = val * usd_price

                chart_history.append({
                    "x": date.strftime('%Y-%m-%d'),
                    "y": round(val, 2)
                })

            # --- FİYAT KAYIT (TL Çevirileri) ---
            final_price = current_price
            if yf_code == "GC=F": final_price = (current_price * usd_price) / 31.1035
            elif yf_code == "BTC-USD": final_price = current_price * usd_price
            elif yf_code == "SI=F": final_price = (current_price * usd_price) / 31.1035 # Gümüş Gram hesabı

            FinancialData.objects.update_or_create(
                symbol=symbol_name,
                defaults={
                    'data_type': dtype,
                    'name': symbol_name, # İsim yerine sembolü kullandık daha temiz dursun
                    'price': Decimal(f"{final_price:.2f}"),
                    'change_day': Decimal(f"{chg_d:.2f}"),
                    'change_week': Decimal(f"{chg_w:.2f}"),
                    'change_month': Decimal(f"{chg_m:.2f}"),
                    'change_year': Decimal(f"{chg_y:.2f}"),
                    'chart_data': json.dumps(chart_history)
                }
            )
            # print(f"✅ {symbol_name} Güncel.") 

        except Exception as e:
            print(f"❌ {symbol_name} Hatası: {e}")

@csrf_exempt
def get_latest_data(request):
    if request.method == 'POST':
        fetch_and_save_data()
        return JsonResponse({'status': 'updated'})
    
    data = list(FinancialData.objects.all().values())
    return JsonResponse({'data': data}, safe=False)

# ... diğer kodların altı ...

def index(request):
    return render(request, 'index.html')