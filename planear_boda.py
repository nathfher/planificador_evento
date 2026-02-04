from datetime import datetime
import funciones_generales as fg
from modulos import Cliente, Personal, ItemReserva

def ejecutar_registro_boda():

    fg.limpiar_pantalla()
    print("==========================================")
    print("   BIENVENIDO AL SISTEMA WEDDING PLANNER  ")
    print("==========================================\n")

    # 1. CARGAR DATOS
    lista_lugares = fg.ensure_file_exist('data/lugares.json', [])
    lista_personal = fg.ensure_file_exist('data/personal.json', [])
    lista_inventario = fg.ensure_file_exist('data/inventario.json', [])
    lista_clientes = fg.ensure_file_exist("data/clientes.json", [])

    if not lista_lugares:
        print("❌ ERROR CRÍTICO: No se puede planear una boda sin lugares en la base de datos.")
        return

    print("✅ Bases de datos cargadas correctamente.")
    input("\nPresione Enter para comenzar el registro...")

    # --- PASO 1: REGISTRO DEL CLIENTE ---
    fg.limpiar_pantalla()
    print("--- PASO 1: REGISTRO DEL CLIENTE ---")

    # --- PASO 2: REGISTRO DEL CLIENTE CON RESTRICCIÓN DE ID ---
    # --- PASO 2: REGISTRO DEL CLIENTE (VERSIÓN ANTIBALAS) ---
    while True:
        try:
            # 1. VALIDAR ID (1000 - 10000)
            id_client = int(input("\nIngrese ID del cliente (1000-10000): "))
            if not 1000 <= id_client <= 10000:
                print("⚠️ Error: El ID debe estar entre 1000 y 10000.")
                continue
            if any(c['id_cliente'] == id_client for c in lista_clientes):
                print("❌ Este ID ya existe. Use uno diferente.")
                continue

            # 2. VALIDAR NOMBRE (Mínimo 8 caracteres y sin números)
            name_client = input("Ingrese nombre completo: ").strip()
            if len(name_client) < 8 or name_client.isdigit():
                print("⚠️ Nombre inválido. Debe ser completo (mín. 8 letras) y no numérico.")
                continue

            # 3. VALIDAR CORREO (Debe ser @gmail.com)
            correo_temp = input("Ingrese correo (@gmail.com): ").lower().strip()
            if not correo_temp.endswith("@gmail.com") or len(correo_temp) < 11:
                print("❌ Correo inválido. Debe ser una cuenta válida de @gmail.com.")
                continue

            # 4. VALIDAR INVITADOS (Máximo 350 que es el límite de tus lugares)
            invitados_val = int(input("¿Cuántos invitados espera? (Máx. 350): "))
            if invitados_val <= 0:
                print("⚠️ Debe tener al menos 1 invitado.")
                continue
            if invitados_val > 350:
                print("❌ Lo sentimos. Ninguno de los salones supera la capacidad de 350 personas.")
                continue

            # 5. VALIDAR PRESUPUESTO (Mínimo razonable, ej: 1000 pesos)
            presupuesto_val = float(input("¿Presupuesto máximo? (Mínimo $1000): "))
            if presupuesto_val < 1500:
                print(
                    f"Con ${presupuesto_val} no es posible organizar una boda. "
                    f"El presupuesto mínimo aceptado es de $1500."
                )
                continue

            # SI LLEGA AQUÍ, ESTÁ PERFECTO
            cliente_actual = Cliente(id_client,
                                    name_client,
                                    correo_temp,
                                    invitados_val,
                                    presupuesto_val)
            lista_clientes.append(cliente_actual.to_dict())
            fg.write_json('data/clientes.json', lista_clientes)

            print(f"\n✅ Cliente '{name_client}' registrado exitosamente.")
            break

        except ValueError:
            print("❌ Error: Por favor, ingrese números válidos para ID, invitados y presupuesto.")

    # --- PASO 2.1: REGISTRO DE FECHA ---
    while True:
        fecha_input = input("\nIngrese la fecha de la boda (DD/MM/AAAA): ")
        try:
            fecha_boda = datetime.strptime(fecha_input, "%d/%m/%Y")
            if fecha_boda < datetime.now():
                print("❌ No puedes elegir una fecha pasada. ¡Planificamos el futuro!")
                continue
            fecha_str = fecha_input
            break
        except ValueError:
            print("⚠️ Formato incorrecto. Debe ser día/mes/año (ej: 15/05/2026)")

    # --- PASO 2.2: REGISTRO DE HORARIOS ---
    while True:
        print(f"\nDefina el horario para el {fecha_str} (Formato 24h, ej: 14:00):")
        h_ini = input("Hora de inicio: ").strip()
        h_fin = input("Hora de finalización: ").strip()

        try:
            # Validamos que el formato sea exactamente HH:MM (evita que pongan solo "14")
            # strptime lanzará error si no tiene los ':' y los minutos
            time_ini = datetime.strptime(h_ini, "%H:%M")
            time_fin = datetime.strptime(h_fin, "%H:%M")

            if time_ini >= time_fin:
                print("❌ La hora de finalización debe ser posterior a la de inicio.")
                continue

            # Calculamos la duración usando la diferencia de tiempo
            duracion_td = time_fin - time_ini
            duracion_horas = duracion_td.seconds / 3600

            if duracion_horas < 2:
                print("⚠️ Una boda debe durar al menos 2 horas. Ajuste el horario.")
                continue

            print(f"✅ Horario validado: {h_ini} a {h_fin} ({duracion_horas:.1f} horas).")
            break

        except ValueError:
            print("❌ Formato de hora inválido. Debe usar HH:MM (ej: 14:00, 09:30).")
            print("   No se aceptan números solos o letras.")

    # --- GUARDAR DATOS DEL CLIENTE (Al final de las validaciones) ---
    cliente_actual = Cliente(id_client, name_client, correo_temp, invitados_val, presupuesto_val)
    lista_clientes.append(cliente_actual.to_dict())
    fg.write_json('data/clientes.json', lista_clientes)

    print(f"\n✅ Cliente {cliente_actual.nombre} y horario registrados con éxito.")
    input("Presione Enter para elegir el lugar...")

    # --- PASO 2: SELECCIÓN DE LUGAR ---
    fg.limpiar_pantalla()

    # Ahora recibimos dos variables
    lugares_libres, sugerencias = fg.get_lugares_disponibles(fecha_str,
                                                            lista_lugares,
                                                            h_ini,
                                                            h_fin,
                                                            invitados_val)

    if not lugares_libres:
        print(f"❌ No hay lugares disponibles para el {fecha_str} a esa hora.")

        if sugerencias:
            print("\n💡 SUGERENCIAS DEL SISTEMA INTELIGENTE:")
            for sug in sugerencias:
                print(f"   -> El lugar '{sug['nombre']}' está libre el día {sug['fecha']}")

        print("\nIntente con otra fecha o lugar.")
        input("Presione Enter para salir...")
        return
    #---SELECCION DEL LUGAR---
    # 1. CREAR UNA LISTA VACÍA PARA LOS LUGARES QUE CUMPLEN
    lugares_aptos = []

    # 2. RECORRER LA LISTA ORIGINAL Y FILTRAR
    for l in lista_lugares:
        # Si la capacidad del lugar es suficiente para los invitados...
        if l['capacidad'] >= cliente_actual.invitados:
            # ... lo agregamos a nuestra lista de opciones válidas
            lugares_aptos.append(l)

    # 3. VALIDAR SI QUEDÓ ALGÚN LUGAR
    if not lugares_aptos:
        print("\n" + "!"*45)
        print(f"❌ ERROR: Ningún salón tiene capacidad para {cliente_actual.invitados} pers.")
        print("!"*45)
        input("Presione Enter para volver...")
        return # Detenemos la función porque no hay opciones
    # 3. MOSTRAR LA TABLA
    print("\n================================")
    print("      SALONES DISPONIBLES       ")
    print("================================")
    print("================================\n")
    for l in lugares_aptos: # <--- Cambiado a lugares_aptos
        print(
            f"ID: {str(l['id_lugar']).ljust(4)} | {l['nombre'].ljust(20)} | "
            f"Cap: {str(l['capacidad']).rjust(3)} pers. | Precio: ${l['precio']:>6}"
        )
    print("============================================\n")

    lugar_elegido = None
    while lugar_elegido is None:
        try:
            id_lug = int(input("Seleccione ID del lugar (o '0' para cancelar): "))

            if id_lug == 0:
                print("Operación cancelada.")
                return

            # Usamos tu función de búsqueda
            lugar_seleccionado = fg.buscar_elemento_id(id_lug, lugares_aptos, 'id_lugar')

            if lugar_seleccionado:
                if fg.can_select_lugar(cliente_actual.presupuesto, lugar_seleccionado['precio']):
                    # --- ÉXITO ---
                    lugar_elegido = lugar_seleccionado

                    # RESTAMOS EL COSTO DEL PRESUPUESTO DEL CLIENTE
                    cliente_actual.presupuesto -= lugar_elegido['precio']

                    print(f"✅ Sede confirmada: {lugar_elegido['nombre']}")
                    print(f"💰 Presupuesto restante: ${cliente_actual.presupuesto}")
                    input("\nPresione Enter para continuar a la contratación de personal...")
                else:
                    print(
                        f"❌ ¡Presupuesto insuficiente! El salón "
                        f"'{lugar_seleccionado['nombre'].ljust(20)}' cuesta "
                        f"${lugar_seleccionado['precio']} y solo tienes ${cliente_actual.presupuesto}."
                    )
                    print("Por favor, elija un lugar acorde a su presupuesto.")
            else:
                print("❌ ID no encontrado o el lugar no es apto para sus invitados.")

        except ValueError:
            print("❌ Por favor, introduce un número válido.")

    # --- PREPARACIÓN DE LISTAS ---
    personal_contratado = []
    servicios_elegidos = []

    # --- PASO 3: CONTRATACIÓN DE PERSONAL ---
    while True:
        fg.limpiar_pantalla()
        # El presupuesto se actualiza aquí arriba cada vez que el bucle reinicia
        print(f"--- PASO 3: CONTRATACIÓN DE PERSONAL (Presupuesto: ${cliente_actual.presupuesto}) ---")

        # Def mensaje en varias líneas para que sea legible
        mensaje_prompt = (
            "\n¿Qué oficio busca? (Fotografia, Seguridad, Estetica, "
            "Planificador, Decoracion o Barman / '0' para continuar): "
        )

        # Ahora input queda corto y limpio
        tipo = input(mensaje_prompt).lower().strip()

        if tipo == '0':
            break

        pers_libres = fg.get_personal_disponible(tipo, lista_personal, fecha_str, h_ini, h_fin)

        if not pers_libres:
            print(f"❌ No hay {tipo} disponible en ese horario.")
            input("Presione Enter para volver a elegir oficio...") # PAUSA 1
            continue

        print(f"\n--- {tipo.upper()} DISPONIBLES ---")
        for p in pers_libres:
            print(f"ID: {p['id_personal']} | Nombre: {p['nombre']} | Sueldo: ${p['sueldo']}")
        print("------------------------------")

        try:
            id_p = int(input(f"ID del {tipo} a contratar (0 para volver): "))
            if id_p == 0:
                continue

            dict_p = fg.contratar_personal(lista_personal, id_p)

            if dict_p:
                # 1. Variables y validación de duplicados
                oficio_p = dict_p['oficio'].lower()
                sueldo_p = dict_p['sueldo']
                ya_contratado = any(p.id_personal == dict_p['id_personal'] for p in personal_contratado)

                if ya_contratado:
                    print(f"⚠️ {dict_p['nombre']} ya ha sido añadido.")
                elif sueldo_p > cliente_actual.presupuesto:
                    print(f"❌ Presupuesto insuficiente. Falta: ${sueldo_p - cliente_actual.presupuesto}")
                else:
                    # 2. Contratación y Resta de presupuesto
                    cliente_actual.presupuesto -= sueldo_p # ESTO actualiza el número de arriba
                    personal_contratado.append(Personal(dict_p['id_personal'], dict_p['nombre'], dict_p['oficio'], sueldo_p))


                    print(f"\n✅ CONFIRMADO: {dict_p['nombre']} como {oficio_p}.")
                    print(f"💰 Nuevo presupuesto restante: ${cliente_actual.presupuesto}")
                # Está fuera de los IFs de éxito/error, así que siempre se detiene.
                input("\nPresione Enter para continuar...") 

            else:
                print("❌ ID no encontrado.")
                input("Presione Enter...") # PAUSA 3

        except ValueError:
            print("⚠️ Error: Use solo números para el ID.")
            input("Presione Enter...") # PAUSA 4

    # --- PASO 4: SELECCIÓN DE INVENTARIO UNIFICADO ---
    # Cubrimos: catering, bebida, postre, mobiliario, tecnologia y decoracion
    categorias_inv = ["catering", "bebida", "postre", "mobiliario", "tecnologia", "decoracion"]

    for cat in categorias_inv:
        fg.limpiar_pantalla()
        print(f"--- PASO 4: SELECCIÓN DE {cat.upper()} (Presupuesto: ${cliente_actual.presupuesto}) ---")

        # Filtramos el inventario general por la categoría actual
        items_categoria = [i for i in lista_inventario if i.get('categoria') == cat]

        if not items_categoria:
            continue # Si no hay nada de esa categoría, saltamos a la siguiente

        for item in items_categoria:
            print(f"ID: {item['id_item']} | {item['nombre'].ljust(30)} | ${item['precio_unidad']} | Stock: {item['cantidad']}")

        while True:
            op = input(f"\nID de {cat} (o '0' para siguiente categoría): ")
            if op == '0': 
                break

            try:
                id_sel = int(op)
                seleccionado = next((x for x in items_categoria if x['id_item'] == id_sel), None)

                if seleccionado:
                    cant = int(input(f"¿Cantidad de {seleccionado['nombre']}?: "))
                    costo_total_item = seleccionado['precio_unidad'] * cant

                    if seleccionado['cantidad'] < cant:
                        print(f"❌ Stock insuficiente. Solo quedan {seleccionado['cantidad']}.")
                    elif costo_total_item > cliente_actual.presupuesto:
                        print(f"❌ No hay presupuesto. Costo: ${costo_total_item} | Tienes: ${cliente_actual.presupuesto}")
                    else:
                        # DESCUENTO TEMPORAL Y REGISTRO
                        cliente_actual.presupuesto -= costo_total_item
                        # No restamos del JSON aquí, solo de la lista en memoria
                        seleccionado['cantidad'] -= cant

                        servicios_elegidos.append(ItemReserva(
                            seleccionado['id_item'],
                            seleccionado['nombre'],
                            seleccionado['precio_unidad'],
                            cant
                        ))
                        print(f"✅ {seleccionado['nombre']} añadido. Presupuesto restante: ${cliente_actual.presupuesto}")
                else:
                    print("❌ ID no válido para esta categoría.")
            except ValueError:
                print("⚠️ Ingrese solo números.")

        input("\nPresione Enter para pasar a la siguiente categoría...")

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
        print("📄 Se ha generado 'ticket_boda.txt' con todos los detalles.")
    else:
        print("\nOpciones descartadas. Volviendo al menú...")

if __name__ == "__main__":
    ejecutar_registro_boda()
