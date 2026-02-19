"""
Módulo de registro y planificación de eventos para 'Raquel & Alba'.
Este módulo gestiona el flujo principal de contratación de personal,
selección de lugar y validación de presupuestos.
"""
from datetime import datetime,timedelta
import re
import funciones_generales as fg
from modulos import Cliente, Personal, ItemReserva

def ejecutar_registro_boda():
    """
    Ejecuta el asistente interactivo para registrar una nueva boda.
    """

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

        if not name_client:
            print("⚠️ El nombre no puede estar vacío.")
            continue

        # Preparación para validaciones
        palabras = name_client.lower().split()
        solo_letras = name_client.replace(" ", "")

        # A. Evitar palabras repetidas (ej: "pedro pedro pedro")
        repetida = any(palabras.count(p) > 2 for p in palabras)

        # B. Evitar "disparates" (Regex para 5 o más consonantes seguidas)
        tiene_basura = re.search(r'[^aeiouáéíóúü\s]{5,}', name_client.lower())

        # --- VALIDACIÓN ÚNICA (ORDENADA) ---
        if len(name_client) < 8:
            print("⚠️ Nombre demasiado corto (mín. 8 caracteres).")
        elif not solo_letras.isalpha():
            print("⚠️ Solo se permiten letras y espacios.")
        elif repetida:
            print("⚠️ Nombre inválido: demasiadas palabras repetidas.")
        elif tiene_basura:
            print("⚠️ El nombre parece inválido (letras aleatorias detectadas).")
        else:
            # ÉXITO: Formateamos y salimos
            name_client = name_client.title()
            break
    # # 3. VALIDAR CORREO
    while True:
        correo_temp = input("Ingrese correo (@gmail.com): ").lower().strip()

        if " " in correo_temp:
            print("❌ El correo no puede contener espacios.")
            continue

        if correo_temp.endswith("@gmail.com"):
            usuario = correo_temp.split('@')[0]

            # --- NUEVAS VALIDACIONES DE SEGURIDAD ---

            # 1. Detectar símbolos repetidos (ej: "......" o "------")
            simbolos_repetidos = re.search(r'[\._-]{2,}', usuario)

            # 2. Detectar si empieza o termina con un símbolo (inválido en Gmail)
            borde_invalido = (
                usuario.startswith(('.', '-', '_')) or
                usuario.endswith(('.', '-', '_'))
            )

            # 3. Detectar caracteres no permitidos ( puntos, guiones y guiones bajos)
            caracteres_prohibidos = re.search(r'[^a-z0-9\._-]', usuario)

            # 4. Tu validación de "basura" (consonantes seguidas)
            es_basura = re.search(r'[^aeiou0-9]{5,}', usuario)

            if len(usuario) < 4:
                print("❌ El nombre de usuario del correo es muy corto (mín. 4 caracteres).")
            elif simbolos_repetidos:
                print("❌ El correo no puede tener puntos o guiones seguidos.")
            elif borde_invalido:
                print("❌ El correo no puede empezar ni terminar con símbolos.")
            elif caracteres_prohibidos:
                print("❌ El correo contiene caracteres no permitidos.")
            elif es_basura:
                print("❌ El correo parece generado aleatoriamente (basura).")
            else:
                # ÉXITO
                break
        else:
            print("❌ Debe ser una dirección válida que termine en @gmail.com")
# 4. VALIDAR INVITADOS (Con lógica de evento real)
    while True:
        try:
            invitados_val = int(input("¿Cuántos invitados espera? (30 - 350): "))
            if invitados_val < 0:
                print("\n❌ ERROR: El presupuesto no puede ser negativo.")
                print("   Por favor, ingrese un monto real (sin signos de menos).")
                continue

            if invitados_val < 30:
                print("⚠️ Lo sentimos. El mínimo aceptado para que la "
                        "logística sea viable es de 30 personas.")
                continue

            if invitados_val > 350:
                print("⚠️ Cantidad excedida. El límite de nuestros salones es 350 invitados.")
                continue

            # Si llega aquí, es porque está entre 30 y 350
            break

        except ValueError:
            print("❌ Error: Ingrese un número entero (ej: 150).")

    # 5. VALIDAR PRESUPUESTO
# 5. VALIDAR PRESUPUESTO
    while True:
        try:
            presupuesto_val = float(input("¿Presupuesto máximo? (Mínimo $4000): "))

            # 1. Filtro de números negativos (La muela de coherencia)
            if presupuesto_val < 0:
                print("\n❌ ERROR: El presupuesto no puede ser negativo.")
                print("   Por favor, ingrese un monto real (sin signos de menos).")
                continue

            # 2. Filtro de presupuesto insuficiente
            if presupuesto_val < 4000:
                print("\n❌ PRESUPUESTO INSUFICIENTE: El mínimo para iniciar es de $4000.")
                print("   Nuestros estándares de calidad requieren una inversión mayor.")
                continue

            # 3. Filtro de presupuesto exagerado (El límite de "billonarios")
            if presupuesto_val > 1000000:
                print("\n🧐 ¡WOW!: Ese es un presupuesto digno de la Realeza.")
                print("   Por seguridad, el límite para cotizaciones automáticas es de $1,000,000.")
                print("   Si es más rico que eso, contacte a Raquel directamente por teléfono. 😉")
                continue

            # Si pasó todos los filtros anteriores, el dato es correcto
            break

        except ValueError:
            print("\n❌ FORMATO INCORRECTO: Ingrese solo números (ej: 50000). No use puntos de mil.")

    # AL FINAL: Creamos el objeto una sola vez
    cliente_actual = Cliente(id_client, name_client, correo_temp, invitados_val, presupuesto_val)
    presupuesto_provisional = cliente_actual.presupuesto # variable temporal
    fecha_boda = None
    input("\nPresione Enter para continuar con el registro de la fecha...")
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
                if t_fin < t_ini:
                    t_fin = t_fin + timedelta(days=1)

                # --- 2. CÁLCULO PARA VALIDAR ---
                diferencia = t_fin - t_ini
                total_segundos = diferencia.total_seconds()
                segundos_minimos = 2 * 3600

                # --- 3. VALIDACIONES ---
                if t_fin == t_ini:
                    print("❌ La hora de fin no puede ser igual a la de inicio.")
                elif total_segundos < segundos_minimos:
                    minutos_reales = total_segundos / 60
                    print(f"❌ Duración insuficiente. Mínimo 2 horas "
                          f"(Su evento dura: {minutos_reales:.0f} min).")
                else:
                    # SI ESTÁ BIEN, SALIMOS
                    break

            except ValueError:
                print("❌ Hora inexistente (use rango 00:00 - 23:59).")
        else:
            print("⚠️ Formato incorrecto. Use HH:MM (ej. 20:00).")

        input("Presione Enter para reintentar...")

    # --- FUERA DEL BUCLE: AQUÍ HACEMOS EL CÁLCULO FINAL ---
    diferencia_final = t_fin - t_ini
    total_horas = diferencia_final.total_seconds() / 3600
    horas = int(total_horas)
    minutos = int((total_horas * 60) % 60)

    print("\n✅ Horario confirmado.")
    print(f"⏱️  Duración total: {horas}h {minutos}min")
    input("\nPresione Enter para continuar con la selección del lugar...")
# --- PASO 3: SELECCIÓN DE LUGAR (Bucle único y limpio) ---
    lugar_elegido = None
    presupuesto_provisional = cliente_actual.presupuesto

    while lugar_elegido is None:
        fg.limpiar_pantalla()
        print(f"{'='*60}\n{'CATÁLOGO DE SALONES DISPONIBLES'.center(60)}\n{'='*60}")
        print(f"💰 Presupuesto disponible: ${cliente_actual.presupuesto:,.2f}\n")

        # 1. OBTENER DISPONIBILIDAD REAL
        lugares_libres, sugerencias = fg.get_lugares_disponibles(
            fecha_str, lista_lugares, h_ini, h_fin, invitados_val
        )

        # 2. VALIDAR SI NO HAY OPCIONES
        if not lugares_libres:
            print(f"❌ No hay lugares disponibles para el {fecha_str}.")
            if sugerencias:
                print("\n💡 SUGERENCIAS EN OTRAS FECHAS:")
                for sug in sugerencias:
                    print(f"   -> '{sug['nombre']}' disponible el día {sug['fecha']}")

            print("\n¿Qué desea hacer?\n1. Cambiar fecha/invitados\n2. Cancelar")
            opc = input("Seleccione: ")
            if opc == '1':
                fecha_str = input("Nueva fecha (DD/MM/AAAA): ")
                invitados_val = int(input("Cantidad de invitados: "))
                continue
            else:
                return

        # 3. MOSTRAR FICHAS DESCRIPTIVAS
        for l in lugares_libres:
            print(f"ID: {str(l['id_lugar']).ljust(3)} | 🏛️  {l['nombre'].upper()}")
            cap = str(l['capacidad']).rjust(3)
            precio_f = f"{l['precio']:>8.2f}"
            print(f"      👥 Capacidad: {cap} pers. | 💰 Precio: ${precio_f}")
            if l.get('servicios_incluidos'):
                servicios_txt = ", ".join(l['servicios_incluidos'])
                print(f"      🎁 Incluye: {servicios_txt}")
            nombre_piscina = "piscina" in l['nombre'].lower()
            servicios_piscina = any(
                "piscina" in s.lower() 
                for s in l.get('servicios_incluidos', [])
            )
            if nombre_piscina or servicios_piscina:
                print("      ⚠️  NOTA: Requiere SEGURIDAD obligatorio.")


        # 4. SELECCIÓN Y VALIDACIÓN ECONÓMICA
        try:
            id_selec = int(input("\nIngrese el ID del lugar para reservar (0 para cancelar): "))
            if id_selec == 0:
                return

            # Buscamos el lugar seleccionado
            seleccionado = fg.buscar_elemento_id(id_selec, lugares_libres, 'id_lugar')

            if seleccionado:
                # Validamos dinero
                if fg.can_select_lugar(cliente_actual.presupuesto, seleccionado['precio']):
                    lugar_elegido = seleccionado
                    # RESTA REAL
                    presupuesto_provisional -= lugar_elegido['precio']

                    print(f"✅ ¡'{lugar_elegido['nombre']}' reservado con éxito!")
                    print(f"💵 Presupuesto restante: ${presupuesto_provisional:,.2f}")
                    input("\nPresione Enter para continuar al personal...")
                else:
                    costo_salon = seleccionado['precio']
                    print(f"❌ PRESUPUESTO INSUFICIENTE. "
                        f"El salón cuesta ${costo_salon:,.2f}")
                    input("Presione Enter para intentar con otro...")
            else:
                print("❌ ID no válido o no disponible en esta fecha.")
                input("Presione Enter...")

        except ValueError:
            print("❌ Error: Ingrese un número de ID válido.")
            input("Presione Enter...")


# --- PASO 4: CONTRATACIÓN DE PERSONAL ---
    personal_contratado = []
    servicios_elegidos = []

    while True:
        fg.limpiar_pantalla()

        # 1. CABECERA DINÁMICA
        equipo_nombres = [p.nombre for p in personal_contratado]
        print("="*60)
        print(f"--- PASO 4: PERSONAL (Presupuesto: ${presupuesto_provisional:,.2f}) ---")
        print(f"Equipo actual: {', '.join(equipo_nombres) if equipo_nombres else 'Ninguno'}")
        print("="*60)

        # 2. SELECCIÓN DE OFICIO
        print("\nOficios disponibles: Fotografia, Seguridad, Estetica, "
              "Planificador, Flores, Iluminacion, Barman")
        tipo = input("¿Qué oficio busca? (o '0' para finalizar): ").lower().strip()

        # --- SALIDA Y VALIDACIÓN BLOQUEANTE ---
        if tipo == '0':
            # Validación de Seguridad/Piscina
            tiene_piscina = (
                "piscina" in lugar_elegido['nombre'].lower() or 
                any("piscina" in s.lower()
                    for s in lugar_elegido.get('servicios_incluidos', []))
            )

            tiene_seguridad = any(
                "seguridad" in p.oficio.lower() 
                for p in personal_contratado
            )
            if tiene_piscina and not tiene_seguridad:
                print("\n" + "!"*60)
                print("❌ ERROR DE SEGURIDAD: El lugar tiene piscina. DEBE contratar Seguridad.")
                print("!"*60)
                input("Presione Enter para volver a contratar...")
                continue
            break # Sale del bucle de personal

        # 3. VALIDAR OFICIO EXISTENTE
        oficios_validos = [
            "fotografia", "seguridad", "estetica", "planificador", 
            "flores", "iluminacion", "barman"
        ]
        if tipo not in oficios_validos:
            print(f"\n❌ ERROR: '{tipo}' no es una categoría válida.")
            print(f"👉 Solo puede elegir entre: {', '.join(oficios_validos)}")
            print("⚠️ Asegúrese de escribirlo correctamente y sin puntos.")
            input("Presione Enter para reintentar...")
            continue

        # 4. BÚSQUEDA DE DISPONIBLES
        pers_libres = fg.get_personal_disponible(tipo, lista_personal, fecha_str)

        if not pers_libres:
            print(f"\n❌ No hay personal de {tipo.upper()} disponible para el {fecha_str}.")
            input("Presione Enter para buscar otro oficio...")
            continue

        # 5. MOSTRAR TABLA Y SELECCIÓN
        fg.imprimir_tabla_personal(pers_libres)

        try:
            id_p = int(input(f"\nID del {tipo} a contratar (0 para volver): "))
            if id_p == 0:
                continue

            # Buscar el objeto real en la lista de libres
            dict_p = fg.buscar_elemento_id(id_p, pers_libres, 'id_personal')

            if dict_p:
                sueldo_p = dict_p['sueldo']

                # VALIDACIÓN: Ya está en el equipo
                if any(p.id_personal == dict_p['id_personal'] for p in personal_contratado):
                    print("\n⚠️ Este trabajador ya fue añadido a su equipo.")

                # VALIDACIÓN: Dinero
                elif sueldo_p > presupuesto_provisional:
                    print("\n❌ PRESUPUESTO INSUFICIENTE.")
                    print(f"Cuesta: ${sueldo_p:,.2f} | Le quedan: ${presupuesto_provisional:,.2f}")

                #  Contratar
                else:
                    presupuesto_provisional -= sueldo_p
                    nuevo_socio = Personal(
                        dict_p['id_personal'],
                        dict_p['nombre'],
                        dict_p['oficio'],
                        sueldo_p,
                        dict_p.get('experiencia', 'Estándar')
                    )
                    personal_contratado.append(nuevo_socio)
                    print(f"\n✅ EXCELENTE: {dict_p['nombre']} ha sido contratado.")
            else:
                print("\n❌ ID no válido o no está en la lista de disponibles.")

            input("\nPresione Enter para continuar...")

        except ValueError:
            print("\n❌ ERROR: El ID debe ser un número entero.")
            input("Presione Enter...")
# --- PASO 4: INVENTARIO CON VALIDACIÓN BLOQUEANTE ---
    tiene_florista = any(p.oficio.lower() == "flores" for p in personal_contratado)
    tiene_iluminador = any(p.oficio.lower() == "iluminacion" for p in personal_contratado)
    tiene_dj = any("dj" in p.oficio.lower() for p in personal_contratado)

    categorias_inv = ["catering", "bebida", "postre", "mobiliario", "tecnologia", "decoracion"]

    for cat in categorias_inv:
        while True:
            fg.limpiar_pantalla()
            presupuesto_antes_de_cat = presupuesto_provisional
            items_en_esta_ronda = []

            print(f"{'='*60}\n{f'PASO 4: {cat.upper()}'.center(60)}\n{'='*60}")
            print(f"💰 Presupuesto para esta sección: ${presupuesto_provisional:,.2f}")

            items_categoria = [i for i in lista_inventario if i.get('categoria') == cat]
            if not items_categoria:
                break

            # --- TABLA DE PRODUCTOS ---
            print(f"\n{'ID':<6} | {'PRODUCTO':<25} | {'PRECIO':<10} | {'STOCK'}")
            print("-" * 60)
            for item in items_categoria:
# Usando f-strings (el estándar actual de Python)
                # 1. Defines el "molde" una sola vez antes del bucle (o dentro)
                formato = "{{:<6}} | {{:<25}} | ${{:<9.2f}} | {{}}"

# 2. En el print solo pasas los datos
                print(formato.format(
                        item['id_item'],
                        item['nombre'],
                        item['precio_unidad'],
                        item['cantidad']
                        ))

            # Bucle de selección
            while True:
                op = input(f"\nID de {cat} (o '0' para finalizar selección): ").strip()
                if op == '0':
                    break

                try:
                    id_sel = int(op)
                    seleccionado = fg.buscar_elemento_id(id_sel, items_categoria, 'id_item')

                    if not seleccionado:
                        print("❌ ID no válido.")
                        continue

                    cant = int(input(f"¿Unidades de '{seleccionado['nombre']}'?: "))
                    if cant <= 0:
                        continue

                    costo = seleccionado['precio_unidad'] * cant

                    if seleccionado['cantidad'] < cant:
                        print("❌ Stock insuficiente.")
                    elif costo > presupuesto_provisional:
                        print("❌ Presupuesto insuficiente.")
                    else:
                        presupuesto_provisional -= costo
                        items_en_esta_ronda.append(ItemReserva(
                            seleccionado['id_item'], seleccionado['nombre'],
                            seleccionado['precio_unidad'], cant
                        ))
                        print(f"✅ Añadido: {seleccionado['nombre']} x{cant}")
                except ValueError:
                    print("⚠️ Ingrese números válidos.")

            # --- VALIDACIÓN BLOQUEANTE ---
            cumple_requisitos = True
            servicios_totales_temp = servicios_elegidos + items_en_esta_ronda
            nombres_comprados = [i.nombre.lower() for i in servicios_totales_temp]

            # VALIDACIÓN DE MOBILIARIO (Ya la tienes)
            if cat == "mobiliario":
                # 1. Extraemos las cantidades en una línea corta
                sillas_pedidas = [i.cantidad_requerida for i in servicios_totales_temp
                                 if "silla" in i.nombre.lower()]
                mesas_pedidas = [i.cantidad_requerida for i in servicios_totales_temp
                                 if "mesa" in i.nombre.lower()]

                # 2. Sumamos el resultado
                cant_sillas = sum(sillas_pedidas)
                cant_mesas = sum(mesas_pedidas)

                # 3. Validación
                sillas_min = int(cliente_actual.invitados * 0.8)
                if cant_sillas < sillas_min:
                    print(f"\n❌ ERROR: Faltan sillas ({cant_sillas}/{sillas_min}).")
                    cumple_requisitos = False
                if cant_sillas < int(cliente_actual.invitados * 0.8):
                    print("\n❌ ERROR: Faltan sillas.")
                    cumple_requisitos = False

                if cant_mesas <= 0:
                    print("\n❌ ERROR: No ha seleccionado ninguna mesa.")
                    cumple_requisitos = False

            # 2. VALIDACIÓN DE TECNOLOGÍA (DJ)
            elif cat == "tecnologia" and tiene_dj:
                # Extraemos la búsqueda a una variable para acortar el if
                tiene_sonido = any("altavoz" in n or "sonido" in n for n in nombres_comprados)
                if not tiene_sonido:
                    print("\n❌ LOGÍSTICA: Tiene DJ pero falta equipo de sonido.")
                    cumple_requisitos = False

            # 3. VALIDACIÓN DE DECORACIÓN (Florista e Iluminador)
            elif cat == "decoracion":
                if tiene_florista:
                    compro_flores = any("flor" in n for n in nombres_comprados)
                    if not compro_flores:
                        print("\n❌ LOGÍSTICA: Tiene Florista pero no compró flores.")
                        cumple_requisitos = False
                if tiene_iluminador:
                    tiene_luces = any("luz" in n or "foco" in n for n in nombres_comprados)
                    if not tiene_luces:
                        print("\n❌ LOGÍSTICA: Tiene Iluminador pero no compró luces.")
                        cumple_requisitos = False

            # --- DECISIÓN FINAL DE LA CATEGORÍA ---
            if cumple_requisitos:
                servicios_elegidos.extend(items_en_esta_ronda)
                break # Rompe el 'while True' de la categoría y pasa a la siguiente
            else:
                print("\n⚠️ SECCIÓN REINICIADA: Debe cumplir los requisitos mínimos.")
                presupuesto_provisional = presupuesto_antes_de_cat
                input("Presione Enter para volver a intentar esta categoría...")

# --- PASO 5: CÁLCULOS Y COTIZACIÓN ---
    # build_cotizacion genera el objeto/diccionario con todos los costos
    cotizacion = fg.build_cotizacion(
        cliente_actual,
        lugar_elegido,
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
        lugar_elegido,
        invitados_val
    )

    if not es_valido:
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
        lista_clientes.append(cliente_actual.to_dict())
        fg.procesar_confirmacion_boda(cotizacion, lista_lugares, lista_personal, lista_inventario)
        # 1. GUARDAR CAMBIOS EN JSON (Persistencia)
        fg.write_json('data/lugares.json', lista_lugares)
        fg.write_json('data/personal.json', lista_personal)
        fg.write_json('data/inventario.json', lista_inventario)
        fg.write_json('data/clientes.json', lista_clientes) # Guardar cliente solo si compró
        # 2. GENERACIÓN DEL TICKET TXT
        # Usamos los datos calculados para que el cliente tenga su comprobante
        fg.generar_ticket(
            cliente_actual,
            lugar_elegido,
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
