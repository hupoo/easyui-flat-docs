import requests
from bs4 import BeautifulSoup

URL = "https://www.jeasyui.cn/document/form/combogrid.html"
html = requests.get(URL, timeout=30).text
print("LEN", len(html))
soup = BeautifulSoup(html, "html.parser")

# find paragraphs mentioning 扩展自 / 依赖
for p in soup.find_all(["p", "div", "span"]):
    txt = p.get_text(strip=True)
    if "扩展自" in txt or "依赖" in txt:
        print(">>", txt[:300])

print("\n=== TABLES ===")
tables = soup.find_all("table")
print("num tables:", len(tables))
for i, t in enumerate(tables):
    # get headers
    headers = [th.get_text(strip=True) for th in t.find_all("th")]
    first_row = [td.get_text(strip=True) for td in t.find_all("tr")[0].find_all("td")] if t.find_all("tr") else []
    print(f"\nTABLE {i}: headers={headers} firstrow={first_row[:6]}")
    rows = t.find_all("tr")
    print("  rows:", len(rows))
