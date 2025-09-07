# api/models_perdidas.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class RegistroPerdidas(models.Model):
    """Modelo para registrar pérdidas de vacunas"""
    
    # Usuario que registra la pérdida
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perdidas_registradas',
        help_text='Usuario que registró la pérdida'
    )
    
    # Información de la pérdida
    cantidad = models.PositiveIntegerField(
        help_text='Cantidad de vacunas perdidas'
    )
    
    lote_vacuna = models.CharField(
        max_length=100,
        help_text='Número de lote de las vacunas perdidas'
    )
    
    motivo = models.TextField(
        blank=True,
        null=True,
        help_text='Motivo de la pérdida (opcional)'
    )
    
    # Foto opcional
    foto = models.ImageField(
        upload_to='perdidas/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='Foto de evidencia (opcional)'
    )
    
    # Ubicación donde ocurrió la pérdida
    latitud = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text='Latitud GPS'
    )
    
    longitud = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text='Longitud GPS'
    )
    
    # Timestamps
    fecha_registro = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora del registro'
    )
    
    fecha_perdida = models.DateField(
        default=timezone.now,
        help_text='Fecha cuando ocurrió la pérdida'
    )
    
    # Campos para sincronización
    sincronizado = models.BooleanField(
        default=False,
        help_text='Indica si ya fue sincronizado con el servidor'
    )
    
    uuid_local = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='UUID generado localmente para sincronización'
    )
    
    class Meta:
        verbose_name = 'Registro de Pérdida'
        verbose_name_plural = 'Registros de Pérdidas'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['-fecha_registro']),
            models.Index(fields=['lote_vacuna']),
            models.Index(fields=['registrado_por']),
        ]
    
    def __str__(self):
        return f"Pérdida de {self.cantidad} vacunas - Lote {self.lote_vacuna} ({self.fecha_perdida})"
    
    def save(self, *args, **kwargs):
        # Generar UUID si no existe (para sincronización offline)
        if not self.uuid_local:
            import uuid
            self.uuid_local = str(uuid.uuid4())
        super().save(*args, **kwargs)