// dcplayer: speelt de schermbestanden van het canvas (*.dc.html) af als werkende app.
// Adres: app.html#/Scherm?sleutel=waarde. De waarden in het adres overschrijven de beginstand van het scherm.
(function () {
  const app = document.getElementById('app');
  const helmet = document.getElementById('helmet');
  const viewport = document.querySelector('meta[name=viewport]');
  const cache = {};
  let current = null;

  class DCLogic {
    constructor(p) { this.props = p || {}; this.state = {}; }
    setState(o) {
      Object.assign(this.state, typeof o === 'function' ? o(this.state) : o);
      schedule();
    }
    forceUpdate() { schedule(); }
  }
  window.DCLogic = DCLogic;

  let pending = false;
  function schedule() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => { pending = false; if (current) paint(); });
  }

  // ---------- sjabloon ----------
  function look(path, ctx) {
    path = path.trim();
    if (path === 'true') return true;
    if (path === 'false') return false;
    let v = ctx;
    for (const k of path.split('.')) { if (v == null) return undefined; v = v[k]; }
    return v;
  }
  function findClose(s, from, tag) {
    let depth = 1;
    const o = new RegExp('<' + tag + '[\\s>]|</' + tag + '>', 'g');
    o.lastIndex = from;
    let m;
    while ((m = o.exec(s))) {
      if (m[0].startsWith('</')) { depth--; if (!depth) return m.index; } else depth++;
    }
    return -1;
  }
  function render(s, ctx, reg) {
    let out = '', i = 0;
    const re = /<sc-(for|if)\b([^>]*)>/g;
    let m;
    while ((m = re.exec(s))) {
      out += subst(s.slice(i, m.index), ctx, reg);
      const tag = 'sc-' + m[1], attrs = m[2], start = m.index + m[0].length;
      const end = findClose(s, start, tag);
      const inner = s.slice(start, end);
      if (m[1] === 'for') {
        const list = look(attrs.match(/list="\{\{([^}]*)\}\}"/)[1], ctx) || [];
        const as = attrs.match(/as="([^"]*)"/)[1];
        list.forEach((it, idx) => { out += render(inner, Object.assign(Object.create(ctx), { [as]: it, $index: idx }), reg); });
      } else {
        const v = look(attrs.match(/value="\{\{([^}]*)\}\}"/)[1], ctx);
        if (v) out += render(inner, ctx, reg);
      }
      i = end + tag.length + 3;
      re.lastIndex = i;
    }
    out += subst(s.slice(i), ctx, reg);
    return out;
  }
  function esc(v) { return String(v).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); }
  function subst(s, ctx, reg) {
    return s.replace(/\{\{([^}]*)\}\}/g, (_, p) => {
      const v = look(p, ctx);
      if (typeof v === 'function') { reg.push(v); return '__h' + (reg.length - 1); }
      return v == null ? '' : esc(v);
    });
  }

  // ---------- scherm laden ----------
  async function load(name) {
    if (cache[name]) return cache[name];
    let src = window.UPK_SRC && window.UPK_SRC[name];
    if (!src) {
      const res = await fetch('bron/' + name + '.dc.html', { cache: 'no-cache' });
      if (!res.ok) throw new Error(name + ' niet gevonden');
      src = await res.text();
    }
    const xdc = src.match(/<x-dc>([\s\S]*?)<\/x-dc>/)[1];
    const hm = xdc.match(/<helmet>([\s\S]*?)<\/helmet>/);
    const body = xdc.replace(/<helmet>[\s\S]*?<\/helmet>/, '');
    const scr = (src.match(/<script type="text\/x-dc"[^>]*>([\s\S]*?)<\/script>/) || [, 'class Component extends DCLogic { renderVals() { return {}; } }'])[1];
    const Component = new Function('DCLogic', scr + '\nreturn Component;')(DCLogic);
    return (cache[name] = { name, helmet: hm ? hm[1] : '', body, Component });
  }

  function parseQuery(q) {
    const o = {};
    new URLSearchParams(q || '').forEach((v, k) => {
      try { o[k] = JSON.parse(v); } catch (e) { o[k] = v; }
    });
    return o;
  }

  async function go() {
    const h = location.hash.replace(/^#\/?/, '') || (window.UPK_START || 'GInlog');
    const [name, q] = h.split('?');
    let def;
    try { def = await load(name); } catch (e) { app.innerHTML = '<p style="padding:24px;font-family:system-ui">Scherm ' + esc(name) + ' bestaat niet.</p>'; return; }
    if (current && current.inst.componentWillUnmount) current.inst.componentWillUnmount();
    const query = parseQuery(q);
    const props = Object.assign({}, window.UPK || {}, query);
    const inst = new def.Component(props);
    Object.assign(inst.state, query);
    current = { def, inst };
    helmet.innerHTML = def.helmet;
    app.innerHTML = '';
    paint(true);
    if (inst.componentDidMount) inst.componentDidMount();
    window.scrollTo(0, 0);
  }

  function paint(fresh) {
    const { def, inst } = current;
    const reg = [];
    let html = render(def.body, inst.renderVals(), reg);
    html = html
      .replace(/\son(Click|Change|Input|Blur|PointerDown|PointerUp|PointerLeave)="__h(\d+)"/g, (_, ev, id) => ' data-on-' + ev.toLowerCase() + '="' + id + '"')
      .replace(/\son[A-Z][a-zA-Z]*=""/g, '')
      .replace(/\s(disabled|checked)="(false|)"/g, '');
    current.reg = reg;
    const tpl = document.createElement('div');
    tpl.innerHTML = html;
    if (fresh) {
      app.replaceChildren(...tpl.childNodes);
      fit();
    } else {
      morphChildren(app, tpl);
      fit();
    }
  }

  // Telefoonschermen vullen het scherm; desktopschermen schalen als geheel.
  function fit() {
    const root = app.firstElementChild;
    if (!root) return;
    const phone = /width:\s*390px/.test(root.getAttribute('style') || '');
    root.classList.add(phone ? 'dc-tel' : 'dc-desk');
    root.classList.toggle('groter', phone && (window.UPK || {}).tekst === 'groter');
    const want = phone ? 'width=device-width, initial-scale=1, viewport-fit=cover' : 'width=1280';
    if (viewport.getAttribute('content') !== want) viewport.setAttribute('content', want);
  }

  // ---------- kleine DOM-morph, zodat animaties, scroll en focus blijven staan ----------
  function morphChildren(a, b) {
    const an = Array.from(a.childNodes), bn = Array.from(b.childNodes);
    for (let i = 0; i < bn.length; i++) {
      if (i >= an.length) { a.appendChild(bn[i]); continue; }
      morph(an[i], bn[i]);
    }
    for (let i = an.length - 1; i >= bn.length; i--) a.removeChild(an[i]);
  }
  function morph(x, y) {
    if (x.nodeType !== y.nodeType || x.nodeName !== y.nodeName) { x.replaceWith(y); return; }
    if (x.nodeType === 3 || x.nodeType === 8) { if (x.nodeValue !== y.nodeValue) x.nodeValue = y.nodeValue; return; }
    if (x.nodeType !== 1) return;
    for (const at of Array.from(x.attributes)) if (!y.hasAttribute(at.name) && at.name !== 'class' ) x.removeAttribute(at.name);
    for (const at of Array.from(y.attributes)) {
      if (at.name === 'class' && x.classList.contains('dc-tel')) continue;
      if (x.getAttribute(at.name) !== at.value) x.setAttribute(at.name, at.value);
    }
    if (x.nodeName === 'INPUT' || x.nodeName === 'TEXTAREA') {
      if (document.activeElement !== x && y.hasAttribute('value')) x.value = y.getAttribute('value');
      x.checked = y.hasAttribute('checked');
      return;
    }
    morphChildren(x, y);
  }

  // ---------- gebeurtenissen ----------
  function fire(type, e) {
    if (!current) return;
    const el = e.target.closest('[data-on-' + type + ']');
    if (!el || !app.contains(el)) return false;
    const fn = current.reg[+el.getAttribute('data-on-' + type)];
    if (fn) fn(e);
    return true;
  }
  app.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (fire('click', e)) { if (a) e.preventDefault(); return; }
    if (!a) return;
    const href = a.getAttribute('href');
    const m = href.match(/^([A-Za-z0-9]+)\.dc\.html(\?[^#]*)?$/);
    if (m) { e.preventDefault(); location.hash = '#/' + m[1] + (m[2] || ''); return; }
    if (href === '#' || href === '') { e.preventDefault(); }
  });
  app.addEventListener('input', (e) => { fire('change', e) || fire('input', e); });
  app.addEventListener('change', (e) => { if (e.target.type === 'checkbox' || e.target.nodeName === 'SELECT') fire('change', e); });
  app.addEventListener('focusout', (e) => fire('blur', e));
  app.addEventListener('pointerdown', (e) => fire('pointerdown', e));
  app.addEventListener('pointerup', (e) => fire('pointerup', e));
  app.addEventListener('pointerleave', (e) => fire('pointerleave', e), true);

  window.addEventListener('hashchange', go);
  window.UPKnaar = (to) => { location.hash = '#/' + to; };
  window.UPKfit = fit;
  go();
})();
