import yfinance as yf

print("--- Bağlantı Testi Başlıyor ---")
try:
    # BIST 100 verisini çekmeyi dene
    bist = yf.Ticker("XU100.IS")
    hist = bist.history(period="1d")
    
    if hist.empty:
        print("❌ HATA: Yahoo Finance boş veri döndürdü. (BIST verisi alınamadı)")
    else:
        print("✅ BAŞARILI: Veri çekildi!")
        print(hist)
except Exception as e:
    print(f"❌ BAĞLANTI HATASI: {e}")