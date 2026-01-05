import requests
import json
import math
import os
import time

# --- ⚙️ TU CONFIGURACIÓN ---
MI_CELULAR = "59174355273" # <--- TU NÚMERO
TIKTOK_COSTO_UNITARIO = 0.31 / 30 
TIKTOK_PACKS = [30, 70, 350, 700, 1400, 3500, 7000, 17500]

# --- 👑 LISTA VIP (50 JUEGOS TOP) ---
# GTA, COD, FIFA, RE, RDR2, GOW, MK, ETC.
VIP_IDS = [
    271590, 730, 550, 252490, 1174180, 105600, 1245620, 1593500, 1817070, 
    292030, 1091500, 578080, 230410, 221100, 250900, 268910, 413150, 
    1085660, 1938090, 892970, 945360, 1172470, 381210, 4000, 2050650, 
    1794680, 304240, 2399830, 1966720, 1238840, 1238810, 1196590, 
    1623730, 1604030, 1326470, 1086940, 1145360, 236390, 2073850, 
    552520, 1240440, 1551360, 1599340, 1659040, 601150, 1151640
]

# API CheapShark
API_DEALS = "https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=60&metacritic=70&onSale=1&pageSize=60&sortBy=Metacritic"
API_GAME = "https://www.cheapshark.com/api/1.0/games?steamAppID="

def limpiar():
    os.system("clear")
    print("=================================")
    print("   🦁 STORELIM v3.1 - MANAGER    ")
    print("=================================")

def get_config():
    limpiar()
    try:
        tasa = float(input("\n💵 Dólar hoy (Ej: 11.5): "))
        return tasa
    except: return 11.5

def calc_bs(usd, tasa):
    if usd == 0: return 0
    return math.ceil(float(usd) * tasa * 1.10)

def procesar_vips(tasa):
    print(f"\n👑 Escaneando {len(VIP_IDS)} Juegos VIP (Esto demora un poco)...")
    lista = []
    
    for i, app_id in enumerate(VIP_IDS):
        try:
            # Pausa pequeña para no saturar la API
            if i % 10 == 0: time.sleep(1)
            
            res = requests.get(f"{API_GAME}{app_id}", timeout=5).json()
            if not res or 'deals' not in res or not res['deals']: continue
            
            deal = res['deals'][0]
            p_usd = float(deal['price'])
            p_orig = float(deal['retailPrice'])
            
            # Formato de precios para la web
            precio_bs = calc_bs(p_usd, tasa)
            
            descuento = 0
            if p_orig > 0: descuento = int(100 - (p_usd / p_orig * 100))
            if descuento < 0: descuento = 0

            lista.append({
                "id": app_id,
                "nombre": res['external'],
                "precio_bs": precio_bs,
                "usd_orig": p_orig,   # Precio original USD
                "usd_now": p_usd,     # Precio actual USD
                "descuento": descuento,
                "imagen": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg",
                "es_vip": True
            })
            # Imprimir progreso en una sola línea
            print(f"\r   Processing: {i+1}/{len(VIP_IDS)} - {res['external'][:15]}...", end="")
        except: pass
    
    print("\n   ✅ VIPs completados.")
    return lista

def procesar_ofertas(tasa):
    print("\n🔥 Buscando las 100 Mejores Ofertas...")
    lista = []
    ids_registrados = set()
    
    # Buscamos 2 páginas para asegurar 100 juegos buenos
    for page in range(2):
        try:
            url = f"{API_DEALS}&pageNumber={page}"
            ofertas = requests.get(url).json()
            
            for g in ofertas:
                sid = g.get('steamAppID')
                # Evitar duplicados con la lista VIP
                if not sid or int(sid) in VIP_IDS or sid in ids_registrados: continue
                
                p_usd = float(g['salePrice'])
                p_orig = float(g['normalPrice'])
                desc = int(float(g['savings']))
                
                lista.append({
                    "id": sid,
                    "nombre": g['title'],
                    "precio_bs": calc_bs(p_usd, tasa),
                    "usd_orig": p_orig,
                    "usd_now": p_usd,
                    "descuento": desc,
                    "imagen": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/header.jpg",
                    "es_vip": False
                })
                ids_registrados.add(sid)
        except Exception as e: print(f"Error pag {page}: {e}")
    
    # Recortar a exactos 100
    return lista[:100]

def procesar_tiktok(tasa):
    print("\n🎵 Generando Packs TikTok...")
    lista = []
    for m in TIKTOK_PACKS:
        costo = m * TIKTOK_COSTO_UNITARIO
        lista.append({"monedas": m, "precio_bs": math.ceil(costo * tasa * 1.10)})
    return lista

def main():
    tasa = get_config()
    vips = procesar_vips(tasa)
    ofertas = procesar_ofertas(tasa)
    packs = procesar_tiktok(tasa)
    
    # Unir VIPs y Ofertas en una sola lista para la web, 
    # pero manteniendo la marca "es_vip" para ordenarlos
    todo_juegos = vips + ofertas
    
    db = {
        "config": {"tasa": tasa, "celular": MI_CELULAR, "costo_tk": TIKTOK_COSTO_UNITARIO},
        "juegos": todo_juegos,
        "tiktok": packs
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4)
    
    print(f"\n✨ REPORTE FINAL ✨")
    print(f"👑 VIPs encontrados: {len(vips)}")
    print(f"🔥 Ofertas cargadas: {len(ofertas)}")
    
    if input("\n¿Subir a GitHub? (s/n): ").lower() == 's':
        os.system("git add . && git commit -m 'Update v3.1' && git push")

if __name__ == "__main__":
    main()

