import requests
from bs4 import BeautifulSoup
import re
import ast
headers = {
    "User-Agent": "PostmanRuntime/7.40.0",
    
}

def generate_page_soup(url):
    print("start")
    response = requests.get(url, headers=headers)
    print(response)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup
url="https://dickiesaustralia.com/products/75394-rockport-khaki"
soup=generate_page_soup(url)

script=str(soup.find_all("script")[-2]).strip()
items=script.split("value: 0,")[1].split("});")[0].split("items: ")[1]
item = re.findall(r"item+.+,",items)
ms=[
    {
        "id":item[0].split(":")[1].strip(",").strip('\" '),
        "name":item[1].split(":")[1].strip(",").strip('\" '),
        "brand":item[2].split(":")[1].strip(",").strip('\" '),
        "category":item[3].split(":")[1].strip(",").strip('\" '),
        "variant":item[4].split(":")[1].strip(",").strip('\" '),
        "price":re.findall(r"price+.+,",items)[0].split(": ")[1].strip(),
        "quantity":re.findall(r"quantity+.+",items)[0].split(": ")[1].strip("\r"),
        "color":[ h.get("href").split("-")[-1]  for a in soup.find_all("div",{'class':"prod-exd-colour-size"}) for h in a.find_all("a")  if h.get("href").split("-")[-1]!='' and h.get("href").split("-")[-1]!='#'],
        
    }
]
print(ms)

print()
