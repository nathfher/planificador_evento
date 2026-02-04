class Cliente:
    """
    Representa al cliente que contrata la boda y almacena sus preferencias básicas.
    
    Atributos:
        id_cliente (int/str): Identificador único del cliente.
        nombre (str): Nombre completo del cliente.
        email (str): Correo electrónico de contacto.
        invitados (int): Cantidad estimada de asistentes al evento.
        presupuesto (float): Monto máximo que el cliente está dispuesto a gastar.
    """
    def __init__(self, id_cliente, nombre, email,invitados,presupuesto):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.email = email
        self.invitados = invitados
        self.presupuesto = presupuesto

    def to_dict(self):
        """Convierte los atributos de la instancia en un diccionario para exportación JSON."""
        return vars(self)

class Lugar:
    """
    Define el espacio físico donde se realizará el evento y sus restricciones.
    
    Atributos:
        id_lugar (int/str): Identificador único del establecimiento.
        nombre (str): Nombre comercial del lugar.
        capacidad (int): Aforo máximo permitido.
        costo (float): Precio base por el alquiler del espacio.
        servicios (list): Lista de servicios incluidos (ej. Wi-Fi, Aire Acondicionado).
        fechas_ocupadas (list): Lista de fechas (strings o datetime) no disponibles.
        inventario (dict): Registro de mobiliario disponible (sillas, mesas, etc.).
    """
    def __init__(self, id_lugar, nombre, capacidad, costo, servicios, fechas_ocupadas, inventario):
        self.id_lugar = id_lugar
        self.nombre = nombre
        self.capacidad = capacidad
        self.costo = costo
        self.servicios = servicios
        self.fechas_ocupadas = fechas_ocupadas
        self.inventario = inventario

    def to_dict(self):
        """Convierte los datos del lugar a formato diccionario."""
        return vars(self)

class Personal:
    """
    Representa a los trabajadores (mozos, fotógrafos, etc.) contratados para el evento.
    
    Atributos:
        id_personal (int/str): Identificador único del trabajador.
        nombre (str): Nombre del empleado.
        oficio (str): Cargo o especialidad (ej. 'Fotógrafo', 'Catering').
        sueldo (float): Pago por evento o jornada.
        fechas_ocupadas (list): Registro de fechas en las que el trabajador ya está comprometido.
    """
    def __init__(self, id_personal, nombre, oficio, sueldo, fechas_ocupadas=None):
        self.id_personal = id_personal
        self.nombre = nombre
        self.oficio = oficio
        self.sueldo = sueldo
        self.fechas_ocupadas = fechas_ocupadas if fechas_ocupadas else []

    def to_dict(self):
        """Convierte los datos del personal a formato diccionario."""
        return vars(self)

class ItemReserva:
    """
    Gestiona un servicio específico y su cantidad dentro de una reserva particular.
    
    Esta clase actúa como un vínculo entre el catálogo general y una boda específica,
    permitiendo calcular costos según la demanda (ej. 100 platos de comida).
    """
    def __init__(self, id_item, nombre, precio_unidad, cantidad_requerida):
        self.id_item_reserva = id_item
        self.nombre = nombre
        self.precio_unidad = precio_unidad
        self.cantidad_requerida = cantidad_requerida

    def calcular_subtotal(self):
        """
        Calcula el costo total de este item multiplicando precio por cantidad.
        
        Returns:
            float: El subtotal calculado para este servicio.
        """
        return self.precio_unidad * self.cantidad_requerida

    def to_dict(self):
        """Convierte el item de reserva a diccionario."""
        return vars(self)

class Cotizacion:
    """Objeto que agrupa todos los elementos de una boda para generar el presupuesto final."""
    def __init__(self, id_cot, cliente, lugar, lista_personal, lista_items, fecha):
        self.id_cot = id_cot
        self.cliente = cliente
        self.lugar = lugar
        self.personal = lista_personal
        self.items = lista_items
        self.fecha = fecha
        self.total = 0

class ItemCatalogo:
    """
    Objeto que agrupa todos los elementos de una boda para generar el presupuesto final.
    
    Funciona como el contenedor principal que relaciona al cliente, el lugar, 
    el staff y los servicios de catering o música en una fecha determinada.
    """
    def __init__(self, id_item, nombre, precio, descripcion, categoria):
        self.id_item = id_item
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.categoria = categoria

    def to_dict(self):
        """Convierte el item del catálogo a formato diccionario."""
        return vars(self)