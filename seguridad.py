from flask import Flask, render_template, request, redirect, url_for
import http.client, json, http.client, urllib.parse, requests, re
from bs4 import BeautifulSoup
from googleapiclient.discovery import build 
from google_play_scraper import search

app = Flask(__name__)

# Función para buscar archivos utilizando la API de Google
def search_files(api_key, cse_id, query):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=5, filter=0).execute()
    return [item['link'] for item in res.get('items', [])]

# Función para buscar aplicaciones en App Store
def search_apps_in_app_store(domain):
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": domain,
        "entity": "software",
        "country": "us",
        "limit": 5
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        apps = []
        for app in results:
            name = app.get("trackName")
            version = app.get("version")
            bundle_id = app.get("bundleId")
            app_url = app.get("trackViewUrl")
            app_image = app.get("artworkUrl100")
            apps.append({
                "name": name,
                "version": version,
                "bundle_id": bundle_id,
                "url": app_url,
                "image": app_image,
                "store": "App Store"
            })
        return apps
    else:
        print(f"Error: Unable to fetch data from App Store (status code {response.status_code})")
        return []
    
# Función para buscar aplicaciones en Play Store
def search_apps_in_play_store(domain):
    results = search(domain, n_hits=5, lang='en', country='us')
    apps = []
    for app in results:
        name = app.get("title")
        app_id = app.get("appId")
        app_url = f"https://play.google.com/store/apps/details?id={app_id}"
        app_image = app.get("icon")
        apps.append({
            "name": name,
            "app_id": app_id,
            "url": app_url,
            "image": app_image,
            "store": "Play Store"
        })
    return apps

# Función para buscar aplicaciones en ambas tiendas
def search_apps_by_domain(domain):
    app_store_apps = search_apps_in_app_store(domain)
    play_store_apps = search_apps_in_play_store(domain)
    return app_store_apps + play_store_apps

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_results', methods=['POST'])
def search_results():
    domain = request.form['domain']
    company = request.form.get('company', '')  # valor vacío por defecto

    subdomains_checked = 'subdomains' in request.form
    emails_checked = 'emails' in request.form
    documents_checked = 'documents' in request.form
    apps_checked = 'applications' in request.form
    technologies_checked = 'technologies' in request.form

    data = {}
    
    #checkbox subdoominios
    if subdomains_checked:
        conn = http.client.HTTPSConnection("subdomain-finder3.p.rapidapi.com")
        headers = {
            'X-RapidAPI-Key': "a78697f918mshef91a67050ba8c8p1d9dedjsn7ed9b8e6705a",
            'X-RapidAPI-Host': "subdomain-finder3.p.rapidapi.com"
        }
        conn.request("GET", f"/v1/subdomain-finder/?domain={domain}", headers=headers)
        res = conn.getresponse()
        data['subdomains'] = json.loads(res.read().decode("utf-8"))        
    
    
    #checkbox emails
    if emails_checked:
        api_key = "225ddb3cfa53cdae1afe2cf6e4663e8d808f94cd"
        conn = http.client.HTTPSConnection("api.hunter.io")
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json"
        }
        params = {
            'domain': domain,
            'company': company,
            'api_key': api_key
        }
        conn.request("GET", f"/v2/domain-search?{urllib.parse.urlencode(params)}", headers=headers)
        res = conn.getresponse()
        data['emails'] = json.loads(res.read().decode("utf-8"))
    
    #checkbox documentos
    if documents_checked:
        api_key = 'AIzaSyD1gBEpncfgy8vF_s9EWd8irMIsphI9m1c'  
        cse_id = '51f926aad6df246f9'  
        
        ##
        # Buscar archivos PDF en Google
        ##
        pdf_query = f"site:{domain} filetype:pdf"
        data['pdf_enlaces'] = search_files(api_key, cse_id, pdf_query)
        
        ##
        # Buscar archivos EXCEL en Google
        ##
        xlsx_query = f"site:{domain} filetype:xlsx"
        data['xlsx_enlaces'] = search_files(api_key, cse_id, xlsx_query)
        
        ##
        # Buscar archivos PPTX en Google
        ##
        pptx_query = f"site:{domain} filetype:pptx"
        data['pptx_enlaces'] = search_files(api_key, cse_id, pptx_query)
        
        ##
        # Buscar archivos DOCX en Google
        ##
        docx_query = f"site:{domain} filetype:docx"
        data['docx_enlaces'] = search_files(api_key, cse_id, docx_query)
    
    #checkbox applicaciones moviles
    if apps_checked:
        data['mobile_apps'] = search_apps_by_domain(domain)
        
   # checkbox technologies
    if technologies_checked:
        api_key = "w3j8vx0maawo0mim295dluqdmoctfgcxemeougfnqz3bs1iqjqvxndmdgl2pjg4ly81l7k"
        response = requests.get(
            "https://whatcms.org/API/Tech",
            params={
                "key": api_key,
                "url": domain
            }
        )

        if response.status_code == 200:
            data['technologies'] = response.json()
            print('hola')
        else:
            data['technologies'] = {'error': f'Error al obtener las tecnologías: {response.status_code}'}

    return render_template('search_results.html', data=data)
    
# if __name__ == '__main__':
#     app.run(debug=True)
    
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')


