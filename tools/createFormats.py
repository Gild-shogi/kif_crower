import shogi
import cshogi
import re
import glob
import time
import datetime
from tools.PatternFacter import Pattern
from cshogi.usi import Engine
from cshogi.cli import usi_info_to_score, usi_info_to_csa_comment, re_usi_info
import configparser
import sys
import shogi.KIF
import json

class Formats:
    """Formats
    ファイル情報を整理して別のファイルにコンバートするためのモジュール

    """
    def __init__(self, path):
        """initialize
        
        Parameters
        ----------
        path:str
            棋譜ファイルのパス
        kif:list -> str
            棋譜ファイルの中身(1行ずつリストで保持）
        fptime: datetime
            先手の残り時間
        lptime: datetime
            後手の残り時間
            
        """
        self.path = path
        with open(path, mode="r", encoding='shift-jis') as f:
            self.kif = f.readlines()
        self.fptime = self.time(mode="n")
        self.lptime = self.time(mode="n")
    
    def readline(self):
        """
        棋譜ファイルのリスト書き出し
        
        Returns
        -------
        kif:list
            棋譜ファイルを1行ごとにリストにしたもの
        """
        return self.kif
    
    def time(self, mode='u'):
        """
        対局開始時の持ち時間を返す関数
        
        Parameters
        ----------
        mode: str
            'u': unixタイムを返す
            'n': 通常の時間を返す
        """
        tmp =  int(self.kif[0][-4])
        thentime = datetime.time(tmp, 0, 0)
        if mode=='n': #normal
            return thentime
        elif mode=='u': # combine
            return datetime.datetime.combine(datetime.date.today(), thentime).timestamp()
        
    def today(self):
        """
        今日の0時0分0秒のUnixタイムを返す
        
        Returns
        -------
        time: float
            Unixタイムをfloat型にしたもの
        """
        init = datetime.time(0, 0, 0)
        return float(datetime.datetime.combine(datetime.date.today(), init).timestamp())
    
    def keep_time(self, mode='u'):    
        """
        対局者の残り時間をリスト管理するもの
        
        Parameters
        ----------
        mode: str
            'u'：Unixタイムを返す
            'n'：通常の時間を返す
        
        Returns
        kt(mode='n'): list -> datetime.datetime
        kt(mode='u'): list -> time(unixtime)
            
        """
        cnt = 1
        kt = []
        for i in self.readline():
            if Pattern(i).move():
                # 正規表現で時間部分の切り出し
                settime = re.findall("(?<=/).+?(?=\))", i)
                settime = settime[0].split(":")
                #print(settime)
                tmptime = datetime.timedelta(hours=int(settime[0]), minutes=int(settime[1]), seconds=int(settime[2]))
                if cnt%2 == 1:
                    self.fptime = datetime.datetime.combine(datetime.date.today(), self.time(mode='n')) - tmptime
                    if mode=='d':
                        kt.append(self.fptime.strftime("%H:%M:%S"))
                    elif mode=='u':
                        kt.append(self.fptime.timestamp())
                else:
                    self.lptime =  datetime.datetime.combine(datetime.date.today(), self.time(mode='n'))- tmptime
                    if mode=='d':
                        kt.append(self.lptime.strftime("%H:%M:%S"))
                    elif mode=='u':
                        kt.append(self.lptime.timestamp())
                cnt = cnt + 1 
        return kt
        
    def normalize_time(self):
        """
        標準化(0から1でスケーリング)した残り時間を返す
        
        Returns
        -------
        time: list -> float
            標準化した残り時間
        """
        tmp = []
        time = []
        for i in self.keep_time(mode='u'):
            j = float(i) - float(self.today())
            k = float(self.time(mode='u')) - self.today()
            tmp.append(j/k)
        time.append([tmp[0], 1])
        tmp = tmp[:-1]
        for i in range(1, len(tmp)):
            if i%2 == 1:
                time.append([tmp[i-1], tmp[i]])
            else:
                time.append([tmp[i], tmp[i-1]])

        return time
        
    def player(self, mode="name"):      
        """
        対局者の情報を返す
        
        Returns:
            playerset: dict
                first->先手の名前
                last -> 後手の名前
        """
        playerset = {}
        playerset["first"], playerset["last"] = "", ""
        with open("./player_num.json", encoding="utf-8", mode="r") as f:
            player_dict = json.load(f)
        for sentence in self.kif:
            if Pattern(sentence).player():
                tmp = ((sentence.split("：")[1]).split("・")[0]).replace("\n", "")
                if playerset["first"] == "":
                    playerset["first"] = tmp[:-2]
                else:
                    playerset["last"] = tmp[:-2]
                    if mode=="name":
                        return playerset
                    if mode=="number":
                        playerset["first"] = player_dict[playerset["first"].replace(" ", "")]
                        playerset["last"] = player_dict[playerset["last"].replace(" ", "")]
                        return playerset
                
                
            
    def kif2sfen(self):
        """sfenの指し手を返す

        Returns
        -------
        sfen: list(str)
            SFENに変換した棋譜
        """
        kif = shogi.KIF.Parser.parse_file(self.path)[0]
        board = cshogi.Board()
        sfen = []
        for i in kif['moves']:
            move = board.push_usi(i)
            sfen.append(board.sfen())
        return sfen
    
    def play_date(self):
        """対局日を返す
        Returns
        -------
        data: list(int)
            ["year", "month", "date"]の順でリストで対局日を返す
        """
        tmp_path = self.path.split("\\")
        tmp = tmp_path[2].split(tmp_path[1])[1]
        return [tmp[:4], tmp[4:6], tmp[6:8]]
        
    def game_score(self):
        """評価値を返す
        Returns
        -------
        scores: list(int)
            評価値の一覧を返す
        """
        sentences = self.kif
        flag = 0
        scores = []
        
        for sentence in sentences:
            for s in sentence.split(" "):
                if flag == 1:
                    if not "詰" in s:
                        scores.append(int(s)/5000)
                    else:
                        scores.append(int(s[0]+"5000")/5000)
                    flag = 0
                if "評価値" == s:
                    flag = 1
        return scores[:-1]

    def winner(self):
        """勝者を先手ならTrue, 後手ならFalseで返す
        returns
        -------
        winner: bool
            勝者
        """
        return len(self.game_score()) % 2 == 1