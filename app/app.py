import csv
import sqlite3
from datetime import datetime
from database import crear_tablas
from pdf_generator import generar_codigo_unico, crear_pdf

def validar_csv(ruta):
    with open(ruta, "r") as f:
        lector = csv.DictReader(f)
        campos_requeridos = {"nombres", "cedula", "grupo", "distrito", "region"}
        
        if not campos_requeridos.issubset(lector.fieldnames):
            raise ValueError("CSV inválido: Faltan campos requeridos")
        
        for idx, fila in enumerate(lector, 1):
            if any(not fila[campo].strip() for campo in campos_requeridos):
                raise ValueError(f"Fila {idx}: Campos vacíos detectados")

def generar_y_guardar(datos):
    conn = sqlite3.connect("data/reconocimientos.db")
    try:
        datos["fecha_creacion"] = datetime.now().strftime("%Y-%m-%d")
        codigo = generar_codigo_unico()
        crear_pdf(codigo, datos)
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reconocimientos 
            (codigo_unico, fecha_creacion, nombres, cedula, grupo, distrito, region)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (codigo, datos["fecha_creacion"], datos["nombres"], datos["cedula"], 
              datos["grupo"], datos["distrito"], datos["region"]))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

def main():
    crear_tablas()
    
    while True:
        print("\n=== Menú Principal ===")
        print("1. Ingresar datos manualmente")
        print("2. Cargar desde CSV")
        print("3. Salir")
        
        opcion = input("Seleccione: ").strip()
        
        if opcion == "1":
            datos = {
                "nombres": input("Nombres completos: ").strip(),
                "cedula": input("Cédula: ").strip(),
                "grupo": input("Grupo scout: ").strip(),
                "distrito": input("Distrito: ").strip(),
                "region": input("Región: ").strip()
            }
            generar_y_guardar(datos)
            print("✓ Reconocimiento generado!")
        
        elif opcion == "2":
            ruta = input("Ruta del CSV: ").strip()
            try:
                validar_csv(ruta)
                with open(ruta, "r") as f:
                    lector = csv.DictReader(f)
                    for fila in lector:
                        generar_y_guardar(fila)
                print(f"✓ {lector.line_num - 1} reconocimientos generados!")
            except Exception as e:
                print(f"Error procesando CSV: {e}")
        
        elif opcion == "3":
            break

main()