import numpy as np

# --- GERÇEK PARAMETRELER ---
GLOBAL_SENSITIVITY = 19787
ORIGINAL_QUERY_RESULT = 4645408
N_RUNS = 1000  # Deneme sayısı

# Gizlilik Bütçeleri
EPSILON_1 = 0.5  # Yüksek Gizlilik
EPSILON_2 = 2.0  # Düşük Gizlilik

def laplace_mechanism(f_D, sensitivity, epsilon, runs):
    """Belirtilen sayıda simülasyon yaparak ortalama gürültü ve kaybı hesaplar."""
    b = sensitivity / epsilon
    
    # 1000 adet rastgele gürültü üretme
    noise_samples = np.random.laplace(loc=0, scale=b, size=runs)
    
    # Ortalama Mutlak Hata (MAE) = Ortalama Fayda Kaybı
    # Gürültünün büyüklüğünün ortalaması, fayda kaybının göstergesidir.
    avg_utility_loss = np.mean(np.abs(noise_samples)) 
    
    # Tek bir deneme sonucu (örnek olarak kullanılabilir)
    example_result = f_D + noise_samples[0]
    
    return avg_utility_loss, example_result, b

# --- Deneyleri Çalıştırma ---

# 1. Yüksek Gizlilik (ε = 0.5)
loss_1, result_1, b1 = laplace_mechanism(ORIGINAL_QUERY_RESULT, GLOBAL_SENSITIVITY, EPSILON_1, N_RUNS)

# 2. Düşük Gizlilik (ε = 2.0)
loss_2, result_2, b2 = laplace_mechanism(ORIGINAL_QUERY_RESULT, GLOBAL_SENSITIVITY, EPSILON_2, N_RUNS)


# --- Raporlama ---

print("  Fayda-Gizlilik Takası Analiz Sonuçları (1000 Simülasyon Ortalaması)")
print(f"Orijinal Sonuç (f(D)): {ORIGINAL_QUERY_RESULT:,.0f} Hisse\n")

print(" 1. Yüksek Gizlilik Senaryosu ε = 0.5 ")
print(f"   *Gizlilik Düzeyi: YÜKSEK")
print(f"   *Laplace Ölçek Parametresi (b): {b1:,.0f} (Yüksek Gürültü)")
print(f"   *Ortalama Fayda Kaybı (MAE):* **{loss_1:,.0f} Hisse")
print(f"   *Oransal Kayıp: {(loss_1 / ORIGINAL_QUERY_RESULT) * 100:.3f}%")
print(f"   *Örnek Gizli Sonuç: {result_1:,.0f} Hisse (Orijinalden uzak)\n")

print(" 2. Düşük Gizlilik Senaryosu (ε = 2.0)")
print(f"   *Gizlilik Düzeyi:* DÜŞÜK")
print(f"   *Laplace Ölçek Parametresi (b): {b2:,.0f} (Düşük Gürültü)")
print(f"   *Ortalama Fayda Kaybı (MAE):* {loss_2:,.0f} Hisse")
print(f"   *Oransal Kayıp:* {(loss_2 / ORIGINAL_QUERY_RESULT) * 100:.3f}%")
print(f"   *Örnek Gizli Sonuç:* {result_2:,.0f} Hisse (Orijinale yakın)")

print("\n---")

