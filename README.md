# 🏍️ Moto_store - E-commerce System

Sustentación de proyecto de desarrollo utilizando **Django** para la gestión integral de una tienda de repuestos y accesorios de motocicletas.

## 🚀 Características principales
* **Gestión de Inventario**: Control de stock de productos y categorías.
* **Sistema de Carrito**: Flujo completo desde la selección de productos hasta el checkout.
* **Plantillas Dinámicas**: Interfaz diseñada con el motor de plantillas de Django.
* **Arquitectura Escalable**: Uso de modelos, vistas y formularios personalizados para una lógica de negocio robusta.

## 🛠️ Tech Stack
* **Backend**: Python, Django.
* **Frontend**: HTML5, CSS3, JavaScript.
* **Base de Datos**: SQLite (Desarrollo) / PostgreSQL (Producción).

## 📂 Estructura del Proyecto
* `/moto_store`: Lógica principal del servidor y configuración.
* `/store`: Aplicación principal del e-commerce (modelos y vistas).
* `/templates`: Vistas del sistema (Carrito, Detalle de producto, Checkout).
* `/static`: Archivos de estilo, logos y recursos visuales.

## 🔧 Instalación y Uso
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Ejecutar migraciones: `python manage.py migrate`.
5. Iniciar servidor: `python manage.py runserver`.
