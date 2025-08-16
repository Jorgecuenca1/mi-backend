# Generated manually to add tipo_usuario field and tecnico_asignado field

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_responsable_lote_vacuna_responsable_nombre_zona_and_more'),
    ]

    operations = [
        # Agregar campo tipo_usuario al modelo Veterinario
        migrations.AddField(
            model_name='veterinario',
            name='tipo_usuario',
            field=models.CharField(
                choices=[('administrador', 'Administrador'), ('vacunador', 'Vacunador'), ('tecnico', 'Técnico')],
                default='vacunador',
                help_text='Tipo de usuario: administrador, vacunador o técnico',
                max_length=15
            ),
        ),
        # Agregar campo tecnico_asignado al modelo Planilla
        migrations.AddField(
            model_name='planilla',
            name='tecnico_asignado',
            field=models.ForeignKey(
                blank=True,
                help_text='Técnico asignado para revisar la planilla',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='planillas_asignadas',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        # Actualizar el help_text del campo assigned_to
        migrations.AlterField(
            model_name='planilla',
            name='assigned_to',
            field=models.ForeignKey(
                help_text='Vacunador que creó la planilla',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='planillas',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

