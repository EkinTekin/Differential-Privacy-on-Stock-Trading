import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- AYARLAR ---
FILE_NAME = 'synthetic_stock_trades.csv'
N_RUNS = 1000        # Simülasyon sayısı
DELTA = 1e-5         # Gaussian için gerekli (olası hata payı)
EPSILON_LIST = [0.5, 2.0] # Test edilecek bütçeler

# =============================================================================
# 1. VERİ YÜKLEME VE HAZIRLIK
# =============================================================================
print("--- 1. VERİ YÜKLEME VE HAZIRLIK ---")
try:
    df = pd.read_csv(FILE_NAME)
    # Temel Temizlik
    df = df[['timestamp', 'ticker', 'broker_id', 'quantity', 'trade_value', 'sector', 'country']]
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['trade_value'] = pd.to_numeric(df['trade_value'], errors='coerce')
    df = df.dropna(subset=['quantity', 'trade_value'])
    print(f"✅ Veri yüklendi ve temizlendi: {len(df)} satır.")
except FileNotFoundError:
    print(f"❌ '{FILE_NAME}' bulunamadı.")
    exit()

# =============================================================================
# 2. MEKANİZMA FONKSİYONLARI (Laplace & Gaussian)
# =============================================================================

def run_simulation(mechanism_name, true_value, sensitivity, epsilon, delta=None, runs=1000):
    """
    Belirli bir mekanizmayı defalarca çalıştırır ve gelişmiş metrikleri hesaplar.
    """
    noise_samples = []
    
    for _ in range(runs):
        if mechanism_name == 'Laplace':
            # Laplace Scale (b) = Delta f / epsilon
            scale = sensitivity / epsilon
            noise = np.random.laplace(0, scale)
            
        elif mechanism_name == 'Gaussian':
            # Gaussian Sigma hesabı (Approximate DP)
            sigma = np.sqrt(2 * np.log(1.25 / delta)) * (sensitivity / epsilon)
            noise = np.random.normal(0, sigma)
            
        noise_samples.append(noise)
    
    noise_samples = np.array(noise_samples)
    noisy_values = true_value + noise_samples
    
    # Metrikler
    mae = np.mean(np.abs(noise_samples))                  # Mean Absolute Error
    mse = np.mean(noise_samples ** 2)                     # Mean Squared Error
    rmse = np.sqrt(mse)                                   # Root Mean Squared Error
    
    if true_value != 0:
        rel_error = (mae / abs(true_value)) * 100         # % Hata
    else:
        rel_error = 0.0
        
    return {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'Rel_Error_%': rel_error
    }

# =============================================================================
# 3. DENEY A: TOPLAM HACİM (CLIPPING UYGULAMASI)
# =============================================================================
print("\n--- 3. DENEY A: TOPLAM HACİM (Clipping ile Güncellendi) ---")

# Hedef Broker'ı Bul
most_active_broker = df['broker_id'].mode()[0]

# --- [DEĞİŞİKLİK BAŞLANGICI: CLIPPING EKLENDİ] ---
# Hocanın uyarısı üzerine: Outlier'ların (Balina işlemlerinin) hassasiyeti patlatmasını önlemek için.
# Veri setindeki max değer yaklaşık 19.787 idi. Biz güvenli bir üst sınır (20.000) belirliyoruz.
CLIPPING_THRESHOLD = 20000 
print(f"⚠️  Outlier Koruması Devrede: Clipping Sınırı = {CLIPPING_THRESHOLD}")

# 1. Veriyi Kırp (10 Milyonluk işlem gelse bile 20.000 sayılacak)
df['clipped_quantity'] = df['quantity'].clip(upper=CLIPPING_THRESHOLD)

# 2. Hassasiyeti Sabitle (Artık verinin max değerine bakmıyoruz, sınıra bakıyoruz)
sensitivity_sum = CLIPPING_THRESHOLD 

# 3. Gerçek Değeri Kırpılmış Veri Üzerinden Hesapla
true_volume = df[df['broker_id'] == most_active_broker]['clipped_quantity'].sum()
# --- [DEĞİŞİKLİK BİTİŞİ] ---

print(f"Hedef: {most_active_broker} Toplam Hacim")
print(f"Gerçek Değer (Clipped): {true_volume:,.0f}")
print(f"Sabit Hassasiyet (Delta f): {sensitivity_sum:,.0f}")

results_data = []

for eps in EPSILON_LIST:
    # Laplace Çalıştır
    lap_res = run_simulation('Laplace', true_volume, sensitivity_sum, eps)
    results_data.append(['Laplace', eps, lap_res['MAE'], lap_res['RMSE'], lap_res['Rel_Error_%']])
    
    # Gaussian Çalıştır
    gauss_res = run_simulation('Gaussian', true_volume, sensitivity_sum, eps, delta=DELTA)
    results_data.append(['Gaussian', eps, gauss_res['MAE'], gauss_res['RMSE'], gauss_res['Rel_Error_%']])

# Sonuçları Tablo Olarak Göster
results_df = pd.DataFrame(results_data, columns=['Mekanizma', 'Epsilon', 'MAE', 'RMSE', 'Hata (%)'])
print(results_df)

# =============================================================================
# 4. DENEY B: EK SORGULAR (Sektörel Dağılım & Ortalama)
# =============================================================================
print("\n--- 4. DENEY B: EK SORGULAR ---")

# --- Soru 1: Sektörel Dağılım (Histogram) ---
print("\n[B1] Sektörel Dağılım (Histogram) - Epsilon: 1.0")
sector_counts = df['sector'].value_counts()
sensitivity_count = 1 # Count sorgusunda hassasiyet her zaman 1'dir.
target_epsilon = 1.0

noisy_sectors = {}
print(f"{'Sektör':<20} | {'Gerçek':<10} | {'Gürültülü (DP)':<15}")
for sector, count in sector_counts.items():
    noise = np.random.laplace(0, sensitivity_count / target_epsilon)
    noisy_val = max(0, int(count + noise)) 
    noisy_sectors[sector] = noisy_val
    print(f"{sector:<20} | {count:<10} | {noisy_val:<15}")


# --- Soru 2: Ortalama İşlem Değeri (Average) ---
print("\n[B2] Ortalama İşlem Değeri (Technology Sektörü) - Epsilon: 1.0")
tech_df = df[df['sector'] == 'Technology']

# --- [NOT: Burası zaten Clipping kullanıyordu, aynı mantık] ---
upper_bound = 100000 
clipped_values = tech_df['trade_value'].clip(upper=upper_bound)

true_avg = clipped_values.mean()

# Bütçeyi böl (Split Budget)
split_eps = target_epsilon / 2

# Gürültülü Toplam
noisy_sum = clipped_values.sum() + np.random.laplace(0, upper_bound / split_eps)
# Gürültülü Sayı
noisy_count = len(clipped_values) + np.random.laplace(0, 1 / split_eps)

if noisy_count < 1: noisy_count = 1
noisy_avg = noisy_sum / noisy_count

print(f"Gerçek Ortalama: {true_avg:,.2f}")
print(f"DP Ortalama:     {noisy_avg:,.2f}")
print(f"Fark:            {abs(true_avg - noisy_avg):,.2f}")

# =============================================================================
# 5. GÖRSELLEŞTİRME
# =============================================================================
print("\n--- 5. GÖRSELLEŞTİRME OLUŞTURULUYOR ---")

plt.figure(figsize=(12, 5))

# Subplot 1: MAE Karşılaştırması
plt.subplot(1, 2, 1)
pivot_df = results_df.pivot(index='Epsilon', columns='Mekanizma', values='MAE')
pivot_df.plot(kind='bar', ax=plt.gca(), color=['orange', 'blue'])
plt.title('Laplace vs Gaussian (MAE Karşılaştırması)')
plt.ylabel('Ortalama Mutlak Hata (MAE)')
plt.xticks(rotation=0)

# Subplot 2: Sektörel Dağılım (Histogram)
plt.subplot(1, 2, 2)
sectors = list(noisy_sectors.keys())
real_vals = [sector_counts[s] for s in sectors]
noise_vals = [noisy_sectors[s] for s in sectors]

x = np.arange(len(sectors))
width = 0.35

plt.bar(x - width/2, real_vals, width, label='Gerçek', color='gray')
plt.bar(x + width/2, noise_vals, width, label='Gürültülü (DP)', color='red', alpha=0.7)
plt.xlabel('Sektörler')
plt.ylabel('İşlem Sayısı')
plt.title('Histogram: Gerçek vs DP (ε=1.0)')
plt.xticks(x, sectors, rotation=45, ha='right')
plt.legend()

plt.tight_layout()
plt.show()

print("✅ Tüm işlemler tamamlandı.")