import urllib.request

url = "https://tenhou.net/sc/raw/list.cgi"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://tenhou.net/sc/raw/"
}

print(f"[{url}] の応答を確認中...")

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode('utf-8', errors='ignore')
        print("-> 取得成功！ 先頭500文字:")
        print("--------------------------------------------------")
        print(body[:500])
        print("--------------------------------------------------")
except urllib.error.HTTPError as e:
    print(f"HTTPエラー: {e.code}")
except Exception as e:
    print(f"エラー: {e}")
