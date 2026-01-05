import requests
import json
import math
import os

# --- ⚙️ TU CONFIGURACIÓN ---
MI_CELULAR = "59174355273" # <--- CAMBIA ESTO
TIKTOK_COSTO_UNITARIO = 0.31 / 30 
TIKTOK_PACKS = [30, 70, 350, 700, 1400, 3500, 7000, 17500]

# --- 👑 LISTA VIP (SELECCIÓN DE ORO) ---
# He incluido: GTA, FIFA(FC), COD, Resident Evil, God of War, Survival, etc.
VIP_IDS = [
    271590, 1174180, 730, 550, 252490, 105600, 1245620, 1593500, # GTA, RDR2, CS2, L4D2, Rust, Terraria, EldenRing, GOW
    1817070, 292030, 1091500, 578080, 230410, 221100, 250900,   # Spiderman, Witcher3, Cyberpunk, PUBG, Warframe, DayZ, Isaac
    268910, 413150, 1085660, 1938090, 892970, 945360, 1172470,  # Cuphead, Stardew, Destiny2, COD, Valheim, AmongUs, Apex
    381210, 4000, 2050650, 1794680, 304240, 2399830, 1966720    # DBD, GarryMod, RE4, VampireSurv, BioShock, ARK, LethalCompany
]

# APIs
API_DEALS = "https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=60&metacritic=75&onSale=1&pageSize=60&sortBy=Metacritic"
API_GAME = "https://www.cheapshark.com/api/1.0/games?steamAppID="

def limpiar():
    os.system("clear")
    print("=================================")
    print("   🦁 STORELIM v3 - MANAGER      ")
    print("=================================")

def get_config():
    limpiar()
    try:
        tasa = float(input("\n💵 Dólar hoy (Ej: 11.5): "))
        msg = input("📢 Mensaje Barra (Enter para default): ")
        if not msg: msg = "🇧🇴 Precios en Bolivianos - Pagos QR - Entrega Inmediata"
        return tasa, msg
    except: return 11.5, "Error en config"

def calc_bs(usd, tasa):
    if usd == 0: return 0 # Para juegos gratis
    # Precio Dólar * Tasa * 1.10 (Comisión) -> Redondeado arriba
    return math.ceil(float(usd) * tasa * 1.10)

def procesar_juegos(tasa):
    lista_final = []
    ids_registrados = set()
    
    print("\n👑 1. Procesando VIPs (Paciencia)...")
    for app_id in VIP_IDS:
        try:
            res = requests.get(f"{API_GAME}{app_id}").json()
            if not res or 'deals' not in res or not res['deals']: continue
            
            deal = res['deals'][0]
            p_usd = float(deal['price'])
            p_orig = float(deal['retailPrice'])
            
            # Calcular precios Bs
            precio_bs = calc_bs(p_usd, tasa)
            precio_orig_bs = calc_bs(p_orig, tasa)
            
            descuento = 0
            if p_orig > 0: descuento = int(100 - (p_usd / p_orig * 100))
            
            # Evitar negativos raros
            if descuento < 0: descuento = 0
            
            juego = {
                "id": app_id,
                "nombre": res['external'],
                "precio_bs": precio_bs,       # Precio final en Bs
                "precio_antes_bs": precio_orig_bs, # Precio tachado en Bs
                "descuento": descuento,
                "imagen": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg",
                "es_vip": True,
                "score": 95 # Valor por defecto alto para VIPs
            }
            lista_final.append(juego)
            ids_registrados.add(str(app_id))
            print(f"   ✅ {res['external'][:20]}...")
        except: pass

    print("\n🔥 2. Buscando Ofertas Top (Metacritic > 75)...")
    try:
        ofertas = requests.get(API_DEALS).json()
        for g in ofertas:
            sid = g.get('steamAppID')
            if not sid or str(sid) in ids_registrados: continue
            
            p_usd = float(g['salePrice'])
            p_orig = float(g['normalPrice'])
            p_bs = calc_bs(p_usd, tasa)
            p_antes = calc_bs(p_orig, tasa)
            desc = int(float(g['savings']))
            score = int(g.get('metacriticScore', 0))

            lista_final.append({
                "id": sid,
                "nombre": g['title'],
                "precio_bs": p_bs,
                "precio_antes_bs": p_antes,
                "descuento": desc,
                "imagen": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{sid}/header.jpg",
                "es_vip": False,
                "score": score
            })
    except Exception as e: print(f"Error ofertas: {e}")

    return lista_final

def procesar_tiktok(tasa):
    print("\n🎵 3. Packs TikTok...")
    lista = []
    for m in TIKTOK_PACKS:
        # Costo USD * Tasa * 1.10
        costo = m * TIKTOK_COSTO_UNITARIO
        lista.append({"monedas": m, "precio_bs": math.ceil(costo * tasa * 1.10)})
    return lista

def main():
    tasa, msg = get_config()
    juegos = procesar_juegos(tasa)
    packs = procesar_tiktok(tasa)
    
    db = {
        "config": {"tasa": tasa, "celular": MI_CELULAR, "msg": msg, "costo_tk": TIKTOK_COSTO_UNITARIO},
        "juegos": juegos,
        "tiktok": packs
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4)
    
    print(f"\n✅ LISTO. {len(juegos)} Juegos | {len(packs)} Packs.")
    if input("¿Subir a GitHub? (s/n): ").lower() == 's':
        os.system("git add . && git commit -m 'Update' && git push")

if __name__ == "__main__":
    main()

