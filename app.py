from flask import Flask, request, jsonify, render_template, send_from_directory
import csv
import sqlite3
from datetime import datetime
from database import crear_tablas
from pdf_generator import generar_codigo_unico, crear_pdf
from io import StringIO
import unicodedata

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'output'

# Servir archivos estáticos de la carpeta output
@app.route('/output/<path:filename>')
def serve_pdf(filename):
    return send_from_directory('output', filename)

# Ruta principal - Lista de reconocimientos
@app.route("/")
def lista_reconocimientos():
    conn = sqlite3.connect('data/reconocimientos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reconocimientos")
    reconocimientos = cursor.fetchall()
    conn.close()
    
    return render_template("lista.html", reconocimientos=reconocimientos)

# Ruta de carga de datos
@app.route("/carga")
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
            raise ValueError(f"Campo requerido faltante: '{campo}'")  # <-- Nueva validación
        valor = campos_normalizados[campo]
        if not valor:
            raise ValueError(f"Campo requerido vacío: '{campo}'")
        datos[campo] = valor
    
    return datos

# Endpoint para procesar CSV
@app.route("/cargar-csv", methods=["POST"])
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
            "total": exitos + len(errores)  # <- Línea corregida
        }), 200
        
    except UnicodeDecodeError:
        return "El archivo no es un CSV válido (codificación incorrecta)", 400
    except Exception as e:
        return f"Error inesperado: {str(e)}", 500

def procesar_fila(fila):
    datos = {
        'nombres': fila['nombres'],
        'cedula': fila['cedula'],
        'grupo': fila['grupo'],
        'distrito': fila['distrito'],
        'region': fila['region']
    }
    generar_y_guardar(datos)

# Mantener el endpoint original para el formulario manual
@app.route("/generar", methods=["POST"])
def generar_reconocimiento():
    datos = {
        'nombres': request.form['nombres'],
        'cedula': request.form['cedula'],
        'grupo': request.form['grupo'],
        'distrito': request.form['distrito'],
        'region': request.form['region']
    }
    return jsonify(generar_y_guardar(datos)), 201

# Reportes
@app.route("/reportes")
def mostrar_reportes():
    return render_template("reportes.html")

@app.route("/exportar")
def generar_reporte():
    region = request.args.get('region', '').strip()
    mes = request.args.get('mes', '').strip()

    conn = sqlite3.connect('data/reconocimientos.db')
    cursor = conn.cursor()
    
    # Construir query dinámica con filtros
    query = "SELECT codigo_unico, fecha_creacion, nombres, cedula, grupo, distrito, region FROM reconocimientos"
    params = []
    
    conditions = []
    if region:
        conditions.append("region = ?")
        params.append(region)
    if mes:
        conditions.append("strftime('%m', fecha_creacion) = ?")
        params.append(f"{mes.zfill(2)}")  # Asegurar formato MM
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    cursor.execute(query, tuple(params))
    datos = cursor.fetchall()
    conn.close()

    # Generar CSV en memoria
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    
    # Encabezados
    csv_writer.writerow([
        'Código único', 'Fecha', 'Nombres', 
        'Cédula', 'Grupo', 'Distrito', 'Región'
    ])
    
    # Datos
    for row in datos:
        csv_writer.writerow(row)
    
    # Configurar respuesta
    response = app.response_class(
        csv_buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-disposition': 'attachment; filename=reporte.csv'}
    )
    
    return response

# Función de generación común
def generar_y_guardar(datos):
    try:
        datos["fecha_creacion"] = datetime.now().strftime("%Y-%m-%d")
        codigo = generar_codigo_unico()
        crear_pdf(codigo, datos)
        
        conn = sqlite3.connect("data/reconocimientos.db")
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
        conn.close()

if __name__ == "__main__":
    crear_tablas()
    app.run(host="0.0.0.0", port=5000, debug=True)