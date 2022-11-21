import re
import requests
from bs4 import BeautifulSoup
import time
import json
from logging import getLogger, config

def save_kif(number=38):
    headers = {
    'User-Agent': 'shogi-kif-crawler(I am robot)'
    }
    url = "http://live.shogi.or.jp/kiou/"
    num = number
    logger.info(f"===================={num}=============================")
    res = requests.get(url+"archive/"+str(num)+".html", headers = headers)
    soup = BeautifulSoup(res.text, "html.parser")
    elems = soup.find_all(href=re.compile("kifu/"+str(num)+"/"))
    
    for e in elems:
        link = e.attrs["href"] # ex. "../kifu/27/ryuou201407010101.html"
        kif_name = (link.split("/")[-1]).split(".")[0] # ex. "ryuou201407010101"
        url_format = url+ "kifu/"+ str(num) + "/" + kif_name+".kif"
        logger.info(url_format)

        
        urlData = requests.get(url_format).content
        with open('kifu/kiou/'+kif_name+".kif", mode="wb") as f:
            f.write(urlData)
        logger.debug("saved: "+ kif_name+".kif")
        time.sleep(60)
    
    if num < 47:
        return save_kif(number=num+1)
    else:
        logger.info("prossess is succed!")

if __name__ =='__main__':
    with open('log_config.json', 'r') as f:
        log_conf = json.load(f)
    config.dictConfig(log_conf)
    logger = getLogger(__name__)

    save_kif()
