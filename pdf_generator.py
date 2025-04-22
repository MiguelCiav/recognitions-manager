import sqlite3
import time
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import config

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
    pdf_path = f"output/{codigo_unico}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    
    # Campos principales (dos columnas)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 700, "Nombre:")
    c.drawString(300, 700, "Cédula:")
    c.setFont("Helvetica", 12)
    c.drawString(50, 680, datos["nombres"])
    c.drawString(300, 680, datos["cedula"])
    
    # Segunda fila de campos
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 650, "Grupo:")
    c.drawString(300, 650, "Distrito:")
    c.setFont("Helvetica", 12)
    c.drawString(50, 630, datos["grupo"])
    c.drawString(300, 630, datos["distrito"])
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, f"Código: {codigo_unico}")
    c.drawString(300, 50, f"Fecha: {datos['fecha_creacion']}")
    
    c.save()
    return pdf_path