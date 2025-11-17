import os
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify

scraper_bp = Blueprint('scraper', __name__)

LOGIN_URL = 'https://registro.scouts.org.ve/users/sign_in' 
MEMBER_SEARCH_URL = 'https://registro.scouts.org.ve/members/status_member_submit'
SCOUT_USERNAME = os.environ.get('SCOUT_USERNAME')
SCOUT_PASSWORD = os.environ.get('SCOUT_PASSWORD')

@scraper_bp.route('/api/get-scout-data/<cedula>')
def get_scout_data(cedula):
    
    # 1. Create a session to persist the login cookie
    with requests.Session() as session:
        
        # --- Part 1: Log In ---
        try:
            # First, get the login page to find the CSRF token
            login_page = session.get(LOGIN_URL)
            login_soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Find the authenticity_token
            token_element = login_soup.find('input', {'name': 'authenticity_token'})
            if not token_element:
                return jsonify({"error": "Login failed. Could not find authenticity_token."}), 401
            
            token = token_element['value']

            # Prepare the login data (payload)
            login_data = {
                'user[email]': SCOUT_USERNAME,
                'user[password]': SCOUT_PASSWORD,
                'authenticity_token': token,
                'commit': 'Iniciar Sesión'
            }

            # Send the POST request to log in
            login_response = session.post(LOGIN_URL, data=login_data)
            
            if "Cerrar Sesión" not in login_response.text:
                 return jsonify({"error": "Login failed. Check credentials or site structure."}), 401

            # --- Part 2: Fetch Member Data ---
            search_params = {
                'cedula': cedula,
                'commit': 'Buscar'
            }
            member_page_response = session.get(MEMBER_SEARCH_URL, params=search_params)
            
            # --- Part 3: Parse the Data ---
            soup = BeautifulSoup(member_page_response.text, 'html.parser')
            
            try:
                # 1. Find Group, District, and Region
                header_info = soup.find('div', class_='profile-header-info')
                if not header_info:
                    raise Exception("Could not find 'profile-header-info' div.")
                
                full_title_p = header_info.find('p', class_='mb-1') 
                if not full_title_p:
                    raise Exception("Could not find the <p> tag containing group info.")
                
                full_title_text = full_title_p.text.strip() 

                # 2. Find the Full Name
                name_strong_tag = soup.find('strong', string='Nombre Completo:')
                if not name_strong_tag:
                    raise Exception("Could not find 'Nombre Completo:' tag.")
                
                full_name = name_strong_tag.parent.text.replace('Nombre Completo:', '').strip()
                
                # --- NEW: Find Joven/Adulto ---
                joven_adulto_tag = soup.find('strong', string='Joven/AdultT_Adulto:')
                if not joven_adulto_tag:
                    # Fallback for the exact string in the HTML sample
                    joven_adulto_tag = soup.find('strong', string='Joven/Adulto:')
                if not joven_adulto_tag:
                    raise Exception("Could not find 'Joven/Adulto:' tag.")
                
                joven_adulto = joven_adulto_tag.parent.text.replace('Joven/Adulto:', '').strip()

                # --- NEW: Find Status ---
                status_tag = soup.find('strong', string='Status:')
                if not status_tag:
                    raise Exception("Could not find 'Status:' tag.")
                
                status = status_tag.parent.text.replace('Status:', '').strip()
                
                # 3. Parse the full_title_text (Grupo/Distrito/Region)
                parts = full_title_text.split('/')
                grupo = parts[0].replace('Grupo', '').strip()
                distrito = parts[1].replace('Distrito', '').strip()
                region = parts[2].replace('Region', '').strip()

                # --- Part 4: Return JSON Data ---
                scout_data = {
                    "nombre": full_name,
                    "cedula": cedula,
                    "grupo": grupo,
                    "distrito": distrito,
                    "region": region,
                    "joven_adulto": joven_adulto, # NEW
                    "status": status             # NEW
                }
                return jsonify(scout_data)

            except Exception as e:
                return jsonify({"error": f"Failed to parse HTML. Cedula might be invalid or page structure changed. Details: {e}"}), 500

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Network request failed: {e}"}), 500