import sqlite3

def crear_tablas():
    conn = sqlite3.connect("data/reconocimientos.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reconocimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_unico TEXT NOT NULL UNIQUE,
            fecha_creacion DATE NOT NULL,
            nombres TEXT NOT NULL,
            cedula TEXT NOT NULL,
            grupo TEXT NOT NULL,
            distrito TEXT NOT NULL,
            region TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contadores (
            mes_año TEXT PRIMARY KEY,
            contador INTEGER NOT NULL CHECK (contador >= 1)
        )
    """)
    
    conn.commit()
    conn.close()