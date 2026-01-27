class Cliente:
    """Representa al cliente que contrata la boda y almacena sus preferencias básicas."""
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
    """Define el espacio físico donde se realizará el evento y sus restricciones."""
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
    """Representa a los trabajadores (mozos, fotógrafos, etc.) contratados para el evento."""
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
    """Gestiona un servicio específico (como un plato de comida) y su cantidad en la reserva."""
    def __init__(self, id_item_reserva, nombre, precio_unitario, cantidad_requerida):
        self.id_item_reserva = id_item_reserva
        self.nombre = nombre
        self.precio_unitario = precio_unitario
        self.cantidad_requerida = cantidad_requerida

    def calcular_subtotal(self):
        """Calcula el costo total de este item multiplicando precio por cantidad."""
        return self.precio_unitario * self.cantidad_requerida

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
    """Representa los productos disponibles en los archivos JSON (Catering/Música)."""
    def __init__(self, id_item, nombre, precio, descripcion, categoria):
        self.id_item = id_item
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.categoria = categoria

    def to_dict(self):
        """Convierte el item del catálogo a formato diccionario."""
        return vars(self)