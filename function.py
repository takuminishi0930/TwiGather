import MeCab #形態素解析
import itertools #多次元リストを一次元化
import re #正規表現
import neologdn
import emoji
from config import *
import collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import pandas as pd

#テキストリスト（シリーズ）→二次元リスト　テキストを単語ごとに分割する
def Divided_Text(text_list):
    divided_text=[]
    
    t = MeCab.Tagger(MECAB_ARGS)#辞書を変更するときは[-d (辞書のpath)]
    for text in text_list:
        text=re.sub(r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+$,%#]+)", "" ,text) #url削除
        text=neologdn.normalize(text) #全角・半角の統一と重ね表現の除去
        text=text.lower()#アルファベット大文字を小文字に変換
        text="".join(["" if c in emoji.UNICODE_EMOJI else c for c in text])#絵文字の除去
        text=re.sub(r'(\d)([,.])(\d+)', r'\1\3', text) #桁区切りの除去
        text=re.sub(r'\d+', '0', text) #数字は全て0に置換
        for i in notation_fluctuation2:
            text=text.replace(i,notation_fluctuation2["{}".format(i)])
        subtext=[]
        node = t.parseToNode(text)
        while node:
            node_data=node.feature.split(",")
            #名詞（一般、サ変接続、形容動詞語幹）、自立動詞、自立形容詞、助動詞「ない」、記号「...」だけ抽出
            if ("名詞,一般" in node.feature and "代名詞" not in node.feature)\
            or "名詞,サ変接続" in node.feature\
            or "名詞,形容動詞語幹" in node.feature\
            or "動詞,自立" in node.feature\
            or "形容詞,自立" in node.feature\
            or ("記号" in node.feature and node_data[-3]=="…")\
            or ("助動詞" in node.feature and node_data[-3]=="ない"):
                if node_data[0]!="名詞" and "*" not in node_data[-3]:
                    if node_data[-3] in notation_fluctuation1.keys():
                        subtext.append(notation_fluctuation1["{}".format(node_data[-3])])
                    #自立動詞、自立形容詞の場合は原型を抽出
                    else:
                        subtext.append(node_data[-3])
                else:
                    if node.surface in notation_fluctuation1.keys():
                        subtext.append(notation_fluctuation1["{}".format(node.surface)])
                    else:
                        subtext.append(node.surface)
            node=node.next
        divided_text.append(subtext)
    return divided_text

def Count_Gragh(df):
    #グラフ作成
	word_list = list(itertools.chain.from_iterable(Divided_Text(df["テキスト"])))
	count_word = collections.Counter(word_list)
	if len(word_list)<10:
		word = list(reversed([i[0] for i in count_word.most_common(len(word_list))]))
		frec = list(reversed([i[1] for i in count_word.most_common(len(word_list))]))
	else:
		word = list(reversed([i[0] for i in count_word.most_common(10)]))
		frec = list(reversed([i[1] for i in count_word.most_common(10)]))
	for index,i in enumerate(word):
		word[index] = i+"({})".format(frec[index])
	fig, ax = plt.subplots(figsize=(7.0, 7.0))
	ax.barh(word, frec)
	fig.savefig("app/static/images/count_word.png")

def Trans_Gragh(word):
    list_csv = os.listdir("app/static/csv")
    trans_list = []
    for i in list_csv:
        df = pd.read_csv("app/static/csv/{}".format(i))
        word_list = list(itertools.chain.from_iterable(Divided_Text(df["テキスト"])))
        count_word = collections.Counter(word_list)
        date = os.path.splitext(os.path.basename(i))[0]
        trans_list.append([count_word[word],date])
    trans_df = pd.DataFrame(trans_list, columns=["単語数","日付"])
    trans_df = trans_df.sort_values("日付")
    dt = pd.to_datetime(list(trans_df["日付"]))
    fig, ax = plt.subplots(figsize=(7.0, 7.0))
    #日付表示フォーマット変更用
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%y/%m/%d"))
    #日付目盛インターバル変更用
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.plot(dt,trans_df["単語数"])
    ax.grid()
    ax.set_title("「"+word+"」の出現回数の推移")
    fig.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95)
    fig.savefig("app/static/images/trans_word.png")
    plt.close()