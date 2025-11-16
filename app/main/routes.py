import sqlite3
from flask import (
    Blueprint, render_template, send_from_directory, current_app
)

# 1. Create the Blueprint
main_bp = Blueprint('main', __name__, template_folder='templates')

# --- Routes ---

@main_bp.route("/")
def lista_reconocimientos():
    db_path = current_app.config['DATABASE_PATH']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reconocimientos")
    reconocimientos = cursor.fetchall()
    conn.close()
    
    return render_template("lista.html", reconocimientos=reconocimientos)

@main_bp.route('/output/<path:filename>')
def serve_pdf(filename):
    # Get the upload folder from the app's config
    output_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(output_folder, filename)