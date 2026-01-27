"""Este programa contiene las funciones generales del sistema"""
import json
import os

def write_json(ruta,data):
    """Escribe datos en archivos JSON"""
    with open(ruta,'w',encoding='utf-8') as f:
        json.dump(data,f,indent=4)

def ensure_file_exist(ruta,data_inicial):
    """Se asegura que existe el archivo, y si no existe, lo crea"""
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

def guardar_elemento(mi_elemento, list_elements, nombre_archivo):
    """Toma a un elemento nuevo y lo registra en la lista general""" 
    nuevo_elemento_dict = vars(mi_elemento).copy() #elemento = cliente,lugar,trabajador
    list_elements.append(nuevo_elemento_dict)
    write_json(nombre_archivo, list_elements)
    print(f"Registro: {mi_elemento.nombre} guardado en {nombre_archivo} con éxito.")

def buscar_elemento_id(id_buscado,list_elements):
    """Busca cualquier elemento revisando sus llaves de ID"""
    for element in list_elements:
        for llave in element:
            if llave.startswith('id') and element[llave] == id_buscado:
                return element
    return None

def actualizar_element(id_element,list_elements,datos_nuevos,element,nombre_archivo):
    """Busca el elemento y si lo encuentra, cambia sus datos por los nuevos"""
    datos_antiguos = buscar_elemento_id(id_element,list_elements)
    if datos_antiguos is None:
        print(f'Error: el {element} con ID: {id_element} no existe.')
        return
    else:
        for llave in datos_nuevos: #llave sería nombre,email, id no se puede mod
            if not llave.startswith('id'):
                datos_antiguos[llave] = datos_nuevos[llave]
    write_json(nombre_archivo, list_elements)
    print(f"'{element}': {id_element} actualizado.")
    return datos_antiguos

def eliminar_elemento(id_eliminar,list_elements,nombre_archivo,llave_id):
    """Crea una lista nueva con todos los clientes exceptuando al eliminado"""
    lista_nueva = []
    element_a_borrar = buscar_elemento_id(id_eliminar,list_elements)
    if element_a_borrar is None:
        return list_elements
    name_element = element_a_borrar['nombre']
    for i in list_elements:
        if i[llave_id] != id_eliminar:
            lista_nueva.append(i)
    write_json(nombre_archivo,lista_nueva)
    print(f'Se ha eliminado a {name_element}, ID: {id_eliminar}')
    return lista_nueva
#llave_fecha seria  ocuapdas en personal y reservadas en lugar
def reservar_fecha(id_elemento,list_elements,fecha_evento,llave_fechas,nombre_archivo):
    """Verifica la disponibilidad de las fechas"""
    elemento_completo = buscar_elemento_id(id_elemento,list_elements) #me devuelve el diccionario
    if elemento_completo is None:
        print("El Id introducido no existe")
        return False
    if fecha_evento in elemento_completo[llave_fechas]:
        print(" Fecha ocupada")
        return False
    else:
        elemento_completo[llave_fechas].append(fecha_evento)
        print("¡Reserva guardada!")
        write_json(nombre_archivo,list_elements)

def eliminar_fecha(id_elemento,list_elements,fecha_evento,llave_fechas,nombre_archivo):
    """Elimina la fecha que se introduce y que se halla en la lista"""
    elemento_completo = buscar_elemento_id(id_elemento,list_elements) #me devuelve el diccionario
    if elemento_completo is None:
        print("El Id no existe")
        return False
    if fecha_evento in elemento_completo[llave_fechas]:
        elemento_completo[llave_fechas].remove(fecha_evento)
        print("¡Reserva eliminada!")
        write_json(nombre_archivo,list_elements)
        return True
    return False

def mostar_lugares(lista_encontrada):
    """Muestra el diccionario de lugares disponibles"""
    if not lista_encontrada:
        print("No hay salones disponibles para esta fecha")
    else:
        print("SALONES DISPONIBLES")
        for l in lista_encontrada:
            print(f"ID: {l['id_lugar']} | {l['nombre']}"
                f"Capacidad: {l['capacidad']} personas | Precio: ${l['costo']}")

        print('')

def mostrar_personal(lista_encontrada):
    """Muestra el diccionario de trabajadores disponibles"""
    if not lista_encontrada:
        print("No se encontró personal disponible")
    else:
        print("PROFESIONALES DISPONIBLES")
        for p in lista_encontrada:
            # Usamos f-strings para que el print sea limpio
            print(f"ID: {p['id_personal']} | Nombre: {p['nombre']} | Costo: ${p['sueldo']}")
        print('')


def get_inventario_disponibles(id_lugar,fecha_evento,lista_lugares):
    """Muesta una lista con los objetos disponibles"""
    lugar = buscar_elemento_id(id_lugar,lista_lugares)
    if lugar is None:
        print("El lugar no existe")
        return False
    inventario_libre = []
    for objeto in lugar['inventario']:
        if fecha_evento not in objeto['fechas ocupadas']:
            inventario_libre.append(objeto)
    return inventario_libre

def hay_conflicto_horario(reserva, fecha_nueva, h_ini_nueva, h_fin_nueva):
    """
    Compara una reserva existente con la nueva petición.
    reserva: dict con {'fecha': '...', 'inicio': int, 'fin': int}
    """
    if reserva['fecha'] == fecha_nueva:
        # Regla de oro: Chocan si el inicio de uno es antes del fin del otro 
        # Y el fin de uno es después del inicio del otro.
        if h_ini_nueva < reserva['fin'] and h_fin_nueva > reserva['inicio']:
            return True
    return False

def get_personal_disponible(tipo_buscado, lista_personal, fecha_evento, h_ini, h_fin):
    """
    Filtra el personal por oficio y verifica que no tenga 
    reservas que se solapen con el horario solicitado.
    """
    personal_disponible = []
    
    for persona in lista_personal:
        # 1. Verificamos el oficio (usamos .lower() para evitar errores de mayúsculas)
        if persona['oficio'].lower() == tipo_buscado.lower():
            
            conflicto = False
            # 2. Revisamos sus fechas ocupadas (que ahora son una lista de diccionarios)
            for reserva in persona['fechas_ocupadas']:
                if hay_conflicto_horario(reserva, fecha_evento, h_ini, h_fin):
                    conflicto = True
                    break # Si choca con una, ya no nos sirve
            
            if not conflicto:
                personal_disponible.append(persona)
                
    return personal_disponible

from datetime import datetime, timedelta

def get_lugares_disponibles(fecha_str, lista_lugares, h_ini, h_fin, invitados):
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
def can_select_lugar(lugar,cant_invitados:int, presupuesto_max:float):
    """Revisa si tu presupuesto y cant_invitados esta acorde con la del lugar"""
    if lugar['capacidad'] < cant_invitados:
        print(f'La capacidad del salón es insuficiente para el número de invitados'
              f'(Máx: {lugar["capacidad"]})')
        return False
    if lugar["costo"] > presupuesto_max:
        print('El costo del salón excede el presupuesto máximo establecido')
        return False
    print('¡Perfecto!.El lugar cumple con los requisitos de capacidad y presupuesto')
    return True

def contratar_personal(lista_personal,id_personal):
    """
    Busca y selecciona a un trabajador del equipo para incluirlo en una boda.
        Returns
        dict: El diccionario con los datos del trabajador si se encuentra.
        None: Si el ID no existe en la lista, permitiendo manejar el error.
    """
    trabajador_encontrado = buscar_elemento_id(id_personal,lista_personal)
    if trabajador_encontrado is None:
        print('El ID no existe')
        return None
    print(f"¡{trabajador_encontrado['nombre']} seleccionado con éxito!")
    return trabajador_encontrado #la list_contratados la lleno en el main

def calcular_costo_personal(lista_contratados):
    """ Mediante un acumulador, con un for recorren la list de contratados"""
    sueldo = 0
    for i in lista_contratados:
        sueldo+=i['costo_servicio']
    return sueldo


def calcular_costo_inventario(lista_inventario):
    """Suma el costo total de los diccionarios en la lista"""
    suma_total = 0
    for i in lista_inventario:
        # Buscamos los valores en el diccionario
        # Si la llave no existe, usamos 0 para que no de error
        precio = i.get('precio_unitario', 0)
        cantidad = i.get('cantidad_requerida', 0)

        suma_total += (precio * cantidad)

    return suma_total

def calculate_total(costo_inv: float,
                    costo_pers:float,
                    costo_lug:float,):
    """Calcula el presupuesto final de la boda"""
    costo_total = costo_inv + costo_pers + costo_lug
    extras = costo_total*0.26 #suma 0,10 de costo_wedding planner y 0,16 de impuestos
    return costo_total + extras

def build_cotizacion(cliente, lug_elegido, sel_pers, lista_items, fecha, h_inicio, h_fin):
    """Construye un diccionario completo incluyendo el bloque horario"""
    
    if can_select_lugar(lug_elegido, cliente.invitados, cliente.presupuesto) is False:
        return 'Error: El lugar no cumple los requisitos'

    # 1. CÁLCULO DE COSTOS
    costo_inv = calcular_costo_inventario(lista_items)
    costo_pers = calcular_costo_personal(sel_pers)
    costo_lug = lug_elegido['costo']

    # Calculamos el total (asegúrate de que calculate_total maneje estos 3 montos)
    total_boda = calculate_total(costo_inv, costo_pers, costo_lug)
    
    # --- NUEVO: Cálculo de duración para el ticket ---
    duracion = h_fin - h_inicio

    # 2. CREAR EL DICCIONARIO FINAL (Incluyendo las nuevas variables)
    cotizacion_final = {
        'id_lugar': lug_elegido['id_lugar'],
        'nombre_lugar': lug_elegido['nombre'], # Útil para el ticket
        'cliente': cliente.nombre,
        'fecha': fecha,
        'h_inicio': h_inicio,      # <--- GUARDADO
        'h_fin': h_fin,            # <--- GUARDADO
        'duracion': duracion,      # <--- DATO EXTRA PARA EL TICKET
        'personal_contratado': sel_pers, 
        'items_pedidos': lista_items,
        'subtotal': costo_inv + costo_lug + costo_pers,
        'total_final': total_boda, # Cambié 'total' por 'total_final' para coincidir con tu pl_boda
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


def liberar_recursos(cotizacion, lista_lugares, lista_personal, lista_inventario):
    """Limpia el sistema y devuelve stock al inventario"""
    fecha = cotizacion['fecha']

    # 1. Liberar el lugar
    id_lugar = cotizacion['id_lugar']
    eliminar_fecha(id_lugar, lista_lugares, fecha, 'fechas_ocupadas', 'lugares.json')

    # 2. Liberar al personal
    for trabajador in cotizacion['personal_contratado']:
        # Si guardaste el personal como objeto usa trabajador.id_personal
        # Si lo guardaste como diccionario usa trabajador['id_personal']
        id_trabajador = trabajador['id_personal'] 
        eliminar_fecha(id_trabajador, lista_personal, fecha, 'fechas_ocupadas', 'personal.json')

    # 3. Devolver al inventario (AQUÍ ES DONDE SE QUITA EL ROJO)
    # Usamos 'lista_inventario' que es el parámetro que declaramos arriba
    for servicio in cotizacion['servicios_elegidos']:
        for item_inv in lista_inventario:
            # Comparamos nombres para devolver las cantidades
            if item_inv['nombre'].lower() in servicio['nombre'].lower():
                item_inv['cantidad'] += servicio['cantidad']
    
    # Guardamos los cambios en el archivo
    write_json('inventario.json', lista_inventario)

def approve_cotizacion(cotizacion, lista_lugares, lista_personal,lista_inventario):
    """Evita reservas accidentales, avisa si se gaurda la cot o no con bool"""
    print(f"RESUMEN DE COTIZACIÓN PARA: {cotizacion['cliente']}")
    print(f"TOTAL A PAGAR: ${cotizacion['total']}")

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
    exito_element = buscar_elemento_id(id_element,list_element)
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

def reducir_inventario(nombre_buscado, cantidad_a_restar, lista_bodega):
    """
    Resta una cantidad específica a un producto del inventario global.

    Args:
        nombre_buscado (str): El nombre exacto del producto (ej: "Vino Tinto").
        cantidad_a_restar (int): El número de unidades que se van a usar.
        lista_bodega (list): La lista de diccionarios que cargaste del JSON.

    Returns:
        bool: Devuelve True si pudo restar, False si hubo algún problema.
    """
    for producto in lista_bodega:
        # 1. Comparamos texto con texto (muy seguro)
        if producto['nombre'] == nombre_buscado:
            # 2. Verificamos que no nos quedemos en negativo
            if producto['cantidad'] >= cantidad_a_restar:
                producto['cantidad'] -= cantidad_a_restar
                print(f"{nombre_buscado} actualizado. Quedan: {producto['cantidad']}")
                return True
            else:
                print(f"No hay suficiente {nombre_buscado} (Solo hay {producto['cantidad']})")
                return False
    print(f"El producto '{nombre_buscado}' no existe en el inventario.")
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
    # 4. DESCUENTO DE INVENTARIO (Pools de Recursos)
    for item in cotizacion['items_pedidos']:
        for inv in lista_inventario:
            if inv['nombre'].lower() in item.nombre.lower():
                inv['cantidad'] -= item.cantidad_requerida

    print("¡SISTEMA ACTUALIZADO! Todos los recursos han sido bloqueados.")

def guardar_resumen_txt(nombre_archivo, cliente, lugar, personal, servicios, subtotal, comision, total):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("==========================================\n")
        f.write("       RESUMEN DE RESERVA DE BODA        \n")
        f.write("==========================================\n\n")

        f.write(f"CLIENTE: {cliente.nombre}\n")
        f.write(f"EMAIL: {cliente.email}\n")
        f.write(f"INVITADOS: {cliente.invitados}\n\n")

        f.write(f"LUGAR: {lugar['nombre']} (${lugar['costo']})\n\n")

        f.write("PERSONAL CONTRATADO:\n")
        for p in personal:
            f.write(f"- {p.nombre} ({p.oficio}): ${p.sueldo}\n")

        f.write("\nSERVICIOS ADICIONALES:\n")
        for item in servicios:
            f.write(f"- {item.nombre} (x{item.cantidad_requerida}): ${item.calcular_subtotal()}\n")

        f.write("\n------------------------------------------\n")
        f.write(f"SUBTOTAL: ${subtotal}\n")
        f.write(f"COMISIÓN (15%): ${comision}\n")
        f.write(f"TOTAL FINAL: ${total}\n")
        f.write("------------------------------------------\n")
        f.write("\n¡Gracias por confiar en nosotros!")

def limpiar_pantalla():
    # 'nt' es para Windows, 'posix' para Mac o Linux
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def guardar_reserva_json(nueva_boda):
    nombre_archivo = 'historial_reservas.json'

    # Intentamos leer lo que ya existe
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o está vacío, empezamos una lista nueva
        historial = []

    # Añadimos la nueva boda a la lista
    historial.append(nueva_boda)

    # Guardamos la lista actualizada
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)


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