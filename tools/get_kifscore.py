import glob
from PatternFacter import Pattern 

def move_format(sentence):
    sentence = sentence.replace("　", "")
    re_s= []
    for i in sentence.split(" "):
        if i != "":
            re_s.append(i)
    return " ".join(re_s[:2])
def check(sentences):
    flag = 0
    score = []
    move = []
    for sentence in sentences:
        if Pattern(sentence).move():
            move.append(move_format(sentence))
        for s in sentence.split(" "):
            if flag==1:
                score.append(int(s))
                flag = 0
            if "評価値" == s:
                flag = 1
    return score, move

def cut_info():
    for path in glob.glob("./kif_sjis/*/*.kif"):
    #for path in glob.glob("kif_sjis\eiou\eiou202106160101.kif"):
        if not path == "kif_sjis\eiou\eiou202106160101.kif":
            with open(path, mode="r", encoding="shift-jis") as f:
                sentences = f.readlines()
            sentences = sentences[:5] + sentences[7:]
            with open(path, mode="w", encoding="shift-jis") as f:
                f.writelines(sentences)

if __name__ == '__main__':
    path = "kif_sjis\eiou\eiou202106160101.kif"
    with open(path, mode="r", encoding="shift-jis") as f:
        sentences = f.readlines()
    cut_info()
    score, move = check(sentences)
    for i, j in zip(score, move):
        print(f"{j}      {i}")  
        