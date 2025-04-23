import sqlite3
import time
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import config
from fillpdf import fillpdfs

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

    fillpdfs.get_form_fields("data/FORMATO_RECONOCIMIENTO.pdf")

    data_dict = {
        'fecha': datos['fecha_creacion'],
        'codigo': codigo_unico,
        'nombre': datos["nombres"],
        'grupo': datos["grupo"],
        'distrito': datos["distrito"],
        'region': datos["region"],
    }

    fillpdfs.write_fillable_pdf('data/FORMATO_RECONOCIMIENTO.pdf', f"output/{codigo_unico}.pdf", data_dict)
    fillpdfs.flatten_pdf(f"output/{codigo_unico}.pdf", f"output/{codigo_unico}.pdf", as_images=True)

    pdf_path = f"output/{codigo_unico}.pdf"

    return pdf_path