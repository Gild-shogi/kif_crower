import numpy as np
import pandas as pd

koma_dic = {"K":1, "R":2, "B":3, "G":4, "S":5, "N": 6, "L": 7, "P": 8,
           "k": -1, "r": -2, "b":-3, "g":-4, "s": -5, "n": -6, "l": -7, "p": -8}
mochi_id = {"R":0, "B": 1, "G": 2, "S":3, "N": 4, "L": 5, "P": 6,
           "r":7, "b": 8, "g":9, "s":10, "n":11, "l":12, "p":13}
nari_dic = {"R":9, "B":10, "r": -9, "b":-10,
            "S":4, "N":4, "L":4, "P":4,
            "s":-4, "n":-4, "l":-4, "p":-4}
class Vecter:
    def __init__(self, sfen, date, blacknum, whitenum, score, time):
        self.vec1 = self.returnVec(sfen)
        self.vec2 = self.allcondition(date, blacknum, whitenum)
        self.score = score
        self.time = time
        self.vec = self.combineVec()
    def returnVec(self, sfen):
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
                            tmp.append(koma_dic[j])
                        else:
                            tmp.append(nari_dic[j])
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
                
        # 手数
        vec4 = [int(num)]
        return pd.DataFrame(vec1+[vec2]+[vec3]+[vec4]).fillna(0).to_numpy()
    
    def condition(self, date, number):
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
        vec1, vec2 = self.vec1, self.vec2
        arr = np.array([self.score, self.time])
        vec2 = np.append(vec2, arr)
        return np.vstack([vec1, np.append(vec2, np.zeros(vec1.shape[1]-vec2.shape[0]))])

if __name__ == '__main__':
    sfen = "lnsg2sn+B/4k1g2/p1pppp2p/6R2/9/2P3P2/PG1PPP1SP/4K4/1+b3G1NL w RL4Psnlp 34"
    date = ["2018", "05", "17"]
    time = 0.5125
    score = 0.026
    print(Vecter(sfen, date, 175, 231, score, time).vec.shape)
    for i in Vecter(sfen, date, 175, 231, score, time).vec:
        print(i)