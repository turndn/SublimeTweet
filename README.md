# Twitter for SubilimeText
It uses [tweepy](https://github.com/tweepy/tweepy)

# Usage
## default_setting.json
consumer_keyなどのデータを正しく入力しておく.
site\_packages\_pathでtweepyのパスを通すので,tweepyのある場所を指定.

## 各種機能
選択した文字列をコマンド及びツイートする場合はツイートする文字列として認識する.

- commands
	- `tl:` or ``(何も選択しない) 自身のタイムラインを取得
	- `[Value]`(何も指定しない場合) そのままツイートする
	- `rp:[tweet id],[Value]` リプライを送る
	- `rt:[tweet id],` リツイートする
	- `fv:[tweet id],` お気に入り登録する
	- `dl:[tweet id],` ツイートを削除する
	- `ll:` リストの一覧を取得
	- `lt:[screen name],[list name],` リストのタイムラインを取得
	- `cf:[screen name],` ユーザをフォローする
	- `df:[screen name],` ユーザをアンフォローする
	- `il:` フォローリクエスト一覧を表示する
  - `mt:` 自分のツイートを取得する

## コマンドパレットからの実行
文字を選択した状態でコマンドパレットの`Tweet: tweet`を選ぶ.


# LICENSE
This software is released under the MIT License, see LICENSE.txt.
