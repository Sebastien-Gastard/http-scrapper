import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from datetime import datetime
import csv
import argparse
import sys

visited = set()
http_links = []
links_404 = []
page_counter = 0

def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc

def extract_links_and_resources(soup, current_url):
    tags_attrs = {
        'a': 'href',
        'img': 'src',
        'script': 'src',
        'iframe': 'src',
        'link': 'href'
    }

    links = set()
    for tag, attr in tags_attrs.items():
        for element in soup.find_all(tag):
            link = element.get(attr)
            if link:
                full_url = urljoin(current_url, link)
                full_url, _ = urldefrag(full_url)  # Supprimer les fragments
                links.add(full_url)
    return links

def crawl(url, base_url):
    global page_counter
    url, _ = urldefrag(url)
    if url in visited:
        return
    visited.add(url)
    page_counter += 1
    print(f"[{page_counter}] Crawling: {url}")
    sys.stdout.flush()

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ Erreur sur {url} : {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = extract_links_and_resources(soup, url)

    for full_url in all_links:
        full_url, _ = urldefrag(full_url)
        parsed = urlparse(full_url)

        # Enregistrer les liens en HTTP
        if parsed.scheme == 'http':
            http_links.append((url, full_url))

        # Suivre les liens internes (HTML uniquement, pas les JS)
        if parsed.scheme in ['http', 'https'] and is_same_domain(base_url, full_url):
            try:
                response = requests.get(full_url, timeout=5)
                response.raise_for_status()
            except requests.RequestException:
                if (full_url, url) not in links_404:
                    links_404.append((url, full_url))
                continue

            if not parsed.path.endswith('.js'):
                crawl(full_url, base_url)

def save_to_csv_http(filename, data):
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Page source', 'Lien HTTP trouvé'])
        writer.writerows(data)

def save_to_csv_404(filename, data):
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Page source', 'Lien 404'])
        writer.writerows(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl a website and extract HTTP links.")
    parser.add_argument("start_url", help="URL de départ pour le crawl")
    args = parser.parse_args()

    print("🔄 Démarrage du crawl...\n")
    start_url = args.start_url

    crawl(start_url, start_url)

    # Générer un nom de fichier dynamique
    domain = urlparse(start_url).netloc.replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename_http = f"liens_http_{domain}_{timestamp}.csv"
    filename_404 = f"liens_404_{domain}_{timestamp}.csv"

    print("\n✅ Crawl terminé.")
    save_to_csv_http(filename_http, http_links)
    print(f"\n{len(http_links)} liens HTTP trouvés. Résultats enregistrés dans '{filename_http}'.")

    save_to_csv_404(filename_404, links_404)
    print(f"\n{len(links_404)} liens 404 trouvés. Résultats enregistrés dans '{filename_404}'.")