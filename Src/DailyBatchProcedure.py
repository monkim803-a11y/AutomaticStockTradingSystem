import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json

INPUT_FILE  = "prime_list.csv"
OUTPUT_FILE = "stocks.csv"

QUERY = "株価 "
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={}&hl=ja&gl=JP&ceid=JP:ja"

POSITIVE_WORDS = [
    "好調", "最高", "増益", "増配", "上昇", "高騰", "買い", "強気", "追い風", "成長",
    "拡大", "改善", "好転", "好材料", "回復", "プラス", "黒字", "好決算", "好評価",
    "ポジティブ", "高評価"
]

NEGATIVE_WORDS = [
    "不調", "悪化", "減益", "減配", "下落", "暴落", "売り", "弱気", "逆風", "縮小",
    "悪材料", "赤字", "マイナス", "減速", "低迷", "不振", "ネガティブ", "下方修正",
    "警戒", "懸念", "下降"
]


# ---------------------------------------------------------
# 感情スコア計算（Ruby のロジックを忠実に移植）
# ---------------------------------------------------------
def sentiment_score(text: str) -> float:
    if not text or not text.strip():
        return 50.0

    normalized = text.lower()

    pos_count = sum(normalized.count(w) for w in POSITIVE_WORDS)
    neg_count = sum(normalized.count(w) for w in NEGATIVE_WORDS)

    total = pos_count + neg_count
    if total == 0:
        return 50.0

    raw = (pos_count - neg_count) / total  # -1〜+1
    score = ((raw + 1) / 2) * 100          # 0〜100
    return round(score, 1)


# ---------------------------------------------------------
# Googleニュース RSS からニュース取得
# ---------------------------------------------------------
def fetch_news(query: str):
    url = GOOGLE_NEWS_RSS.format(requests.utils.quote(query))
    headers = {"User-Agent": "Python Sentiment Script"}

    xml_text = requests.get(url, headers=headers).text
    root = ET.fromstring(xml_text)

    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        desc = item.findtext("description", "")
        date = item.findtext("pubDate", "")

        score = sentiment_score(f"{title} {desc}")

        items.append({
            "title": title,
            "link": link,
            "date": date,
            "score": score,
            "query": query
        })

    return items


# ---------------------------------------------------------
# Yahooファイナンスから株価情報を取得
# ---------------------------------------------------------
def fetch_price(code: str):
    url = f"https://finance.yahoo.co.jp/quote/{code}.T"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    # window.__PRELOADED_STATE__ を含む script を探す
    script_text = None
    for s in soup.find_all("script"):
        if "window.__PRELOADED_STATE__" in s.text:
            script_text = s.text
            break

    if not script_text:
        print("PRELOADED_STATE が見つかりませんでした")
        return None

    # JSON抽出（Ruby の正規表現より安全で読みやすい）
    json_text = script_text.split("window.__PRELOADED_STATE__ = ", 1)[1]
    json_text = json_text.strip().rstrip(";")

    data = json.loads(json_text)
    quote = data

    # ニュース取得
    name = quote["mainStocksPriceBoard"]["priceBoard"]["name"]
    news_items = fetch_news(QUERY + name + str(code))

    avg_score = round(sum(item["score"] for item in news_items) / len(news_items), 1)

    return {
        "code": code,
        "name": name,
        "price": quote["mainStocksPriceBoard"]["priceBoard"]["price"],
        "change": quote["mainStocksPriceBoard"]["priceBoard"]["priceChange"],
        "change_percent": quote["mainStocksPriceBoard"]["priceBoard"]["priceChangeRate"],
        "updated": quote["mainStocksPriceBoard"]["priceBoard"]["priceDateTime"],
        "volume": quote["mainStocksDetail"]["detail"]["volume"],
        "per": quote["mainStocksDetail"]["referenceIndex"]["per"],
        "pbr": quote["mainStocksDetail"]["referenceIndex"]["pbr"],
        "eps": quote["mainStocksDetail"]["referenceIndex"]["eps"],
        "bps": quote["mainStocksDetail"]["referenceIndex"]["bps"],
        "roe": quote["mainStocksDetail"]["referenceIndex"]["roe"],
        "daily_trans_data": quote["mainItemDetailChartSetting"]["timeSeriesData"]["histories"],
        "news_positive_score": avg_score
    }

# ---------------------------------------------------------
# 動作確認
# ---------------------------------------------------------
if __name__ == "__main__":
    result = fetch_price("7203")  # トヨタ
    print(json.dumps(result, indent=2, ensure_ascii=False))
