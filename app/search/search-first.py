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
        Max_tweet_id=Search_Tweets[-1].id
        print("search{0}回目 通算{1}回目 {2}".format(count,total,Max_tweet_id-1))
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
            	api = tweepy.API(auth)
            else:
            	auth = tweepy.OAuthHandler(consumer_key2, consumer_secret2)
            	auth.set_access_token(access_token2, access_token_secret2)
            	api = tweepy.API(auth)
            print("search{0}回目 通算{1}回目 {2}".format(count,total,Max_tweet_id-1))
            if total>360:
                break
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

df=search_tweets()
search_date=datetime.date(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
df["日付"]=search_date
print("検索完了")
PATH="{}.csv".format(search_date)
df.to_csv("../static/csv/{}".format(PATH),index=False)
