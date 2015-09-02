#Twitter for SubilimeText
It uses [tweepy](https://github.com/tweepy/tweepy)

#Usage
##default_setting.json
consumer_keyなどのデータを正しく入力しておく.
site\_packages\_pathでtweepyのパスを通すので,tweepyのある場所を指定.

##各種機能
選択した文字列をコマンド及びツイートする場合はツイートする文字列として認識する.

- commands
	- "tl:" or ""(何も選択しない) 自身のタイムラインを取得
	- "_Value_"(何も指定しない場合) そのままツイートする
	- "rp:_tweet id_,_Value_" リプライを送る
	- "rt:_tweet id_," リツイートする
	- "fv:_tweet id_," お気に入り登録する
	- "dl:_tweet id_," ツイートを削除する
	- "ll:" リストの一覧を取得
	- "lt:_screen name_,_list name_," リストのタイムラインを取得
	- "cf:_user id_," ユーザをフォローする
	- "df:_user id_," ユーザをアンフォローする
	- "il:" フォローリクエスト一覧を表示する

##コマンドパレットからの実行
文字を選択した状態でコマンドパレットの"Tweet: tweet"を選ぶ.
