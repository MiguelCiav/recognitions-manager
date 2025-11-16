import sqlite3
import csv
from io import StringIO
from flask import (
    Blueprint, request, render_template, current_app, Response
)

# 1. Create the Blueprint
reports_bp = Blueprint('reports', __name__, template_folder='templates')

# --- Routes ---

@reports_bp.route("/reportes")
def mostrar_reportes():
    # Flask will look for 'reportes.html' in app/templates/
    return render_template("reportes.html")

@reports_bp.route("/exportar")
def generar_reporte():
    region = request.args.get('region', '').strip()
    mes = request.args.get('mes', '').strip()

    db_path = current_app.config['DATABASE_PATH']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "SELECT codigo_unico, fecha_creacion, nombres, cedula, grupo, distrito, region FROM reconocimientos"
    params = []
    
    conditions = []
    if region:
        conditions.append("region = ?")
        params.append(region)
    if mes:
        conditions.append("strftime('%m', fecha_creacion) = ?")
        params.append(f"{mes.zfill(2)}")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    cursor.execute(query, tuple(params))
    datos = cursor.fetchall()
    conn.close()

    # Generate CSV in memory
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow([
        'Código único', 'Fecha', 'Nombres', 
        'Cédula', 'Grupo', 'Distrito', 'Región'
    ])
    for row in datos:
        csv_writer.writerow(row)
    
    # Configure response
    return Response(
        csv_buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-disposition': 'attachment; filename=reporte.csv'}
    )