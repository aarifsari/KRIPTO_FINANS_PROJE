import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { RefreshCw, TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';
import './App.css';

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString());

  const API_URL = 'http://127.0.0.1:8000/api/data/';

  // Veri Çekme Fonksiyonu
  const fetchData = async (isManual = false) => {
    if (isManual) setLoading(true);
    try {
      if (isManual) {
        // Manuel tetikleme varsa backend'e POST atıp taze veri çektiriyoruz
        await axios.post(API_URL);
      }
      // Sadece okuma (GET)
      const response = await axios.get(API_URL);
      setData(response.data.data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error("Veri hatası:", error);
    } finally {
      if (isManual) setLoading(false);
    }
  };

  // Otomatik Güncelleme (Sayfa açılınca ve her 30 saniyede bir)
  useEffect(() => {
    fetchData(); // İlk açılışta çek
    
    const interval = setInterval(() => {
      fetchData(); // 30 saniyede bir arka planda güncelle
    }, 30000);

    return () => clearInterval(interval); // Sayfa kapanırsa döngüyü durdur
  }, []);

  // Grafik verisini hazırlama (Sayısal değerleri düzeltme)
  const chartData = data.map(item => ({
    name: item.symbol,
    Fiyat: parseFloat(item.price),
    Degisim24s: parseFloat(item.daily_change_percent),
    Degisim7g: parseFloat(item.long_term_change_percent || 0),
  }));

  return (
    <div className="dashboard-container">
      {/* --- SIDEBAR --- */}
      <aside className="sidebar">
        <div className="logo">
          <Activity size={28} color="#4f46e5" />
          <h2>FinDash</h2>
        </div>
        <nav>
          <a href="#" className="active"><TrendingUp size={18} /> Piyasalar</a>
          <a href="#"><DollarSign size={18} /> Portföy</a>
        </nav>
      </aside>

      {/* --- MAIN CONTENT --- */}
      <main className="main-content">
        
        {/* Header */}
        <header className="header">
          <div>
            <h1>Piyasa Genel Bakış</h1>
            <p className="subtitle">Canlı finansal veriler ve analizler</p>
          </div>
          <div className="header-actions">
            <span className="last-updated">Son Güncelleme: {lastUpdated}</span>
            <button onClick={() => fetchData(true)} disabled={loading} className="refresh-btn">
              <RefreshCw size={18} className={loading ? 'spin' : ''} />
              {loading ? 'Yükleniyor...' : 'Yenile'}
            </button>
          </div>
        </header>

        {/* Özet Kartları */}
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Toplam Varlık Sayısı</h3>
            <div className="value">{data.length}</div>
            <div className="icon-bg"><Activity /></div>
          </div>
          <div className="stat-card">
            <h3>En Yüksek Fiyat</h3>
            <div className="value">
              {data.length > 0 ? 
                Math.max(...data.map(i => parseFloat(i.price))).toLocaleString('tr-TR', {style: 'currency', currency: 'TRY'}) 
                : '₺0,00'}
            </div>
            <div className="icon-bg"><DollarSign /></div>
          </div>
        </div>

        {/* İçerik Grid (Tablo ve Grafik) */}
        <div className="content-grid">
          
          {/* Sol Taraf: Tablo */}
          <div className="panel table-panel">
            <h3>Varlık Listesi</h3>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Sembol</th>
                    <th>İsim</th>
                    <th>Fiyat (TRY)</th>
                    <th>24s %</th>
                    <th>7g %</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item, index) => (
                    <tr key={index}>
                      <td className="symbol-cell">{item.symbol}</td>
                      <td>{item.name}</td>
                      <td className="price-cell">
                        {parseFloat(item.price).toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺
                      </td>
                      <td style={{ color: item.daily_change_percent > 0 ? '#10b981' : '#ef4444' }}>
                        <div className="trend-cell">
                          {item.daily_change_percent > 0 ? <TrendingUp size={14}/> : <TrendingDown size={14}/>}
                          %{parseFloat(item.daily_change_percent).toFixed(2)}
                        </div>
                      </td>
                      <td style={{ color: (item.long_term_change_percent || 0) > 0 ? '#10b981' : '#ef4444' }}>
                        %{(parseFloat(item.long_term_change_percent) || 0).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Sağ Taraf: Grafik */}
          <div className="panel chart-panel">
            <h3>Performans Karşılaştırması (24s vs 7g)</h3>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{fontSize: 12}} />
                  <YAxis tick={{fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                  />
                  <Legend />
                  <Bar dataKey="Degisim24s" name="24s Değişim %" fill="#8884d8" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Degisim7g" name="7g Değişim %" fill="#82ca9d" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;