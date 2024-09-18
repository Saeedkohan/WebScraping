import threading
import requests
from bs4 import BeautifulSoup
import json
import os 
from operator import itemgetter
import math
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# هدر درخواست HTTP
headers = {
    "User-Agent": "PostmanRuntime/7.40.0",
    "Accept": "*/*"
}

base_url = "https://dickiesaustralia.com"
data_file = "dickies.json"

# تابع برای ارسال درخواست HTTP به یک URL مشخص
def fetch_url_content(url):
    retry_strategy = Retry(
        total=7,
        status_forcelist=[429, 500, 502, 503, 504, 400],
        allowed_methods=["GET", "POST"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        response = session.get(url, headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# تابع برای ساختن soup از محتوای صفحه
def generate_page_soup(url):
    response = fetch_url_content(url)
    if response:
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    return None


def extract_category_urls(soup):
    category_urls = [base_url + href.get("href") for menu_item in soup.find_all("li", {"class": "cc-dropdown"}) for href in menu_item.find_all("a")]
    return category_urls

# /////////////////////////////////
def calculate_page_count(category_url):
    try:
        soup = generate_page_soup(category_url)
        if soup:
            total_products = soup.find("div", {"class": "ms-auto d-none d-lg-block"}).text.strip().split(" ")[0]
            product_urls = [base_url + href.get("href") for href in soup.find_all("a", {"class": "item-link prod-listing-link"})]
            return math.ceil(int(total_products) / len(product_urls))
    except:
        print(f"///////////Error in calculate_page_count")
        return 1

# ////////////////////////

def scrape_page_urls(category_url):
    total_pages = calculate_page_count(category_url)
    print(total_pages)
    if total_pages is not None:
        total_pages+=1

        for page_num in range(1,total_pages):
            print(f"Scraping: {category_url}?page={page_num}")
            save_page_url(f"{category_url}?page={page_num}")
    else :
        save_page_url(f"{category_url}")

# ////////////////////   save page

def save_page_url(product_url):
    
    print("///////////////////////",page_urls_exist(product_url,load_page_urls()))
    if not page_urls_exist(product_url,load_page_urls()):
           
        loaded = {
            "page_urls": []
        }

        data_file = "page_urls.json"   


        try:
            with open(data_file) as f:
                file_contents = json.loads(f.read())

                for item in file_contents["page_urls"]:
                    loaded["page_urls"].append(item)

        except FileNotFoundError:
            with open(data_file, "w") as f:
                pass

        loaded["page_urls"].append(product_url)
        with open(data_file, "w") as f:
            json.dump(loaded, f)
    else:
        return
          
def page_urls_exist(product_url,exist_product_urls):
   
    return product_url in exist_product_urls["page_urls"]

def load_page_urls():
    
    if not os.path.exists("page_urls.json"):
            return {"page_urls": []}
    with open("page_urls.json","rt",encoding="utf-8-sig") as json_file :
        loaded_data=json.load(json_file)
        return loaded_data
   
   
# //////////////////////    get priduct url
def get_product_urls(url):
    soup=generate_page_soup(url)
    product_urls=soup.find_all("a",{"class":"item-link prod-listing-link"})
    for a in  product_urls:
        save_products_url(base_url+"/"+a.get("href"))




def save_products_url(product_url):
    
    print("///////////////////////",product_urls_exist(product_url,load_product_urls()))
    if not product_urls_exist(product_url,load_product_urls()):
           
        loaded = {
            "product_urls": []
        }

        data_file = "product_urls.json"   


        try:
            with open(data_file) as f:
                file_contents = json.loads(f.read())

                for item in file_contents["product_urls"]:
                    loaded["product_urls"].append(item)

        except FileNotFoundError:
            with open(data_file, "w") as f:
                pass

        loaded["product_urls"].append(product_url)
        with open(data_file, "w") as f:
            json.dump(loaded, f)
    else:
        return
          
def product_urls_exist(product_url,exist_product_urls):
   
    return product_url in exist_product_urls["product_urls"]

def load_product_urls():
    
    if not os.path.exists("product_urls.json"):
            return {"product_urls": []}
    with open("product_urls.json","rt",encoding="utf-8-sig") as json_file :
        loaded_data=json.load(json_file)
        return loaded_data
   
   
# /////////////////////////// get data 
def get_product_data(url):
    soup=generate_page_soup(url)
    try:
        print(url.split(".html")[0].split("/")[-1])
     

        print("/////////////////////////",soup.find("span",{"class":"b-price-item"}).text.strip())

        # data={
        #     "id":url.split(".html")[0].split("/")[-1],
        #     "name":soup.find("h1",{"class":"b-product_details-name"}).text.strip(),
        #     "price":soup.find("span",{"class":"b-price-item"}).text.strip(),
        #     "color":get_product_colors()

        # } 
 
        # print(data)

        # save_data(load_products(),data)
 
    except:
        print("None")
        return "None"
    
def get_product_colors(soup):
   return [ i  for i in  soup.find("div",{"class":"b-variations_item-content m-list"}).text.strip().split("\n") if not i==" " and i=="Color"] 

# //////////////////////////////// save darta


def save_data(products,data):      

    print(product_exist(products,data))
    if not product_exist(products,data):

        loaded = {
            "products": []
        }

        try:
            with open(data_file) as f:
                file_contents = json.loads(f.read())

                for item in file_contents["products"]:
                    loaded["products"].append(item)

        except FileNotFoundError:
            with open(data_file, "w") as f:
                pass

        loaded["products"].append(data)
        with open(data_file, "w") as f:
            json.dump(loaded, f)
    else:
        return

def product_exist(products,product):
    product_ids=list(map(itemgetter("id"),products["products"]))
    if product["id"] in product_ids:
        return True
    else:
       return False
def load_products():
    if not os.path.exists(data_file):
        return {"products": []}
    with open(data_file,"rt",encoding="utf-8-sig") as json_file :
        loaded_data=json.load(json_file)
        return loaded_data

def start_scraping_with_threads():
    # این قسمت کد درسته موقتا خط گرفتم
    # soup = generate_page_soup(base_url)
    # if soup:
    #     category_urls = extract_category_urls(soup)

    #     threads = []
    #     for category_url in category_urls:
    #         thread = threading.Thread(target=scrape_page_urls, args=(category_url,))
    #         threads.append(thread)
    #         thread.start()

    #     for thread in threads:
    #         thread.join()

    # threads2 = []

    # for url in load_page_urls()["page_urls"]:
    #     print(url)
    #     thread = threading.Thread(target=get_product_urls, args=(url,))
    #     threads2.append(thread)
    #     thread.start()

    # for thread in threads2:
    #     thread.join()    
    
    
    threads3 = []

    for url in load_product_urls()["product_urls"]:
        # print(url)
        thread = threading.Thread(target=get_product_data, args=(url,))
        threads3.append(thread)
        thread.start()

    for thread in threads3:
        thread.join()

start_scraping_with_threads()
print("Scraping finished")
