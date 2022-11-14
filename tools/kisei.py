import re
import requests
from bs4 import BeautifulSoup
import time
import json
from logging import getLogger, config

def save_kif():
    headers = {
    'User-Agent': 'shogi-kif-crawler(I am robot)'
    }
    url = "http://live.shogi.or.jp/kisei/"
    res = requests.get(url+"archive/index.html", headers = headers)
    soup = BeautifulSoup(res.text, "html.parser")
    elems = soup.find_all(href=re.compile("kifu/"))
    
    for e in elems:
        link = e.attrs["href"] # ex. "../kifu/27/ryuou201407010101.html"
        
        kif_name = (link.split("/")[-1]).split(".")[0] # ex. "ryuou201407010101"
        number = link.split("/")[-2]
        if number.isdecimal():
            number = int(number)
        else:
            continue
        logger.debug(number)
        url_format = url+"kifu/"+str(number)+"/"+kif_name+".kif"
        logger.info(url_format)

        if number > 83:
            urlData = requests.get(url_format).content
            with open('kifu/kisei/'+kif_name+".kif", mode="wb") as f:
                f.write(urlData)
            logger.debug("saved: "+ kif_name+".kif")
            time.sleep(60)
    

if __name__ =='__main__':
    with open('log_config.json', 'r') as f:
        log_conf = json.load(f)
    config.dictConfig(log_conf)
    logger = getLogger(__name__)

    save_kif()
