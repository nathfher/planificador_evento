from datetime import datetime,timedelta
import funciones_generales as fg
from modulos import Cliente, Personal, ItemReserva

def ejecutar_registro_boda():

    fg.limpiar_pantalla()
    print("=================================================")
    print("   BIENVENIDO AL SISTEMA RAQUEL & ALBA PLANNER  ")
    print("=================================================\n")

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
        
        # 1. Verificamos que no esté vacío después del strip
        if not name_client:
            print("⚠️ El nombre no puede estar vacío.")
            continue

        # 2. Reemplazamos espacios para validar solo letras
        # Esto permite nombres como "Raquel García" pero bloquea "Raquel_García"
        solo_letras = name_client.replace(" ", "")

        # 3. Validaciones combinadas:
        if len(name_client) < 8:
            print("⚠️ Nombre demasiado corto. Debe tener mín. 8 caracteres.")
        elif not solo_letras.isalpha():
            print("⚠️ Nombre inválido. No use números, guiones ni símbolos (solo letras).")
        else:
            # Si pasa todo, salimos
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
            presupuesto_val = float(input("¿Presupuesto máximo? (Mínimo $3000): "))
            if presupuesto_val >= 3000:
                break
            print("❌ El presupuesto mínimo aceptado es de $3000.")
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
        hoy = datetime.now().date()
        try:
            fecha_boda = datetime.strptime(fecha_input, "%d/%m/%Y").date()
            if fecha_boda < hoy:
                print("❌ No puedes elegir una fecha pasada. ¡Planificamos el futuro!")
                continue
            # 2. Validar el límite de 2 años (Evita el año 2100)
            limite_futuro = hoy + timedelta(days=730) # 2 años aprox.
            if fecha_boda > limite_futuro:
                print("⚠️ Error: No aceptamos reservas con más de 2 años de antelación.")
                print(f"El límite máximo es: {limite_futuro.strftime('%d/%m/%Y')}")
                continue
            fecha_str = fecha_input
            break # Fecha válida, pasamos a la hora
        except ValueError:
            print("⚠️ Formato incorrecto. Debe ser día/mes/año (ej: 15/05/2026)")

    # --- PASO 2.2: REGISTRO DE HORARIOS ---
    print(f"\nDefina el horario para el {fecha_str} (Formato 24h, ej: 12:00 o 17:30):")
    while True:
        # VALIDACIONES ESTRICTAS:
        # 1. Debe tener exactamente 5 caracteres (00:00)
        # 2. Debe tener un solo ':' en la posición 2
        # 3. Solo debe haber un ':' en toda la cadena
        h_ini = input("Hora de inicio: ").strip()
        if len(h_ini) == 5 and h_ini[2] == ":" and h_ini.count(":") == 1:
            try:
                t_ini = datetime.strptime(h_ini, "%H:%M")
                break
            except ValueError:
                print("❌ Hora inexistente. Use el rango 00:00 - 23:59.")
        else:
            print("⚠️ Formato incorrecto. Use estrictamente HH:MM (5 caracteres y un solo ':').")
            print("Ejemplo: Para las 3 de la tarde, escriba 15:00")

    while True:
        h_fin = input("Hora de finalización (Formato HH:MM, ej. 21:30): ").strip()

        if len(h_fin) == 5 and h_fin[2] == ":" and h_fin.count(":") == 1:
            try:
                t_ini = datetime.strptime(h_ini, "%H:%M")
                t_fin = datetime.strptime(h_fin, "%H:%M")

                # --- 1. AJUSTE DE MEDIA NOCHE ---
                # Si fin es menor que inicio (ej: 02:00 < 22:00), sumamos un día
                if t_fin < t_ini:
                    t_fin = t_fin + timedelta(days=1)

                # --- 2. CÁLCULO REAL ---
                diferencia = t_fin - t_ini
                total_segundos = diferencia.total_seconds()
                segundos_minimos = 2 * 3600 # 2 horas

                # --- 3. VALIDACIONES DE NEGOCIO ---
                if t_fin == t_ini:
                    print("❌ La hora de fin no puede ser igual a la de inicio.")
                elif total_segundos < segundos_minimos:
                    minutos_reales = total_segundos / 60
                    print(f"❌ Duración insuficiente. Mínimo 2 horas (Su evento dura: {minutos_reales:.0f} min).")
                else:
                    # PERFECTO
                    break

            except ValueError:
                print("❌ Hora inexistente (use rango 00:00 - 23:59).")
        else:
            print("⚠️ Formato incorrecto. Use HH:MM (ej. 20:00).")

        input("Presione Enter para reintentar...")

    # Fuera del bucle, confirmamos éxito
        horas_finales = (t_fin - t_ini).total_seconds() / 3600
        print(f"✅ Horario confirmado. Duración total: {horas_finales:.1f} horas.")
        input("\nPresione Enter para continuar con la selección del lugar...")

# --- PASO 3: SELECCIÓN DE LUGAR (Dentro de un bucle de reintento) ---
    while True:
        fg.limpiar_pantalla()
        print(f"{'='*60}\n{'CATÁLOGO DE SALONES DISPONIBLES'.center(60)}\n{'='*60}")

        # 1. OBTENER DISPONIBILIDAD REAL
        lugares_libres, sugerencias = fg.get_lugares_disponibles(
            fecha_str, lista_lugares, h_ini, h_fin, invitados_val
        )

        # 2. VALIDAR SI NO HAY OPCIONES
        if not lugares_libres:
            print(f"\n❌ No hay lugares disponibles para el {fecha_str} a las {h_ini}.")
            if sugerencias:
                print("\n💡 SUGERENCIAS EN OTRAS FECHAS:")
                for sug in sugerencias:
                    print(f"   -> '{sug['nombre']}' disponible el día {sug['fecha']}")

            print("\n¿Qué desea hacer?")
            print("1. Cambiar fecha/hora o invitados (Reintentar)")
            print("2. Cancelar y volver al menú principal")
            opc = input("Seleccione una opción: ")

            if opc == '1':
                fecha_input = input("Nueva fecha (DD/MM/AAAA): ")
                # Aquí podrías meter la validación de fecha que hicimos antes
                fecha_str = fecha_input
                invitados_val = int(input("Nueva cantidad de invitados: "))
                continue  # <--- Ahora sí funciona: vuelve al inicio del while
            else:
                return # Sale al menú principal

        # 3. SI HAY LUGARES, MOSTRAR FICHAS DESCRIPTIVAS
        for l in lugares_libres:
            print(f"ID: {str(l['id_lugar']).ljust(3)} | 🏛️  {l['nombre'].upper()}")
            print(f"      👥 Capacidad: {str(l['capacidad']).rjust(3)} pers. | 💰 Precio: ${l['precio']:>8.2f}")

            if l.get('servicios_incluidos'):
                servicios_str = ", ".join(l['servicios_incluidos'])
                print(f"      🎁 Incluye: {servicios_str}")

            if "piscina" in l['nombre'].lower() or any("piscina" in s.lower() for s in l.get('servicios_incluidos', [])):
                print("      ⚠️  NOTA: Este lugar requiere personal de SEGURIDAD obligatorio.")

            print("-" * 60)

        # 4. SELECCIÓN FINAL
        try:
            id_selec = int(input("\nIngrese el ID del lugar que desea reservar: "))
            # Buscamos el lugar por ID dentro de los que están libres
            lugar_elegido = next((lug for lug in lugares_libres if lug['id_lugar'] == id_selec), None)

            if lugar_elegido:
                print(f"✅ ¡'{lugar_elegido['nombre']}' seleccionado con éxito!")
                input("Presione Enter para continuar al personal...")
                break # <--- Rompe el while y pasa al Paso 4
            else:
                print("❌ El ID ingresado no está en la lista de lugares disponibles.")
                input("Presione Enter para intentar de nuevo...")
        except ValueError:
            print("❌ Por favor, ingrese un número de ID válido.")
            input("Presione Enter para intentar de nuevo...")

    # --- 4. BUCLE DE SELECCIÓN Y VALIDACIÓN ---
    presupuesto_provisional = cliente_actual.presupuesto
    lugar_elegido = None
    while lugar_elegido is None:
        try:
            print(f"\n💰 Su presupuesto actual: ${cliente_actual.presupuesto:,.2f}")
            id_lug = int(input("Seleccione el ID del lugar que desea (o '0' para cancelar): "))

            if id_lug == 0:
                print("Operación cancelada por el usuario.")
                return

            # Buscamos en la lista de los que están LIBRES y tienen CAPACIDAD
            lugar_seleccionado = fg.buscar_elemento_id(id_lug, lugares_libres, 'id_lugar')

            if lugar_seleccionado:
                # Validamos si el dinero le alcanza
                if fg.can_select_lugar(cliente_actual.presupuesto, lugar_seleccionado['precio']):
                    lugar_elegido = lugar_seleccionado
                    if "piscina" in lugar_elegido['nombre'].lower() or any("piscina" in s.lower() for s in lugar_elegido.get('servicios_incluidos', [])):
                        print("\n📢 AVISO: Este lugar tiene piscina. El sistema le obligará a contratar Seguridad más adelante.")

                    # Restamos del presupuesto provisional para los siguientes pasos
                    presupuesto_provisional -= lugar_elegido['precio']

                    print(f"\n✅ EXCELENTE ELECCIÓN: {lugar_elegido['nombre']}")
                    print(f"💵 Presupuesto restante para catering y personal: ${presupuesto_provisional:,.2f}")
                    input("\nPresione Enter para continuar a la contratación de personal...")
                else:
                    print(
                        f"\n❌ ¡PRESUPUESTO INSUFICIENTE! \n"
                        f"   El salón '{lugar_seleccionado['nombre']}' cuesta ${lugar_seleccionado['precio']:,.2f} \n"
                        f"   y su límite es de ${cliente_actual.presupuesto:,.2f}."
                    )
            else:
                print("❌ ID no válido o el lugar no cumple con los requisitos de su fecha/invitados.")

        except ValueError:
            print("❌ Error: Por favor, introduce un número de ID válido.")
    # --- PREPARACIÓN DE LISTAS ---
    personal_contratado = []
    servicios_elegidos = []

        # --- PASO 4: CONTRATACIÓN DE PERSONAL ---
    while True:
        fg.limpiar_pantalla()
    # Mostramos quiénes ya están en el equipo para no perder la cuenta
        equipo_nombres = [p.nombre for p in personal_contratado]
        print(f"--- PASO 4: PERSONAL (Disponible: ${presupuesto_provisional:,.2f}) ---")
        print(f"Equipo actual: {', '.join(equipo_nombres) if equipo_nombres else 'Ninguno'}")

        mensaje_prompt = ("\n¿Qué oficio busca? (Fotografia, Seguridad, Estetica, "
                      "Planificador, Flores, Iluminacion, Barman / '0' para finalizar): ")
        tipo = input(mensaje_prompt).lower().strip()

        if tipo == '0':
        # Validación de Seguridad/Piscina
            tiene_piscina = "piscina" in lugar_elegido['nombre'].lower() or \
                any("piscina" in s.lower() for s in lugar_elegido.get('servicios_incluidos', []))
            tiene_seguridad = any("seguridad" in p.oficio.lower() for p in personal_contratado)

            if tiene_piscina and not tiene_seguridad:
                print("\n❌ BLOQUEO: El lugar tiene piscina. DEBE contratar Seguridad.")
                input("Presione Enter para volver...")
                continue
            break

        oficios_validos = ["fotografia", "seguridad", "estetica", "planificador", "flores", "iluminacion", "barman"]
        if tipo not in oficios_validos:
            print(f"❌ '{tipo}' no es válido.")
            input("Presione Enter...")
            continue

    # Búsqueda real de disponibles
        pers_libres = fg.get_personal_disponible(tipo, lista_personal, fecha_str, h_ini, h_fin)

        if not pers_libres:
            print(f"❌ No hay {tipo} disponible para esa fecha/hora.")
            input("Presione Enter...")
            continue

        fg.imprimir_tabla_personal(pers_libres)

        try:
            id_p = int(input(f"ID del {tipo} a contratar (0 para volver): "))
            if id_p == 0:
                continue

        # CAMBIO CLAVE: Buscar solo entre los que están LIBRES
            dict_p = fg.buscar_elemento_id(id_p, pers_libres, 'id_personal')

            if dict_p:
                sueldo_p = dict_p['sueldo']
            # Evitar duplicados
                if any(p.id_personal == dict_p['id_personal'] for p in personal_contratado):
                    print("⚠️ Este trabajador ya está en tu equipo.")
                elif sueldo_p > presupuesto_provisional:
                    print(f"❌ Presupuesto insuficiente. Falta: ${sueldo_p - presupuesto_provisional:,.2f}")
                else:
                # Si todo está ok, contratamos
                    presupuesto_provisional -= sueldo_p
                # Creamos el objeto (Asegúrate que 'Personal' esté importado)
                    nuevo_socio = Personal(
                        dict_p['id_personal'],
                        dict_p['nombre'],
                        dict_p['oficio'],
                        sueldo_p,
                        dict_p.get('experiencia', 'Estándar')
                    )
                    personal_contratado.append(nuevo_socio)
                    print(f"✅ CONFIRMADO: {dict_p['nombre']} se une a la boda.")
            else:
                print("❌ ID no válido o el trabajador no está disponible.")

            input("\nPresione Enter para continuar...")

        except ValueError:
            print("⚠️ Error: Ingrese un número de ID válido.")
            input("Presione Enter...")
    # --- PASO 4: INVENTARIO CON VALIDACIÓN BLOQUEANTE ---
    tiene_florista = any(p.oficio.lower() == "flores" for p in personal_contratado)
    tiene_iluminador = any(p.oficio.lower() == "iluminacion" for p in personal_contratado)

    categorias_inv = ["catering", "bebida", "postre", "mobiliario", "tecnologia", "decoracion"]

    for cat in categorias_inv:
        while True: # Bucle de categoría para evitar que avancen si no cumplen requisitos
            fg.limpiar_pantalla()
            print(f"--- PASO 4: {cat.upper()} (Disponible: ${presupuesto_provisional:,.2f}) ---")
            
            if cat == "decoracion":
                if tiene_florista: print("🌸 NOTA: Tiene Florista. Compre flores/arcos.")
                if tiene_iluminador: print("💡 NOTA: Tiene Iluminador. Compre luces/LED.")

            items_categoria = [i for i in lista_inventario if i.get('categoria') == cat]
            if not items_categoria: break

            # Mostrar tabla (resumido para el ejemplo)
            print(f"{'ID':<6} | {'PRODUCTO':<25} | {'PRECIO':<10} | {'STOCK'}")
            for item in items_categoria:
                print(f"{item['id_item']:<6} | {item['nombre']:<25} | {item['precio_unidad']:<10} | {item['cantidad']}")

            # Bucle de selección de productos
            while True:
                op = input(f"\nID de {cat} ('0' para intentar finalizar categoría): ").strip()
                if op == '0': break 

                try:
                    id_sel = int(op)
                    seleccionado = fg.buscar_elemento_id(id_sel, items_categoria, 'id_item')
                    if seleccionado:
                        # --- VALIDACIONES DE CONFLICTO INMEDIATAS ---
                        nombre_n = seleccionado['nombre'].lower()
                        tiene_dj = any("dj" in p.oficio.lower() for p in personal_contratado)
                        
                        if "rock" in nombre_n and tiene_dj:
                            print("❌ Conflicto: No se puede tener Banda de Rock y DJ.")
                            continue
                        if "mariachi" in nombre_n and "cristal" in lugar_elegido['nombre'].lower():
                            print("❌ El Palacio de Cristal no admite Mariachis.")
                            continue

                        cant = int(input(f"¿Unidades de '{seleccionado['nombre']}'?: "))
                        costo = seleccionado['precio_unidad'] * cant

                        if seleccionado['cantidad'] < cant:
                            print("❌ Stock insuficiente.")
                        elif costo > presupuesto_provisional:
                            print("❌ Presupuesto insuficiente.")
                        else:
                            presupuesto_provisional -= costo
                            servicios_elegidos.append(ItemReserva(seleccionado['id_item'], seleccionado['nombre'], seleccionado['precio_unidad'], cant))
                            print(f"✅ Añadido. Restante: ${presupuesto_provisional:,.2f}")
                    else:
                        print("❌ ID no válido.")
                except ValueError:
                    print("⚠️ Use números.")

            # --- VALIDACIÓN AL INTENTAR SALIR DE LA CATEGORÍA ---
            # Si el usuario presiona 0, verificamos si puede irse
            cumple_requisitos = True
            if cat == "mobiliario":
                cant_sillas = sum(item.cantidad_requerida for item in servicios_elegidos if "silla" in item.nombre.lower())
                sillas_min = int(cliente_actual.invitados * 0.8)
                if cant_sillas < sillas_min:
                    print(f"\n❌ NO PUEDE CONTINUAR: Faltan sillas ({cant_sillas}/{sillas_min} mín).")
                    input("Presione Enter para volver a comprar mobiliario...")
                    cumple_requisitos = False
            
            if cat == "decoracion":
                nombres_c = [item.nombre.lower() for item in servicios_elegidos]
                if tiene_florista and not any("flor" in n for n in nombres_c):
                    print("\n❌ LOGÍSTICA: Contrató Florista pero no compró flores.")
                    input("Presione Enter para corregir...")
                    cumple_requisitos = False

            if cumple_requisitos:
                break # Sale del bucle de la categoría actual y va a la siguiente

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
    es_valido, mensaje = fg.val_restricc(
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
        # --- ANTES DE MOSTRAR EL TOTAL FINAL ---
    valido, mensaje = fg.val_restricc(personal_contratado, servicios_elegidos, lugar_elegido, cliente_actual.invitados)

    if not valido:
        print("\n" + "!"*60)
        print(f" ❌ ATENCIÓN: {mensaje}")
        print("!"*60)
        print("No se puede proceder con la reserva. Por favor, revise sus selecciones.")
        input("Presione Enter para reiniciar el proceso...")
        return # Esto rompe la función y no guarda nada en el JSON
    # Pasamos las listas para que, si confirma, la función pueda actualizar el stock
    print("\n✅ Logística validada con éxito.")
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
