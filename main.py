import locale
import funciones_generales as fg
import planear_boda # Importamos el otro archivo

# --- CONFIGURACIÓN DE IDIOMA ---
try:
    # Intento para Windows
    locale.setlocale(locale.LC_TIME, 'spanish')
except locale.Error:
    try:
        # Intento para Linux/Mac
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        # Si falla ambos, usará el sistema por defecto (inglés)
        pass

def ver_historial():
    """
    Carga y muestra en pantalla todas las bodas registradas en el historial JSON.
    
    Acciones:
    - Recupera la lista de bodas desde 'historial_reservas.json'.
    - Itera sobre los registros para mostrar detalles clave como: 
      nombre del cliente, lugar seleccionado y monto total pagado.
    - Maneja casos donde el archivo no existe o el historial está vacío.
    """
    fg.limpiar_pantalla()
    print("==========================================")
    print("       HISTORIAL DE BODAS REGISTRADAS     ")
    print("==========================================\n")

    # Usamos tu función de seguridad para cargar el archivo
    reservas = fg.ensure_file_exist('data/historial_reservas.json', [])
    ganancia_total_empresa = 0
    if not reservas:
        print("⚠️ No se encontraron bodas registradas en el historial.")
    else:
        # Recorremos cada reserva guardada
        for i, boda in enumerate(reservas, 1):
            # Accedemos a los datos navegando por las llaves del diccionario
            # Recuerda que 'cliente' ahora es un diccionario porque usaste to_dict()
            nombre_cliente = boda['cliente']['nombre']
            total = boda['total_final']
            comision = boda.get('comision', 0) # <--- Extraemos la comisión
            ganancia_total_empresa += comision # <--- Sumamos

            print(f"{i}. CLIENTE: {nombre_cliente}")
            print(f"   TOTAL: ${total:.2f} | COMISIÓN EMPRESA: ${comision:.2f}")
            print("-" * 40)
            # Opcional: Mostrar cuántos servicios contrató
            cant_servicios = len(boda.get('servicios', []))
            print(f"   SERVICIOS: {cant_servicios} contratados")
            print("-" * 40)
    # --- REPORTE FINAL ---
        print("\n💰 RESUMEN FINANCIERO DE LA AGENCIA")
        print(f"   Total acumulado por comisiones: ${ganancia_total_empresa:,.2f}")
        print("==========================================")

    print("\n==========================================")
    input("Presione Enter para volver al Menú Principal...")

def main():
    """
    Punto de entrada principal de la aplicación Wedding Planner.
    
    Gestiona el bucle principal de la interfaz de consola, permitiendo al 
    usuario navegar entre las opciones de registro de nuevas bodas, 
    consulta del historial financiero y salida del sistema.
    """
    while True:
        fg.limpiar_pantalla()
        print("=== MENU RAQUEL & ALBA PLANNER ===")
        print("1. Nueva Boda")
        print("2. Ver Historial")
        print("3. Salir")

        op = input("Seleccione: ")

        if op == "1":
            planear_boda.ejecutar_registro_boda() # Llamamos a la función del otro archivo
        elif op == "2":
            ver_historial()
        elif op == "3":
            break

if __name__ == "__main__":
    main()