import os
import csv
import sqlite3
import unicodedata
from datetime import datetime
from flask import (
    Blueprint, request, jsonify, render_template, current_app
)
from .generator import generar_codigo_unico, crear_pdf 

pdf_bp = Blueprint('pdf', __name__, template_folder='templates')

@pdf_bp.route("/carga")
def mostrar_carga():
    return render_template("carga.html")

def normalizar_texto(texto):
    texto_sin_tildes = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode()
    return texto_sin_tildes.strip().lower()

def validar_fila_csv(fila):
    campos_requeridos = ["nombres", "cedula", "grupo", "distrito", "region"]
    campos_normalizados = {}
    
    # Paso 1: Normalizar claves y valores
    for k, v in fila.items():
        clave = unicodedata.normalize('NFKD', k).encode('ASCII', 'ignore').decode().strip().lower()
        valor = str(v).strip().replace('"', '').strip() if v is not None else ""
        campos_normalizados[clave] = valor
    
    # Paso 2: Validar presencia y no vacío
    datos = {}
    for campo in campos_requeridos:
        if campo not in campos_normalizados:
            raise ValueError(f"Campo requerido faltante: '{campo}'")
        valor = campos_normalizados[campo]
        if not valor:
            raise ValueError(f"Campo requerido vacío: '{campo}'")
        datos[campo] = valor
    
    return datos

@pdf_bp.route("/cargar-csv", methods=["POST"])
def procesar_csv():
    REQUIRED_FIELDS = {"nombres", "cedula", "grupo", "distrito", "region"}
    
    if 'csv' not in request.files:
        return "No se encontró archivo CSV", 400
    
    archivo = request.files['csv']
    
    try:
        # Leer y validar estructura básica
        contenido = archivo.stream.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(contenido)
        
        # Validar encabezados
        encabezados_normalizados = [normalizar_texto(campo) for campo in csv_reader.fieldnames]
        missing = REQUIRED_FIELDS - set(encabezados_normalizados)

        if missing:
            return f"Campos requeridos faltantes: {', '.join(missing)}", 400
        
        # Procesar filas con registro de errores
        exitos = 0
        errores = []
        
        for idx, fila in enumerate(csv_reader, start=2):
            try:
                # Usar la función de validación
                datos = validar_fila_csv(fila)
                generar_y_guardar(datos)
                exitos += 1
                
            except Exception as e:
                errores.append({
                    "fila": idx,
                    "error": str(e),
                    "datos": fila
                })
        
        # Generar reporte de resultados
        return jsonify({
            "exitos": exitos,
            "errores": errores,
            "total": exitos + len(errores)
        }), 200
        
    except UnicodeDecodeError:
        return "El archivo no es un CSV válido (codificación incorrecta)", 400
    except Exception as e:
        return f"Error inesperado: {str(e)}", 500

@pdf_bp.route("/generar", methods=["POST"])
def generar_reconocimiento():
    datos = {
        'nombres': request.form['nombres'],
        'cedula': request.form['cedula'],
        'grupo': request.form['grupo'],
        'distrito': request.form['distrito'],
        'region': request.form['region']
    }
    generar_y_guardar(datos)
    return render_template("carga.html")


    datos = {
        'nombres': request.form['nombres'],
        'cedula': request.form['cedula'],
        'grupo': request.form['grupo'],
        'distrito': request.form['distrito'],
        'region': request.form['region']
    }
    db_path = current_app.config['DATABASE_PATH']
    generar_y_guardar(datos, db_path)
    # Redirect back to the charge page
    return render_template("carga.html")

# --- Helper Functions ---

def generar_y_guardar(datos, db_path):
    """
    Common function to generate PDF and save to database.
    (This was missing from your app.py)
    """
    try:
        datos["fecha_creacion"] = datetime.now().strftime("%Y-%m-%d")
        codigo = generar_codigo_unico()
        
        # We get the output folder from the app config
        output_folder = current_app.config['UPLOAD_FOLDER']
        crear_pdf(codigo, datos, output_folder) # Assuming crear_pdf takes the output path
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reconocimientos 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (None, codigo, datos["fecha_creacion"], datos["nombres"], 
             datos["cedula"], datos["grupo"], datos["distrito"], datos["region"]))
        conn.commit()
        
        return {"status": "success", "codigo": codigo}
        
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()

def normalizar_texto(texto):
    # Fixed typo: unicodedd -> unicodedata
    texto_sin_tildes = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode()
    return texto_sin_tildes.strip().lower()
