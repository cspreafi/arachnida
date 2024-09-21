#source arachnida_venv/bin/activate

import os
import sys
from urllib.parse import urlparse, urljoin
import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup

def get_images(start_url, url, max_depth=5, save_path='./data/', extensions=['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
    # Check if the directory exists, if not, create it
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Parse the URL
    parsed_url = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_url)

    def download_image(img_url, img_name):
        try:
            response = requests.get(img_url, stream=True, timeout=10)
            response.raise_for_status()
            with open(os.path.join(save_path, img_name), 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        except requests.exception.Timeout :
            print(f"Failed to dowload image timeout: {img_url}")
        except requests.exception.HTTPError as http_err:
            print(f"HTTP error occured: {http_err}")
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")

    def crawl(url, depth=0):
        if depth >= max_depth:
            return
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    img_name = os.path.basename(urljoin(url, src))
                    print(f"dowload image link: {url}")
                    download_image(src, img_name)

            for link in soup.find_all('a'):
                href = link.get('href')
                if href and not href.startswith('#'):
                    full_url = urljoin(url, href)
                    print(f"Following link: {full_url}")
                    if recursive:
                        parsed_url = urlparse(full_url)
                        start_parsed_url = urlparse(start_url)
                        if parsed_url.netloc == start_parsed_url.netloc:
                            crawl(full_url, depth + 1)
        except Exception as e:
            print(f"Error processing {url}: {e}")

# need a database of the url because it goes on the same url

    crawl(url, 0)

if __name__ == "__main__":
    args = sys.argv[1:]
    url = None
    recursive = False
    limit_depth = 5
    save_path = './data/'
    print("Arguments:", args)

    for arg in args:
        if arg == '-r':
            recursive = True
        elif arg.startswith('-l'):
            limit_depth = int(arg.split('=')[1])
        elif arg.startswith('-p'):
            save_path = arg.split('=')[1]
        else:
            url = arg
    start_url = url
    if url:
        get_images(start_url, url, limit_depth, save_path, recursive)
