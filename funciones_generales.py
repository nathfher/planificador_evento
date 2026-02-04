"""Este programa contiene las funciones generales del sistema"""
from datetime import datetime,timedelta
import json
import os

def write_json(ruta,data):
    """
    Guarda información en un archivo JSON.
    Recibe la ruta del archivo y los datos (listas o diccionarios) para escribirlos 
    con un formato ordenado (indentación de 4 espacios).
    """
    with open(ruta,'w',encoding='utf-8') as f:
        json.dump(data,f,indent=4)

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

def actualizar_element(id_element, list_elements, datos_nuevos, element_tipo, nombre_archivo, llave_id):
    """
    Busca un elemento por su ID y actualiza sus datos.
    - llave_id: debe ser 'id_cliente', 'id_personal', 'id_lugar', etc.
    """
    # 1. Buscamos usando la llave exacta que pasamos por parámetro
    datos_antiguos = buscar_elemento_id(id_element, list_elements, llave_id)
    
    if datos_antiguos is None:
        print(f"Error: el '{element_tipo}' con ID: {id_element} no existe.")
        return None
    
    # 2. Actualizamos los campos
    for llave in datos_nuevos:
        # Protección para que NUNCA se cambie el ID por error
        if not llave.startswith('id'):
            datos_antiguos[llave] = datos_nuevos[llave]
    
    # 3. Guardamos los cambios en el JSON
    write_json(nombre_archivo, list_elements)
    print(f"✅ '{element_tipo}' con ID: {id_element} actualizado correctamente.")
    
    return datos_antiguos

#llave_fecha seria  ocuapdas en personal y reservadas en lugar

def get_inventario_disponibles(id_lugar,fecha_evento,lista_lugares):
    """
    Filtra los objetos del inventario de un lugar específico que no tienen 
    reservas para la fecha indicada. Retorna una lista con los objetos libres.
    """
    lugar = buscar_elemento_id(id_lugar,lista_lugares,'id_lugar')
    if lugar is None:
        print("El lugar no existe")
        return False
    inventario_libre = []
    for objeto in lugar['inventario']:
        if fecha_evento not in objeto['fechas ocupadas']:
            inventario_libre.append(objeto)
    return inventario_libre

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
    """
    Construye el objeto maestro de la cotización con toda la metadata del evento.
    
    Realiza las siguientes acciones:
    1. Ejecuta los cálculos financieros detallados.
    2. Registra el bloque horario y calcula la duración del evento.
    3. Estructura un diccionario final listo para ser guardado o impreso.
    """
    # 1. CÁLCULO DE COSTOS
    costo_inv = calcular_costo_inventario(lista_items)
    costo_pers = sum(p.sueldo for p in sel_pers)
    costo_lug = lug_elegido['precio']

    # Calculamos el total (asegúrate de que calculate_total maneje estos 3 montos)
    subtotal = costo_inv + costo_lug + costo_pers
    comision_val = subtotal * 0.10  # 10% de Wedding Planner
    total = calculate_total(costo_inv, costo_pers, costo_lug)
    # 2. CREAR EL DICCIONARIO FINAL (Incluyendo las nuevas variables)
    cotizacion_final = {
        'id_lugar': lug_elegido['id_lugar'],
        'nombre_lugar': lug_elegido['nombre'], # Útil para el ticket
        'cliente': cliente.nombre,
        'fecha': fecha,
        'h_inicio': h_inicio,      # <--- GUARDADO
        'h_fin': h_fin,            # <--- GUARDADO
        'personal_contratado': sel_pers, 
        'items_pedidos': lista_items,
        'subtotal': subtotal,
        'comision': comision_val,
        'total_final': total, # Cambié 'total' por 'total_final' para coincidir con tu pl_boda
        'estado': 'Pendiente'
    }

    return cotizacion_final


def guardar_cotizacion(cotizacion_reciente, list_cotizaciones):
    """Agrega una nueva cotización al historial y la guarda en el archivo físico.

    Esta función actualiza la lista de cotizaciones en la memoria del programa 
    y sincroniza esos cambios con el archivo 'cotizaciones.json' para que 
    la información sea persistente.

    Args:
        cotizacion_reciente (dict): El diccionario que contiene todos los datos 
            de la cotización que se acaba de generar.
        list_cotizaciones (list): La lista que contiene todas las cotizaciones 
            previas cargadas desde el sistema.

    Returns:
        None: La función no devuelve valores, realiza una acción de guardado 
            y muestra un mensaje de confirmación"""
    list_cotizaciones.append(cotizacion_reciente)
    write_json('cotizaciones.json', list_cotizaciones)
    print("Cotización guardada en el historial.")


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

def bloquear_fecha(id_element,list_element,fecha_nueva):
    """Bloquea la fecha que ha sido ocuapda"""
    exito_element = buscar_elemento_id(id_element,list_element, 'id_element')
    if exito_element is None:
        return 'El ID introducido no existe'
    if fecha_nueva not in exito_element['fechas_ocupadas']:
        exito_element['fechas_ocupadas'].append(fecha_nueva)
        # 2. Identificamos si es lugar o personal para dar el mensaje correcto
        if 'id_lugar' in exito_element:
            print(f"✅ El lugar: {exito_element['nombre']} bloqueado para el {fecha_nueva}")
        elif 'id_personal' in exito_element:
            print(f"✅ El trabajador: {exito_element['nombre']} bloqueado para el {fecha_nueva}")
        return True
    else:
        print(f"❌ Error: La fecha {fecha_nueva} ya está ocupada para {exito_element['nombre']}")
        return False

def procesar_confirmacion_boda(cotizacion, lista_lugares, lista_personal, lista_inventario):
    # Creamos el bloque horario que se guardará en los archivos
    bloque = {
        "fecha": cotizacion['fecha'],
        "inicio": cotizacion['h_inicio'],
        "fin": cotizacion['h_fin']
    }

    # Bloqueamos el lugar
    for lug in lista_lugares:
        if lug['id_lugar'] == cotizacion['id_lugar']:
            lug['fechas_ocupadas'].append(bloque) # <--- Guardamos el diccionario

    # Bloqueamos al personal
    for p_contratado in cotizacion['personal_contratado']:
        for p_total in lista_personal:
            if p_total['id_personal'] == p_contratado.id_personal:
                p_total['fechas_ocupadas'].append(bloque)
    # 4. DESCUENTO DE INVENTARIO
    for item in cotizacion['items_pedidos']:
        for inv in lista_inventario:
            # Buscamos por ID que es más seguro que el nombre
            if inv['id_item'] == item.id_item_reserva:
                inv['cantidad'] -= item.cantidad_requerida

    print("¡SISTEMA ACTUALIZADO! Todos los recursos han sido bloqueados.")

def limpiar_pantalla():
    # 'nt' es para Windows, 'posix' para Mac o Linux
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def guardar_reserva_json(nueva_boda):
    # 1. Decimos dónde se va a guardar (en la carpeta data)
    nombre_archivo = 'data/historial_reservas.json'

    # 2. Leemos lo que ya hay en el archivo.
    # Si no existe, historial será una lista vacía []
    historial = ensure_file_exist(nombre_archivo, [])

    # 3. Convertimos la boda en un "diccionario" (formato JSON)
    # Como 'nueva_boda' es un objeto de clase, necesitamos vars()
    boda_diccionario = vars(nueva_boda)

    # 4. Agregamos la nueva boda a la lista que ya teníamos
    historial.append(boda_diccionario)

    # 5. Escribimos la lista completa de nuevo en el archivo
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)
    
    print("✅ La boda se guardó correctamente en el historial.")

def liberar_recursos(cotizacion, lista_lugares, lista_personal, lista_inventario):
    fecha_boda = cotizacion['fecha']

    # 1. Liberar lugar
    lugar = buscar_elemento_id(cotizacion['id_lugar'], lista_lugares, 'id_lugar')
    if lugar:
        lugar['fechas_ocupadas'] = [f for f in lugar['fechas_ocupadas'] if f['fecha'] != fecha_boda]

    # 2. Liberar personal
    for p_contratado in cotizacion['personal_contratado']:
        p_maestro = buscar_elemento_id(p_contratado.id_personal, lista_personal, 'id_personal')
        if p_maestro:
            p_maestro['fechas_ocupadas'] = [f for f in p_maestro['fechas_ocupadas'] if f['fecha'] != fecha_boda]

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
        f.write(f"COSTO LUGAR: ${lugar['costo']}\n\n")

        # Uso de 'personal'
        f.write("PERSONAL CONTRATADO:\n")
        for p in personal:
            # Aquí 'p' es un objeto de la clase Personal
            f.write(f"- {p.nombre} ({p.oficio}): ${p.sueldo}\n")

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


def validar_restricciones_inteligentes(personal_contratado, servicios_elegidos, lugar_seleccionado):
    """
    Analiza la combinación de recursos para evitar conflictos de negocio.
    """
    # 1. Normalizamos a minúsculas para que la búsqueda no falle por una mayúscula
    oficios_p = [p.oficio.lower() for p in personal_contratado]
    nombres_s = [s.nombre.lower() for s in servicios_elegidos]
    nombre_lugar = lugar_seleccionado['nombre'].lower()
    
    # --- REGLA 1: CO-REQUISITOS (Necesitas A para tener B) ---

    # Si eligen 'Barra Libre de Coctelería' (catering.json)
    if any("coctelería" in s for s in nombres_s):
        # Debe haber alguien con oficio 'Sommelier / Barman' (personal.json)
        if not any("barman" in o for o in oficios_p):
            return False, "La 'Barra Libre' requiere contratar al 'Sommelier / Barman' en el paso de Personal."

    # Si eligen 'Solo de Violín Eléctrico' (musica.json)
    if any("violín" in s for s in nombres_s):
        # Exigimos al 'Maestro de Ceremonias' (personal.json)
        if "maestro de ceremonias" not in oficios_p:
            return False, "El 'Solo de Violín' requiere un 'Maestro de Ceremonias' para el protocolo."


    # --- REGLA 2: EXCLUSIÓN MUTUA (No puedes mezclar A con B) ---

    # Si el lugar es el 'Palacio de Cristal'
    if "cristal" in nombre_lugar:
        # No permitimos 'Mariachi Real de Oro' (por el eco y volumen en cristal)
        if any("mariachi" in s for s in nombres_s):
            return False, "El Palacio de Cristal no admite Mariachis por restricciones de acústica."

    # Si contratan al 'DJ Carlos'
    if "música" in oficios_p and any("dj" in p.nombre.lower() for p in personal_contratado):
        # No pueden contratar la 'Banda de Rock' (conflicto de equipos de sonido)
        if any("rock" in s for s in nombres_s):
            return False, "No se puede tener DJ y Banda de Rock en el mismo evento (conflicto de audio)."
    # En tu personal tienes "Maquillaje y Peinado". 
    # Si alguien elige un "Banquete Gala" (Catering), el protocolo exige verse impecable.
    if any("gala" in s for s in nombres_s) and "maquillaje y peinado" not in oficios_p:
        return False, "Los eventos de 'Gala' requieren contratar el servicio de 'Maquillaje y Peinado' para los anfitriones."

    # 2. REGLA DE SEGURIDAD EN TERRAZA (Lugar + Personal)
    # Tu 'Terraza del Sol' tiene una piscina. Por seguridad, no debería alquilarse sin vigilancia.
    if "terraza" in nombre_lugar and "seguridad" not in str(oficios_p):
        return False, "La 'Terraza del Sol' tiene piscina y requiere contratar 'Seguridad y Valet Parking' obligatorio."
    # Si todo pasó las pruebas:
    return True, ""