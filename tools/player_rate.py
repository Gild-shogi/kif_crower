import numpy as np
import pandas as pd
import json
import csv
import kishi
import time
from logging import getLogger, config
from urllib.error import HTTPError


if __name__ =='__main__':
    # ログのセッティング
    with open('log_config.json', 'r') as f:
        log_conf = json.load(f)
    config.dictConfig(log_conf)
    logger = getLogger(__name__)
    
    players = ['郷田真隆', '真田圭一', '青嶋未来', '丸山忠久', '佐藤康光', '都成竜馬', '佐藤和俊', '藤井猛', '石川優太', '石井健太郎', '黒沢怜生', '三浦弘行', '菅井竜也', '糸谷哲郎', '羽生善治', '折田翔吾',  '斎藤慎太郎', '豊島将之', '森内俊之', '山崎隆之', '八代弥', '脇謙二', '梶浦宏孝', '澤田真吾', '松尾歩', '久保利明', '阿久津主税', '池永天志', '大橋貴洸', '佐々木大地', '橋本崇載', '高野智史', '増田康宏', '佐藤天彦', '井田明宏', '木村一基', '徳田拳士', '村山慈明', '木村一基', '深浦康市', '三枚堂達也', '中村太地', '千田翔太', '中座真', '千葉幸生', '出口若武', '広瀬章人', '服部慎一郎', '阿部健治郎', '鈴木大介', '羽生善治', '藤井聡太', '西田拓也', '永瀬拓矢', '本田奎', '井出隼平', '佐々木勇気', '佐藤紳哉', '稲葉陽', '近藤誠也', '渡辺明']
    number = []

    # 対象棋士の棋士番号の読み込み
    for i in players:
        number.append(kishi.number(i))
    number.sort()

    # CSVHeaderの設定
    header = ["年", "月", "日", "レーティング"]

    # スクレイピング
    for i in range(len(number)):
        f = open("./rating_data/"+str(number[i])+".csv", mode="w+", encoding="utf-8", newline="")
        writer = csv.writer(f, delimiter=",")
        data = []
        data.append(header)
        logger.info(f"=================棋士番号：{number[i]}=====================")
        for j in range(2013, 2023):
            # 存在しないページの時はHTTPErrorが起こるので無視して次のページへ行く
            try:
                url = "http://kishibetsu.com/"+str(j)+"R/1"+str(number[i])+".html"
                logger.debug(url)
                table = pd.read_html(url)[0]
                date_list = table[table.columns[0][0], table.columns[0][1]]["日付"].to_numpy().tolist()
                rate_list = table[table.columns[0][0], table.columns[0][1]]["レート"]["対戦前"].to_numpy().tolist()
                for z in range(len(rate_list)):
                    date_tmp = date_list[z][0]
                    rate_tmp = rate_list[z]
                    if type(date_tmp) == str and type(rate_tmp) == int:
                        year, mounth, day = j, date_tmp.split('月')[0], (date_tmp.split('月')[1]).replace("日", "")
                        data.append([year, mounth, day, rate_tmp])
                    else:
                        pass
                time.sleep(100) #負荷軽減
            except HTTPError:
                logger.debug(f"{j}年のレーティングデータなし")
                time.sleep(60)  #負荷軽減

        for j in data:
            writer.writerow(j)
        f.close()
