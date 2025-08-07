# VetControl - Sistema de Vacunación Veterinaria

## 🐕 Descripción

VetControl es un sistema integral de gestión y control de vacunación veterinaria para mascotas, desarrollado con Django y diseñado para facilitar el trabajo de veterinarios en campo.

## ✨ Características Principales

- **Gestión de Planillas**: Organización por municipio, zona urbana/rural y centro poblado
- **Registro de Responsables**: Información completa de propietarios de mascotas
- **Control de Mascotas**: Datos detallados incluyendo fotos y georreferenciación
- **Sistema de Autenticación**: Login seguro para veterinarios
- **Reportes Detallados**: Estadísticas por municipio y zona
- **Interfaz Moderna**: Diseño responsivo y fácil de usar

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- pip
- virtualenv (recomendado)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd mi-backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar la base de datos**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Crear superusuario**
```bash
python manage.py createsuperuser
```

6. **Ejecutar el servidor**
```bash
python manage.py runserver
```

## 📱 Uso del Sistema

### 1. Inicio de Sesión
- Accede a `http://localhost:8000/login/`
- Ingresa las credenciales del veterinario
- El sistema redirigirá automáticamente al dashboard

### 2. Selección de Planilla
- Desde el menú principal, haz clic en "Agregar Responsable"
- Selecciona la planilla correspondiente a tu zona de trabajo
- Verás información detallada de la planilla (municipio, zona, etc.)

### 3. Registro de Responsable y Mascotas
- Completa los datos del responsable:
  - Nombre completo
  - Teléfono
  - Finca/Propiedad
  - Zona de vacunación
  - Lote de vacuna
- Agrega las mascotas del responsable:
  - Nombre, tipo (perro/gato), raza
  - Color y antecedente vacunal
  - Coordenadas GPS (opcional)
  - Foto de la mascota (opcional)

### 4. Visualización de Reportes
- Accede a "Reportes" desde el menú principal
- Visualiza estadísticas por municipio
- Analiza distribución urbana/rural
- Revisa porcentajes de vacunación

## 🏗️ Estructura del Proyecto

```
mi-backend/
├── api/
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas y lógica de negocio
│   ├── forms.py           # Formularios
│   ├── urls.py            # URLs de la aplicación
│   └── templates/api/     # Plantillas HTML
│       ├── base.html      # Plantilla base
│       ├── login.html     # Página de login
│       ├── landing.html   # Página principal
│       ├── elegir_planilla.html  # Selección de planilla
│       └── responsable_form.html # Formulario de responsable
├── backend/
│   ├── settings.py        # Configuración de Django
│   └── urls.py            # URLs principales
└── media/                 # Archivos subidos (fotos)
```

## 🔧 Configuración Avanzada

### Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Configuración de Base de Datos
El sistema usa SQLite por defecto. Para producción, considera usar PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vetcontrol_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📊 Modelos de Datos

### Veterinario
- Usuario personalizado con permisos específicos
- Asignación de planillas de trabajo

### Planilla
- Nombre y asignación a veterinario
- Municipio, zona urbana/rural
- Centro poblado y zona específica

### Responsable
- Datos personales del propietario
- Información de la finca/propiedad
- Control de vacunación (zona, lote)

### Mascota
- Información básica (nombre, tipo, raza)
- Antecedente vacunal
- Georreferenciación (latitud/longitud)
- Foto de la mascota

## 🎨 Características de la Interfaz

### Diseño Responsivo
- Adaptable a dispositivos móviles y tablets
- Navegación intuitiva
- Formularios optimizados

### Experiencia de Usuario
- Animaciones suaves
- Mensajes de feedback
- Validación en tiempo real
- Carga progresiva de formularios

### Accesibilidad
- Contraste adecuado
- Navegación por teclado
- Etiquetas descriptivas

## 🔒 Seguridad

- Autenticación requerida para funciones críticas
- Validación de formularios
- Protección CSRF
- Sanitización de datos

## 🚀 Despliegue

### Docker (Recomendado)
```bash
docker-compose up -d
```

### Servidor Tradicional
```bash
python manage.py collectstatic
python manage.py runserver 0.0.0.0:8000
```

## 📞 Soporte

Para soporte técnico o consultas:
- Email: soporte@vetcontrol.com
- Documentación: [docs.vetcontrol.com](https://docs.vetcontrol.com)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Desarrollado con ❤️ para facilitar el control veterinario territorial**
