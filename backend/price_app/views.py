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
    # Türler: CRYPTO, STOCK, FOREX, COMMODITY
    assets = [
        # --- ANA 4'LÜ ---
        ("BTC-USD", "BTC", "CRYPTO"),
        ("XU100.IS", "XU100", "STOCK"),
        ("GC=F", "GRAM-ALTIN", "COMMODITY"),
        ("TRY=X", "USD/TRY", "FOREX"),

        # --- DİĞER KRİPTOLAR ---
        ("ETH-USD", "Ethereum", "CRYPTO"),
        ("SOL-USD", "Solana", "CRYPTO"),
        ("AVAX-USD", "Avalanche", "CRYPTO"),
        ("DOGE-USD", "Dogecoin", "CRYPTO"),

        # --- DİĞER BORSA (BIST 30 ÖNCÜLERİ) ---
        ("THYAO.IS", "THY", "STOCK"),
        ("GARAN.IS", "Garanti BBVA", "STOCK"),
        ("ASELS.IS", "Aselsan", "STOCK"),
        ("EREGL.IS", "Ereğli Demir Çelik", "STOCK"),
        ("AKBNK.IS", "Akbank", "STOCK"),

        # --- DİĞER DÖVİZ & EMTİA ---
        ("EURTRY=X", "EUR/TRY", "FOREX"),
        ("GBPTRY=X", "GBP/TRY", "FOREX"),     # Sterlin
        ("EURUSD=X", "EUR/USD", "FOREX"),     # Euro/Dolar Paritesi
        ("BZ=F", "Brent Petrol", "COMMODITY"),
        ("SI=F", "Gümüş", "COMMODITY"),
    ]

    try:
        usd_t = yf.Ticker("TRY=X")
        hist_usd = usd_t.history(period="5d").ffill()
        usd_price = hist_usd['Close'].iloc[-1]
    except:
        usd_price = 36.00

    for yf_code, symbol_name, dtype in assets:
        try:
            ticker = yf.Ticker(yf_code)
            # Veri çekme (2 Yıllık - Garanti olsun)
            hist = ticker.history(period="2y")
            
            if hist.empty: continue

            hist = hist.ffill() 
            current_price = hist['Close'].iloc[-1]

            # Helper: Geçmiş fiyat bulucu
            def get_past_price(days_ago):
                try:
                    target_date = hist.index[-1] - datetime.timedelta(days=days_ago)
                    idx = hist.index.get_indexer([target_date], method='pad')[0]
                    if idx < 0: return current_price
                    return hist['Close'].iloc[idx]
                except:
                    return current_price

            price_1d = hist['Close'].iloc[-2]
            price_1w = get_past_price(7)
            price_1m = get_past_price(30)
            price_1y = get_past_price(365)

            chg_d = ((current_price - price_1d) / price_1d) * 100
            chg_w = ((current_price - price_1w) / price_1w) * 100
            chg_m = ((current_price - price_1m) / price_1m) * 100
            chg_y = ((current_price - price_1y) / price_1y) * 100

            # Grafik Verisi (Son 45 gün)
            chart_history = []
            recent_data = hist.tail(45)
            
            for date, row in recent_data.iterrows():
                val = row['Close']
                # TL Çevirileri
                if yf_code == "GC=F" or yf_code == "SI=F": val = (val * usd_price) / 31.1035
                elif dtype == "CRYPTO": val = val * usd_price # Kriptoları TL yap
                elif yf_code == "BZ=F": val = val * usd_price # Petrol TL
                
                # EUR/USD gibi pariteler olduğu gibi kalsın
                
                chart_history.append({
                    "x": date.strftime('%Y-%m-%d'),
                    "y": round(val, 2)
                })

            # Fiyat Kayıt (TL Çevirileri)
            final_price = current_price
            if yf_code == "GC=F" or yf_code == "SI=F": final_price = (current_price * usd_price) / 31.1035
            elif dtype == "CRYPTO": final_price = current_price * usd_price
            elif yf_code == "BZ=F": final_price = current_price * usd_price

            FinancialData.objects.update_or_create(
                symbol=symbol_name,
                defaults={
                    'data_type': dtype,
                    'name': symbol_name,
                    'price': Decimal(f"{final_price:.2f}"),
                    'change_day': Decimal(f"{chg_d:.2f}"),
                    'change_week': Decimal(f"{chg_w:.2f}"),
                    'change_month': Decimal(f"{chg_m:.2f}"),
                    'change_year': Decimal(f"{chg_y:.2f}"),
                    'chart_data': json.dumps(chart_history)
                }
            )

        except Exception as e:
            print(f"Hata ({symbol_name}): {e}")

@csrf_exempt
def get_latest_data(request):
    if request.method == 'POST':
        fetch_and_save_data()
        return JsonResponse({'status': 'updated'})
    
    data = list(FinancialData.objects.all().values())
    return JsonResponse({'data': data}, safe=False)

def index(request):
    return render(request, 'index.html')