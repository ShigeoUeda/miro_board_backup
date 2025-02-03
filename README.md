# miro_board_backup

miroのボードのバックアップを行う。

## インストール

```sh
$ git clone
$ cd miro_board_backup
$ python -m venv venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
#
$ nano .env
```

** .envファイル**

miroのAPIトークンを格納する。

```txt
MIRO_ACCESS_TOKEN=eyJtaXJ..........
```

## バックアップ処理

```sh
# ボードリストを取得し、board_list.csvに保存
$ python miro_list_boards.py
# board_list.csvにあるボードIDを使用してバックアップを行う。出力先は./backups
$ python miro_board_backups.py -c board_list.csv -i 2
```
