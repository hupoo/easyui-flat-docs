# -*- coding: utf-8 -*-
"""Scrape jeasyui.cn API pages into components_raw.json."""
import json
import re
import requests
from bs4 import BeautifulSoup

BASE = "https://www.jeasyui.cn/document/{cat}/{name}.html"

# component -> category (best guess; scraper falls back to other categories on 404)
COMPONENTS = {
    "validatebox": "form",
    "textbox": "form",
    "combo": "form",
    "combobox": "form",
    "datebox": "form",
    "datetimebox": "form",
    "numberbox": "form",
    "filebox": "form",
    "calendar": "form",
    "timespinner": "form",
    "spinner": "form",
    "combogrid": "form",
    "combotree": "form",
    "combotreegrid": "form",
    "slider": "base",
    "searchbox": "base",
    "panel": "layout",
    "datagrid": "datagrid",
    "treegrid": "datagrid",
    "propertygrid": "datagrid",
    "tree": "datagrid",
}
CATS = ["form", "base", "layout", "datagrid", "menu", "window"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def fetch(name, cat):
    url = BASE.format(cat=cat, name=name)
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 200 and "jeasyui" in r.text:
        return r.text, url
    return None, url


def get_html(name, cat):
    html, url = fetch(name, cat)
    if html:
        return html, url
    for c in CATS:
        if c == cat:
            continue
        html, url = fetch(name, c)
        if html:
            return html, url
    return None, url


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def extract_extends(soup, name):
    """Find the canonical '扩展自 $.fn.X.defaults' clause (excluding the
    '使用$.fn.SELF.defaults重写' rewrite sentence)."""
    extends = []
    for p in soup.find_all("p"):
        t = p.get_text()
        if "扩展自" in t:
            m = re.search(r"扩展自\s*(.*?)(?:\s*。|\s*使用)", t)
            clause = m.group(1) if m else t
            found = re.findall(r"fn\.([A-Za-z]\w*)\.defaults", clause)
            if found:
                extends = found
                break
    # fallback: any 扩展自 X(...) 和 Y(...)
    if not extends:
        txt = soup.get_text()
        m = re.search(r"扩展自\s*([A-Za-z]\w*)\s*(?:\([^)]*\))?\s*(?:和\s*([A-Za-z]\w*))?", txt)
        if m:
            extends = [x for x in m.groups() if x]
    # dedupe + drop self
    seen = set()
    out = []
    for e in extends:
        if e and e != name and e not in seen:
            seen.add(e)
            out.append(e)
    return out


# Only these are real component plugins that can appear as a dependency.
KNOWN_DEP_COMPONENTS = {
    "tooltip", "linkbutton", "panel", "calendar", "resizable", "draggable",
    "droppable", "pagination", "menubutton", "spinner", "textbox",
    "timespinner", "combo", "datagrid", "tree", "treegrid", "validatebox",
    "numberbox", "datebox", "combobox",
}


def extract_depends(soup, name):
    """Extract 依赖关系 bullet list, keeping only known component plugins."""
    anchor = None
    for p in soup.find_all(["p", "div", "span", "h4", "h5", "h3"]):
        t = p.get_text()
        if "依赖关系" in t or ("依赖" in t and len(t) < 40):
            anchor = p
            break
    if anchor is None:
        return []
    candidates = []
    ul = anchor.find_next("ul") if anchor.name in ("p", "div", "span", "h4", "h5", "h3") else None
    if ul:
        for li in ul.find_all("li"):
            candidates.append(clean(li.get_text()))
    else:
        after = anchor.get_text()
        after = after.split("依赖关系")[-1] if "依赖关系" in after else after
        candidates = re.findall(r"[•·\-\*]\s*([A-Za-z]\w*)", after)
    deps = []
    for c in candidates:
        if re.match(r"^[a-z]\w*$", c) and c in KNOWN_DEP_COMPONENTS and c != name:
            deps.append(c)
    # dedupe
    seen = set()
    out = []
    for d in deps:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def detect_table_type(headers):
    h = " ".join(headers)
    if "方法" in h:
        return "methods"
    if "事件" in h:
        return "events"
    if "属性" in h:
        return "properties"
    return None


def col_index(headers, keywords):
    for i, h in enumerate(headers):
        for kw in keywords:
            if kw in h:
                return i
    return None


def parse_table(table):
    rows = table.find_all("tr")
    if not rows:
        return None, []
    # header row = first row with <th>, else first row
    header_cells = rows[0].find_all(["th", "td"])
    headers = [clean(c.get_text()) for c in header_cells]
    ttype = detect_table_type(headers)
    if not ttype:
        return None, []
    name_i = col_index(headers, ["名"])
    type_i = col_index(headers, ["类型", "值类型"])
    default_i = col_index(headers, ["默认值"])
    params_i = col_index(headers, ["参数"])
    desc_i = col_index(headers, ["描述", "说明"])
    items = []
    for tr in rows[1:]:
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        vals = [clean(c.get_text()) for c in cells]
        if not any(vals):
            continue
        name = vals[name_i] if name_i is not None and name_i < len(vals) else (vals[0] if vals else "")
        if not name:
            continue
        item = {"name": name}
        if ttype == "properties":
            item["type"] = vals[type_i] if type_i is not None and type_i < len(vals) else ""
            item["default"] = vals[default_i] if default_i is not None and default_i < len(vals) else ""
            item["desc"] = vals[desc_i] if desc_i is not None and desc_i < len(vals) else ""
        else:
            item["params"] = vals[params_i] if params_i is not None and params_i < len(vals) else ""
            item["desc"] = vals[desc_i] if desc_i is not None and desc_i < len(vals) else ""
        items.append(item)
    return ttype, items


def extract_title_desc(soup):
    title = ""
    h = soup.find(["h1", "h2", "h3"])
    if h:
        title = clean(h.get_text())
    # intro paragraph = first <p> that has some length
    desc = ""
    for p in soup.find_all("p"):
        t = clean(p.get_text())
        if len(t) > 20 and ("扩展自" in t or "控件" in t or "组件" in t or "用于" in t):
            desc = t
            break
    return title, desc


def main():
    result = {}
    for name, cat in COMPONENTS.items():
        html, url = get_html(name, cat)
        if not html:
            print(f"[SKIP] {name}: not found (tried {url})")
            continue
        soup = BeautifulSoup(html, "html.parser")
        extends = extract_extends(soup, name)
        depends = extract_depends(soup, name)
        title, desc = extract_title_desc(soup)
        props, events, methods = [], [], []
        for table in soup.find_all("table"):
            ttype, items = parse_table(table)
            if ttype == "properties":
                props += items
            elif ttype == "events":
                events += items
            elif ttype == "methods":
                methods += items
        result[name] = {
            "name": name,
            "display": title or name,
            "category": cat,
            "url": url,
            "extends": extends,
            "depends": depends,
            "desc": desc,
            "properties": props,
            "events": events,
            "methods": methods,
        }
        print(f"[OK] {name}: extends={extends} depends={depends} "
              f"props={len(props)} events={len(events)} methods={len(methods)} url={url}")
    with open("components_raw.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nTotal components: {len(result)} -> components_raw.json")


if __name__ == "__main__":
    main()
