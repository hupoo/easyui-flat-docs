const fs = require('fs');
const { JSDOM } = require('jsdom');

const HTML = 'E:/documents/easyui文档/easyui-new-docs/index.html';
const html = fs.readFileSync(HTML, 'utf8');
const errors = [];

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  beforeParse(window) {
    window.HTMLElement.prototype.scrollIntoView = function () {};
    // provide a no-op IntersectionObserver so the real code path runs (jsdom lacks it)
    window.IntersectionObserver = class {
      constructor(cb) { this.cb = cb; }
      observe() {} unobserve() {} disconnect() {}
    };
  },
});
dom.window.addEventListener('error', e => errors.push('error:' + (e.message || e.error)));

setTimeout(() => {
  const d = dom.window.document;
  const navItems = d.querySelectorAll('.nav-item');
  const secs = d.querySelectorAll('section.comp');
  const inner = d.getElementById('content-inner');
  const menuBtn = d.getElementById('menuBtn');
  const backdrop = d.getElementById('backdrop');
  const cssInline = d.querySelector('style').textContent;

  // 1) search filters nav
  const search = d.getElementById('search');
  search.value = 'combo';
  search.dispatchEvent(new dom.window.Event('input'));
  const visibleAfterSearch = [...navItems].filter(r => r.style.display !== 'none').length;
  // reset
  search.value = '';
  search.dispatchEvent(new dom.window.Event('input'));

  // 2) click first nav item -> goTo mounts its tables
  const first = d.querySelector('.nav-item');
  first.dispatchEvent(new dom.window.Event('click'));
  const mountedCount = [...d.querySelectorAll('.tables')].filter(t => t.getAttribute('data-loaded') === '1').length;

  // 3) source filter: pick combogrid, set select to __own__
  const cg = d.getElementById('combogrid');
  const sel = cg ? cg.querySelector('.srcfilter') : null;
  let filterOk = false, ownVisible = 0;
  if (sel) {
    sel.value = '__own__';
    sel.dispatchEvent(new dom.window.Event('change', { bubbles: true }));
    const rows = cg.querySelectorAll('tbody tr');
    ownVisible = [...rows].filter(r => r.style.display !== 'none').length;
    filterOk = rows.length > 0 && ownVisible >= 1 && ownVisible < rows.length;
  }

  // 4) mobile drawer toggle
  let drawerOk = false;
  if (menuBtn && backdrop) {
    menuBtn.dispatchEvent(new dom.window.Event('click'));
    drawerOk = !backdrop.classList.contains('pointer-events-none');
  }

  const result = {
    navItems: navItems.length,
    sections: secs.length,
    hasContentInner: !!inner,
    hasMenuBtn: !!menuBtn,
    hasBackdrop: !!backdrop,
    cssIsTailwind: cssInline.includes('.lg\\:hidden') || cssInline.length > 8000,
    cssBytes: cssInline.length,
    visibleAfterSearchCombo: visibleAfterSearch,
    mountedTablesAfterClick: mountedCount,
    sourceFilterOwnVisible: ownVisible,
    sourceFilterOk: filterOk,
    drawerOpensOnClick: drawerOk,
    jsErrors: errors,
  };
  console.log(JSON.stringify(result, null, 2));
}, 400);
