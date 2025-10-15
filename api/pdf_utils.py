"""
Utilidades para generación de PDFs con ReportLab
Incluye fix de compatibilidad para Python 3.8
"""
import sys

def setup_reportlab_compatibility():
    """
    Fix para compatibilidad de ReportLab con Python 3.8
    El problema es que ReportLab usa el parámetro 'usedforsecurity' que no existe en Python 3.8
    """
    if sys.version_info < (3, 9):
        # Parche para Python 3.8 y versiones anteriores
        import hashlib

        # Guardar la función original
        _original_md5 = hashlib.md5

        # Crear wrapper que elimina el parámetro problemático
        def _md5_wrapper(*args, **kwargs):
            # Eliminar el parámetro 'usedforsecurity' si existe
            kwargs.pop('usedforsecurity', None)
            return _original_md5(*args, **kwargs)

        # Reemplazar la función md5
        hashlib.md5 = _md5_wrapper

        # También aplicar el mismo fix para openssl_md5 si existe
        try:
            from hashlib import __get_builtin_constructor
            _original_get_builtin = __get_builtin_constructor

            def _get_builtin_wrapper(name):
                builtin_func = _original_get_builtin(name)
                if name == 'md5':
                    def _wrapped(*args, **kwargs):
                        kwargs.pop('usedforsecurity', None)
                        return builtin_func(*args, **kwargs)
                    return _wrapped
                return builtin_func

            hashlib.__get_builtin_constructor = _get_builtin_wrapper
        except (ImportError, AttributeError):
            pass

# Aplicar el fix automáticamente al importar este módulo
setup_reportlab_compatibility()
