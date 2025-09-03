# api/models.py

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Veterinario(AbstractUser):
    """Usuario personalizado para veterinarios,
       con related_name únicos en los M2M heredados."""
    TIPO_USUARIO_CHOICES = [
        ('administrador', 'Administrador'),
        ('vacunador', 'Vacunador'),
        ('tecnico', 'Técnico'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='vacunador',
        help_text='Tipo de usuario en el sistema'
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='veterinario_groups',
        related_query_name='veterinario',
        help_text='Grupos a los que pertenece este veterinario'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='veterinario_user_permissions',
        related_query_name='veterinario',
        help_text='Permisos específicos de este veterinario'
    )

class Planilla(models.Model):
    TIPO_ZONA_CHOICES = [
        ('urbano', 'Urbano'),
        ('rural', 'Rural'),
    ]
    
    nombre = models.CharField(max_length=100)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='planillas',
        null=True,
        blank=True,
        help_text="Vacunador principal asignado (compatibilidad)"
    )
    
    # Nuevos campos para múltiples asignaciones
    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planillas_asignadas',
        limit_choices_to={'tipo_usuario': 'tecnico'},
        help_text="Técnico principal asignado"
    )
    
    vacunadores_adicionales = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='planillas_como_vacunador_adicional',
        limit_choices_to={'tipo_usuario': 'vacunador'},
        help_text="Vacunadores adicionales asignados"
    )
    
    tecnicos_adicionales = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='planillas_como_tecnico_adicional',
        limit_choices_to={'tipo_usuario': 'tecnico'},
        help_text="Técnicos adicionales asignados"
    )
    
    municipio = models.CharField(max_length=100, default="Sin especificar", help_text="Nombre del municipio")
    urbano_rural = models.CharField(max_length=10, choices=TIPO_ZONA_CHOICES, default="urbano", help_text="Tipo de zona: urbano o rural")
    centro_poblado_vereda_barrio = models.CharField(max_length=100, default="Sin especificar", help_text="Centro poblado, vereda o barrio")
    zona = models.CharField(max_length=100, default="Sin especificar", help_text="Zona específica")
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"

    def __str__(self):
        return f"{self.nombre} ({self.assigned_to.username if self.assigned_to else 'Sin asignar'})"
    
    def get_all_vacunadores(self):
        """Retorna todos los vacunadores asignados (principal + adicionales)"""
        vacunadores = []
        if self.assigned_to and self.assigned_to.tipo_usuario == 'vacunador':
            vacunadores.append(self.assigned_to)
        vacunadores.extend(self.vacunadores_adicionales.all())
        return vacunadores
    
    def get_all_tecnicos(self):
        """Retorna todos los técnicos asignados (principal + adicionales)"""
        tecnicos = []
        if self.tecnico_asignado:
            tecnicos.append(self.tecnico_asignado)
        tecnicos.extend(self.tecnicos_adicionales.all())
        return tecnicos
    
    def user_can_access(self, user):
        """Verifica si un usuario puede acceder a esta planilla"""
        if user.tipo_usuario == 'administrador':
            return True
        elif user.tipo_usuario == 'vacunador':
            return (self.assigned_to == user or 
                   user in self.vacunadores_adicionales.all())
        elif user.tipo_usuario == 'tecnico':
            return (self.tecnico_asignado == user or 
                   user in self.tecnicos_adicionales.all())
        return False

class Responsable(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    finca = models.CharField(max_length=100)
    planilla = models.ForeignKey(Planilla, on_delete=models.CASCADE, related_name='responsables')
    
    # Nuevos campos para control de vacunación
    zona = models.CharField(max_length=100, default="Sin especificar", help_text="Zona específica de vacunación")
    nombre_zona = models.CharField(max_length=150, default="Sin especificar", help_text="Nombre descriptivo de la zona")
    lote_vacuna = models.CharField(max_length=50, default="Sin especificar", help_text="Lote de la vacuna utilizada")
    
    # Campo para rastrear quién creó este responsable
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsables_creados',
        help_text="Usuario que creó este responsable"
    )
    
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.finca}"

class Mascota(models.Model):
    TIPO_CHOICES = [('perro', 'Perro'), ('gato', 'Gato')]
    RAZA_PERRO = [('M', 'M'), ('H', 'H'), ('PME', 'PME')]
    RAZA_GATO = [('M', 'M'), ('H', 'H')]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='perro')
    raza = models.CharField(max_length=10, default='M')
    color = models.CharField(max_length=50, default='Sin especificar')
    antecedente_vacunal = models.BooleanField(default=False)
    esterilizado = models.BooleanField(default=False, help_text="Indica si la mascota está esterilizada")
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE, related_name='mascotas', null=True, blank=True)
    
    # Nuevos campos para georreferenciación
    latitud = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True, help_text="Latitud de la ubicación de la mascota")
    longitud = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True, help_text="Longitud de la ubicación de la mascota")
    
    # Nuevo campo para foto de la mascota
    foto = models.ImageField(upload_to='mascotas/fotos/', null=True, blank=True, help_text="Foto de la mascota")
    
    # Campo para rastrear quién creó esta mascota
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mascotas_creadas',
        help_text="Usuario que creó esta mascota"
    )
    
    creado = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def getRazasPorTipo(tipo):
        if tipo == 'perro':
            return [choice[0] for choice in Mascota.RAZA_PERRO]
        elif tipo == 'gato':
            return [choice[0] for choice in Mascota.RAZA_GATO]
        return ['M']

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
