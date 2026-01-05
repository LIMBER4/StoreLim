import requests
import json
import math
import os
import time

# --- ⚙️ CONFIGURACIÓN MAESTRA ---
# Tu celular
MI_CELULAR = "59170000000" # CAMBIAR POR TU NUMERO

# TikTok: Base de costos (Extraído de tus datos: 30 monedas = 0.31 USD)
TIKTOK_COSTO_UNITARIO = 0.31 / 30 

# Paquetes a generar (Tus 5 oficiales + 2 grandes inventados)
TIKTOK_PACKS = [30, 350, 700, 1400, 3500, 7000, 17500]

# Steam
STEAM_URL = "https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=60&metacritic=75&onSale=1&pageSize=60"

def get_dolar_rate():
    """Pregunta al usuario el precio del dólar hoy"""
    os.system("clear")
    print("=================================")
    print("   👑 PANEL ADMIN: STORELIM v2   ")
    print("=================================")
    try:
        tasa = float(input("\n💵 ¿A cuánto está el Dólar Paralelo hoy? (Ej: 11.50): "))
        return tasa
    except:
        print("Error: Pon un número válido (usa punto, no coma).")
        exit()

def procesar_tiktok(tasa_dolar):
    print("🎵 Calculando precios de TikTok...")
    lista_packs = []
    
    for monedas in TIKTOK_PACKS:
        # Fórmula: (Monedas * CostoUnitario * Dolar * 1.10)
        costo_usd = monedas * TIKTOK_COSTO_UNITARIO
        precio_bs = math.ceil(costo_usd * tasa_dolar * 1.10)
        
        lista_packs.append({
            "monedas": monedas,
            "precio_bs": precio_bs
        })
    return lista_packs

def procesar_steam(tasa_dolar):
    print("🎮 Buscando ofertas en Steam...")
    lista_juegos = []
    try:
        data = requests.get(STEAM_URL).json()
        for game in data:
            steam_id = game.get('steamAppID')
            if not steam_id: continue
            
            p_usd_sale = float(game['salePrice'])
            p_usd_normal = float(game['normalPrice'])
            descuento = int(float(game['savings']))
            
            # Cálculo Bolivianos
            precio_bs = math.ceil(p_usd_sale * tasa_dolar * 1.10)
            
            lista_juegos.append({
                "id": steam_id,
                "nombre": game['title'],
                "precio_orig_usd": p_usd_normal,
                "precio_final_usd": p_usd_sale,
                "descuento": descuento,
                "precio_bs": precio_bs,
                "imagen": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{steam_id}/header.jpg"
            })
    except Exception as e:
        print(f"Error en Steam: {e}")
    
    return lista_juegos

def main():
    # 1. Pedir Dólar
    dolar_hoy = get_dolar_rate()
    
    # 2. Generar datos
    datos_steam = procesar_steam(dolar_hoy)
    datos_tiktok = procesar_tiktok(dolar_hoy)
    
    # 3. Estructura FINAL del JSON (Data Unificada)
    db_completa = {
        "config": {
            "tasa_dolar": dolar_hoy,
            "celular": MI_CELULAR,
            "costo_tiktok_unitario": TIKTOK_COSTO_UNITARIO
        },
        "tiktok_packs": datos_tiktok,
        "steam": datos_steam
    }
    
    # 4. Guardar archivo
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db_completa, f, indent=4)
        
    print(f"\n✅ TODO LISTO REY.")
    print(f"- Steam: {len(datos_steam)} juegos.")
    print(f"- TikTok: {len(datos_tiktok)} packs generados.")
    print(f"- Archivo 'data.json' actualizado.")
    
    # 5. Opción de subir automáticamente
    subir = input("\n¿Subir a GitHub ahora? (s/n): ")
    if subir.lower() == 's':
        os.system("git add .")
        os.system(f'git commit -m "Actualizacion Dolar {dolar_hoy}"')
        os.system("git push")
        print("\n🚀 ¡Subido! La web se actualizará en 1 min.")

if __name__ == "__main__":
    main()

