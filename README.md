# 💍 Raquel & Alba Planner - Sistema de Gestión Nupcial

Sistema integral de planificación de bodas inspirado en la serie *La que se avecina*. Este software actúa como un organizador de eventos con "cabeza fría", gestionando recursos, personal y presupuestos para evitar desastres logísticos.
> 📖 **DOCUMENTACIÓN IMPORTANTE:**
> Para conocer a fondo la lógica de programación, las reglas de negocio y los desafíos técnicos superados, por favor lea el **[Informe Técnico detallado aquí](./Informe_Tecnico.md)**.
## 1. Requisitos del Sistema
Para ejecutar este programa, su computadora debe cumplir con lo siguiente:
* **Lenguaje:** Python 3.8 o superior.
* **Librerías:** No requiere instalaciones externas (usa librerías estándar como `json`, `os`, `datetime` y `locale`).
* **Sistema Operativo:** Compatible con Windows, Linux y macOS (el sistema detecta el SO para configurar las fechas en español y limpiar la consola).

## 2. Estructura de Archivos
* `main.py`: Punto de entrada y menú principal.
* `planear_boda.py`: Lógica del asistente de registro paso a paso.
* `funciones_generales.py`: Funciones de cálculo, validación y manejo de archivos JSON.
* `modulos.py`: Definición de clases (Cliente, Lugar, Personal, ItemReserva).
* `data/`: Carpeta que contiene los archivos JSON (Bases de datos de salones, personal e inventario).

## 3. Instalación y Ejecución
1. Descargue o clone el repositorio en su PC.
2. Asegúrese de que la carpeta `data/` contenga los archivos: `lugares.json`, `personal.json`, `inventario.json` y `clientes.json`.
3. Abra una terminal en la carpeta del proyecto.
4. Ejecute el comando:
   ```bash
   python main.py