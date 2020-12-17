# proxyUtil


## 概要

この proxyUtil は、PyPAC をForkし、機能を追加した者です。
ライセンス、および本書にないその他の使用方法については、PyPACのドキュメントを併せてご確認ください。
Fork元のPyPACへの影響が最小限となるように勤めています。


## インストール方法
- pip install https://github.com/actlaboratory/proxyutil/archive/0.2.2.zip


## 追加機能の使用方法

class virtualProxyEnviron():
    このオブジェクトは、PACから取得したプロキシ設定値を環境変数に適用するためのものです。
    def __init__(self, proxy_auth, url):
        ＜パラメータ＞
        proxy_auth = None
            プロキシ認証。デフォルトは認証なし
        URL = https://www.riken.jp/
            このURLと通信するためのPACを自動で取得します。デフォルトは理化学研究所
    def set_environ(self, server, port):
        環境変数をセットします。serverとportを指定して、手動で登録することもできます。
    def unset_environ(self):
        環境変数の設定を元に戻します。


## 更新履歴

- Version 0.2.2 2020.12.17
	- レジストリを閉じる際にエラーが出る場合がある問題を修正

- Version 0.2.1 2020.12.09
	- プロキシ情報のレジストリが存在しないときのエラーを修正

- Version 0.2.0 2020.11.23
	- set_environでのサーバ名とポートの直接指定に対応。
	- レジストリに格納されたプロキシ設定の読み込みに対応。

- Version 0.1.1 2020.11.15
	- pyInstaller用fookを追加

- Version 0.1 2020.09.25
    - 初回リリース
