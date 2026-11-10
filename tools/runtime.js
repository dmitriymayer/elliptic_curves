import * as React from 'react';
import { createRoot } from 'react-dom/client';
const h = React.createElement;

const BOOL = new Set(['disabled','checked','selected','hidden','readonly','open','multiple','required','autofocus','novalidate','default','reversed','async','defer','loop','muted','controls','playsinline']);
const RENAME = {class:'className','for':'htmlFor',tabindex:'tabIndex',readonly:'readOnly',colspan:'colSpan',rowspan:'rowSpan',
  maxlength:'maxLength',minlength:'minLength',autocomplete:'autoComplete',spellcheck:'spellCheck',contenteditable:'contentEditable',
  autofocus:'autoFocus',novalidate:'noValidate',crossorigin:'crossOrigin',srcset:'srcSet',enterkeyhint:'enterKeyHint',inputmode:'inputMode',
  'xlink:href':'xlinkHref','xml:space':'xmlSpace',cellpadding:'cellPadding',cellspacing:'cellSpacing',datetime:'dateTime',usemap:'useMap'};
const NOWS = new Set(['table','thead','tbody','tfoot','tr','colgroup','select']);

function parseStyle(str) {
  const out = {};
  let depth = 0, cur = '', parts = [];
  for (const ch of String(str)) {
    if (ch === '(') depth++; else if (ch === ')') depth--;
    if (ch === ';' && depth === 0) { parts.push(cur); cur = ''; } else cur += ch;
  }
  parts.push(cur);
  for (const p of parts) {
    const i = p.indexOf(':'); if (i < 0) continue;
    let k = p.slice(0, i).trim(); const v = p.slice(i + 1).trim(); if (!k) continue;
    if (!k.startsWith('--')) {
      k = k.toLowerCase();
      if (k.startsWith('-ms-')) k = k.slice(1);
      k = k.replace(/^-/, '').replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      if (p.slice(0, i).trim().startsWith('-webkit-')) k = 'W' + k.slice(1);
      if (p.slice(0, i).trim().startsWith('-moz-')) k = 'M' + k.slice(1);
    }
    out[k] = v;
  }
  return out;
}

function lit(path) {
  if (path === 'true') return [true, true]; if (path === 'false') return [true, false];
  if (path === 'null') return [true, null]; if (path === 'undefined') return [true, undefined];
  if (/^-?\d+(\.\d+)?$/.test(path)) return [true, Number(path)];
  const m = /^(['"])(.*)\1$/.exec(path); if (m) return [true, m[2]];
  return [false];
}
function look(path, scope) {
  const l = lit(path); if (l[0]) return l[1];
  const seg = path.split('.');
  let v = scope[seg[0]];
  for (let i = 1; i < seg.length; i++) { if (v == null) return undefined; v = v[seg[i]]; }
  return v;
}
const str = (v) => (v == null || v === false || v === true) ? '' : String(v);
function val(x, scope) {
  if (typeof x === 'string') return x;
  if (x.h !== undefined) return look(x.h, scope);
  return x.i.map((p) => typeof p === 'string' ? p : str(look(p.h, scope))).join('');
}

function props(tag, attrs, scope, isStatic) {
  const p = {};
  for (const [name0, raw] of attrs) {
    if (name0.startsWith('hint-')) continue;
    let name = name0, v = val(raw, scope);
    const literal = typeof raw === 'string';
    const lower = name.toLowerCase();
    if (lower === 'style') { p.style = typeof v === 'string' ? parseStyle(v) : v; continue; }
    if (BOOL.has(lower) && literal) v = true;
    if (RENAME[lower]) name = RENAME[lower];
    if (tag === 'input' || tag === 'textarea' || tag === 'select') {
      if (literal && name === 'value') name = 'defaultValue';
      if (literal && name === 'checked') name = 'defaultChecked';
    }
    if (/^on[A-Z]/.test(name) && typeof v !== 'function') continue;
    p[name] = v;
  }
  return p;
}

function kids(list, scope, svg, parentTag) {
  const out = [];
  for (const n of list) {
    const r = node(n, scope, svg, parentTag);
    if (r !== null && r !== undefined) out.push(r);
  }
  return out;
}

function node(n, scope, svg, parentTag) {
  const k = n[0];
  if (k === 't') {
    const s = n[1].map((p) => typeof p === 'string' ? p : str(look(p.h, scope))).join('');
    if (!s) return null;
    if ((NOWS.has(parentTag) || (svg && parentTag !== 'text' && parentTag !== 'tspan')) && !s.trim()) return null;
    return s;
  }
  if (k === 'e') {
    if (n[4] && n.cache) return n.cache;
    const tag = n[1];
    const isSvg = svg || tag === 'svg';
    const childSvg = isSvg && tag !== 'foreignObject';
    const p = props(tag, n[2], scope, n[4]);
    const c = kids(n[3], scope, childSvg, tag);
    const el = h(tag, p, ...c);
    if (n[4]) n.cache = el;
    return el;
  }
  if (k === 'f') {
    const list = look(n[1], scope) || [];
    return Array.from(list).map((item, i) => {
      const s = Object.create(scope); s[n[2]] = item; s.$index = i;
      return h(React.Fragment, { key: i }, ...kids(n[3], s, svg, parentTag));
    });
  }
  if (k === 'i') {
    return look(n[1], scope) ? h(React.Fragment, null, ...kids(n[2], scope, svg, parentTag)) : null;
  }
  return null;
}

let TREE = [];
class DCLogic extends React.Component {
  renderVals() { return {}; }
  render() {
    const vals = this.renderVals() || {};
    return h(React.Fragment, null, ...kids(TREE, Object.create(vals), false, 'div'));
  }
}

window.DC = {
  mount(tree, factory) {
    TREE = tree;
    const Component = factory(DCLogic, React);
    const el = document.getElementById('dc-root');
    createRoot(el).render(h(Component, {}));
  },
};
