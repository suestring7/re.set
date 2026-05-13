// Theme palette for re.set — multiple options the user can pick from
window.RESET_THEMES = {
  lavender: {
    name: '薰衣草 Lavender',
    bg: '#F7F7F9',
    card: '#FFFFFF',
    acc: '#B794F4',
    acc2: '#7C3AED',
    accSoft: 'rgba(183,148,244,0.12)',
    text: '#111827',
    sub: '#374151',
    muted: '#9CA3AF',
    line: '#E5E7EB',
    nav: '#EFECF8',
    green: '#059669',
    amber: '#D97706',
    red: '#DC2626',
  },
  sage: {
    name: '苔原 Sage',
    bg: '#F4F5F0',
    card: '#FBFCF8',
    acc: '#8FB382',
    acc2: '#3F6B3A',
    accSoft: 'rgba(143,179,130,0.14)',
    text: '#1F2A1C',
    sub: '#3F4A3A',
    muted: '#8E978A',
    line: '#E2E5DB',
    nav: '#ECEFE3',
    green: '#3F6B3A',
    amber: '#B07B2A',
    red: '#A23E2C',
  },
  ink: {
    name: '墨色 Ink',
    bg: '#0F1115',
    card: '#181B22',
    acc: '#E4B363',
    acc2: '#F2C879',
    accSoft: 'rgba(228,179,99,0.14)',
    text: '#ECECEE',
    sub: '#B7B9C0',
    muted: '#7A7E88',
    line: '#262A33',
    nav: '#13161C',
    green: '#7BBE9C',
    amber: '#E4B363',
    red: '#E08872',
  },
  paper: {
    name: '纸本 Paper',
    bg: '#F5F1E8',
    card: '#FBF8F0',
    acc: '#C5705D',
    acc2: '#8C3B2C',
    accSoft: 'rgba(197,112,93,0.12)',
    text: '#1A1814',
    sub: '#3D3A33',
    muted: '#8C857A',
    line: '#E5DECC',
    nav: '#EDE5D2',
    green: '#5A7A3F',
    amber: '#A66B1F',
    red: '#8C3B2C',
  },
  cool: {
    name: '青蓝 Cool',
    bg: '#F2F5F9',
    card: '#FFFFFF',
    acc: '#6FA0D6',
    acc2: '#2A5A93',
    accSoft: 'rgba(111,160,214,0.12)',
    text: '#0F1B2A',
    sub: '#2D3D52',
    muted: '#94A3B5',
    line: '#DDE5EE',
    nav: '#E6EDF6',
    green: '#1B7B5E',
    amber: '#B27A1A',
    red: '#B33A3A',
  },
};

window.applyResetTheme = function(themeId, root) {
  const t = window.RESET_THEMES[themeId] || window.RESET_THEMES.lavender;
  const el = root || document.documentElement;
  el.style.setProperty('--bg', t.bg);
  el.style.setProperty('--card', t.card);
  el.style.setProperty('--acc', t.acc);
  el.style.setProperty('--acc2', t.acc2);
  el.style.setProperty('--acc-soft', t.accSoft);
  el.style.setProperty('--text', t.text);
  el.style.setProperty('--sub', t.sub);
  el.style.setProperty('--muted', t.muted);
  el.style.setProperty('--line', t.line);
  el.style.setProperty('--nav', t.nav);
  el.style.setProperty('--green', t.green);
  el.style.setProperty('--amber', t.amber);
  el.style.setProperty('--red', t.red);
};
