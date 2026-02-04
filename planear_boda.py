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
    # 1. VALIDAR ID (Minibucle independiente)
    while True:
        try:
            id_client = int(input("\nIngrese ID del cliente (1000-10000): "))
            if not 1000 <= id_client <= 10000:
                print("⚠️ Error: El ID debe estar entre 1000 y 10000.")
                continue
            if any(c['id_cliente'] == id_client for c in lista_clientes):
                print("❌ Este ID ya existe. Use uno diferente.")
                continue
            break # ID correcto, salimos de ESTE bucle
        except ValueError:
            print("❌ Error: Ingrese un número entero para el ID.")

    # 2. VALIDAR NOMBRE
    while True:
        name_client = input("Ingrese nombre completo: ").strip()
        # Verificamos longitud y que no tenga números
        if len(name_client) < 8 or any(char.isdigit() for char in name_client):
            print("⚠️ Nombre inválido. Debe tener mín. 8 letras y no contener números.")
            continue
        break

    # 3. VALIDAR CORREO
    while True:
        correo_temp = input("Ingrese correo (@gmail.com): ").lower().strip()

        # Verificamos que tenga un '@', que termine en '@gmail.com'
        # y que haya algo antes del '@'
        if "@gmail.com" in correo_temp and correo_temp.endswith("@gmail.com"):
            # Extraemos la parte antes del @ para ver si es válida
            usuario = correo_temp.split('@')[0]
            if len(usuario) > 2:
                break # Correo válido
            else:
                print("❌ El nombre de usuario del correo es muy corto.")
        else:
            print("❌ Correo inválido. Asegúrese de que termine exactamente en @gmail.com")

    # 4. VALIDAR INVITADOS (Con su propio try/except)
    while True:
        try:
            invitados_val = int(input("¿Cuántos invitados espera? (Máx. 350): "))
            if 0 < invitados_val <= 350:
                break
            print("⚠️ Cantidad inválida. El límite de nuestros salones es 350.")
        except ValueError:
            print("❌ Ingrese un número entero para la cantidad de invitados.")

    # 5. VALIDAR PRESUPUESTO
    while True:
        try:
            presupuesto_val = float(input("¿Presupuesto máximo? (Mínimo $1500): "))
            if presupuesto_val >= 1500:
                break
            print("❌ El presupuesto mínimo aceptado es de $1500.")
        except ValueError:
            print("❌ Ingrese un valor numérico (ej: 5000.50).")

    # AL FINAL: Creamos el objeto una sola vez
    cliente_actual = Cliente(id_client, name_client, correo_temp, invitados_val, presupuesto_val)
    presupuesto_provisional = cliente_actual.presupuesto # variable temporal
    lista_clientes.append(cliente_actual.to_dict())
    fg.write_json('data/clientes.json', lista_clientes)

    print(f"\n✅ Cliente '{name_client}' registrado exitosamente.")

    # --- PASO 2.1: REGISTRO DE FECHA ---
    while True:
        fecha_input = input("\nIngrese la fecha de la boda (DD/MM/AAAA): ")
        try:
            fecha_boda = datetime.strptime(fecha_input, "%d/%m/%Y")
            if fecha_boda < datetime.now():
                print("❌ No puedes elegir una fecha pasada. ¡Planificamos el futuro!")
                continue
            fecha_str = fecha_input
            break # Fecha válida, pasamos a la hora
        except ValueError:
            print("⚠️ Formato incorrecto. Debe ser día/mes/año (ej: 15/05/2026)")

    # --- PASO 2.2: REGISTRO DE HORARIOS ---
    while True:
        print(f"\nDefina el horario para el {fecha_str} (Formato 24h, ej: 14:00):")
        h_ini = input("Hora de inicio: ").strip()
        h_fin = input("Hora de finalización: ").strip()

        try:
            time_ini = datetime.strptime(h_ini, "%H:%M")
            time_fin = datetime.strptime(h_fin, "%H:%M")

            if time_ini >= time_fin:
                print("❌ La hora de finalización debe ser posterior a la de inicio.")
                continue

            duracion_horas = (time_fin - time_ini).seconds / 3600

            if duracion_horas < 2:
                print("⚠️ Una boda debe durar al menos 2 horas. Ajuste el horario.")
                continue

            print(f"✅ Horario validado: {h_ini} a {h_fin} ({duracion_horas:.1f} horas).")
            
            # CAMBIO AQUÍ: Usamos input() en lugar de print() para forzar la pausa
            input("\nPresione Enter para continuar a la selección de lugar...") 
            
            break
        except ValueError:
            print("❌ Formato de hora inválido. Use HH:MM (ej: 14:00).")
    # --- PASO 3: SELECCIÓN DE LUGAR ---
    fg.limpiar_pantalla()

    # 1. OBTENER DISPONIBILIDAD REAL (Fecha + Horario + Capacidad)
    lugares_libres, sugerencias = fg.get_lugares_disponibles(
        fecha_str, lista_lugares, h_ini, h_fin, invitados_val
    )

    # 2. VALIDAR SI HAY OPCIONES DISPONIBLES
    if not lugares_libres:
        print(f"❌ No hay lugares disponibles para el {fecha_str} a esa hora.")
        if sugerencias:
            print("\n💡 SUGERENCIAS DEL SISTEMA INTELIGENTE:")
            for sug in sugerencias:
                print(f"   -> El lugar '{sug['nombre']}' está libre el día {sug['fecha']}")
        print("\nIntente con otra fecha o reduzca el número de invitados.")
        input("Presione Enter para volver al menú...")
        return

    # 3. MOSTRAR LA TABLA DE LUGARES APTOS Y LIBRES
    print("\n" + "="*50)
    print("           SALONES DISPONIBLES              ".center(50))
    print("="*50)
    for l in lugares_libres: # Usamos la lista que ya filtró fg.get_lugares_disponibles
        print(
            f"ID: {str(l['id_lugar']).ljust(4)} | {l['nombre'].ljust(20)} | "
            f"Cap: {str(l['capacidad']).rjust(3)} pers. | Precio: ${l['precio']:>6.2f}"
        )
    print("="*50 + "\n")

    # 4. BUCLE DE SELECCIÓN
    lugar_elegido = None
    while lugar_elegido is None:
        try:
            id_lug = int(input("Seleccione ID del lugar (o '0' para cancelar): "))

            if id_lug == 0:
                print("Operación cancelada.")
                return

            # Buscamos en la lista de los que están LIBRES y tienen CAPACIDAD
            lugar_seleccionado = fg.buscar_elemento_id(id_lug, lugares_libres, 'id_lugar')

            if lugar_seleccionado:
                # Validamos si el dinero le alcanza
                if fg.can_select_lugar(cliente_actual.presupuesto, lugar_seleccionado['precio']):
                    lugar_elegido = lugar_seleccionado

                    #Restamos de la temporal, NO del objeto
                    presupuesto_provisional -= lugar_elegido['precio']

                    print(f"\n✅ Sede confirmada: {lugar_elegido['nombre']}")
                    print(f"💰 Presupuesto estimado restante: ${presupuesto_provisional:,.2f}")
                    input("\nPresione Enter para continuar a la contratación de personal...")
                else:
                    print(
                        f"❌ ¡Presupuesto insuficiente! El salón "
                        f"'{lugar_seleccionado['nombre']}' cuesta ${lugar_seleccionado['precio']} "
                        f"y solo tienes ${cliente_actual.presupuesto}."
                    )
            else:
                print("❌ ID no válido o el lugar no está disponible para estas condiciones.")

        except ValueError:
            print("❌ Por favor, introduce un número válido.")

    # --- PREPARACIÓN DE LISTAS ---
    personal_contratado = []
    servicios_elegidos = []

    # --- PASO 3: CONTRATACIÓN DE PERSONAL ---
    while True:
        fg.limpiar_pantalla()
        # El presupuesto se actualiza aquí arriba cada vez que el bucle reinicia
        print(f"--- PASO 3: PERSONAL (Dinero disponible: ${presupuesto_provisional:,.2f}) ---")
        # Def mensaje en varias líneas para que sea legible
        mensaje_prompt = (
            "\n¿Qué oficio busca? (Fotografia, Seguridad, Estetica, "
            "Planificador, Decoracion o Barman / '0' para continuar): "
        )

        # Ahora input queda corto y limpio
        tipo = input(mensaje_prompt).lower().strip()
        # 1. Validar que no sea un número (excepto el '0' para salir)
        if tipo == '0':
            break
        oficios_validos = ["fotografia", "seguridad", "estetica", "planificador", "decoracion", "barman"]
        if tipo not in oficios_validos:
            print(f"❌ '{tipo}' no es una opción válida.")
            print(f"Opciones aceptadas: {', '.join(oficios_validos)}")
            continue
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
                ya_contratado = any(
                    p.id_personal == dict_p['id_personal']
                    for p in personal_contratado
                )

                if ya_contratado:
                    print(f"⚠️ {dict_p['nombre']} ya ha sido añadido.")
                elif sueldo_p > presupuesto_provisional: # Validamos contra la temporal
                    print(f"❌ Dinero insuficiente. Falta: ${sueldo_p - presupuesto_provisional:,.2f}")
                else:
                    # CAMBIO: Restamos de la temporal, NO de cliente_actual
                    presupuesto_provisional -= sueldo_p
                    personal_contratado.append(Personal(dict_p['id_personal'], dict_p['nombre'], dict_p['oficio'], sueldo_p))

                    print(f"\n✅ CONFIRMADO: {dict_p['nombre']} como {oficio_p}.")
                    print(f"💰 Dinero restante estimado: ${presupuesto_provisional:,.2f}")
                # Está fuera de los IFs de éxito/error, así que siempre se detiene.
                input("\nPresione Enter para continuar...")

            else:
                print("❌ ID no encontrado.")
                input("Presione Enter...") # PAUSA 3

        except ValueError:
            print("⚠️ Error: Use solo números para el ID.")
            input("Presione Enter...") # PAUSA 4

    # Cubrimos: catering, bebida, postre, mobiliario, tecnologia y decoracion
    categorias_inv = ["catering", "bebida", "postre", "mobiliario", "tecnologia", "decoracion"]

    for cat in categorias_inv:
        fg.limpiar_pantalla()
        titulo = f"--- PASO 4: SELECCIÓN DE {cat.upper()} ---"
        print(titulo)
        print(f"💰 Presupuesto disponible: ${presupuesto_provisional:,.2f}\n")

        items_categoria = []
        for i in lista_inventario:
            if i.get('categoria') == cat:
                items_categoria.append(i)

        if not items_categoria:
            continue

        # Tabla alineada con ljust y rjust
        encabezado = (
            f"{'ID'.ljust(6)} | "
            f"{'PRODUCTO'.ljust(25)} | "
            f"{'PRECIO U.'.rjust(10)} | "
            f"{'STOCK'.rjust(7)}"
        )
        print(encabezado)
        print("-" * 65)
        for item in items_categoria:
            print(
                f"{str(item['id_item']).ljust(5)} | "
                f"{item['nombre'].ljust(30)} | "
                f"${str(item['precio_unidad']).rjust(9)} | "
                f"{item['cantidad']}"
            )

        while True:
            op = input(f"\nID de {cat} (o '0' para siguiente categoría): ").strip()
            if op == '0':
                break

            try:
                id_sel = int(op)
                seleccionado = fg.buscar_elemento_id(id_sel, items_categoria, 'id_item')

                if seleccionado:
                    cant = int(input(f"¿Cuántas unidades de '{seleccionado['nombre']}'?: "))
                    costo_total_item = seleccionado['precio_unidad'] * cant

                    if seleccionado['cantidad'] < cant:
                        print(f"❌ Stock insuficiente. Solo quedan {seleccionado['cantidad']}.")
                    elif costo_total_item > presupuesto_provisional:
                        print(
                            f"❌ Presupuesto insuficiente. Costo: ${costo_total_item} "
                            f"| Tienes: ${presupuesto_provisional}"
                        )
                    else:
                        # Registro de compra
                        presupuesto_provisional -= costo_total_item
                        # Guardamos en la lista de reservas
                        servicios_elegidos.append(ItemReserva(
                            seleccionado['id_item'],
                            seleccionado['nombre'],
                            seleccionado['precio_unidad'],
                            cant
                        ))
                        print(f"✅ Añadido. Presupuesto restante: ${presupuesto_provisional:,.2f}")
                else:
                    print("❌ ID no válido para esta categoría.")
            except ValueError:
                print("⚠️ Error: Ingrese solo números.")

        input("\nPresione Enter para pasar a la siguiente categoría...")

# --- PASO 5: CÁLCULOS Y COTIZACIÓN ---
    # build_cotizacion genera el objeto/diccionario con todos los costos
    cotizacion = fg.build_cotizacion(
        cliente_actual,
        lugar_seleccionado,
        personal_contratado,
        servicios_elegidos,
        fecha_str,
        h_ini,
        h_fin
    )

    # --- PASO 5.5: VALIDACIÓN INTELIGENTE (EL FILTRO DE SEGURIDAD) ---
    # Lo hacemos ANTES de pedir la confirmación
    es_valido, mensaje = fg.validar_restricciones_inteligentes(
        personal_contratado,
        servicios_elegidos,
        lugar_seleccionado,
        invitados_val
    )

    if not es_valido:
        print("\n" + "!"*50)
        print("❌ ERROR DE LOGÍSTICA DETECTADO:")
        print(f"👉 {mensaje}")
        print("!"*50)
        print("\nNo podemos proceder con esta cotización. Por favor, reinicie el proceso.")
        input("Presione Enter para volver al menú...")
        return # Aquí detienes el proceso para que no se guarde nada malo

    # --- PASO 6: CIERRE Y BLOQUEO ---
    # Pasamos las listas para que, si confirma, la función pueda actualizar el stock
    confirmado = fg.approve_cotizacion(
        cotizacion,
        lista_lugares,
        lista_personal,
        lista_inventario
    )
    if confirmado:
        fg.procesar_confirmacion_boda(cotizacion, lista_lugares, lista_personal, lista_inventario)
        # 1. GUARDAR CAMBIOS EN JSON (Persistencia)
        fg.write_json('data/lugares.json', lista_lugares)
        fg.write_json('data/personal.json', lista_personal)
        fg.write_json('data/inventario.json', lista_inventario)
        # 2. GENERACIÓN DEL TICKET TXT
        # Usamos los datos calculados para que el cliente tenga su comprobante
        fg.generar_ticket(
            cliente_actual,
            lugar_seleccionado,
            personal_contratado,
            servicios_elegidos,
            cotizacion['subtotal'],
            cotizacion['comision'],
            cotizacion['total_final'],
            fecha_boda
        )
        fg.guardar_reserva_json(cotizacion)
        print("\n" + "🎉" * 20)
        print("¡BODA REGISTRADA Y RESERVADA CON ÉXITO!".center(40))
        print("🎉" * 20)
    else:
        print("\n⚠️ Registro cancelado. Los recursos no han sido bloqueados.")
