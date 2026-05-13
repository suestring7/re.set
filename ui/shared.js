/**
 * re.set — shared client helpers (no bundler; attach to window.RS).
 */
(function (global) {
  'use strict';

  var DEFAULT_TYPES = [
    { id: 'work',          label: 'Work',          color: '#6366F1', weight: 1 },
    { id: 'entertainment', label: 'Entertainment', color: '#EC4899', weight: 1 },
    { id: 'life',          label: 'Life',          color: '#10B981', weight: 1 },
    { id: 'restroom',      label: 'Restroom',      color: '#B794F4', weight: 0, parent_id: 'life' },
  ];

  function escapeAttr(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;');
  }

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
      try { cb(out); } catch (e2) {}
    }
    return out;
  }

  function ACT_COLORS(types, id) {
    var arr, sid;
    if (id === undefined) { arr = _typeCache; sid = types; }
    else { arr = types || []; sid = id; }
    return (arr.find(function (t) { return t.id === sid; }) || {}).color || '#9CA3AF';
  }

  function ACT_LABEL(types, id) {
    var arr, sid;
    if (id === undefined) { arr = _typeCache; sid = types; }
    else { arr = types || []; sid = id; }
    return (arr.find(function (t) { return t.id === sid; }) || {}).label || sid || '';
  }

  function fmtMin(minutes, lang) {
    var n = Math.max(0, parseInt(minutes, 10) || 0);
    var zh = lang === 'zh';
    if (n < 60) return n + (zh ? ' 分钟' : ' min');
    var h = Math.floor(n / 60), r = n % 60;
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
   * Render activity-type chips grouped by parent into a container element.
   * Calls onSelect(id) when a chip is clicked (id=null to deselect).
   *
   * Required CSS (add to page):
   *   .chip { ... }
   *   .chip.sel { ... }
   *   .chip-sub { font-size:11px; border-left-width:3px; }
   *   .chip-group-hdr { font-size:10px; font-weight:600; color:#9CA3AF;
   *                     text-transform:uppercase; letter-spacing:.05em;
   *                     width:100%; margin-top:6px; }
   */
  function renderGroupedChips(container, types, selId, onSelect) {
    container.innerHTML = '';
    var topLevel = types.filter(function (t) { return !t.parent_id; });
    var byParent = {};
    types.filter(function (t) { return t.parent_id; }).forEach(function (t) {
      if (!byParent[t.parent_id]) byParent[t.parent_id] = [];
      byParent[t.parent_id].push(t);
    });

    topLevel.forEach(function (parent) {
      var children = byParent[parent.id] || [];

      // Parent chip
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chip' + (selId === parent.id ? ' sel' : '');
      btn.textContent = parent.label;
      if (selId === parent.id) btn.style.background = parent.color;
      btn.onclick = function () { onSelect(selId === parent.id ? null : parent.id); };
      container.appendChild(btn);

      // Sub-type chips
      children.forEach(function (child) {
        var cBtn = document.createElement('button');
        cBtn.type = 'button';
        cBtn.className = 'chip chip-sub' + (selId === child.id ? ' sel' : '');
        cBtn.textContent = child.label;
        if (selId === child.id) {
          cBtn.style.background = child.color;
          cBtn.style.borderColor = child.color;
        } else {
          cBtn.style.borderLeftColor = parent.color;
        }
        cBtn.onclick = function () { onSelect(selId === child.id ? null : child.id); };
        container.appendChild(cBtn);
      });
    });

    // Orphaned sub-types whose parent no longer exists
    var knownIds = new Set(topLevel.map(function (t) { return t.id; }));
    types.filter(function (t) { return t.parent_id && !knownIds.has(t.parent_id); })
      .forEach(function (orphan) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'chip' + (selId === orphan.id ? ' sel' : '');
        btn.textContent = orphan.label;
        if (selId === orphan.id) btn.style.background = orphan.color;
        btn.onclick = function () { onSelect(selId === orphan.id ? null : orphan.id); };
        container.appendChild(btn);
      });
  }

  /**
   * Inline activity-type editor (mutates `types` array in place).
   * Includes a Parent dropdown for hierarchical categories.
   */
  function renderTypeManager(containerEl, types, onSave, options) {
    options = options || {};
    var lang = options.lang || 'zh';
    var fixedIds = new Set(options.fixedIds || ['work', 'entertainment', 'life']);
    var ph = lang === 'en' ? 'New type name…' : '新种类名称…';
    var noneLabel = lang === 'en' ? '— None —' : '— 无父类 —';
    var onDel = options.onAfterDelete || function () {};

    function topLevelTypes() {
      return types.filter(function (t) { return !t.parent_id; });
    }

    function parentOpts(curParentId, excludeId) {
      return '<option value="">' + noneLabel + '</option>' +
        topLevelTypes()
          .filter(function (t) { return t.id !== excludeId; })
          .map(function (t) {
            return '<option value="' + escapeAttr(t.id) + '"'
              + (t.id === curParentId ? ' selected' : '') + '>'
              + escapeAttr(t.label) + '</option>';
          }).join('');
    }

    function runSave() { return Promise.resolve(onSave(types)); }

    function paint() {
      var rows = types.map(function (tp, i) {
        var locked = fixedIds.has(tp.id);
        return '<div class="tm-row" data-i="' + i + '">'
          + '<input class="tm-color ns" type="color" value="' + escapeAttr(tp.color)
          + '" data-act="color" data-i="' + i + '">'
          + '<input class="tm-label" type="text" value="' + escapeAttr(tp.label)
          + '" data-act="label" data-i="' + i + '">'
          + '<select class="tm-parent" data-act="parent" data-i="' + i + '">'
          + parentOpts(tp.parent_id || '', tp.id) + '</select>'
          + '<button type="button" class="tm-del ns" data-act="del" data-i="' + i + '"'
          + (locked ? ' style="opacity:.3;pointer-events:none" title="默认分类"' : '')
          + '>×</button>'
          + '</div>';
      }).join('');

      var newParentOpts = '<option value="">' + noneLabel + '</option>'
        + topLevelTypes().map(function (t) {
            return '<option value="' + escapeAttr(t.id) + '">' + escapeAttr(t.label) + '</option>';
          }).join('');

      var tail = '<div class="tm-row" style="margin-top:6px;padding-top:6px;border-top:1px solid #f0f0f3">'
        + '<input class="tm-color ns" type="color" id="tm-new-color" value="#7C5CFC">'
        + '<input class="tm-label" type="text" id="tm-new-label" placeholder="' + escapeAttr(ph) + '" data-act="new-label">'
        + '<select class="tm-parent" id="tm-new-parent">' + newParentOpts + '</select>'
        + '<button type="button" class="tm-del ns" data-act="add" style="opacity:1;color:#7C3AED;font-size:16px;font-weight:700">+</button>'
        + '</div>';

      containerEl.innerHTML = rows + tail;

      containerEl.oninput = function (e) {
        var t = e.target;
        var act = t.dataset && t.dataset.act;
        if (act === 'color') {
          types[+t.dataset.i].color = t.value;
          runSave();
        } else if (act === 'label') {
          types[+t.dataset.i].label = t.value;
          runSave();
        } else if (act === 'parent') {
          types[+t.dataset.i].parent_id = t.value || null;
          runSave().then(function () { paint(); });
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
          types.forEach(function (t) { if (t.parent_id === id) t.parent_id = null; });
          types.splice(di, 1);
          onDel(id);
          runSave().then(function () { paint(); });
        } else if (act === 'add') {
          var labelEl  = containerEl.querySelector('#tm-new-label');
          var colorEl  = containerEl.querySelector('#tm-new-color');
          var parentEl = containerEl.querySelector('#tm-new-parent');
          if (!labelEl) return;
          var label = labelEl.value.trim();
          if (!label) { labelEl.focus(); return; }
          var color    = colorEl ? colorEl.value : '#7C5CFC';
          var parentId = parentEl ? (parentEl.value || null) : null;
          var id = label.toLowerCase()
            .replace(/[^a-z0-9一-鿿]+/g, '_')
            .replace(/^_+|_+$/g, '') || 'c' + Date.now();
          types.push({ id: id, label: label, color: color, weight: 1, parent_id: parentId });
          labelEl.value = '';
          if (colorEl)  colorEl.value  = '#7C5CFC';
          if (parentEl) parentEl.value = '';
          runSave().then(function () { paint(); });
        }
      };
    }

    paint();
  }

  // ── Exercise SVG icons ────────────────────────────────────────────
  var _EX_ICONS = {
    S2: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<circle cx="16" cy="9" r="4"/>'
        + '<path d="M16 13v8M11 17c2-1 8-1 10 0M16 21l-3 6M16 21l3 6"/>'
        + '<path d="M19 9c2 1 4 3 4 5" stroke-dasharray="2 2"/>'
        + '</svg>';
    },
    S5: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<circle cx="16" cy="8" r="3"/>'
        + '<path d="M16 11v9M9 15c3-2 11-2 14 0M16 20l-4 7M16 20l4 7"/>'
        + '<path d="M7 13c-1 2 0 4 2 4M25 13c1 2 0 4-2 4" stroke-dasharray="1.5 2"/>'
        + '</svg>';
    },
    S7: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<circle cx="13" cy="9" r="3"/>'
        + '<path d="M13 12c0 4 4 4 6 6M13 18l-2 9M19 18l2 9M9 22h12"/>'
        + '</svg>';
    },
    C1: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<circle cx="16" cy="16" r="9" opacity=".4"/>'
        + '<circle cx="16" cy="16" r="5"/>'
        + '<path d="M16 7v3M16 22v3M7 16h3M22 16h3"/>'
        + '</svg>';
    },
    C4: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<circle cx="6" cy="16" r="2.2"/>'
        + '<path d="M8 17h17M25 13v4M5 19l-2 2M27 19l-1 2"/>'
        + '<path d="M9 17l13-3" stroke-dasharray="1 2"/>'
        + '</svg>';
    },
    C6: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<circle cx="6" cy="20" r="2"/>'
        + '<path d="M7 19l18-12M25 7v3M5 22v3M16 13l3 3"/>'
        + '</svg>';
    },
    T1: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<circle cx="16" cy="9" r="3"/>'
        + '<path d="M16 12v9M9 16h14M16 21l-3 6M16 21l3 6"/>'
        + '<rect x="5" y="3" width="3" height="6" rx="1"/>'
        + '<rect x="24" y="3" width="3" height="6" rx="1"/>'
        + '</svg>';
    },
    T3: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<circle cx="16" cy="9" r="3"/>'
        + '<path d="M16 12v9M16 21l-3 6M16 21l3 6"/>'
        + '<path d="M16 14l-6 4M16 14l6 4"/>'
        + '<rect x="7" y="16" width="3" height="6" rx="1"/>'
        + '<rect x="22" y="16" width="3" height="6" rx="1"/>'
        + '</svg>';
    },
    E1: function (c) {
      return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6" stroke-linecap="round">'
        + '<path d="M3 16c4-6 9-9 13-9s9 3 13 9c-4 6-9 9-13 9S7 22 3 16z"/>'
        + '<circle cx="16" cy="16" r="3.5"/>'
        + '<circle cx="16" cy="16" r="1" fill="' + c + '"/>'
        + '</svg>';
    },
  };

  function _defaultIcon(c) {
    return '<svg viewBox="0 0 32 32" fill="none" stroke="' + c + '" stroke-width="1.6">'
      + '<circle cx="16" cy="16" r="10"/>'
      + '</svg>';
  }

  function getExIconSVG(id, color) {
    var c = color || 'currentColor';
    var fn = _EX_ICONS[id];
    return fn ? fn(c) : _defaultIcon(c);
  }
  // ──────────────────────────────────────────────────────────────────

  var RS = {
    DEFAULT_TYPES:        DEFAULT_TYPES,
    loadActivityTypes:    loadActivityTypes,
    ACT_COLORS:           ACT_COLORS,
    ACT_LABEL:            ACT_LABEL,
    fmtMin:               fmtMin,
    saveActivityTypes:    saveActivityTypes,
    renderTypeManager:    renderTypeManager,
    renderGroupedChips:   renderGroupedChips,
    getExIconSVG:         getExIconSVG,
  };

  global.RS              = RS;
  global.loadActivityTypes = loadActivityTypes;
  global.ACT_COLORS      = ACT_COLORS;
  global.ACT_LABEL       = ACT_LABEL;
  global.fmtMin          = fmtMin;
  global.getExIconSVG    = getExIconSVG;
})(typeof window !== 'undefined' ? window : this);
