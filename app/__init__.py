import os
import sqlite3
from flask import Flask
from .database import crear_tablas

def create_app():
    """
    The application factory.
    """
    
    app = Flask(__name__)
    app.config.from_object('config.Config')

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    data_dir = os.path.dirname(app.config['DATABASE_PATH'])
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Note: Tailwind/CSS is built by the Vite frontend pipeline and
    # served as static files from `app/static/dist`. No Flask-side
    # Tailwind extension is needed here.

    @app.before_first_request
    def initialize_database():
        db_path = app.config['DATABASE_PATH']
        crear_tablas(db_path)
    
    from .scraper.routes import scraper_bp
    app.register_blueprint(scraper_bp)
    
    from .pdf.routes import pdf_bp
    app.register_blueprint(pdf_bp)
    
    from .reports.routes import reports_bp
    app.register_blueprint(reports_bp)
    
    from .main.routes import main_bp
    app.register_blueprint(main_bp)

    return app