# Informe de Proyecto: Raquel & Alba Planner

## 1. Introducción y el "Porqué" de este proyecto
Este proyecto se llama **Raquel & Alba Planner** y nace inspirado en uno de los momentos más caóticos de la serie *La que se avecina*. Se tomó como ejemplo el episodio donde Raquel Villanueva y Alba Recio intentan organizar la boda de Diego, el amor platónico de la secundaria de Raquel.

En la serie, aquel evento fue el primero y el último que hicieron, y terminó siendo un desastre total. El problema fue que Diego se casaba con la que era la mejor amiga de Raquel (llevaban 20 años juntos) y los sentimientos de Raquel arruinaron la logística. Este software se creó precisamente para evitar que los "dramas" arruinen un negocio. Se pensó en un sistema que sea el "organizador con cabeza fría" que ellas no tuvieron, asegurando que todo salga perfecto, aunque el organizador tenga el corazón roto.

## 2. Cómo se organizó el proyecto
Para que no fuera un lío de códigos, se decidió separar el proyecto en partes fáciles de entender (Estructura de archivos):

* **`data/` (Bases de Datos JSON):** Aquí se guarda la lista de salones, los trabajadores y el inventario. Es como el libro de registros de la agencia para no inventarse cosas.
* **`funciones_generales.py` (El Cerebro):** Es la parte que hace los cálculos, revisa las reglas y maneja los archivos.
* **`planear_boda.py` (La Lógica):** Contiene el paso a paso del registro de la boda.
* **`modulos.py`:** Donde se definen las clases (Cliente, Lugar, etc.).
* **`main.py` (El Menú):** Es lo que usa el organizador para navegar por el sistema.

## 3. Las Reglas de Oro (Restricciones)
Para que la boda no termine en un caos como el de la serie, se implementaron unas reglas que el programa revisa automáticamente:

### I. Cosas que son obligatorias (Inclusión)
* **Seguridad ante todo:** Si se elige la "Terraza del Sol", como tiene piscina, el sistema obliga a contratar personal de **Seguridad**. Así se evita que algún invitado termine en el agua por los líos de la fiesta.
* **Protocolo de Gala:** Si el banquete es de lujo, el sistema obliga a contratar **Maquillaje y Peinado**. Se busca que los novios estén impecables y no se descuide la imagen del evento.

### II. Cosas que están prohibidas (Exclusión)
* **El eco del Palacio de Cristal:** Se bloqueó la opción de llevar **Mariachis** al Palacio de Cristal. Por lógica de sonido, el eco ahí dentro sería un desastre y el sistema no permite ese error.
* **Guerra de Sonido:** No se puede contratar un **DJ** y una **Banda de Rock** al mismo tiempo. Se hizo así para evitar conflictos con los equipos de sonido y que la música no sea un ruido insoportable.

### III. El buscador de fechas ("Buscar Hueco")
Si el salón ya está ocupado el día que el cliente quiere, el programa no se detiene. Se creó una función que busca en los **3 días siguientes** y le propone al usuario la próxima fecha disponible.

## 4. Gestión de Costos y Transparencia
A diferencia de los presupuestos "a ojo" que podrían hacerse en Montepinar, este sistema es exacto. El motor de cotización calcula automáticamente:

* **Subtotal:** Suma de alquiler del lugar, sueldos del personal y servicios de catering o música.
* **Comisión de Agencia:** Se aplica un **10% fijo** sobre el subtotal (la ganancia de Raquel y Alba).
* **Impuestos (IVA):** Se calcula el **16%** sobre el total. Al finalizar, se genera un archivo `ticket_boda.txt` con todo el desglose legal para que el cliente no tenga dudas.

## 5. Problemas que se resolvieron

* **Guardar los datos:** Costó un poco hacer que la información de las bodas se guardara bien en los archivos JSON sin perder datos. Se solucionó creando una función que convierte los objetos del código en listas que el archivo puede entender.
* **Inconsistencia en el Nombramiento de Variables**: Se corrigieron múltiples errores de ejecución provocados por llamar a una misma variable de distintas formas (ej: total en JSON vs total_final en Python). Se estandarizó el vocabulario técnico para asegurar la integridad de los cálculos.
* **El idioma de las fechas:** Al principio los meses daban problemas según si la computadora era Windows o Linux. Se arregló con un código que detecta el sistema y pone los meses en español correctamente.
* **El stock del almacén (Pools):** Fue un reto controlar que no se gastaran más cosas de las que hay (como platos o bebidas). Se logró programar una función que resta del inventario según el número de invitados.

## 6. Instrucciones de Uso
1.  Asegúrese de tener la carpeta `data/` con los archivos JSON iniciales.
2.  Ejecute el programa:
    ```bash
    python main.py
    ```
3.  Siga los pasos del asistente: Registro de cliente -> Selección de fecha -> Lugar -> Personal -> Servicios adicionales.
4.  Revise el ticket generado en la raíz del proyecto tras confirmar la reserva.

## 7. Conclusión
**Raquel & Alba Planner** es el programa que habría salvado aquel evento de la serie. Mientras Raquel sufría por ver a su amor platónico casarse con su mejor amiga, este software se habría encargado de que la comida llegara a tiempo y los músicos no chocaran. Se consiguió crear una aplicación donde manda el código y no los sentimientos, asegurando que cada boda sea un éxito rotundo.