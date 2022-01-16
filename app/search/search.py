import tweepy
import pandas as pd
import sys
import datetime
from config import *
from pycaret.classification import *
import MeCab #形態素解析
import itertools #多次元リストを一次元化
import re #正規表現
import neologdn
import emoji

MECAB_SETTING = "/etc/mecabrc"
MECAB_DICTIONARY = "/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"
MECAB_ARGS = " -r " + MECAB_SETTING + " -d " + MECAB_DICTIONARY

#表記ゆれ修正用辞書
notation_fluctuation1={"むり":"無理","ムリ":"無理","いう":"言う","わかる":"分かる"
                      ,"こと":"事","おもう":"思う","ひと":"人","だれか":"誰か"
                      ,"ヤバい":"やばい","駄目":"だめ","ダメ":"だめ","こまる":"困る"
                      ,"いや":"嫌","つらい":"辛い","きつい":"辛い","できる":"出来る"
                      ,"しんどい":"辛い","こわい":"怖い","マジ":"まじ","しぬ":"死ぬ"
                      ,"やめる":"辞める"}
notation_fluctuation2={"わからない":"分からない","わからん":"分からない","分からん":"分からない"
                       ,"わかりません":"分かりません","わかんない":"分からない","おしえて":"教えて"
                       ,"マジで":"まじ","できん":"出来ない","めんどい":"面倒","就活どう":"就活、どう"
                       ,"めんどくさい":"面倒","しんどい":"辛い","書けん":"書けない","ほんと":"本当"
                       ,"できない":"出来ない","かけない":"書けない","しなきゃ":"しないと","やだ":"嫌だ"
                      ,"ムズイ":"難しい","むずい":"難しい","きつい":"辛い","だるい":"面倒"
                      ,"ほんっと":"本当","やべえ":"やばい","ほんま":"本当","たすけて":"助けて","たすける":"助ける"
                      ,"...":"…","、、、":"…","・・・":"…"}

def search_tweets():
    search_date=datetime.date(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
    total=0
    for index,temp_keyword in enumerate(keyword_list):
        count=0
        print("「{0}」で検索".format(temp_keyword))
        keyword=[temp_keyword]
        keyword.append("exclude:retweets")
        keyword.append("exclude:replies")
        keyword.append("since:{}".format(search_date+datetime.timedelta(days=-1)))
        keyword.append("until:{}".format(search_date))

        Search_word=" ".join(keyword)
        count+=1
        total+=1
        print("search{0}回目 通算{1}回目".format(count,total))
        
        if total%2==0:
        	auth = tweepy.OAuthHandler(consumer_key1, consumer_secret1)
        	auth.set_access_token(access_token1, access_token_secret1)
        	api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,timeout=200)
        else:
        	auth = tweepy.OAuthHandler(consumer_key2, consumer_secret2)
        	auth.set_access_token(access_token2, access_token_secret2)
        	api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,timeout=200)
            	
        Search_Tweets=api.search(q=Search_word,count=100,tweet_mode = "extended")
        Search_Tweets_df_data = [[i.user.name,i._json["full_text"],"https://Twitter.com/{}/status/{}".format(i.user.screen_name,i.id)] for i in Search_Tweets if not (len(i._json["full_text"])>80 or "@" in i._json["full_text"] or "質問箱" in i._json["full_text"] or "http" in i._json["full_text"] or "【" in i._json["full_text"] or "◆" in i._json["full_text"] or "■" in i._json["full_text"] or "●" in i._json["full_text"] or "★" in i._json["full_text"] or "『" in i._json["full_text"] or "「" in i._json["full_text"] or "転職" in i._json["full_text"] or "エージェント" in i._json["full_text"])]
        Search_Tweets_df_columns = ["ユーザーネーム","テキスト","URL"]
        Search_Tweets_df = pd.DataFrame(
            data = Search_Tweets_df_data,
            columns = Search_Tweets_df_columns
            )
        if index==0:
            total_df=Search_Tweets_df.copy()
        else:
            total_df=pd.concat([total_df,Search_Tweets_df])

        while (len(Search_Tweets)!=0):
            Max_tweet_id=Search_Tweets[-1].id
            count+=1
            total+=1
            if total%2==0:
            	auth = tweepy.OAuthHandler(consumer_key1, consumer_secret1)
            	auth.set_access_token(access_token1, access_token_secret1)
            	api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,timeout=200)
            else:
            	auth = tweepy.OAuthHandler(consumer_key2, consumer_secret2)
            	auth.set_access_token(access_token2, access_token_secret2)
            	api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,timeout=200)
            print("search{0}回目 通算{1}回目".format(count,total))
            Search_Tweets=api.search(q=Search_word,count=100,tweet_mode = "extended",max_id=Max_tweet_id-1)
            Search_Tweets_df_data = [[i.user.name,i._json["full_text"],"https://Twitter.com/{}/status/{}".format(i.user.screen_name,i.id)] for i in Search_Tweets if not (len(i._json["full_text"])>80 or "@" in i._json["full_text"] or "質問箱" in i._json["full_text"] or "http" in i._json["full_text"] or "【" in i._json["full_text"] or "◆" in i._json["full_text"] or "■" in i._json["full_text"] or "●" in i._json["full_text"] or "★" in i._json["full_text"] or "『" in i._json["full_text"] or "「" in i._json["full_text"] or "転職" in i._json["full_text"] or "エージェント" in i._json["full_text"])]
            Search_Tweets_df_sub = pd.DataFrame(
                data = Search_Tweets_df_data,
                columns = Search_Tweets_df_columns
                )
            total_df=pd.concat([total_df,Search_Tweets_df_sub])
        final_df=total_df.copy().reset_index(drop=True)
    for index,i in enumerate(total_df.duplicated("テキスト")):
        if i==True:
            final_df.drop(index,inplace=True)
    return final_df

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

def Test_TFIDF(test_df):
    count_train_word_df=pd.read_excel("count_train_word.xlsx")
    idf_df=pd.read_excel("idf.xlsx")
    count_train_word={count_train_word_df["単語"][i]:count_train_word_df["回数"][i] for i in range(len(count_train_word_df))}
    idf={idf_df["単語"][i]:idf_df["idf値"][i] for i in range(len(idf_df))}
    divided_test_text=Divided_Text(test_df["テキスト"])
    test_tfidf=[]
    for i in divided_test_text:
        temp=[]
        for j in count_train_word.keys():
            if j in i:
                temp.append(i.count(j)/len(i)*idf["{}".format(j)])
            else:
                temp.append(0)
        test_tfidf.append(temp)
    sub_test_tfidf_df=pd.DataFrame(data=test_tfidf,index=test_df["テキスト"],columns=count_train_word.keys())
    test_tfidf_df=pd.merge(sub_test_tfidf_df,test_df,on="テキスト")
    return test_tfidf_df

df=search_tweets()
search_date=datetime.date(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
df["日付"]=search_date
print("検索完了")
print("分類開始")
test_data=Test_TFIDF(df)
model=load_model("lr")
test_predictions=predict_model(model,data=test_data)
PATH="{}.csv".format(search_date)
test_predictions[["ユーザーネーム","テキスト","URL","日付"]][test_predictions["Label"]==1].to_csv("../static/csv/{}".format(PATH),index=False)
print("分類終了")