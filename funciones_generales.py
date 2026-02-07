"""Este programa contiene las funciones generales del sistema"""
from datetime import datetime,timedelta
from modulos import Personal,ItemReserva
import json
import os

def write_json(ruta,data):
    """
    Guarda información en un archivo JSON.
    Recibe la ruta del archivo y los datos (listas o diccionarios) para escribirlos 
    con un formato ordenado (indentación de 4 espacios).
    """
    with open(ruta,'w',encoding='utf-8') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)

def ensure_file_exist(ruta,data_inicial):
    """
    Verifica si un archivo existe. Si existe, lo lee y devuelve su contenido.
    Si no existe, crea el archivo con la 'data_inicial' que le enviemos 
    (por ejemplo, una lista vacía []) para evitar errores de lectura.
    """
    if os.path.exists(ruta):
        with open(ruta,'r',encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(ruta,'w',encoding='utf-8') as f:
            if data_inicial is not None:
                json.dump(data_inicial,f,indent=4)
            else:
                json.dump({},f,indent=4)
    return data_inicial

def buscar_elemento_id(id_buscado, list_elements, llave_id):
    """
    Busca un ID comparándolo únicamente con la llave específica (ej: 'id_item').
    Esto evita confusiones entre archivos.
    """
    for element in list_elements:
        # Usamos .get() para que si la llave no existe en ese objeto, no explote
        if element.get(llave_id) == id_buscado:
            return element
    return None

def hay_conflicto_horario(lista_reservas, fecha_nueva, h_ini_nueva, h_fin_nueva):
    """
    Comprueba si el nuevo horario choca con las reservas existentes.
    """
    for reserva in lista_reservas:
        # PRIMERO: Nos aseguramos de que 'reserva' sea un diccionario
        if not isinstance(reserva, dict):
            continue

        if reserva.get('fecha') == fecha_nueva:
            # Extraemos horas y convertimos a objetos time para comparar
            formato = "%H:%M"
            h_ini_ex = datetime.strptime(reserva['hora_inicio'], formato).time()
            h_fin_ex = datetime.strptime(reserva['hora_fin'], formato).time()

            nueva_ini = datetime.strptime(h_ini_nueva, formato).time()
            nueva_fin = datetime.strptime(h_fin_nueva, formato).time()

            # Lógica de colisión de intervalos
            if (nueva_ini < h_fin_ex) and (nueva_fin > h_ini_ex):
                return True # ¡Hay choque!
    return False


def get_personal_disponible(tipo_buscado, lista_personal, fecha, h_ini, h_fin):
    disponibles = []
    formato_hora = "%H:%M"

    # 1. NORMALIZACIÓN DE BÚSQUEDA
    busqueda = tipo_buscado.lower().strip().replace("ú", "u").replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o")

    try:
        boda_inicio = datetime.strptime(h_ini, formato_hora).time()
        boda_fin = datetime.strptime(h_fin, formato_hora).time()

        for p in lista_personal:
            # 2. NORMALIZACIÓN DEL DATO DEL JSON
            # Buscamos en 'categoria' o en 'oficio' para mayor seguridad
            categoria_trabajador = p.get('categoria', p.get('oficio', '')).lower().replace("ú", "u").replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o")

            if busqueda in categoria_trabajador:

                # 3. FILTRO DE FECHA (Bloqueos totales por vacaciones/feriados)
                fechas_bloqueadas = p.get('fechas_ocupadas', [])
                if fecha in fechas_bloqueadas:
                    continue

                # 4. FILTRO DE HORARIO (Agenda del día)
                agenda_dia = p.get('agenda', {}).get(fecha, [])
                hay_conflicto = False

                for intervalo in agenda_dia:
                    hora_ocu_ini = datetime.strptime(intervalo['inicio'], formato_hora).time()
                    hora_ocu_fin = datetime.strptime(intervalo['fin'], formato_hora).time()

                    # Lógica de solapamiento
                    if boda_inicio < hora_ocu_fin and boda_fin > hora_ocu_ini:
                        hay_conflicto = True
                        break

                # 5. RESULTADO FINAL
                # Debe estar FUERA del bucle 'for intervalo', pero DENTRO del 'if busqueda'
                if not hay_conflicto:
                    disponibles.append(p)

    except (ValueError, TypeError, KeyError) as e:
        # CORRECCIÓN: Usamos 'as e' para ver el error real, no el nombre de la variable buscada
        print(f"⚠️ Error técnico al validar disponibilidad: {e}")
        return []

    return disponibles

def get_lugares_disponibles(fecha_str, lista_lugares, h_ini, h_fin, invitados):
    """
    Motor de búsqueda de ubicaciones con sistema de recomendación:
    1. Busca lugares que cumplan con la capacidad y disponibilidad horaria.
    2. Si no hay éxito, busca automáticamente en los 3 días posteriores para 
       sugerir alternativas al usuario.
    Retorna una tupla (lista_disponibles, lista_sugerencias).
    """
    # 1. Intento original
    disponibles = []
    for lugar in lista_lugares:
        if lugar['capacidad'] >= invitados:
            if not hay_conflicto_horario(lugar['fechas_ocupadas'], fecha_str, h_ini, h_fin):
                disponibles.append(lugar)

    # 2. Si hay disponibles, los retornamos normal
    if disponibles:
        return disponibles, None # None significa que no hubo necesidad de sugerencias

    # 3. SI NO HAY: Buscamos sugerencias (Motor Inteligente)
    sugerencias = []
    fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")

    # Buscamos en los próximos 3 días
    for i in range(1, 4):
        nueva_fecha_obj = fecha_obj + timedelta(days=i)
        nueva_fecha_str = nueva_fecha_obj.strftime("%d/%m/%Y")

        for lugar in lista_lugares:
            if lugar['capacidad'] >= invitados:
                if not hay_conflicto_horario(lugar['fechas_ocupadas'], nueva_fecha_str, h_ini, h_fin):
                    sugerencias.append({
                        "nombre": lugar['nombre'],
                        "fecha": nueva_fecha_str
                    })

    return [], sugerencias

def contratar_personal(lista_personal,id_personal):
    """
    Busca y selecciona a un trabajador del equipo para incluirlo en una boda.
        Returns
        dict: El diccionario con los datos del trabajador si se encuentra.
        None: Si el ID no existe en la lista, permitiendo manejar el error.
    """
    trabajador_encontrado = buscar_elemento_id(id_personal,lista_personal, 'id_personal')
    if trabajador_encontrado is None:
        print('El ID no existe')
        return None
    print(f"¡{trabajador_encontrado['nombre']} seleccionado con éxito!")
    return trabajador_encontrado #la list_contratados la lleno en el main


def calcular_costo_inventario(lista_items):
    """
    Suma el subtotal de todos los servicios elegidos (Catering y Música).
    """
    total = 0
    for i in lista_items:
        # Como 'i' es un objeto de clase ItemReserva, usamos sus funciones
        total += i.calcular_subtotal()
    return total

def calculate_total(costo_inv: float,
                    costo_pers:float,
                    costo_lug:float,):
    """
    Calcula el presupuesto final de la boda aplicando cargos adicionales.
    
    Suma los tres costos base (inventario, personal y lugar) y añade un 26% 
    extra que corresponde a:
    - 10% por honorarios del Wedding Planner.
    - 16% por impuestos (IVA).
    """
    costo_total = costo_inv + costo_pers + costo_lug
    extras = costo_total*0.26 #suma 0,10 de costo_wedding planner y 0,16 de impuestos
    return costo_total + extras

def build_cotizacion(cliente, lug_elegido, sel_pers, lista_items, fecha, h_inicio, h_fin):
    # 1. CÁLCULO DE COSTOS BASE
    costo_inv = calcular_costo_inventario(lista_items)
    costo_pers = sum(p.sueldo for p in sel_pers)
    costo_lug = lug_elegido['precio']

    # 2. CÁLCULOS FINANCIEROS
    subtotal = costo_inv + costo_lug + costo_pers
    comision_val = subtotal * 0.10  # 10% de Wedding Planner
    total_final = subtotal + comision_val # <--- AQUÍ: Sumar la comisión al total

    # 3. ESTRUCTURA FINAL
    cotizacion_final = {
        'id_lugar': lug_elegido['id_lugar'],
        'nombre_lugar': lug_elegido['nombre'],
        'cliente': cliente.nombre,
        'fecha': fecha,
        'h_inicio': h_inicio,
        'h_fin': h_fin,
        'personal_contratado': sel_pers, 
        'items_pedidos': lista_items,
        'subtotal': subtotal,
        'comision': comision_val,
        'total_final': total_final, # Asegúrate de que este nombre coincida con el ticket
        'estado': 'Pendiente'
    }
    return cotizacion_final

def approve_cotizacion(cotizacion, lista_lugares, lista_personal,lista_inventario):
    """Evita reservas accidentales, avisa si se gaurda la cot o no con bool"""
    print(f"RESUMEN DE COTIZACIÓN PARA: {cotizacion['cliente']}")
    print(f"TOTAL A PAGAR: ${cotizacion['total_final']}")

    confirmar = input("¿Desea confirmar y aprobar esta boda? (S/N): ").lower()

    if confirmar == 'si':
        cotizacion['estado'] = 'Aprobado'
        print("Boda aprobada oficialmente.")
        return True
    else:
        print("Cotización rechazada. Liberando recursos...")
        # AQUÍ RESOLVEMOS EL DETALLE:
        liberar_recursos(cotizacion, lista_lugares, lista_personal,lista_inventario)
        return False

def procesar_confirmacion_boda(cotizacion, lista_lugares, lista_personal, lista_inventario):
    # este es el bloque horario que se guardará en los archivos
    bloque = {
        "fecha": cotizacion['fecha'],
        "inicio": cotizacion['h_inicio'],
        "fin": cotizacion['h_fin']
    }

    # 1. Bloqueamos el lugar
    for lug in lista_lugares:
        if lug['id_lugar'] == cotizacion['id_lugar']:
            if 'fechas_ocupadas' not in lug:
                lug['fechas_ocupadas'] = []
            lug['fechas_ocupadas'].append(bloque)

    # 2. Bloqueamos al personal
    for p_contratado in cotizacion['personal_contratado']:
        for p_total in lista_personal:
            # p_contratado es OBJETO (usa punto .id_personal)
            # p_total es DICCIONARIO (usa corchetes ['id_personal'])
            if p_total.get('id_personal') == p_contratado.id_personal:
                if 'fechas_ocupadas' not in p_total:
                    p_total['fechas_ocupadas'] = []
                p_total['fechas_ocupadas'].append(bloque)

    # 3. DESCUENTO DE INVENTARIO
    for item in cotizacion['items_pedidos']:
        for inv in lista_inventario:
            if inv['id_item'] == item.id_item_reserva:
                inv['cantidad'] -= item.cantidad_requerida

    print("¡SISTEMA ACTUALIZADO! Todos los recursos han sido bloqueados.")

def limpiar_pantalla():
    # 'nt' es para Windows, 'posix' para Mac o Linux
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def guardar_reserva_json(cotizacion):
    # 1. Decimos dónde se va a guardar (en la carpeta data)
    nombre_archivo = 'data/historial_reservas.json'

    # 2. Leemos lo que ya hay en el archivo.
    # Si no existe, historial será una lista vacía []
    historial = ensure_file_exist(nombre_archivo, [])
    boda_para_guardar = cotizacion.copy() # Copiamos para no dañar la original
# Convertimos los objetos de personal a diccionarios
    boda_para_guardar['personal_contratado'] = [
        vars(p) if hasattr(p, '__dict__') else p for p in cotizacion['personal_contratado']
    ]
    # Convertimos los objetos de servicios a diccionarios
    boda_para_guardar['items_pedidos'] = [
        vars(s) if hasattr(s, '__dict__') else s for s in cotizacion['items_pedidos']
    ]

    historial.append(boda_para_guardar)
    write_json(nombre_archivo, historial)
    print("✅ Boda guardada en el historial de reservas.")

    print("✅ La boda se guardó correctamente en el historial.")

def liberar_recursos(cotizacion, lista_lugares, lista_personal, lista_inventario):
    fecha_boda = cotizacion['fecha']

    # 1. Liberar lugar
    lugar = buscar_elemento_id(cotizacion['id_lugar'], lista_lugares, 'id_lugar')
    if lugar:
        lugar['fechas_ocupadas'] = [f for f in lugar['fechas_ocupadas'] if f['fecha'] != fecha_boda]

    # 2. Liberar personal
    for p_contratado in cotizacion['personal_contratado']:
        # Obtenemos el ID de forma segura sea objeto o dicc
        id_a_liberar = getattr(p_contratado, 'id_personal', None) or p_contratado.get('id_personal')
        
        p_maestro = buscar_elemento_id(id_a_liberar, lista_personal, 'id_personal')
        
        if p_maestro:
            # Filtramos para quitar el bloque horario de esa fecha
            p_maestro['fechas_ocupadas'] = [f for f in p_maestro.get('fechas_ocupadas', []) 
                                            if f.get('fecha') != fecha_boda]
    # 3. Devolver Inventario
    for servicio in cotizacion['items_pedidos']:
        for item_inv in lista_inventario:
            if item_inv['id_item'] == servicio.id_item_reserva:
                item_inv['cantidad'] += servicio.cantidad_requerida

def generar_ticket(cliente, lugar, personal, servicios, subtotal, comision, total, fecha_boda):
    with open("ticket_boda.txt", "w", encoding="utf-8") as f:
        f.write("==========================================\n")
        f.write("          TICKET DE RESERVA - BODA        \n")
        f.write("==========================================\n\n")

        # Uso de 'cliente' y 'fecha_boda'
        f.write(f"CLIENTE: {cliente.nombre}\n")
        f.write(f"EMAIL: {cliente.email}\n")
        f.write(f"FECHA DEL EVENTO: {fecha_boda.strftime('%d de %B de %Y')}\n")
        f.write("------------------------------------------\n\n")

        # Uso de 'lugar'
        f.write(f"LUGAR SELECCIONADO: {lugar['nombre']}\n")
        f.write(f"COSTO LUGAR: ${lugar['precio']}\n\n")

        # Uso de 'personal'
        f.write("PERSONAL CONTRATADO:\n")
        for p in personal:
            # Aquí 'p' es un objeto de la clase Personal
            f.write(f"- {p.nombre} ({p.oficio} - Nivel: {p.experiencia}): ${p.sueldo}\n")

        # Uso de 'servicios'
        f.write("\nSERVICIOS ADICIONALES:\n")
        for item in servicios:
            # Aquí 'item' es un objeto ItemReserva
            f.write(f"- {item.nombre} (x{item.cantidad_requerida}): ${item.calcular_subtotal()}\n")

        f.write("\n------------------------------------------\n")
        # Uso de 'subtotal', 'comision' y 'total'
        f.write(f"SUBTOTAL: ${subtotal:.2f}\n")
        f.write(f"COMISIÓN (15%): ${comision:.2f}\n")
        f.write(f"TOTAL FINAL: ${total:.2f}\n")
        f.write("------------------------------------------\n")
        f.write("\n¡Gracias por confiar en nosotros!")

def can_select_lugar(presupuesto_cliente, precio_lugar):
    """
    Comprueba si el cliente tiene dinero suficiente para el salón.
    """
    if presupuesto_cliente >= precio_lugar:
        return True
    else:
        return False

def imprimir_tabla_personal(lista_disponibles):
    """Dibuja la tabla con la nueva columna de EXPERIENCIA"""
    if not lista_disponibles:
        return # Si no hay nadie, no dibuja nada

    # Ajustamos el ancho para que se vea profesional
    print(f"\n{'ID':<5} | {'NOMBRE':<22} | {'EXPERIENCIA':<18} | {'SUELDO'}")
    print("-" * 65)

    for p in lista_disponibles:
        # Extraemos con .get para que si no existe 'experiencia' no explote
        idx = p.get('id_personal', '??')
        nom = p.get('nombre', 'N/A')
        exp = p.get('experiencia', 'Estandar') # Aquí saldrá "Alta" o "Media"
        sue = p.get('sueldo', 0)

        print(f"{idx:<5} | {nom:<22} | {exp:<18} | ${sue:<10}")
    print("-" * 65)

def val_restricc(personal_contratado, servicios_elegidos, lugar_seleccionado, num_invitados):
    # 1. NORMALIZACIÓN (Fundamental para evitar errores de tildes o mayúsculas)
    oficios_p = [p.oficio.lower().strip() for p in personal_contratado]
    nombres_s = [s.nombre.lower().strip() for s in servicios_elegidos]
    # CORRECCIÓN: Usamos una variable distinta para no sobreescribir el diccionario original
    nombre_lug = lugar_seleccionado['nombre'].lower()

    # --- REGLA 1: CO-REQUISITOS (Dependencias) ---
    if any("cocteleria" in s or "barra libre" in s for s in nombres_s):
        if not any("barman" in o or "sommelier" in o for o in oficios_p):
            return False, "La 'Barra Libre' requiere contratar al 'Sommelier / Barman'."

    if any("violin" in s for s in nombres_s):
        if not any("maestro de ceremonias" in o for o in oficios_p):
            return False, "El 'Solo de Violín' requiere un 'Maestro de Ceremonias'."

    # --- REGLA 2: EXCLUSIONES (Lo que NO puede ir junto) ---
    # Conflicto de Acústica en el Palacio de Cristal
    if "cristal" in nombre_lug and any("mariachi" in s for s in nombres_s):
        return False, "El Palacio de Cristal no admite Mariachis por restricciones de eco."

    # Conflicto de Audio: DJ vs Banda de Rock
    tiene_dj = any("dj" in o for o in oficios_p)
    tiene_rock = any("rock" in s for s in nombres_s)
    if tiene_dj and tiene_rock:
        return False, "Conflicto de audio: No se puede contratar DJ y Banda de Rock simultáneamente."

    # --- REGLA 3: SEGURIDAD ---
    # La Terraza requiere seguridad por la piscina
    if "terraza" in nombre_lug and not any("seguridad" in o for o in oficios_p):
        return False, "La 'Terraza del Sol' requiere 'Seguridad' obligatorio por la piscina."

    # --- REGLA 4: MOBILIARIO ---
    cant_sillas = sum(s.cantidad_requerida for s in servicios_elegidos if "silla" in s.nombre.lower())
    if num_invitados > 0 and cant_sillas < (num_invitados * 0.8):
        return False, f"Mobiliario insuficiente: Tiene {cant_sillas} sillas para {num_invitados} invitados (Mín. 80%)."

    # --- REGLA 5: INFRAESTRUCTURA (Tecnología) ---
    necesita_audio = any(m in s for s in nombres_s for m in ["dj", "rock", "banda", "mariachi"])
    tiene_equipo = any("sonido" in s or "parlante" in s for s in nombres_s)
    if necesita_audio and not tiene_equipo:
        return False, "Música detectada: Es obligatorio incluir 'Equipo de Sonido Profesional'."

    return True, ""