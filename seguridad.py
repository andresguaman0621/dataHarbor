
#Manejo de archivos json
import json

#Manejo acractaeristicas del sistema
import os

#conectar Frontend
from flask import Flask, render_template, request

#Llamado API
import requests

#Busqueda evanazada
from googleapiclient.discovery import build 
from google_play_scraper import search

app = Flask(__name__)


#APIS EN VARIBALES DEL SISTEMA
API_KEYS = {
    'subdomain_finder': os.environ.get('SUBDOMAIN_API'),
    'hunter_io': os.environ.get('EMAIL_API'),
    'google_search': os.environ.get('GOOGLE_API'),
    'whatcms': os.environ.get('CMS_API')
}
GOOGLE_CSE_ID = os.environ.get('CSE_ID')

#FUNCION PARA BUSCAR SUBDOMINIOS
def search_subdomains(domain):
    url = f"https://subdomain-finder3.p.rapidapi.com/v1/subdomain-finder/?domain={domain}"
    headers = {
        'X-RapidAPI-Key': API_KEYS['subdomain_finder'],
        'X-RapidAPI-Host': "subdomain-finder3.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

#FUNCION PARA BUSCAR CORREOS
def search_emails(domain, company=''):
    params = {
        'domain': domain,
        'company': company,
        'api_key': API_KEYS['hunter_io']
    }
    url = f"https://api.hunter.io/v2/domain-search?{requests.compat.urlencode(params)}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

#FUNCION PARA BUSCAR ARCHIVOS
def search_files(query):
    service = build("customsearch", "v1", developerKey=API_KEYS['google_search'])
    res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=5, filter=0).execute()
    return [item['link'] for item in res.get('items', [])]

#FUNCION PARA BUSCAR APPS EN APP STORE
def search_apps_in_app_store(domain):
    params = {
        "term": domain,
        "entity": "software",
        "country": "us",
        "limit": 5
    }
    response = requests.get("https://itunes.apple.com/search", params=params)
    if response.status_code == 200:
        data = response.json()
        return [{
            "name": app.get("trackName"),
            "version": app.get("version"),
            "bundle_id": app.get("bundleId"),
            "url": app.get("trackViewUrl"),
            "image": app.get("artworkUrl100"),
            "store": "App Store"
        } for app in data.get("results", [])]
    return []

#FUNCION PARA BUSCAR APPS EN PLAY STORE
def search_apps_in_play_store(domain):
    results = search(domain, n_hits=5, lang='en', country='us')
    return [{
        "name": app.get("title"),
        "app_id": app.get("appId"),
        "url": f"https://play.google.com/store/apps/details?id={app.get('appId')}",
        "image": app.get("icon"),
        "store": "Play Store"
    } for app in results]

#FUNCION PARA BUSCAR TECNOLOGIAS 
def search_technologies(domain):
    params = {
        "key": API_KEYS['whatcms'],
        "url": domain
    }
    response = requests.get("https://whatcms.org/API/Tech", params=params)
    return response.json() if response.status_code == 200 else {'error': f'Error al obtener las tecnologías: {response.status_code}'}


#PROGARAMA FUNCIONAL

#ARMAR URL
@app.route('/')
def index():
    return render_template('index.html')

#ARMAR URL
@app.route('/search_results', methods=['POST'])
def search_results():
    domain = request.form['domain']
    company = request.form.get('company', '')
    
    checks = {
        'subdomains': 'subdomains' in request.form,
        'emails': 'emails' in request.form,
        'documents': 'documents' in request.form,
        'applications': 'applications' in request.form,
        'technologies': 'technologies' in request.form
    }

    #ALMACENA TODA LA INFORMACION
    data = {}
    
    if checks['subdomains']:
        data['subdomains'] = search_subdomains(domain)
    
    if checks['emails']:
        data['emails'] = search_emails(domain, company)
    
    if checks['documents']:
        for file_type in ['pdf', 'xlsx', 'pptx', 'docx']:
            query = f"site:{domain} filetype:{file_type}"
            data[f'{file_type}_enlaces'] = search_files(query)
    
    if checks['applications']:
        data['mobile_apps'] = search_apps_in_app_store(domain) + search_apps_in_play_store(domain)
        
    if checks['technologies']:
        data['technologies'] = search_technologies(domain)

    return render_template('search_results.html', data=data)
    
if __name__ == '__main__':
    app.run(debug=True)
