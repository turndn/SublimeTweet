#Twitter for SubilimeText
It uses tweepy(https://github.com/tweepy/tweepy)

#Usage
default_setting.json
データを正しく入力しておく.
site\_packages\_pathでtweepyのパスを通すので,tweepyのある場所を指定.
Selected string is command.
- commands
	- "tl:" 自身のタイムラインを取得
	- 何も指定しない場合: そのままツイートする
	- "rp:_tweet id_,_Value_" リプライを送る
	- "rt:_tweet id_," リツイートする
	- "fv:_tweet id_" お気に入り登録する
	- "dl:_tweet id_" ツイートを削除する
	- "ll:" リストの一覧を取得
	- "lt:_screen name_,_list name_,"リストのタイムラインを取得
