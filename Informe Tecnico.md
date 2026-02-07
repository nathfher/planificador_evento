# Informe Técnico: Sistema de Planificación Inteligente de Eventos

## I. Introducción y Dominio
Se seleccionó el dominio de la organización de bodas bajo la marca "Raquel & Alba Planner". La aplicación gestiona eventos que consumen recursos finitos (mobiliario, personal especializado y sedes físicas). El sistema no funciona como una simple base de datos, sino como un **motor de planificación** que garantiza la viabilidad operativa de cada evento mediante la resolución de conflictos de tiempo y espacio.

## II. Estructura y Diseño
El proyecto se diseñó bajo una arquitectura modular para separar la lógica de negocio de la persistencia de datos:
* **Capa de Datos:** Se empleó formato JSON para simular una base de datos relacional, permitiendo la actualización de stock en tiempo real.
* **Lógica de Negocio:** Se implementó un motor de validación cruzada que analiza la compatibilidad entre el lugar elegido, el personal contratado y los ítems de inventario.

## III. Reglas de Negocio y Restricciones
Se definieron un conjunto de restricciones basadas en la seguridad y el confort del asistente:
1.  **Restricción Acústica:** Se bloquea la contratación de música de alto impacto (Mariachis) en entornos con materiales reflectantes (Palacio de Cristal).
2.  **Validación de Recursos (Pools):** El sistema calcula que el mobiliario reservado cubra al menos el 80% de los invitados y 1 mesa por cada 10 personas.
3.  **Seguridad Preventiva:** Se impone la contratación de personal de seguridad ante la presencia de riesgos físicos (piscinas en "Terraza del Sol").



## IV. Problemas Enfrentados durante el Desarrollo
* **Gestión de Codificación:** Se presentó un conflicto con caracteres especiales (ñ, acentos) al serializar los archivos JSON. Se resolvió mediante la estandarización de codificación UTF-8 y el parámetro `ensure_ascii=False`.
* **Normalización de Tiempos:** El cálculo de intervalos que cruzan la medianoche representó un desafío logístico. Se solucionó mediante el uso de la librería `datetime` y objetos `timedelta` para verificar colisiones en reservas nocturnas.
* **Validación de Salida:** Inicialmente, los errores de stock se notificaban al final del proceso. Se rediseñó el flujo para incluir validaciones preventivas inmediatamente después de la selección de cada categoría, mejorando la experiencia del usuario.

## V. Conclusión
La implementación demuestra que la gestión de eventos complejos requiere un balance entre flexibilidad y restricciones estrictas. El uso de validaciones intermedias asegura que no se generen compromisos de recursos imposibles de cumplir.