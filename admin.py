import requests
import json
import math
import os
import time

# --- ⚙️ CONFIGURACIÓN ---
MI_CELULAR = "59174355273" # <--- TU NÚMERO
TIKTOK_COSTO_UNITARIO = 0.31 / 30 
TIKTOK_PACKS = [30, 70, 350, 700, 1400, 3500, 7000, 17500]

# --- 👑 LISTA VIP (IDs DE STEAM) ---
VIP_IDS = [
    271590, 730, 550, 252490, 1174180, 105600, 1245620, 1593500, 
    1817070, 292030, 1091500, 578080, 230410, 221100, 250900,   
    268910, 413150, 1085660, 1938090, 892970, 945360, 1172470,  
    381210, 4000, 2050650, 1794680, 304240, 2399830, 1966720,   
    1238840, 1238810, 1196590, 1623730, 1604030, 1326470,       
    552520, 1551360, 1151640, 2073850                           
]

# API
API_STEAM_DIRECT = "https://store.steampowered.com/api/appdetails?cc=us&filters=price_overview,basic&appids="
API_OFERTAS = "https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=60&metacritic=75&onSale=1&pageSize=60&sortBy=Metacritic"

def limpiar():
    os.system("clear")
    print("=================================")
    print("   🦁 STORELIM v3.4 - FINAL      ")
    print("=================================")

def get_config():
    limpiar()
    try:
        tasa = float(input("\n💵 Dólar hoy (Ej: 11.5): "))
        msg = input("📢 Mensaje Barra (Enter para default): ")
        if not msg: msg = "🇧🇴 Recargas Seguras y Juegos Steam al mejor precio."
        return tasa, msg
    except: return 11.5, "StoreLim Bolivia"

def calc_bs(usd, tasa):
    if usd <= 0: return 0
    return math.ceil(float(usd) * tasa * 1.10)

def procesar_vips_steam(tasa):
    print(f"\n👑 Conectando a servidores de Steam ({len(VIP_IDS)} juegos)...")
    lista = []
    
    for i, app_id in enumerate(VIP_IDS):
        try:
            time.sleep(0.5) # Pausa anti-bloqueo
            url = f"{API_STEAM_DIRECT}{app_id}"
            raw = requests.get(url).json()
            
            if str(app_id) in raw and raw[str(app_id)]['success']:
                data = raw[str(app_id)]['data']
                nombre = data['name']
                
                usd_now = 0.0
                usd_orig = 0.0
                descuento = 0
                
                # DETECCIÓN INTELIGENTE DE PRECIOS
                if 'price_overview' in data:
                    usd_now = data['price_overview']['final'] / 100
                    usd_orig = data['price_overview']['initial'] / 100
                    descuento = data['price_overview']['discount_percent']
                elif data.get('is_free'):
                    usd_now = 0.0
                    usd_orig = 0.0
                else:
                    # Si no tiene precio (ej: no disponible), saltamos
                    continue 

                # Si precio original es 0 (ej: juego gratis), igualamos para evitar errores
                if usd_orig == 0: usd_orig = usd_now

                lista.append({
                    "id": app_id,
                    "nombre": nombre,
                    "precio_bs": calc_bs(usd_now, tasa),
                    "usd_orig": round(usd_orig, 2),
                    "usd_now": round(usd_now, 2),
                    "descuento": descuento,
                    "imagen": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg",
                    "es_vip": True
                })
                print(f"\r   ✅ Cargado: {i+1}/{len(VIP_IDS)}", end="")
            else:
                pass
        except: pass

    print("\n   ✨ VIPs Completados.")
    return lista

def procesar_ofertas(tasa):
    print("\n🔥 Buscando Ofertas (Restaurando sección)...")
    lista = []
    ids_registrados = set()
    
    for page in range(2):
        try:
            url = f"{API_OFERTAS}&pageNumber={page}"
            ofertas = requests.get(url).json()
            
            for g in ofertas:
                sid = g.get('steamAppID')
                if not sid or int(sid) in VIP_IDS or sid in ids_registrados: continue
                
                p_usd = float(g['salePrice'])
                p_orig = float(g['normalPrice'])
                desc = int(float(g['savings']))
                
                # Evitar juegos sin precio
                if p_orig == 0: p_orig = p_usd

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
        except: pass
    
    return lista[:100]

def procesar_tiktok(tasa):
    print("\n🎵 Packs TikTok...")
    lista = []
    for m in TIKTOK_PACKS:
        costo = m * TIKTOK_COSTO_UNITARIO
        lista.append({"monedas": m, "precio_bs": math.ceil(costo * tasa * 1.10)})
    return lista

def main():
    tasa, msg = get_config()
    
    vips = procesar_vips_steam(tasa)
    ofertas = procesar_ofertas(tasa)
    packs = procesar_tiktok(tasa)
    
    # UNIR TODO (AQUÍ ES DONDE ME ASEGURO QUE LAS OFERTAS ESTÉN)
    todo_juegos = vips + ofertas
    
    db = {
        "config": {"tasa": tasa, "celular": MI_CELULAR, "msg": msg, "costo_tk": TIKTOK_COSTO_UNITARIO},
        "juegos": todo_juegos,
        "tiktok": packs
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4)
    
    print(f"\n✨ REPORTE FINAL ✨")
    print(f"👑 VIPs: {len(vips)}")
    print(f"🔥 Ofertas: {len(ofertas)}")
    print(f"📂 Total Juegos en Web: {len(todo_juegos)}")
    
    if input("\n¿Subir a GitHub? (s/n): ").lower() == 's':
        os.system("git add . && git commit -m 'Fix Final' && git push")

if __name__ == "__main__":
    main()

