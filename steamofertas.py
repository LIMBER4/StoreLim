import requests
import json
import os
import time
import schedule
import subprocess
import math

# --- ⚙️ CONFIGURACIÓN DEL CAZADOR ---
METACRITIC_MIN = 75       # Bajé un poco para que salgan más juegos en la web
DESCUENTO_MIN = 50        # Porcentaje mínimo de descuento
CHECK_INTERVAL_HOURS = 4  # Cada cuántas horas buscar
HISTORIAL_FILE = "ofertas_vistas.json"
WEB_FILE = "juegos.json"  # EL ARCHIVO PARA TU PÁGINA WEB

# --- 🇧🇴 CALCULADORA BOLIVIA ---
DOLAR_PARALELO = 9.98    # ¿A cuánto consigues el dólar/saldo? (Edita esto)
COMISION = 0.10           # Tu ganancia (10%)

# API de CheapShark (Store ID 1 = Steam)
API_URL = f"https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=60&metacritic={METACRITIC_MIN}&onSale=1&sortBy=Savings&pageSize=60" 
# Nota: Añadí 'pageSize=60' para que tu catálogo tenga bastantes juegos.

def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def guardar_historial(vistos):
    with open(HISTORIAL_FILE, "w") as f:
        json.dump(list(vistos), f)

def calcular_precio_bs(precio_usd):
    """Convierte USD a Bolivianos, suma comisión y redondea."""
    costo = float(precio_usd) * DOLAR_PARALELO
    precio_final = costo * (1 + COMISION)
    # Redondear al entero superior (ej: 45.2 -> 46) para que se vea limpio
    return math.ceil(precio_final)

def notificar(titulo, precio_bs, descuento, link):
    """Envía notificación a Android."""
    mensaje = f"🇧🇴 {precio_bs} Bs. | -{descuento}% OFF"
    cmd = [
        "termux-notification",
        "--title", f"🔥 {titulo}",
        "--content", mensaje,
        "--priority", "high",
        "--button1", "VER EN STEAM",
        "--button1-action", f"termux-open-url '{link}'"
    ]
    subprocess.run(cmd)

def buscar_ofertas():
    print(f"\n[{time.strftime('%H:%M')}] 🔎 Escaneando ofertas y actualizando la WEB...")

    vistos = cargar_historial()
    catalogo_web = [] # Aquí guardaremos la lista para la página

    try:
        response = requests.get(API_URL, timeout=10)
        ofertas = response.json()

        count_notif = 0
        
        for game in ofertas:
            try:
                # Datos básicos
                deal_id = game['dealID']
                titulo = game['title']
                descuento = float(game['savings'])
                steam_id = game.get('steamAppID', None)
                precio_sale_usd = float(game['salePrice'])

                # Si no tiene ID de steam, lo saltamos (necesitamos la imagen)
                if not steam_id:
                    continue

                # --- 1. PREPARAR DATOS PARA LA WEB ---
                # Calculamos el precio en Bolivianos
                precio_en_bolivianos = calcular_precio_bs(precio_sale_usd)
                
                # Creamos el objeto del juego para el JSON
                juego_para_web = {
                    "id": steam_id,
                    "nombre": titulo,
                    "precio": precio_en_bolivianos,
                    "imagen": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{steam_id}/header.jpg"
                }
                
                # Lo añadimos a la lista del catálogo
                catalogo_web.append(juego_para_web)

                # --- 2. SISTEMA DE NOTIFICACIONES (Solo si es nuevo) ---
                if deal_id not in vistos and descuento >= DESCUENTO_MIN:
                    link_steam = f"https://store.steampowered.com/app/{steam_id}/"
                    
                    print(f"✅ Nuevo: {titulo} -> {precio_en_bolivianos} Bs")
                    notificar(titulo, precio_en_bolivianos, int(descuento), link_steam)
                    
                    vistos.add(deal_id)
                    count_notif += 1
                    time.sleep(1) # Pausa pequeña

            except Exception as e:
                print(f"Error procesando un juego: {e}")
                continue

        # --- 3. GUARDAR ARCHIVOS ---
        
        # A) Guardar historial de notificaciones
        if count_notif > 0:
            guardar_historial(vistos)
            print(f"✨ Se notificaron {count_notif} ofertas nuevas.")
        
        # B) GUARDAR EL JSON PARA LA WEB (Esto es lo nuevo)
        # Esto sobrescribe el archivo juegos.json con las ofertas ACTUALES
        with open(WEB_FILE, 'w', encoding='utf-8') as f:
            json.dump(catalogo_web, f, indent=4, ensure_ascii=False)
        
        print(f"🌐 Web Actualizada: {len(catalogo_web)} juegos guardados en '{WEB_FILE}'")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

# --- 🚀 MOTOR PRINCIPAL ---
def main():
    os.system("clear")
    print("=======================================")
    print("   🇧🇴 STEAM BOLIVIA UPDATER 🇧🇴       ")
    print(f"   Dólar: {DOLAR_PARALELO} Bs | Margen: {int(COMISION*100)}%")
    print("=======================================")

    buscar_ofertas() # Ejecutar al iniciar

    schedule.every(CHECK_INTERVAL_HOURS).hours.do(buscar_ofertas)

    print(f"\n💤 Esperando {CHECK_INTERVAL_HOURS} horas para la próxima actualización...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()

