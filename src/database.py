"""
Módulo de base de datos para PT_CALIDAD
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json
import os
from pathlib import Path

class DatabaseManager:
    """Gestor de base de datos SQLite"""
    
    def __init__(self, db_path="data/pt_calidad.db"):
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos y crear tablas si no existen"""
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.connection = sqlite3.connect(self.db_path)
        self.create_tables()
    
    def create_tables(self):
        """Crear tablas de la base de datos"""
        cursor = self.connection.cursor()
        
        # Tabla de evaluaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT NOT NULL,
                product_name TEXT NOT NULL,
                batch_number TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                evaluator TEXT NOT NULL,
                evaluation_date DATE NOT NULL,
                shift TEXT NOT NULL,
                line TEXT NOT NULL,
                visual_score REAL NOT NULL,
                dimension_score REAL NOT NULL,
                functionality_score REAL NOT NULL,
                total_score REAL NOT NULL,
                defect_quantity INTEGER DEFAULT 0,
                defect_types TEXT,
                defect_severity TEXT,
                defect_notes TEXT,
                result TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de criterios de calidad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_criteria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                criterion_name TEXT NOT NULL,
                weight_percentage REAL NOT NULL,
                min_score INTEGER NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
        
        # Insertar datos iniciales si las tablas están vacías
        self.insert_initial_data()
    
    def insert_initial_data(self):
        """Insertar datos iniciales en la base de datos"""
        cursor = self.connection.cursor()
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Insertar usuario administrador por defecto
            cursor.execute('''
                INSERT INTO users (username, full_name, email, role, status)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'Administrador', 'admin@empresa.com', 'Administrador', 'active'))
        
        # Verificar criterios de calidad
        cursor.execute("SELECT COUNT(*) FROM quality_criteria")
        if cursor.fetchone()[0] == 0:
            # Insertar criterios por defecto
            default_criteria = [
                ('Aspecto Visual', 25.0, 7, 'Evaluación del aspecto visual del producto'),
                ('Dimensiones', 30.0, 8, 'Verificación de dimensiones según especificaciones'),
                ('Funcionalidad', 35.0, 8, 'Pruebas de funcionalidad básica'),
                ('Embalaje', 5.0, 6, 'Estado del embalaje y etiquetado'),
                ('Peso', 5.0, 7, 'Verificación del peso del producto')
            ]
            
            for criterion in default_criteria:
                cursor.execute('''
                    INSERT INTO quality_criteria (criterion_name, weight_percentage, min_score, description)
                    VALUES (?, ?, ?, ?)
                ''', criterion)
        
        self.connection.commit()
    
    def add_evaluation(self, evaluation_data):
        """
        Agregar nueva evaluación
        
        Args:
            evaluation_data (dict): Datos de la evaluación
            
        Returns:
            int: ID de la evaluación creada
        """
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO evaluations (
                product_code, product_name, batch_number, quantity, evaluator,
                evaluation_date, shift, line, visual_score, dimension_score,
                functionality_score, total_score, defect_quantity, defect_types,
                defect_severity, defect_notes, result, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            evaluation_data['product_code'],
            evaluation_data['product_name'],
            evaluation_data['batch_number'],
            evaluation_data['quantity'],
            evaluation_data['evaluator'],
            evaluation_data['evaluation_date'],
            evaluation_data['shift'],
            evaluation_data['line'],
            evaluation_data['visual_score'],
            evaluation_data['dimension_score'],
            evaluation_data['functionality_score'],
            evaluation_data['total_score'],
            evaluation_data['defect_quantity'],
            json.dumps(evaluation_data.get('defect_types', [])),
            evaluation_data.get('defect_severity', ''),
            evaluation_data.get('defect_notes', ''),
            evaluation_data['result'],
            evaluation_data.get('notes', '')
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_evaluations(self, filters=None):
        """
        Obtener evaluaciones con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            
        Returns:
            pandas.DataFrame: Evaluaciones filtradas
        """
        query = "SELECT * FROM evaluations"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    conditions.append(f"{key} = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        return pd.read_sql_query(query, self.connection, params=params)
    
    def get_evaluation_stats(self, date_from=None, date_to=None):
        """
        Obtener estadísticas de evaluaciones
        
        Args:
            date_from (str): Fecha de inicio (YYYY-MM-DD)
            date_to (str): Fecha de fin (YYYY-MM-DD)
            
        Returns:
            dict: Estadísticas
        """
        query = "SELECT * FROM evaluations"
        conditions = []
        params = []
        
        if date_from:
            conditions.append("evaluation_date >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("evaluation_date <= ?")
            params.append(date_to)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        df = pd.read_sql_query(query, self.connection, params=params)
        
        if df.empty:
            return {
                'total_evaluations': 0,
                'avg_score': 0,
                'approval_rate': 0,
                'total_defects': 0
            }
        
        total_evaluations = len(df)
        avg_score = df['total_score'].mean()
        approval_rate = (df['result'].str.contains('Aprobado').sum() / total_evaluations) * 100
        total_defects = df['defect_quantity'].sum()
        
        return {
            'total_evaluations': total_evaluations,
            'avg_score': round(avg_score, 2),
            'approval_rate': round(approval_rate, 2),
            'total_defects': total_defects
        }
    
    def add_user(self, user_data):
        """
        Agregar nuevo usuario
        
        Args:
            user_data (dict): Datos del usuario
            
        Returns:
            int: ID del usuario creado
        """
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, full_name, email, role, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_data['username'],
            user_data['full_name'],
            user_data['email'],
            user_data['role'],
            user_data.get('status', 'active')
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_users(self):
        """
        Obtener todos los usuarios
        
        Returns:
            pandas.DataFrame: Lista de usuarios
        """
        return pd.read_sql_query("SELECT * FROM users ORDER BY created_at DESC", self.connection)
    
    def update_user_status(self, user_id, status):
        """
        Actualizar estado de usuario
        
        Args:
            user_id (int): ID del usuario
            status (str): Nuevo estado
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE users SET status = ? WHERE id = ?
        ''', (status, user_id))
        self.connection.commit()
    
    def get_quality_criteria(self):
        """
        Obtener criterios de calidad
        
        Returns:
            pandas.DataFrame: Criterios de calidad
        """
        return pd.read_sql_query(
            "SELECT * FROM quality_criteria WHERE is_active = 1 ORDER BY weight_percentage DESC",
            self.connection
        )
    
    def update_quality_criteria(self, criteria_id, criteria_data):
        """
        Actualizar criterio de calidad
        
        Args:
            criteria_id (int): ID del criterio
            criteria_data (dict): Nuevos datos del criterio
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE quality_criteria 
            SET criterion_name = ?, weight_percentage = ?, min_score = ?, description = ?
            WHERE id = ?
        ''', (
            criteria_data['criterion_name'],
            criteria_data['weight_percentage'],
            criteria_data['min_score'],
            criteria_data.get('description', ''),
            criteria_id
        ))
        self.connection.commit()
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Instancia global de la base de datos
db_manager = DatabaseManager()
