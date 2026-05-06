/**
 * re.set — shared client helpers (no bundler; attach to window.RS).
 */
(function (global) {
  'use strict';

  var DEFAULT_TYPES = [
    { id: 'work', label: 'Work', color: '#6366F1', weight: 1 },
    { id: 'entertainment', label: 'Entertainment', color: '#EC4899', weight: 1 },
    { id: 'life', label: 'Life', color: '#10B981', weight: 1 },
  ];

  function escapeAttr(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;');
  }

  /**
   * @param {function(Array)=} cb optional callback with loaded types
   * @returns {Promise<Array>}
   */
  /** Last successful fetch from loadActivityTypes — enables ACT_COLORS(id) one-arg form */
  var _typeCache = [];

  async function loadActivityTypes(cb) {
    var out;
    try {
      var r = await fetch('/api/activity-types');
      var data = await r.json();
      out = Array.isArray(data) ? data : JSON.parse(JSON.stringify(DEFAULT_TYPES));
    } catch (e) {
      out = JSON.parse(JSON.stringify(DEFAULT_TYPES));
    }
    _typeCache = out;
    if (typeof cb === 'function') {
      try {
        cb(out);
      } catch (e2) {}
    }
    return out;
  }

  function ACT_COLORS(types, id) {
    var arr;
    var sid;
    if (id === undefined) {
      arr = _typeCache;
      sid = types;
    } else {
      arr = types || [];
      sid = id;
    }
    return (arr.find(function (t) {
      return t.id === sid;
    }) || {}).color || '#9CA3AF';
  }

  function ACT_LABEL(types, id) {
    var arr;
    var sid;
    if (id === undefined) {
      arr = _typeCache;
      sid = types;
    } else {
      arr = types || [];
      sid = id;
    }
    return (arr.find(function (t) {
      return t.id === sid;
    }) || {}).label || sid || '';
  }

  /** Unified duration formatter: "45 分钟" / "1h 30m" */
  function fmtMin(minutes, lang) {
    var n = Math.max(0, parseInt(minutes, 10) || 0);
    var zh = lang === 'zh';
    if (n < 60) return n + (zh ? ' 分钟' : ' min');
    var h = Math.floor(n / 60);
    var r = n % 60;
    return r ? h + 'h ' + r + 'm' : h + 'h';
  }

  async function saveActivityTypes(types) {
    await fetch('/api/activity-types', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(types),
    });
  }

  /**
   * Inline activity-type editor (mutates `types` array in place).
   * @param {HTMLElement} containerEl
   * @param {Array<object>} types
   * @param {function(Array):void|Promise<void>} onSave — called after every mutation
   * @param {{lang?: string, fixedIds?: string[], onAfterDelete?: function(string)}} options
   */
  function renderTypeManager(containerEl, types, onSave, options) {
    options = options || {};
    var lang = options.lang || 'zh';
    var fixedIds = new Set(options.fixedIds || ['work', 'entertainment', 'life']);
    var ph = lang === 'en' ? 'New type name…' : '新种类名称…';
    var onDel = options.onAfterDelete || function () {};

    function runSave() {
      return Promise.resolve(onSave(types));
    }

    function paint() {
      var rows = types
        .map(function (tp, i) {
          var locked = fixedIds.has(tp.id);
          return (
            '<div class="tm-row" data-i="' +
            i +
            '">' +
            '<input class="tm-color ns" type="color" value="' +
            escapeAttr(tp.color) +
            '" data-act="color" data-i="' +
            i +
            '">' +
            '<input class="tm-label" type="text" value="' +
            escapeAttr(tp.label) +
            '" data-act="label" data-i="' +
            i +
            '">' +
            '<button type="button" class="tm-del ns" data-act="del" data-i="' +
            i +
            '"' +
            (locked ? ' style="opacity:.3;pointer-events:none" title="默认分类"' : '') +
            '>×</button>' +
            '</div>'
          );
        })
        .join('');
      var tail =
        '<div class="tm-row" style="margin-top:6px;padding-top:6px;border-top:1px solid #f0f0f3">' +
        '<input class="tm-color ns" type="color" id="tm-new-color" value="#7C5CFC">' +
        '<input class="tm-label" type="text" id="tm-new-label" placeholder="' +
        escapeAttr(ph) +
        '" data-act="new-label">' +
        '<button type="button" class="tm-del ns" data-act="add" style="opacity:1;color:#7C3AED;font-size:16px;font-weight:700">+</button>' +
        '</div>';
      containerEl.innerHTML = rows + tail;

      containerEl.oninput = function (e) {
        var t = e.target;
        var act = t.dataset && t.dataset.act;
        if (act === 'color') {
          var ci = +t.dataset.i;
          types[ci].color = t.value;
          runSave();
        } else if (act === 'label') {
          var li = +t.dataset.i;
          types[li].label = t.value;
          runSave();
        }
      };

      containerEl.onclick = function (e) {
        var btn = e.target.closest('[data-act]');
        if (!btn || !containerEl.contains(btn)) return;
        var act = btn.dataset.act;
        if (act === 'del') {
          var di = +btn.dataset.i;
          var id = types[di] && types[di].id;
          if (fixedIds.has(id)) return;
          types.splice(di, 1);
          onDel(id);
          runSave().then(function () {
            paint();
          });
        } else if (act === 'add') {
          var labelEl = containerEl.querySelector('#tm-new-label');
          var colorEl = containerEl.querySelector('#tm-new-color');
          if (!labelEl) return;
          var label = labelEl.value.trim();
          if (!label) {
            labelEl.focus();
            return;
          }
          var color = colorEl ? colorEl.value : '#7C5CFC';
          var id = label
            .toLowerCase()
            .replace(/[^a-z0-9\u4e00-\u9fff]+/g, '_')
            .replace(/^_+|_+$/g, '') ||
            'c' + Date.now();
          types.push({ id: id, label: label, color: color, weight: 1 });
          labelEl.value = '';
          if (colorEl) colorEl.value = '#7C5CFC';
          runSave().then(function () {
            paint();
            setTimeout(function () {
              var e2 = containerEl.querySelector('#tm-new-label');
              if (e2) e2.focus();
            }, 50);
          });
        }
      };
    }

    paint();
  }

  var RS = {
    DEFAULT_TYPES: DEFAULT_TYPES,
    loadActivityTypes: loadActivityTypes,
    ACT_COLORS: ACT_COLORS,
    ACT_LABEL: ACT_LABEL,
    fmtMin: fmtMin,
    saveActivityTypes: saveActivityTypes,
    renderTypeManager: renderTypeManager,
  };

  global.RS = RS;
  global.loadActivityTypes = loadActivityTypes;
  global.ACT_COLORS = ACT_COLORS;
  global.ACT_LABEL = ACT_LABEL;
  global.fmtMin = fmtMin;
})(typeof window !== 'undefined' ? window : this);
