# 棋譜ファイルの中から適合パターンのみを別ファイルに補完したい
# パターンに合致するものはTrueを返す
class Pattern:
    """棋譜ファイルのふるい
    持ち時間/開始・終了時間/対局者/指し手の宣言/指した手のみをとりだす
    
    Parameters
    ----------
    text: str
        1行ずつ棋譜ファイルを読み込む
    """
    def __init__(self, text):
        self.text = text
        
    def time(self):
        """文章の判定：持ち時間
        Returns
        ----------
        fact: bool
            持ち時間ならTrue
        """
        return self.text[:4] == '持ち時間'
    def start_time(self):
        """文章の判定：開始時間
        Returns
        ----------
        fact: bool
            開始時間ならTrue
        """
        return self.text[:2] == '開始'
    def end_time(self):
        """文章の判定：終了時間
        Returns
        ----------
        fact: bool
            終了時間ならTrue
        """
        return self.text[:2] == '終了'
    def player(self):
        """文章の判定：対局者
        Returns
        ----------
        fact: bool
            対局者ならTrue
        """
        return ((self.text[:3]=='先手：') or (self.text[:3]=='後手：'))
    def must_sentence(self):
        """文章の判定：宣言
        Returns
        ----------
        fact: bool
            指し手の宣言ならTrue
        """
        return self.text[:2] == '手数'
    def move(self):
        """文章の判定：指し手
        Returns
        ----------
        fact: bool
            指し手ならTrue
        """
        #tmp = self.text.split(' ')
        #mv = tmp[3]
        #return mv.isdecimal()
        return self.text[0] == ' '
    
    def fact_text(self):
        """文章のファクトチェック
        Returns
        ----------
        fact: bool
            読み込んだ文章が適合する内容であればTrueを返す
        """
        return self.time() or self.player() or self.must_sentence() or self.move()
    def fact_kif(self):
        """棋譜のファクトチェック
        Returns
        ----------
        fact: bool
            読み込んだ棋譜が時間を記録していればTrueを返す
            具体的には、最後の手の持ち時間が0時間になっていなければTrue
        """
        return (not ('( 0:00/00:00:00)' in self.text)) and ('( ' in self.text)