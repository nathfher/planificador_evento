import locale
import funciones_generales as fg
import planear_boda as pb # Importamos el otro archivo

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
    """
    fg.limpiar_pantalla()
    print("==========================================")
    print("       HISTORIAL DE BODAS REGISTRADAS     ")
    print("==========================================\n")

    reservas = fg.ensure_file_exist('data/historial_reservas.json', [])
    ganancia_total_empresa = 0

    if not reservas:
        print("⚠️ No se encontraron bodas registradas en el historial.")
    else:
        for i, boda in enumerate(reservas, 1):
            name_client = boda.get('cliente', 'Cliente Desconocido')
            total = boda['total_final']
            comision = boda.get('comision', 0)
            ganancia_total_empresa += comision

            print(f"{i}. CLIENTE: {name_client}")
            print(f"   TOTAL: ${total:.2f} | COMISIÓN EMPRESA: ${comision:.2f}")
            print("-" * 40)
            cant_servicios = len(boda.get('servicios', []))
            print(f"   SERVICIOS: {cant_servicios} contratados")
            print("-" * 40)

        # AHORA ESTO ESTÁ DENTRO DEL 'ELSE' (8 espacios de sangría)
        print("\n💰 RESUMEN FINANCIERO DE LA AGENCIA")
        print(f"   Total acumulado por comisiones: ${ganancia_total_empresa:,.2f}")
        print("==========================================")

    # ESTO DEBE TENER 4 ESPACIOS (Alineado con el 'if')
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
            pb.ejecutar_registro_boda() # Llamamos a la función del otro archivo
        elif op == "2":
            ver_historial()
        elif op == "3":
            break
        else:
            # ESTO evita que el programa se quede "tieso"
            print(f"⚠️ '{op}' no es una opción válida.")
            input("Presione Enter para intentar de nuevo...")
            # El bucle while True hará que el menú aparezca otra vez

if __name__ == "__main__":
    main()