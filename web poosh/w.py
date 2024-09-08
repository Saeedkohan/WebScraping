from operator import itemgetter
from bs4 import BeautifulSoup
import requests
import json
import re
import os
from requests.adapters import HTTPAdapter, Retry


headers = {
    "User-Agent": "PostmanRuntime/7.40.0"
}
base_url = "https://www.webpoosh.com/"

# ////////////////////////////////   generate_page_soup    

def generate_soup(url):
    retry_strategy = Retry(
    total=5,  
    status_forcelist=[429, 500, 502, 503, 504,11001,11001,10191,8877],  
    allowed_methods=["GET", "POST"],  
    backoff_factor=1  )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()

    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:

        response = http.get(url,headers=headers)
        soup = BeautifulSoup(response.content , "html.parser")
        return soup

    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')



def save_data(products,data):      

    print(product_exist(products,data))
    if not product_exist(products,data):

        loaded = {
            "products": []
        }

        data_file = "w.json"  


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
    
        
    print("//;;;/;k")
    if not os.path.exists("w.json"):
        return {"products": []}
    
    with open("w.json","rt") as json_file :
        loaded_data=json.load(json_file)
        # print(loaded_data)
        print("ppppp")

        return loaded_data



def get_product_data(url):
    # print("/////////",url)
    try:
        soup=generate_soup(url)
        ii=url.split("products/")[1].split("-")
        id=ii[-2]+"-"+ii[-1]
        
        
        data={
            "id":id,
            "name":soup.find("h1",{"class":"h3 product__details-title mb--20"}).text.strip(),
            "price":soup.find("div",{"class":"money new-price"}).text.strip(),
            "image":get_product_images(soup),
            "color":soup.find("strong",{"class":"swatch-label"}).text.strip(),
            "size":[text.text.strip()  for text  in soup.find_all("span",{"class":"tile-text p-1"})],
            "description":get_product_description(soup),
            "care":get_product_care(soup),
        }
        print(data["color"])
        save_data(load_products(),data)
        # save_da-ta(data)
    except:
        print("none")
        return None

    

def get_all_product_urls(url):
    count=0
    while True :
        soup=generate_soup(url+f"?page={count}")


        if  soup.find("div",{"class":"paginate_link"}) :
            count+=1
            urls=soup.find_all("a",{"class":"product-image-wrapper"})
            if  len(urls) !=0:
                print("####",count)

                [get_product_data(u.get("href"))  for u in urls ]
            else:
                print("     bre")
                break
        else:
            urls=soup.find_all("a",{"class":"product-image-wrapper"})
            [get_product_data(u.get("href"))  for u in urls ]

            break





def get_product_images(soup):
    images_container = soup.find("div", {"class": "col-md-3 nav-slider"}).find_all("img")
    images = []
    for image in images_container:
        images.append(image["src"])
    return images


def get_product_description(soup):
    description = soup.find("div" , {"class" : "col-12 product-custom-description"}).text.strip()
    return description.split("روش شستشو و نگهداری")[0]

def get_product_care(soup):
    care = soup.find("div", {"class": "col-12 product-custom-description"}).text.strip()
    return care.split("روش شستشو و نگهداری")[1]


def get_category_url(soup):
   return[a.get("href")   for a in  soup.find_all("a",{"class":"preventMultiSubmit"})]

def start():
    print("start")
    soup=generate_soup(base_url)
    category_urls=get_category_url(soup)
    for url  in category_urls:
        # print(url)
        get_all_product_urls(url)
        

start()

print("end")