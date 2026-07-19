import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json

INPUT_FILE  = "prime_list.csv"
OUTPUT_FILE = "stocks.csv"

QUERY = "株価 銘柄コード "
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
import urllib.request
import re
import json

def http_get(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req) as res:
        return res.read().decode("utf-8")

# ---------------------------------------------------------
# 数値正規化関数
# ---------------------------------------------------------
def normalize_number(value):
    if not value:
        return None
    value = value.replace(",", "").replace("倍", "").replace("%", "")
    # 億・万を数値に変換
    if "億" in value:
        value = value.replace("億", "")
        try:
            return float(value) * 1e8
        except ValueError:
            return None
    if "万" in value:
        value = value.replace("万", "")
        try:
            return float(value) * 1e4
        except ValueError:
            return None
    try:
        return float(value)
    except ValueError:
        return None


# ---------------------------------------------------------
# ① 基本情報ページ https://irbank.net/[code]
# ---------------------------------------------------------
def fetch_irbank_basic(code):
    url = f"https://irbank.net/{code}"
    html = http_get(url)

    def find(pattern):
        m = re.search(pattern, html)
        return m.group(1) if m else None

    data = {
        "code": code,
        "PER": normalize_number(find(r"PER（連）.*?class=\"text\">([\d\.]+)倍")),
        "PBR": normalize_number(find(r"PBR（連）.*?class=\"text\">([\d\.]+)倍")),
        "ROE": normalize_number(find(r"ROE（連）.*?class=\"text\">([\d\.]+)%")),
        "ROA": normalize_number(find(r"ROA（連）.*?class=\"text\">([\d\.]+)%")),
        "EPS": normalize_number(find(r"EPS（連）.*?class=\"text\">([\d\.]+)")),
        "BPS": normalize_number(find(r"BPS（連）.*?class=\"text\">([\d\.]+)")),
        # 出来高（5日）構造に対応：co_br が変化率、co_sm が値
        "volume_5d_change": find(r"出来高（5日）.*?class=\"co_br\">([\-+\d\.%]+)"),
        "volume_5d_value": find(r"出来高（5日）.*?class=\"co_sm\">([\d,]+)")
    }

    return data


# ---------------------------------------------------------
# ② チャートページ https://irbank.net/[code]/chart
# ---------------------------------------------------------
def fetch_irbank_chart(code):
    url = f"https://irbank.net/{code}/chart"
    html = http_get(url)

    table_match = re.search(r'<table id="tbc".*?</table>', html, re.DOTALL)
    if not table_match:
        return []

    table_html = table_match.group(0)
    rows = re.findall(r'<tr.*?</tr>', table_html, re.DOTALL)

    chart_data = []
    for row in rows[:20]:
        cells = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 10:
            continue
        clean = [re.sub(r'<.*?>', '', c).strip() for c in cells]

        chart_data.append({
            "date": clean[0],
            "open": normalize_number(clean[1]),
            "high": normalize_number(clean[2]),
            "low": normalize_number(clean[3]),
            "close": normalize_number(clean[4]),
            "change": clean[5],
            "volume": normalize_number(clean[6]),
            "market_cap": normalize_number(clean[7]),
            "deviation_25d": clean[8],
            "PER": normalize_number(clean[9]),
            "PBR": normalize_number(clean[10]) if len(clean) > 10 else None
        })

    return chart_data


# ---------------------------------------------------------
# ③ 全データ統合
# ---------------------------------------------------------
def fetch_irbank_all(code):
    basic = fetch_irbank_basic(code)
    chart = fetch_irbank_chart(code)

    # ニュース取得
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
import urllib.request
import re
import json

def http_get(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req) as res:
        return res.read().decode("utf-8")

# ---------------------------------------------------------
# 数値正規化関数
# ---------------------------------------------------------
def normalize_number(value):
    if not value:
        return None
    value = value.replace(",", "").replace("倍", "").replace("%", "")
    # 億・万を数値に変換
    if "億" in value:
        value = value.replace("億", "")
        try:
            return float(value) * 1e8
        except ValueError:
            return None
    if "万" in value:
        value = value.replace("万", "")
        try:
            return float(value) * 1e4
        except ValueError:
            return None
    try:
        return float(value)
    except ValueError:
        return None


# ---------------------------------------------------------
# ① 基本情報ページ https://irbank.net/[code]
# ---------------------------------------------------------
def fetch_irbank_basic(code):
    url = f"https://irbank.net/{code}"
    html = http_get(url)

    def find(pattern):
        m = re.search(pattern, html)
        return m.group(1) if m else None

    data = {
        "code": code,
        "PER": normalize_number(find(r"PER（連）.*?class=\"text\">([\d\.]+)倍")),
        "PBR": normalize_number(find(r"PBR（連）.*?class=\"text\">([\d\.]+)倍")),
        "ROE": normalize_number(find(r"ROE（連）.*?class=\"text\">([\d\.]+)%")),
        "ROA": normalize_number(find(r"ROA（連）.*?class=\"text\">([\d\.]+)%")),
        "EPS": normalize_number(find(r"EPS（連）.*?class=\"text\">([\d\.]+)")),
        "BPS": normalize_number(find(r"BPS（連）.*?class=\"text\">([\d\.]+)")),
        # 出来高（5日）構造に対応：co_br が変化率、co_sm が値
        "volume_5d_change": find(r"出来高（5日）.*?class=\"co_br\">([\-+\d\.%]+)"),
        "volume_5d_value": find(r"出来高（5日）.*?class=\"co_sm\">([\d,]+)")
    }

    return data


# ---------------------------------------------------------
# ② チャートページ https://irbank.net/[code]/chart
# ---------------------------------------------------------
def fetch_irbank_chart(code):
    url = f"https://irbank.net/{code}/chart"
    html = http_get(url)

    table_match = re.search(r'<table id="tbc".*?</table>', html, re.DOTALL)
    if not table_match:
        return []

    table_html = table_match.group(0)
    rows = re.findall(r'<tr.*?</tr>', table_html, re.DOTALL)

    chart_data = []
    for row in rows[:20]:
        cells = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 10:
            continue
        clean = [re.sub(r'<.*?>', '', c).strip() for c in cells]

        chart_data.append({
            "date": clean[0],
            "open": normalize_number(clean[1]),
            "high": normalize_number(clean[2]),
            "low": normalize_number(clean[3]),
            "close": normalize_number(clean[4]),
            "change": clean[5],
            "volume": normalize_number(clean[6]),
            "market_cap": normalize_number(clean[7]),
            "deviation_25d": clean[8],
            "PER": normalize_number(clean[9]),
            "PBR": normalize_number(clean[10]) if len(clean) > 10 else None
        })

    return chart_data


# ---------------------------------------------------------
# ③ 全データ統合
# ---------------------------------------------------------
def fetch_irbank_all(code):
    basic = fetch_irbank_basic(code)
    chart = fetch_irbank_chart(code)

    # ニュース取得
    news_items = fetch_news(QUERY + name + str(code))
    avg_score = round(sum(item["score"] for item in news_items) / len(news_items), 1)

    return {
        "code": code,
        "basic": basic,
        "chart_20days": chart,
        "news_positive_score": avg_score
    }

# ---------------------------------------------------------
# 動作確認
# ---------------------------------------------------------
if __name__ == "__main__":
    result = fetch_price("7203")  # トヨタ
    print(json.dumps(result, indent=2, ensure_ascii=False))
