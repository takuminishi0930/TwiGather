#Flaskとrender_template（HTMLを表示させるための関数）をインポート
from flask import Flask,render_template,request
import pandas as pd
import os
from function import *
import datetime
import japanize_matplotlib

#グラフ設定
plt.rcParams["figure.subplot.left"] = 0.25

#Flaskオブジェクトの生成
app = Flask(__name__)

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/menu",methods=["POST"])
def menu_post():
	q = request.form.get("q")
	y = request.form.get("y")
	t = request.form.get("t")
	if q==None:
		#ログイン後はこっち
		dt = datetime.datetime.now()-datetime.timedelta(days=1)
		q = ""
	else:
		#翌日/昨日ボタンはこっち
		dt = str(request.form.get("n"))
		dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
	if request.form.get("y")=="":
		dt -= datetime.timedelta(days=1)
	elif request.form.get("t")=="":
		dt += datetime.timedelta(days=1)
	filepath = "app/static/csv/{}.csv".format(dt.date())
	istomorrow = True
	isyesterday = True
	beforetoday = datetime.datetime.now()-datetime.timedelta(days=1)
	if dt.date()==beforetoday.date():
		istomorrow = False
	dt2 = dt-datetime.timedelta(days=1)
	filepath2 = "app/static/csv/{}.csv".format(dt2.date())
	#dt2とfilepath2は前日のデータがあるか判定するためだけの変数
	if os.path.isfile(filepath2)==False:
		isyesterday = False
		#ファイルが存在しない場合の判定変数
	df = pd.read_csv(filepath,encoding="utf-8")
	header = df.columns
	record = df.values.tolist()
	len_df = len(df)
	Count_Gragh(df)
	plt.close()
	return render_template("menu.html",header=header,record=record,len_df=len_df\
		,dt=dt.date(),istomorrow=istomorrow,isyesterday=isyesterday)

@app.route("/check",methods=["POST"])
def check_post():
	dt = str(request.form.get("n"))
	dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
	list_csv = os.listdir("app/static/csv")
	concat_df = pd.DataFrame()
	for i in list_csv:
		temp_df = pd.read_csv("app/static/csv/{}".format(i))
		concat_df = pd.concat([concat_df,temp_df])
	concat_df.drop_duplicates(keep=False,subset=["ユーザーネーム","テキスト"],inplace=True)
	#ユーザー名もテキストも重複する場合はbotとみなして削除+ユーザー名が重複するツイートを並び替えて表示
	check_df = concat_df[concat_df.duplicated(keep=False,subset="ユーザーネーム")].sort_values("ユーザーネーム")
	header = check_df.columns
	record = check_df.values.tolist()
	len_df = len(check_df)
	Count_Gragh(check_df)
	plt.close()
	return render_template("check.html",header=header,record=record,len_df=len_df,dt=dt.date())

@app.route("/search",methods=["POST"])
def search_post():
	dt = str(request.form.get("n"))
	dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
	q = request.form.get("q")
	if q==None:
		q = ""
	list_csv = os.listdir("app/static/csv")
	concat_df = pd.DataFrame()
	for i in list_csv:
		temp_df = pd.read_csv("app/static/csv/{}".format(i))
		concat_df = pd.concat([concat_df,temp_df])
	searched_df = concat_df.query('テキスト.str.contains("{}")'.format(q), engine="python").sort_values("日付",ascending=False)
	header = searched_df.columns
	record = searched_df.values.tolist()
	len_df = len(searched_df)
	Count_Gragh(searched_df)
	plt.close()
	return render_template("search.html",header=header,record=record,len_df=len_df,q=q,dt=dt.date())

@app.route("/trans",methods=["POST"])
def trans_post():
	dt = str(request.form.get("n"))
	dt = datetime.datetime.strptime(dt,"%Y-%m-%d")
	w = request.form.get("w")
	if request.form.get("w")==None:
		w = ""
	Trans_Gragh(w)
	return render_template("trans.html",dt=dt.date())

if __name__ == "__main__":
    app.run(debug=True)