
        
import os
import requests
import json
import threading
from concurrent.futures import ThreadPoolExecutor

lock = threading.Lock()

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def requests_retry_session(
    retries=5,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def download_images(image_urls, id):
    
    if not os.path.exists("amiri_images"):
        os.makedirs("amiri_images")
    
    for num, url in enumerate(image_urls):
        try:
            if not os.path.exists(f"amiri_images/{id}"):
                os.makedirs(f"amiri_images/{id}")

            response = requests_retry_session().get(url)
            if response.status_code == 200:
                with open(f"amiri_images/{id}/{num}.jpg", 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded image {num} for id {id}")
            else:
                print(f"Failed to download: {image_urls}")
                save_to_file("faild_img2", {"url": image_urls, "id": id})
        except Exception as e:
            print(f"Error downloading {image_urls}: {e}")
            save_to_file("faild_img2", {"url": image_urls, "id": id})


def save_to_file(filename, value):
    with lock:  
        print("Saving data to file")
        data = {filename: []}
        if os.path.exists(f"{filename}.json"):
            with open(f"{filename}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
        if value not in data[filename]:
            data[filename].append(value)
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)


def read_json(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        return json.load(file)


data = read_json('products.json')


with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for product in data["products"]:
        image_urls = product.get("images")
        product_id = product.get("product_id")
        futures.append(executor.submit(download_images, image_urls, product_id))

    
    for future in futures:
        future.result() 


