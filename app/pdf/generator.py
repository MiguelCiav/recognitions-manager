import sqlite3
import time
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from fillpdf import fillpdfs
from flask import current_app

def generar_codigo_unico():
    intentos = 3
    for _ in range(intentos):
        conn = None
        try:
            conn = sqlite3.connect("data/reconocimientos.db")
            cursor = conn.cursor()
            mes_año = datetime.now().strftime("%m%y")
            
            conn.execute("BEGIN IMMEDIATE")
            cursor.execute("SELECT contador FROM contadores WHERE mes_año = ?", (mes_año,))
            resultado = cursor.fetchone()
            
            if resultado:
                nuevo_contador = resultado[0] + 1
                cursor.execute("UPDATE contadores SET contador = ? WHERE mes_año = ?", (nuevo_contador, mes_año))
            else:
                nuevo_contador = 1
                cursor.execute("INSERT INTO contadores (mes_año, contador) VALUES (?, ?)", (mes_año, nuevo_contador))
            
            codigo = f"CCRL-{mes_año}-{nuevo_contador:03d}"
            conn.commit()
            return codigo
        except sqlite3.OperationalError:
            if conn: conn.rollback()
            time.sleep(0.1)
        finally:
            if conn: conn.close()
    raise RuntimeError("Error: No se pudo generar el código después de 3 intentos")

def crear_pdf(codigo_unico, datos):

    # --- THIS IS THE FIX ---
    # Get the directory of the *current file* (generator.py)
    # This will be /app/app/pdf/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go *up one level* (to /app/app/) and then into 'static'
    # This path is now 100% reliable
    static_dir = os.path.join(current_dir, '..', 'static')
    
    # Build the full path to the template
    format_path = os.path.join(static_dir, "FORMATO_RECONOCIMIENTO.pdf")
    
    # Get the upload folder path (this one is fine)
    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{codigo_unico}.pdf")
    # -----------------------

    # This check is now very useful for debugging
    if not os.path.exists(format_path):
        raise FileNotFoundError(f"Template file not found at: {format_path}")

    fillpdfs.get_form_fields(format_path)

    data_dict = {
        'fecha': datos['fecha_creacion'],
        'codigo': codigo_unico,
        'nombre': datos["nombres"],
        'grupo': datos["grupo"],
        'distrito': datos["distrito"],
        'region': datos["region"],
    }

    fillpdfs.write_fillable_pdf(format_path, output_path, data_dict)
    fillpdfs.flatten_pdf(output_path, output_path, as_images=True)

    pdf_path = output_path

    return pdf_path

# --- DELETED THE DUPLICATE/BUGGY generar_y_guardar FUNCTION ---
# It is correctly defined in routes.py