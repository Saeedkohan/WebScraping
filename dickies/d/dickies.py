
import requests
from bs4 import BeautifulSoup
import json
import os 
from operator import itemgetter
import math
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


headers = {

    # "User-Agent" : "PostmanRuntime/7.37.0",
    "User-Agent" : "PostmanRuntime/7.40.0",
    # "User-Agent" : ua
    "Accept":"*/*"

}



base_url="https://dickiesaustralia.com"
data_file = "dickies.json" 

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


def requests_page_url(url):
    retry_strategy = Retry(
    total=7,  
    status_forcelist=[429, 500, 502, 503, 504,400],  
    allowed_methods=["GET", "POST"],  
    backoff_factor=1  )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()

    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url,headers=headers)
        return response
    
    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')

def generate_page_soup(url):

    response=requests_page_url(url)
    print(response)
    soup = BeautifulSoup(response.content , "html.parser")
    return soup



# /////////////////////////////////////






def get_product_data(url):
    soup=generate_page_soup(url)
    try:
     

        # print(soup)

        data={
            # "id":url.split(".html")[0].split("/")[-1],
            # "name":soup.find("h1",{"class":"b-product_details-name"}).text.strip(),
            # "price":soup.find("span",{"class":"b-price-item"}).text.strip(),
            # "color":get_product_colors()

        } 
 
        print(data)

        # save_data(load_products(),data)
 
    except:
        print("None")
        return "None"
    
# //////////////////////////////   ctegory 

def get_category_urls(soup):


    [ save_category_urls(  base_url + href.get("href")) for a in soup.find_all("li",{"class":"cc-dropdown"})  for href in  a.find_all("a") ]



def save_category_urls(category_url):
 
    if not category_urls_exist(category_url,load_category_urls()):
       
        loaded = {
            "category_urls": []
        }

        data_file = "category_urls.json"   


        try:
            with open(data_file) as f:
                file_contents = json.loads(f.read())

                for item in file_contents["category_urls"]:
                    loaded["category_urls"].append(item)

        except FileNotFoundError:
            with open(data_file, "w") as f:
                pass

        loaded["category_urls"].append(category_url)
 
        with open(data_file, "w") as f:
            json.dump(loaded, f)
    else:
        return

def category_urls_exist(category_url,exist_category_urls):
    return category_url in exist_category_urls["category_urls"]

def load_category_urls():
    if not os.path.exists("category_urls.json"):
            return {"category_urls": []}
    with open("category_urls.json","rt",encoding="utf-8-sig") as json_file :
        loaded_data=json.load(json_file)
        return loaded_data

# //////////////////////////////////////////////// Count
def get_page_count(category_url):

    try:
        soup=generate_page_soup(category_url)    
        page_count=soup.find("div",{"class":"ms-auto d-none d-lg-block"}).text.strip().split(" ")[0]
        product_url=[ base_url +href.get("href")   for href in   soup.find_all("a",{"class":"item-link prod-listing-link"})  ]
        return math.ceil(int(page_count)/len(product_url))


    except:
        return 
# ////////////////////////////////////////// get all product



def get_all_product_url(category_url):
    page_count=get_page_count(category_url)  
    print(page_count)
    for i in range(page_count):
        print("////////",category_url+"?page={0}".format(i))    



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
   
   
   
    # print("llll")
    # [ get_product_data(base_url+url.get("href")) for url in soup.find_all("a",{"class":"b-product_tile-image_link"})]
            






# ////////////////////////////////
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
# ////////////////////////////////

# def get_product_colors(soup):
#    return [ i  for i in  soup.find("div",{"class":"b-variations_item-content m-list"}).text.strip().split("\n") if not i==" " and i=="Color"] 


# ////////////////////////////////


def start():
    soup=generate_page_soup(base_url)
    
    get_category_urls(soup)

    # for category_url in load_category_urls()["category_urls"] :
    #     print("category_url :     ////  ",category_url)
    #     get_all_product_url(category_url)


start()
print("End")
