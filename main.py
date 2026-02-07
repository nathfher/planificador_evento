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

def main():
    """
    Punto de entrada principal de la aplicación Wedding Planner.
    
    Gestiona el bucle principal de la interfaz de consola, permitiendo al 
    usuario navegar entre las opciones de registro de nuevas bodas, 
    consulta del historial financiero y salida del sistema.
    """
    while True:
        fg.limpiar_pantalla()
        print("=== MENU RAQUEL & ALBA PLANNER ===\n 1. Nueva boda\n 2. Ver Historial\n 3. Salir")

        op = input("Seleccione: ")

        if op == "1":
            pb.ejecutar_registro_boda() # Llamamos a la función del otro archivo
        elif op == "2":
            fg.ver_historial()
        elif op == "3":
            break
        else:
            # ESTO evita que el programa se quede "tieso"
            print(f"⚠️ '{op}' no es una opción válida.")
            input("Presione Enter para intentar de nuevo...")
            # El bucle while True hará que el menú aparezca otra vez

if __name__ == "__main__":
    main()