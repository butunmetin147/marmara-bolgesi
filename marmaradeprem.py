import requests, certifi
from datetime import datetime, timedelta
url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/archive?limit=500"
data = requests.get(url, verify=certifi.where()).json()["result"]

one_week_ago = datetime.now() - timedelta(days=7)

marmara_depremleri = []
fay_uzeri = []

MARMARA_BOUNDS = {
    "lat_min": 39.5,
    "lat_max": 41.5,
    "lng_min": 25.9,
    "lng_max": 31.5
}
NORTH_MARMARA_FAULT = [
    (40.8, 27.5),  # Tekirdağ açıkları
    (40.9, 28.5),  # Marmara Ereğlisi
    (40.9, 29.5),  # Silivri
    (40.8, 30.5),  # Adalar açıkları
    (40.7, 29.9),  # Çınarcık Havzası (Yalova açıkları)
    (40.6, 30.2),  # Yalova - Altınova
    (40.7, 30.4),  # Karamürsel - Gölcük açıkları
    (40.7, 30.6),  # İzmit Körfezi
    (40.8, 30.8),  # Sapanca Gölü (Sakarya)
    (40.9, 31.0)   # Akyazı - Sakarya
]
def is_in_marmara(lat, lng):
    return (
        MARMARA_BOUNDS["lat_min"] <= lat <= MARMARA_BOUNDS["lat_max"]
        and MARMARA_BOUNDS["lng_min"] <= lng <= MARMARA_BOUNDS["lng_max"]
    )
import math

def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def is_on_north_marmara_fault(lat, lng, threshold_km=20):
    for f_lat, f_lng in NORTH_MARMARA_FAULT:
        if distance_km(lat, lng, f_lat, f_lng) <= threshold_km:
            return True
    return False



for d in data:
    if "geojson" not in d or "coordinates" not in d["geojson"]:
        continue

    lng, lat = d["geojson"]["coordinates"]

    date = datetime.strptime(
        d["date_time"],
        "%Y-%m-%d %H:%M:%S"
    )

    if date >= one_week_ago and is_in_marmara(lat, lng):
        marmara_depremleri.append(d)

        if is_on_north_marmara_fault(lat, lng):
            fay_uzeri.append(d)


print("📍 MARMARA DEPREM HAFTALIK RAPORU")
print("---------------------------------")
print(f"Toplam deprem sayısı: {len(marmara_depremleri)}")
print(f"Kuzey Marmara Fayı üzerindekiler: {len(fay_uzeri)}")

buyukler = [d for d in marmara_depremleri if float(d["mag"]) >= 4]
print(f"4.0 ve üzeri depremler: {len(buyukler)}")

rapor = f"""
Marmara Denizi ve çevresinde son 1 hafta içerisinde
toplam {len(marmara_depremleri)} deprem meydana geldi.

Bu depremlerin {len(fay_uzeri)} tanesi
Kuzey Marmara Fayı hattı üzerinde gerçekleşti.

Uzmanlar, Marmara Bölgesi için
sismik hareketliliğin yakından takip edilmesi gerektiğini belirtiyor.
"""

print(rapor)
print("İlk Marmara depremi:", marmara_depremleri[0]["title"])
