import numpy as np
import pandas as pd

koma_dic = {"K":1, "R":2, "B":3, "G":4, "S":5, "N": 6, "L": 7, "P": 8,
           "k": -1, "r": -2, "b":-3, "g":-4, "s": -5, "n": -6, "l": -7, "p": -8}
mochi_id = {"R":0, "B": 1, "G": 2, "S":3, "N": 4, "L": 5, "P": 6,
           "r":7, "b": 8, "g":9, "s":10, "n":11, "l":12, "p":13}
nari_dic = {"R":9, "B":10, "r": -9, "b":-10,
            "S":4, "N":4, "L":4, "P":4,
            "s":-4, "n":-4, "l":-4, "p":-4}
# normalize
koma_dic_n = {"K":1/10, "R":2/10, "B":3/10, "G":4/10, "S":5/10, "N": 6/10, "L": 7/10, "P": 8/10,
           "k": -1/10, "r": -2/10, "b":-3/10, "g":-4/10, "s": -5/10, "n": -6/10, "l": -7/10, "p": -8/10}

nari_dic_n = {"R":9/10, "B":10/10, "r": -9/10, "b":-10/10,
            "S":4/10, "N":4/10, "L":4/10, "P":4/10,
            "s":-4/10, "n":-4/10, "l":-4/10, "p":-4/10}

class Vecter:
    """学習データをベクトル化する
    
    機械学習に適したデータにするために、必要なデータをまとめて、
    numpy配列として返す
    特に理由はないが、(しいて言うならデータのサイズを小さくするため)
    sfenから抽出できるデータ以外は一つの配列にまとめている

    Parameter
    ---------
    sfen:str
        局面と持ち駒、手番、手数のUSIプロトコルに基づく型式
    date:list(int)
        対局日、リストには[年, 月, 日]の順番で格納される
    blacknum:int
        先手の棋士番号
    whitenum: int
        後手の棋士番号
    score:
        局面の評価値
    time:
        その手番の人物の残り時間
    """
    def __init__(self, sfen, date, blacknum, whitenum, score, time):
        self.vec1 = self.returnVec(sfen)
        self.vec2 = self.allcondition(date, blacknum, whitenum)
        self.score = score
        self.time = time
        self.vec = self.combineVec()
    def returnVec(self, sfen):
        """sfenデータのベクトル化
        Parameters
        ----------
        sfen:str
            USIプロトコルの局面データ

        Returns
        -------
        vec: np.ndarray
            横13(最長の配列の長さ)、
            縦12(局面：9，手番：1，持ち駒1，手数：1)        
            のnumpy配列を返す
        """
        block = sfen.split(" ")
        kyokumen, bw, mochi, num = block[0], block[1], block[2], block[3]
        
        # 局面
        vec1 = []
        for i in kyokumen.split("/"):
            tmp = []
            flag = True
            for j in i:
                if not j.isdecimal():
                    if j == "+":
                        flag = False
                    else:
                        if flag:
                            tmp.append(koma_dic_n[j])
                        else:
                            tmp.append(nari_dic_n[j])
                            flag = True
                else:
                    tmp.extend([0]*int(j))
            vec1.append(tmp)
        
        # 手番
        vec2 = [0]*1 if bw=="b" else [1]*1
        
        # 持ち駒
        vec3 = [0] * 7 * 2
        cnt = 1
        if mochi != "-":
            for i in range(len(mochi)):
                if not mochi[i].isdecimal():
                    vec3[mochi_id[mochi[i]]] = vec3[mochi_id[mochi[i]]] + cnt
                    cnt = 1
                else:
                    cnt = int(mochi[i])
        vec3[0] = vec3[0] / 2; vec3[1] = vec3[1] / 2; vec3[2] = vec3[2] / 4; vec3[3] = vec3[3] / 4; vec3[4] = vec3[4] / 4; vec3[5] = vec3[5] / 4; vec3[6] = vec3[6] / 18
        vec3[7] = vec3[7] / 2; vec3[8] = vec3[8] / 2; vec3[9] = vec3[9] / 4; vec3[10] = vec3[10] / 4; vec3[11] = vec3[11] / 4; vec3[12] = vec3[12] / 4; vec3[13] = vec3[13] / 18
        # 手数
        vec4 = [int(num)/300]
        return pd.DataFrame(vec1+[vec2]+[vec3]+[vec4]).fillna(0).to_numpy()
    
    def condition(self, date, number):
        """状態を正規化して返す
        入力された棋士のレーティング推移のデータを呼び出し、
        その棋士の対局年の最大レートと最小レートを使用して、
        その日の棋士の調子を正規化して表現する。

        Parameter
        ---------
        date: list(int) -> 日付
        number:int -> 棋士番号

        Returns
        -------
        condition: float32
        """
        date = [int(n) for n in date]
        data = pd.read_csv("./rating_data/"+str(number)+".csv")
        oneyear = data.query("年=="+str(date[0]))
        max = oneyear["レーティング"].max()
        min = oneyear["レーティング"].min()
        playdate = data.query("年=="+str(date[0])).query("月=="+str(date[1])).query("日=="+str(date[2]))["レーティング"]
        normalize = (playdate-min) / (max-min)
        return normalize.to_numpy()
    
    def allcondition(self, date, blacknum, whitenum):
        bcondition = self.condition(date, blacknum)
        wcondition = self.condition(date, whitenum)
        return np.append(bcondition, wcondition)
    
    def combineVec(self):
        """
        1~9行目：棋譜
        10行目：手番(0:先手, 1:後手)
        11行目：持ち駒
        12行目：手数
        13行目：先手の状態、後手の状態
        14行目：評価値
        15行目：残り時間
        vec1: sfenからの情報
        vec2: 棋士の調子
        """

        vec1, vec2 = self.vec1, self.vec2
        #if self.score == None or self.score == 0:
         #   logger.error("評価値がありません")
          #  exit(1)
        self.score = np.array([self.score], dtype=np.float64)
        self.time = np.array(self.time, dtype=np.float64)
        #vec2 = np.append(vec2, arr)
        combVec = vec1
        combVec = np.vstack([combVec, np.append(self.vec2, np.zeros(combVec.shape[1] - self.vec2.shape[0]))])
        combVec = np.vstack([combVec, np.append(self.score, np.zeros(combVec.shape[1] - self.score.shape[0]))])
        combVec = np.vstack([combVec, np.append(self.time, np.zeros(combVec.shape[1] - self.time.shape[0]))])
        return combVec

if __name__ == '__main__':
    sfen = "lnsg2sn+B/4k1g2/p1pppp2p/6R2/9/2P3P2/PG1PPP1SP/4K4/1+b3G1NL w RL4Psnlp 34"
    date = ["2018", "05", "17"]
    time = [0.5125, 0.452]
    score = 0.026
    vec = Vecter(sfen, date, 175, 231, score, time).vec
    print(vec.shape)
    print(vec)
    #for i in Vecter(sfen, date, 175, 231, score, time).vec:
     #   print(i)
