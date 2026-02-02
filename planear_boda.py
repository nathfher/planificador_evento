from datetime import datetime
import funciones_generales as fg
from modulos import Cliente, Personal, ItemReserva

def ejecutar_registro_boda():
    """
    Ejecuta el asistente interactivo para la planificación integral de una boda.
    
    Este es el motor principal de la interfaz de usuario. Realiza las siguientes acciones:
    1. Carga las bases de datos desde archivos JSON (Lugares, Personal, Inventario, etc.).
    2. Registra los datos del cliente y valida su presupuesto y número de invitados.
    3. Gestiona la selección del lugar verificando disponibilidad de fechas y horarios.
    4. Permite la contratación de personal y servicios de catálogo (Catering y Música),
       aplicando reglas de negocio, seguridad y restricciones de exclusión mutua.
    5. Calcula la cotización final incluyendo comisiones de agencia e impuestos.
    6. Confirma la reserva bloqueando los recursos y generando un ticket físico (.txt).

    No recibe parámetros de entrada y no retorna valores, ya que gestiona la 
    persistencia directamente a través de funciones auxiliares.
    """

    fg.limpiar_pantalla()
    print("==========================================")
    print("   BIENVENIDO AL SISTEMA WEDDING PLANNER  ")
    print("==========================================\n")

    # 1. CARGAR DATOS
    lista_lugares = fg.ensure_file_exist('data/lugares.json', [])
    lista_personal = fg.ensure_file_exist('data/personal.json', [])
    lista_inventario = fg.ensure_file_exist('data/inventario.json', [])
    lista_clientes = fg.ensure_file_exist("data/clientes.json", [])
    lista_catering = fg.ensure_file_exist('data/catering.json', [])
    lista_musica = fg.ensure_file_exist('data/musica.json', [])

    if not lista_lugares:
        print("❌ ERROR CRÍTICO: No se puede planear una boda sin lugares en la base de datos.")
        return

    print("✅ Bases de datos cargadas correctamente.")
    input("\nPresione Enter para comenzar el registro...")

    # --- PASO 1: REGISTRO DEL CLIENTE ---
    fg.limpiar_pantalla()
    print("--- PASO 1: REGISTRO DEL CLIENTE ---")

    while True:
        id_input = input("Ingrese el ID único del cliente (solo números): ")
        try:
            # Intentamos convertir la entrada a entero
            id_cliente = int(id_input)
            break  # Si tiene éxito, rompemos el bucle y continuamos
        except ValueError:
            # Si ocurre un error de valor (puso letras), mostramos aviso
            print("❌ Error: El ID debe ser un número entero. Intente de nuevo.")
    # --- AQUÍ VA LA VALIDACIÓN ---
    id_existe = any(c['id_cliente'] == id_cliente for c in lista_clientes)

    if id_existe:
        print(f"\n⚠️ ERROR: El ID '{id_cliente}' ya está registrado.")
        print("No se puede duplicar clientes. Volviendo al menú...")
        input("Presione Enter para continuar...")
        return # Esto detiene el registro y te saca al menú principal

    nombre_usuario = input("Ingrese el nombre completo del cliente: ")

    while True:
        correo_temp = input("Ingrese el correo electrónico: ")
        if "@" in correo_temp:
            correo_usuario = correo_temp
            break
        print("❌ ¡Correo inválido! Debe contener un símbolo '@'.")

    while True:
        try:
            presupuesto_val = float(input("¿Cuál es el presupuesto máximo?: "))
            break
        except ValueError:
            print("❌ ¡Error! Ingresa un monto de dinero válido.")

    while True:
        try:
            invitados_val = int(input("¿Cuántos invitados se esperan?: "))
            break
        except ValueError:
            print("❌ ¡Error! Por favor, ingresa un número entero.")

    # --- REGISTRO DE FECHA Y HORARIOS ---
    while True:
        fecha_input = input("Ingrese la fecha de la boda (DD/MM/AAAA): ")
        try:
            fecha_boda = datetime.strptime(fecha_input, "%d/%m/%Y")
            if fecha_boda < datetime.now():
                print("❌ No puedes elegir una fecha pasada.")
            else:
                fecha_str = fecha_input # Guardamos el string para las búsquedas
                break
        except ValueError:
            print("⚠️ Formato incorrecto. Debe ser día/mes/año (ej: 15/05/2026)")

    # --- NUEVO: Captura de Horas (Integrado) ---
    while True:
        print("\nDefina el horario del evento (Formato 24h):")
        h_ini = input("Hora de inicio (ej: 14 o 14:30): ").strip()
        h_fin = input("Hora de finalización (ej: 22 o 22:00): ").strip()

        # 1. Quitamos los ':' para verificar que no haya letras (como 'helloworld')
        prueba_ini = h_ini.replace(":", "")
        prueba_fin = h_fin.replace(":", "")

        if prueba_ini.isdigit() and prueba_fin.isdigit():
            # 2. Convertimos a números SOLO para validar el rango y calcular duración
            # Tomamos solo los primeros dígitos antes de los ':' para la hora
            hora_i = int(h_ini.split(":")[0])
            hora_f = int(h_fin.split(":")[0])

            if 0 <= hora_i < 24 and 0 <= hora_f < 24 and hora_i < hora_f:
                duracion = hora_f - hora_i
                print(f"✅ Horario reservado: {h_ini} a {h_fin} ({duracion} horas).")
                break
            else:
                print("❌ Horario ilógico. Asegúrate de que la hora sea entre 0-23 y que el fin sea después del inicio.")
        else:
            print("❌ ¡Error! No introduzcas letras. Usa números (ej: 14 o 14:30).")
    # Guardamos los datos del cliente
    cliente_actual = Cliente(id_cliente, nombre_usuario, correo_usuario, invitados_val, presupuesto_val)
    fg.guardar_elemento(cliente_actual, lista_clientes, 'clientes.json')
    print(f"✅ Cliente {cliente_actual.nombre} registrado.")
    input("Presione Enter para elegir el lugar...")

    # --- PASO 2: SELECCIÓN DE LUGAR ---
    fg.limpiar_pantalla()

    # Ahora recibimos dos variables
    lugares_libres, sugerencias = fg.get_lugares_disponibles(fecha_str, lista_lugares, h_ini, h_fin, invitados_val)

    if not lugares_libres:
        print(f"❌ No hay lugares disponibles para el {fecha_str} a esa hora.")

        if sugerencias:
            print("\n💡 SUGERENCIAS DEL SISTEMA INTELIGENTE:")
            for sug in sugerencias:
                print(f"   -> El lugar '{sug['nombre']}' está libre el día {sug['fecha']}")

        print("\nIntente con otra fecha o lugar.")
        input("Presione Enter para salir...")
        return

    fg.mostar_lugares(lugares_libres)
    lugar_elegido = None  # Empezamos sin nada

    while lugar_elegido is None:  # Mientras no tengamos un lugar válido...
        try:
            id_lug = int(input("\nSeleccione ID del lugar (o '0' para cancelar): "))
        
            if id_lug == 0:
                print("Operación cancelada.")
                return # Salimos de la función si se arrepienten

            lugar_seleccionado = next((l for l in lugares_libres if l['id_lugar'] == id_lug), None)

            if lugar_seleccionado:
            # Usamos tu función can_select_lugar
                if fg.can_select_lugar(cliente_actual.presupuesto, lugar_seleccionado['precio']):
                    lugar_elegido = lugar_seleccionado # <--- ESTO ROMPE EL BUCLE
                    print(f"✅ Sede confirmada: {lugar_elegido['nombre']}")
                else:
                    print(f"❌ ¡Presupuesto insuficiente! El salón cuesta ${lugar_seleccionado['precio']} y solo tienes ${cliente_actual.presupuesto}.")
                    print("Por favor, elija un lugar acorde a su presupuesto.")
            else:
                print("❌ ID no encontrado en la lista de salones disponibles.")
            
        except ValueError:
            print("❌ Por favor, introduce un número válido.")

    # --- PREPARACIÓN DE LISTAS ---
    personal_contratado = []
    servicios_elegidos = []

    # --- PASO 3: CONTRATACIÓN DE PERSONAL ---
    while True:
        fg.limpiar_pantalla()
        print(f"--- PASO 3: CONTRATACIÓN DE PERSONAL (Presupuesto: ${cliente_actual.presupuesto}) ---")
        tipo = input("\n¿Qué oficio busca? (Fotografia, Seguridad, Estetica, Musica, Planificador, Decoracion o Barman / '0' para continuar): ").lower().strip()

        if tipo == '0': 
            break

        # Búsqueda de personal en personal.json
        pers_libres = fg.get_personal_disponible(tipo, lista_personal, fecha_str, h_ini, h_fin)

        if not pers_libres:
            print(f"❌ No hay {tipo} disponible en ese horario.")
            input("Pulse Enter...")
            continue

        fg.mostrar_personal(pers_libres)
        try:
            id_p = int(input(f"ID del {tipo} a contratar (0 para volver): "))
            if id_p == 0: continue

            dict_p = fg.contratar_personal(lista_personal, id_p) #DICT_P DICCIONARIO DEL PERSONAL
            if dict_p:
                nombre_p = dict_p['nombre'].lower()
                oficio_p = dict_p['oficio'].lower()
                    
                    # --- AQUÍ INSERTAS LA VALIDACIÓN DE EXCLUSIÓN ---
                    # REGLA: DJ vs BANDA DE ROCK (Sentido A)
                if "dj" in nombre_p:
                        # Revisamos si ya existe la Banda de Rock en servicios_elegidos
                    if any("rock" in s.nombre.lower() for s in servicios_elegidos):
                        print("❌ Conflicto: No puede contratar al DJ porque ya eligió la 'Banda de Rock'.")
                        input("Presione Enter para continuar...")
                        continue # Detiene la contratación y vuelve a pedir ID
                    else:
                        print("⚠️  AVISO: Al contratar este DJ, se bloqueará la opción de 'Banda de Rock'.")
                # 2. REGLA: TERRAZA -> SEGURIDAD (La que pediste)
                if "terraza" in lugar_seleccionado['nombre'].lower() and "seguridad" in oficio_p:
                    print("✅ Requisito de seguridad para la Terraza cubierto.")

                # --- GUARDAR SI NO ESTÁ REPETIDO ---
                if any(p.id_personal == dict_p['id_personal'] for p in personal_contratado):
                    print("⚠️ Ya contratado.")
                else:
                    personal_contratado.append(Personal(dict_p['id_personal'], dict_p['nombre'], dict_p['oficio'], dict_p['sueldo']))
                    print(f"✅ {dict_p['nombre']} añadido.")
                if any(p.id_personal == dict_p['id_personal'] for p in personal_contratado):
                    print("⚠️ Ya contratado.")
                else:
                    personal_contratado.append(Personal(dict_p['id_personal'], dict_p['nombre'], dict_p['oficio'], dict_p['sueldo']))
                    print(f"✅ {dict_p['nombre']} añadido.")
            else: print("❌ ID no válido.")
        except ValueError: 
            print("⚠️ Ingrese un número.")
            input("\nPresione Enter...")

    # --- PASO 4: SELECCIÓN DE SERVICIOS (CATÁLOGOS) ---
    # Definimos los catálogos para procesarlos en un solo bucle limpio
    catalogos = [
        {"nombre": "CATERING", "lista": lista_catering},
        {"nombre": "MÚSICA", "lista": lista_musica}
    ]

    for cat in catalogos:
        fg.limpiar_pantalla()
        print(f"--- PASO 4: MENÚ DE {cat['nombre']} ---")
        for item in cat['lista']:
            print(f"ID: {item['id_item']} | {item['nombre']} | ${item['precio_unidad']}")

        while True:
            op = input(f"\nID de {cat['nombre']} (o '0' para siguiente): ")
            if op == '0': break
            
            try:
                id_sel = int(op)
                seleccionado = next((x for x in cat['lista'] if x['id_item'] == id_sel), None)
                
                if seleccionado:
                    # --- AQUÍ VA LA VALIDACIÓN PREVENTIVA ---
                    if "gala" in seleccionado['nombre'].lower():
                        print("\n" + "!"*45)
                        print("⚠️  ATENCIÓN: Los servicios de 'Gala' requieren")
                        print("   contratar 'Maquillaje y Peinado' más adelante.")
                        print("!"*45 + "\n")

                        confirmar = input("¿Está de acuerdo en añadir este requisito a su búsqueda de personal posterior? (S/N): ").upper().strip()
                        if confirmar != 'S':
                            print("❌ Selección cancelada. Para elegir este menú debe aceptar el protocolo.")
                            continue # Salta el resto del bucle y pide otro ID
                    cant = int(input(f"¿Cantidad de {seleccionado['nombre']}?: "))

                    # Validación de Inventario unificada
                    recurso = next((i for i in lista_inventario if i['nombre'].lower() in seleccionado['nombre'].lower()), None)

                    if recurso and recurso['cantidad'] < cant:
                        print(f"❌ Stock insuficiente. Solo quedan {recurso['cantidad']}.")
                    else:
                        servicios_elegidos.append(ItemReserva(seleccionado['id_item'], seleccionado['nombre'], seleccionado['precio_unidad'], cant))
                        print(f"✅ {seleccionado['nombre']} añadido.")
                else:
                    print("❌ ID no encontrado.")
            except ValueError:
                print("⚠️ Ingrese solo números.")
    # --- PASO 4.3: VALIDACIÓN INTELIGENTE ---
    valido, mensaje = fg.validar_restricciones_inteligentes(personal_contratado,
                                                            servicios_elegidos,
                                                            lugar_seleccionado)

    if not valido:
        print("\n" + "!"*40)
        print(f"ATENCIÓN: {mensaje}")
        print("!"*40)
        print("\nNo podemos proceder con esta configuración. Ajuste sus selecciones.")
        input("Presione Enter para volver al menú...")
        return # Aquí cortamos la ejecución y regresamos al menú principal

    # --- PASO 5: CÁLCULOS Y COTIZACIÓN ---
    # build_cotizacion usa el string de fecha para el registro
    cotizacion = fg.build_cotizacion(
        cliente_actual,
        lugar_seleccionado,
        personal_contratado,
        servicios_elegidos,
        fecha_str,
        h_ini,
        h_fin
    )

    # --- PASO 6: CIERRE Y BLOQUEO ---
    # approve_cotizacion muestra el resumen y pide confirmación (S/N)
    if fg.approve_cotizacion(cotizacion, lista_lugares, lista_personal,lista_inventario):

        # Procesa bloqueos de fechas en listas y resta inventario
        fg.procesar_confirmacion_boda(cotizacion, lista_lugares, lista_personal, lista_inventario)

        # Guardar cambios en archivos físicos
        fg.write_json('data/lugares.json', lista_lugares)
        fg.write_json('data/personal.json', lista_personal)
        fg.write_json('data/inventario.json', lista_inventario)

        # Generar archivos finales
        fg.guardar_reserva_json(cotizacion)
        # fg.generar_ticket(...) # Si tienes la función habilitada

        print("\n✅ ¡Boda planificada y recursos bloqueados con éxito!")
        # 3. GENERACIÓN DEL TICKET TXT (Lo que te faltaba)
        # Usamos los datos calculados en 'cotizacion'
        fg.generar_ticket(
            cliente_actual,
            lugar_seleccionado,
            personal_contratado,
            servicios_elegidos,
            cotizacion['subtotal'],
            cotizacion['comision'],
            cotizacion['total_final'],
            fecha_boda # El objeto datetime para que el ticket ponga la fecha bonita
        )

        print("\n✅ ¡Boda planificada con éxito!")
        print("📄 Se ha generado 'resumen_boda.txt' con todos los detalles.")
    else:
        print("\nOpciones descartadas. Volviendo al menú...")

if __name__ == "__main__":
    ejecutar_registro_boda()
