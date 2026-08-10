# -*- coding: utf-8 -*-
"""Render components_flat.json into a static, single-page HTML documentation site."""
import json
import html

ROOT = "E:/documents/easyui文档/easyui-new-docs"
SITE = ROOT  # index.html goes to site root

FAMILIES = [
    ("表单输入", ["validatebox", "textbox", "combo", "combobox", "datebox",
                  "datetimebox", "numberbox", "filebox", "calendar", "timespinner",
                  "spinner", "searchbox", "slider"]),
    ("表格 / 数据网格", ["panel", "datagrid", "treegrid", "propertygrid"]),
    ("树", ["tree"]),
    ("组合下拉框（Combo + Grid/Tree）", ["combogrid", "combotree", "combotreegrid"]),
]

CATEGORY_CN = {
    "form": "form", "base": "base", "layout": "layout", "datagrid": "datagrid",
}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def build_nav(flat):
    groups = []
    for fam, names in FAMILIES:
        items = []
        for n in names:
            if n not in flat:
                continue
            c = flat[n]
            items.append({
                "name": n,
                "display": esc(c["display"] or n),
                "p": c["counts"]["properties"],
                "e": c["counts"]["events"],
                "m": c["counts"]["methods"],
            })
        if items:
            groups.append({"family": fam, "items": items})
    return groups


def render():
    with open("components_flat.json", encoding="utf-8") as f:
        flat = json.load(f)

    nav = build_nav(flat)

    # pre-escape all string fields for safe innerHTML insertion
    data = {}
    for name, c in flat.items():
        def clean_items(lst):
            out = []
            for it in lst:
                d = {k: esc(it.get(k, "")) for k in
                     ("name", "type", "default", "params", "desc", "source")}
                d["overridden"] = bool(it.get("overridden"))
                out.append(d)
            return out
        data[name] = {
            "name": name,
            "display": esc(c.get("display", name)),
            "category": esc(c.get("category", "")),
            "url": esc(c.get("url", "")),
            "depends": [esc(x) for x in c.get("depends", [])],
            "desc": esc(c.get("desc", "")),
            "chains": c.get("inheritance_chains", []),
            "properties": clean_items(c.get("properties", [])),
            "events": clean_items(c.get("events", [])),
            "methods": clean_items(c.get("methods", [])),
            "counts": c.get("counts", {}),
        }

    payload = {
        "nav": nav,
        "data": data,
        # source labels: component display name keyed by name for breadcrumb links
        "labels": {n: (flat[n].get("display") or n) for n in flat},
    }

    css = """
    :root{
      --bg:#ffffff; --panel:#f7f8fa; --border:#e5e7eb; --text:#1f2933;
      --muted:#6b7280; --accent:#2563eb; --accent-soft:#eff6ff;
      --own:#10b981; --over:#f59e0b; --chip:#eef2ff;
    }
    *{box-sizing:border-box}
    html,body{margin:0;height:100%}
    html{scroll-behavior:smooth}
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
      color:var(--text);background:var(--bg);font-size:14px;line-height:1.6}
    a{color:var(--accent);text-decoration:none}
    a:hover{text-decoration:underline}
    #layout{display:flex;min-height:100vh}
    /* sidebar */
    #sidebar{width:280px;flex:0 0 280px;background:var(--panel);border-right:1px solid var(--border);
      position:sticky;top:0;height:100vh;overflow-y:auto;padding:18px 14px}
    #sidebar h1{font-size:16px;margin:0 0 4px}
    #sidebar .sub{color:var(--muted);font-size:12px;margin-bottom:14px}
    #search{width:100%;padding:8px 10px;border:1px solid var(--border);border-radius:8px;
      font-size:13px;margin-bottom:14px;background:#fff}
    .nav-group{margin-bottom:14px}
    .nav-group > .gtitle{font-size:12px;font-weight:700;color:var(--muted);
      text-transform:uppercase;letter-spacing:.04em;margin:10px 4px 6px}
    .nav-item{display:flex;justify-content:space-between;align-items:center;
      padding:6px 10px;border-radius:8px;cursor:pointer;gap:8px}
    .nav-item:hover{background:var(--accent-soft)}
    .nav-item.active{background:var(--accent);color:#fff}
    .nav-item.active .nm{color:#fff}
    .nav-item.active .cnt{color:#dbeafe}
    .nav-item.active .cnt b{color:#fff}
    .nav-item .nm{font-weight:600}
    .nav-item .cnt{font-size:11px;color:var(--muted);white-space:nowrap}
    .nav-item .cnt b{color:var(--accent)}
    /* main */
    #content{flex:1;padding:28px 36px;max-width:1100px}
    header.top{border-bottom:1px solid var(--border);padding-bottom:14px;margin-bottom:24px}
    header.top h1{margin:0 0 6px;font-size:22px}
    header.top p{color:var(--muted);margin:4px 0}
    .legend{display:flex;gap:14px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--muted)}
    .legend .pill{padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600}
    .pill.own{background:#ecfdf5;color:#047857}
    .pill.over{background:#fef3c7;color:#b45309}
    .pill.src{background:var(--chip);color:#4338ca}
    section.comp{border-top:1px solid var(--border);padding:26px 0;scroll-margin-top:16px}
    section.comp:first-of-type{border-top:none}
    .comp h2{margin:0 0 2px;font-size:20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
    .badge{font-size:11px;font-weight:600;color:var(--muted);background:var(--panel);
      border:1px solid var(--border);border-radius:6px;padding:1px 7px}
    .orig{font-size:12px}
    .desc{color:var(--muted);margin:6px 0 12px}
    .chains{display:flex;flex-direction:column;gap:6px;margin:10px 0 6px;flex-wrap:wrap}
    .chain{font-size:13px;background:var(--panel);border:1px solid var(--border);
      border-radius:8px;padding:6px 10px;display:inline-flex;gap:6px;align-items:center;flex-wrap:wrap;width:fit-content}
    .chain .arrow{color:var(--muted)}
    .chain .me{font-weight:700;color:var(--accent)}
    .chain a.src{font-weight:600}
    .deps{font-size:12px;color:var(--muted);margin:6px 0 14px}
    .toolbar{display:flex;align-items:center;gap:10px;margin:6px 0 10px;flex-wrap:wrap}
    .toolbar select{padding:5px 8px;border:1px solid var(--border);border-radius:6px;background:#fff;font-size:12px}
    .toolbar .hint{font-size:12px;color:var(--muted)}
    table{width:100%;border-collapse:collapse;margin:6px 0 18px;font-size:13px}
    caption{text-align:left;font-weight:700;font-size:14px;margin:10px 0 4px;color:var(--text)}
    th,td{border:1px solid var(--border);padding:7px 9px;vertical-align:top;text-align:left}
    thead th{background:var(--panel);position:sticky;top:0;font-size:12px}
    tbody tr:nth-child(even){background:#fafbfc}
    td.name{font-family:"SFMono-Regular",Consolas,monospace;font-weight:600;color:#0f172a;white-space:nowrap}
    td.src{white-space:nowrap}
    .srcpill{display:inline-flex;gap:5px;align-items:center;background:var(--chip);color:#4338ca;
      border-radius:999px;padding:1px 9px;font-size:11px;font-weight:600}
    .srcpill.own{background:#ecfdf5;color:#047857}
    .tag-over{font-size:10px;font-weight:700;color:#b45309;background:#fef3c7;border-radius:4px;padding:0 5px;margin-left:4px}
    .empty{color:var(--muted);font-style:italic;padding:4px 0}
    code{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:0 4px;font-size:12px}
    @media(max-width:820px){#sidebar{display:none}#content{padding:18px}}
    """

    js = """
    const PAYLOAD = __PAYLOAD__;
    const NAV = PAYLOAD.nav, DATA = PAYLOAD.data, LABELS = PAYLOAD.labels;

    function el(tag, attrs, htmlContent){
      const e=document.createElement(tag);
      if(typeof attrs === 'string'){
        if(attrs) e.className = attrs;
      } else if(attrs){
        for(const k in attrs) e.setAttribute(k, attrs[k]);
      }
      if(htmlContent!==undefined) e.innerHTML=htmlContent;
      return e;
    }

    // ---- sidebar ----
    function buildSidebar(){
      const sb=document.getElementById('sidebar-nav');
      NAV.forEach(g=>{
        const grp=el('div','nav-group');
        grp.appendChild(el('div','gtitle', g.family));
        g.items.forEach(it=>{
          const row=el('div','nav-item');
          row.setAttribute('data-name', it.name);
          row.appendChild(el('span','nm', it.display));
          row.appendChild(el('span','cnt',
            'P<b>'+it.p+'</b> · E<b>'+it.e+'</b> · M<b>'+it.m+'</b>'));
          row.addEventListener('click', ()=>goTo(it.name, true));
          grp.appendChild(row);
        });
        sb.appendChild(grp);
      });
    }

    function setActive(name){
      document.querySelectorAll('.nav-item').forEach(r=>{
        r.classList.toggle('active', r.getAttribute('data-name')===name);
      });
    }

    function goTo(name, resetSearch){
      const sec=document.getElementById(name);
      if(!sec) return;
      mountTables(name);
      location.hash='#'+name;
      sec.scrollIntoView({behavior:'smooth'});
      setActive(name);
      if(resetSearch){
        document.getElementById('search').value='';
        applySearch('');
      }
    }

    function applySearch(q){
      q=q.trim().toLowerCase();
      let first=null;
      document.querySelectorAll('.nav-item').forEach(row=>{
        const nm=row.getAttribute('data-name').toLowerCase();
        const disp=row.querySelector('.nm').textContent.toLowerCase();
        const show=(!q || nm.includes(q) || disp.includes(q));
        row.style.display=show?'':'none';
        if(show && !first) first=row.getAttribute('data-name');
      });
      document.querySelectorAll('.nav-group').forEach(g=>{
        const any=[...g.querySelectorAll('.nav-item')].some(r=>r.style.display!=='none');
        g.style.display=any?'':'none';
      });
      return first;
    }

    // ---- breadcrumb ----
    function chainHtml(chains, self){
      return chains.map(ch=>{
        // ch is root->leaf; reverse to leaf->root
        const rev=[...ch].reverse();
        return '<span class="chain">'+rev.map((n,i)=>{
          if(n===self) return '<span class="me">'+self+'</span>';
          return '<a class="src" href="#'+n+'">'+esc(LABELS[n]||n)+'</a>';
        }).join('<span class="arrow">→</span>')+'</span>';
      }).join('');
    }
    function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
    function jump(n){ location.hash='#'+n;
      const s=document.getElementById(n); if(s) s.scrollIntoView({behavior:'smooth'}); }

    // ---- table builder ----
    function srcCell(src, self){
      if(src===self) return '<span class="srcpill own">自身</span>';
      return '<a class="srcpill" href="#'+src+'">'+esc(LABELS[src]||src)+'</a>';
    }
    function tableHtml(kind, rows, self, title){
      if(!rows.length) return '<div class="empty">（无'+kind+'／全部继承自祖先）</div>';
      let head='';
      if(kind==='属性') head='<th>属性名</th><th>类型</th><th>说明</th><th>默认值</th><th>来源</th>';
      else head='<th>'+(kind==='事件'?'事件名':'方法名')+'</th><th>参数</th><th>说明</th><th>来源</th>';
      let body='';
      rows.forEach(r=>{
        const over=r.overridden?'<span class="tag-over">重写</span>':'';
        const nameCell='<td class="name">'+r.name+over+'</td>';
        if(kind==='属性'){
          body+='<tr data-src="'+r.source+'">'+nameCell+'<td>'+r.type+'</td><td>'+r.desc+'</td><td><code>'+r.default+'</code></td><td class="src">'+srcCell(r.source,self)+'</td></tr>';
        }else{
          body+='<tr data-src="'+r.source+'">'+nameCell+'<td><code>'+r.params+'</code></td><td>'+r.desc+'</td><td class="src">'+srcCell(r.source,self)+'</td></tr>';
        }
      });
      return '<table><caption>'+title+'</caption><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table>';
    }

    function sectionHtml(c){
      const self=c.name;
      const sec=el('section','comp');
      sec.id=self;
      let h='<h2>'+c.display+' <span class="badge">'+self+'</span> '+
            '<span class="badge">'+c.category+'</span> '+
            '<a class="orig" href="'+c.url+'" target="_blank" rel="noopener">原站 ↗</a></h2>';
      sec.appendChild(el('div','',h));
      if(c.desc) sec.appendChild(el('div','desc', c.desc));
      // chains
      const chainsWrap=el('div','chains', chainHtml(c.chains, self));
      sec.appendChild(el('div','', '<div style="font-size:12px;color:var(--muted);margin-bottom:2px">继承链（点击祖先可跳转）：</div>'));
      sec.appendChild(chainsWrap);
      if(c.depends && c.depends.length)
        sec.appendChild(el('div','deps','依赖组件：'+c.depends.map(d=>'<a href="#'+d+'">'+d+'</a>').join('、')));
      // toolbar (always present so the filter dropdown works without mounting tables)
      const sources=[...new Set([...c.properties,...c.events,...c.methods].map(r=>r.source))];
      let opts='<option value="__all__">全部来源</option><option value="__own__">仅自身新增</option>';
      sources.forEach(s=>{ opts+='<option value="'+s+'">'+(s===self?'自身':(LABELS[s]||s))+'</option>'; });
      const counts='属性 '+c.counts.properties+' · 事件 '+c.counts.events+' · 方法 '+c.counts.methods;
      sec.appendChild(el('div','toolbar',
        '<span class="hint">'+counts+'</span>'+
        '<label class="hint">按来源筛选：</label><select class="srcfilter" data-self="'+self+'">'+opts+'</select>'));
      // lazy tables container (mounted on demand / when near viewport)
      const tc=el('div','tables'); tc.setAttribute('data-loaded','0'); tc.setAttribute('data-name',self);
      sec.appendChild(tc);
      return sec;
    }

    // ---- lazy mount / unmount of a section's heavy tables ----
    function mountTables(self){
      const sec=document.getElementById(self);
      if(!sec) return;
      const tc=sec.querySelector('.tables');
      if(!tc || tc.getAttribute('data-loaded')==='1') return;
      const c=DATA[self];
      tc.appendChild(el('div','', tableHtml('属性',c.properties,self,'属性（Properties）')));
      tc.appendChild(el('div','', tableHtml('事件',c.events,self,'事件（Events）')));
      tc.appendChild(el('div','', tableHtml('方法',c.methods,self,'方法（Methods）')));
      tc.style.minHeight='';
      tc.setAttribute('data-loaded','1');
    }
    function unmountTables(self){
      const sec=document.getElementById(self);
      if(!sec) return;
      const tc=sec.querySelector('.tables');
      if(!tc || tc.getAttribute('data-loaded')!=='1') return;
      // preserve height to avoid scroll jump, then drop the heavy DOM
      tc.style.minHeight=tc.offsetHeight+'px';
      tc.innerHTML='';
      tc.setAttribute('data-loaded','0');
    }

    function filterSec(self, val){
      const sec=document.getElementById(self);
      sec.querySelectorAll('tbody tr').forEach(tr=>{
        const src=tr.getAttribute('data-src');
        let show=true;
        if(val==='__all__') show=true;
        else if(val==='__own__') show=(src===self);
        else show=(src===val);
        tr.style.display=show?'':'none';
      });
    }

    function renderAll(){
      const main=document.getElementById('content');
      const intro=el('header','top',
        '<h1>EasyUI 扁平化 API 文档</h1>'+
        '<p>基于国内站点 <a href="https://www.jeasyui.cn/" target="_blank" rel="noopener">jeasyui.cn</a> 重构。'+
        '官方文档按「扩展自 X」层层嵌套，查 combogrid 的方法要跳 combo → validatebox 与 datagrid → panel，极不友好。</p>'+
        '<p>本站点已将每个组件<b>全部可用的属性 / 事件 / 方法扁平化合并到一张表</b>，并用「来源」列标注该成员实际定义在哪个祖先组件；带 <span class="pill over">重写</span> 标记表示在当前组件中被重写。</p>'+
        '<div class="legend">'+
        '<span><span class="pill own">自身</span> 当前组件新增/重写</span>'+
        '<span><span class="pill src">祖先名</span> 继承自该祖先</span>'+
        '<span><span class="pill over">重写</span> 覆盖了祖先同名成员</span>'+
        '</div>');
      main.appendChild(intro);
      Object.keys(DATA).forEach(n=>{ main.appendChild(sectionHtml(DATA[n])); });
    }

    document.addEventListener('DOMContentLoaded',()=>{
      buildSidebar();
      renderAll();
      const secIds=[...document.querySelectorAll('section.comp')].map(s=>s.id);
      // initial: mount the first couple of sections for a good first paint
      secIds.slice(0,2).forEach(mountTables);
      const searchEl=document.getElementById('search');
      searchEl.addEventListener('input', e=>applySearch(e.target.value));
      searchEl.addEventListener('keydown', e=>{
        if(e.key==='Enter'){ const first=applySearch(e.target.value); if(first) goTo(first, true); }
      });
      // delegated "filter by source" handler for the per-section selects
      document.getElementById('content').addEventListener('change', e=>{
        const sel=e.target.closest('.srcfilter');
        if(sel){
          const self=sel.getAttribute('data-self');
          mountTables(self);
          filterSec(self, sel.value);
        }
      });
      function ensureMounted(id){ if(id && document.getElementById(id)) mountTables(id); }
      window.addEventListener('hashchange', ()=>{ const id=location.hash.slice(1); ensureMounted(id); if(id) setActive(id); });
      if(location.hash){ const id=location.hash.slice(1); const s=document.getElementById(id); if(s){ ensureMounted(id); s.scrollIntoView(); setActive(id); } }
      // scroll spy: highlight nav as you scroll the documentation
      if('IntersectionObserver' in window){
        const spy=new IntersectionObserver(entries=>{
          entries.forEach(en=>{ if(en.isIntersecting) setActive(en.target.id); });
        }, {rootMargin:'-20% 0px -70% 0px', threshold:0});
        secIds.forEach(id=>spy.observe(document.getElementById(id)));
        // lazy mount/unmount heavy tables: keep only near-viewport sections mounted
        const lazy=new IntersectionObserver(entries=>{
          entries.forEach(en=>{
            const id=en.target.id;
            if(en.isIntersecting){ mountTables(id); }
            else {
              const r=en.boundingClientRect, vh=window.innerHeight||800;
              if(r.bottom < -1500 || r.top > vh+1500) unmountTables(id);
            }
          });
        }, {root:null, rootMargin:'600px 0px', threshold:0});
        secIds.forEach(id=>lazy.observe(document.getElementById(id)));
      }
    });
    """

    page = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EasyUI 扁平化 API 文档</title>
<style>__CSS__</style>
</head>
<body>
<div id="layout">
  <aside id="sidebar">
    <h1>EasyUI 文档</h1>
    <div class="sub">扁平化 · 含全部继承成员</div>
    <input id="search" type="text" placeholder="搜索组件…" autocomplete="off">
    <div id="sidebar-nav"></div>
  </aside>
  <main id="content"></main>
</div>
<script>__JS__</script>
</body>
</html>"""

    page = page.replace("__CSS__", css).replace("__JS__", js)
    page = page.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False))

    out = f"{SITE}/index.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("Wrote", out, "size=", len(page))


if __name__ == "__main__":
    render()
