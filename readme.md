# proxyUtil


## 概要

この proxyUtil は、PyPAC をForkし、機能を追加した者です。
ライセンス、および本書にないその他の使用方法については、PyPACのドキュメントを併せてご確認ください。
Fork元のPyPACへの影響が最小限となるように勤めています。


## インストール方法
- pip install https://github.com/actlaboratory/proxyutil/archive/0.1.zip


## 追加機能の使用方法

class virtualProxyEnviron():
    このオブジェクトは、PACから取得したプロキシ設定値を環境変数に適用するためのものです。
    def __init__(self, proxy_auth, url):
        ＜パラメータ＞
        proxy_auth = None
            プロキシ認証。デフォルトは認証なし
        URL = https://www.riken.jp/
            このURLと通信するためのPACを自動で取得します。デフォルトは理化学研究所
    def set_environ(self):
        環境変数をセットします。
    def unset_environ(self):
        環境変数の設定を元に戻します。


## 更新履歴
- Version 0.1 2020.09.25
    - 初回リリース
