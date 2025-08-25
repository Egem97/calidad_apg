"""
Configuración del sistema PT_CALIDAD
"""
import yaml
import os
import json

from pathlib import Path

# Configuración por defecto
DEFAULT_CONFIG = {
    "app": {
        "name": "PACKING APG",
        "version": "1.0.0",
        "description": "Sistema de Control de Calidad",
        "author": "Equipo de Desarrollo"
    },
    "database": {
        "type": "sqlite",
        "path": "data/pt_calidad.db",
        "backup_enabled": True,
        "backup_frequency": "daily"
    },
    "quality": {
        "min_score_approval": 8.0,
        "max_defects_allowed": 2,
        "auto_reject_threshold": 70,
        "require_photos": True,
        "require_notes": True
    },
    "notifications": {
        "email_enabled": True,
        "sms_enabled": False,
        "daily_reports": True,
        "weekly_reports": True,
        "monthly_reports": True
    },
    "ui": {
        "theme": "light",
        "language": "es",
        "timezone": "America/Lima"
    }
}


# Cargar configuración desde YAML
def load_config():
    """
    Carga la configuración desde el archivo config.yaml
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de configuración en {config_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error al leer el archivo YAML: {e}")
        return None

def save_config(config, config_path="config.yaml"):
    """
    Guardar configuración en archivo JSON
    
    Args:
        config (dict): Configuración a guardar
        config_path (str): Ruta al archivo de configuración
    """
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar configuración: {e}")

def get_config_value(key_path, default=None):
    """
    Obtener valor de configuración por ruta de claves
    
    Args:
        key_path (str): Ruta de claves separadas por puntos (ej: "app.name")
        default: Valor por defecto si no se encuentra
        
    Returns:
        Valor de configuración
    """
    config = load_config()
    keys = key_path.split('.')
    
    try:
        value = config
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def update_config_value(key_path, value):
    """
    Actualizar valor de configuración
    
    Args:
        key_path (str): Ruta de claves separadas por puntos
        value: Nuevo valor
    """
    config = load_config()
    keys = key_path.split('.')
    
    # Navegar hasta el último nivel
    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Asignar el valor
    current[keys[-1]] = value
    
    # Guardar configuración
    save_config(config)

def reset_config():
    """
    Restablecer configuración a valores por defecto
    """
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG

def validate_config(config):
    """
    Validar configuración
    
    Args:
        config (dict): Configuración a validar
        
    Returns:
        tuple: (is_valid, errors)
    """
    errors = []
    
    # Validar estructura básica
    required_sections = ['app', 'database', 'quality', 'notifications', 'ui']
    for section in required_sections:
        if section not in config:
            errors.append(f"Sección '{section}' faltante")
    
    # Validar valores específicos
    if 'quality' in config:
        quality = config['quality']
        if not isinstance(quality.get('min_score_approval'), (int, float)):
            errors.append("min_score_approval debe ser un número")
        if not isinstance(quality.get('max_defects_allowed'), int):
            errors.append("max_defects_allowed debe ser un entero")
    
    return len(errors) == 0, errors
