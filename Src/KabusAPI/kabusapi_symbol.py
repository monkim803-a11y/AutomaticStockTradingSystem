import urllib.request
import json
import pprint

# symbol.py

import urllib.request
import urllib.parse
import json


class Symbol:
    def __init__(self,
                 code="5401",
                 market=1,
                 addinfo=False,
                 api_key=""):

        self.code = code
        self.market = market
        self.addinfo = addinfo
        self.api_key = api_key

    # URL を自動生成
    def build_url(self):
        base = "http://localhost:18080/kabusapi/symbol/"
        return f"{base}{self.code}@{self.market}"

    # GET パラメータを dict → URL エンコード
    def build_params(self):
        return urllib.parse.urlencode({
            "addinfo": str(self.addinfo).lower()
        })

    # API 呼び出し
    def get(self):
        url = f"{self.build_url()}?{self.build_params()}"

        req = urllib.request.Request(url, method="GET")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-API-KEY", self.api_key)

        try:
            with urllib.request.urlopen(req) as res:
                content = json.loads(res.read())
                return {
                    "status": res.status,
                    "response": content
                }

        except urllib.error.HTTPError as e:
            content = json.loads(e.read())
            return {
                "status": e.code,
                "response": content
            }

        except Exception as e:
            return {
                "status": "error",
                "response": str(e)
            }

