// Sample exercise data (subset of the full library) and helpers
const SAMPLE_EX = [
  { id:'S2', name:'颈部侧拉', sets:2, duration_per_set:15, score:8, category:'stretch', subcategory:'neck', description:'坐直，右手放在左耳上方，缓缓向右下方拉伸，感受左侧颈部的伸展。' },
  { id:'S5', name:'肩部环绕', sets:2, duration_per_set:20, score:10, category:'stretch', subcategory:'shoulder', description:'双肩缓慢向后画圆，肩胛骨主动收拢，让胸口打开。' },
  { id:'S7', name:'坐姿扭转', sets:2, duration_per_set:15, score:9, category:'stretch', subcategory:'spine', description:'坐姿双手放在椅背上，缓慢向右扭转脊柱，保持然后换边。' },
  { id:'C1', name:'箱式呼吸', sets:1, duration_per_set:60, score:13, category:'core', subcategory:'breathing', description:'吸气 4 秒、屏息 4 秒、呼气 4 秒、屏息 4 秒，循环 4 次。' },
  { id:'C4', name:'平板支撑', sets:2, duration_per_set:30, score:14, category:'core', subcategory:'plank', description:'前臂支撑，身体保持一条直线，腹部收紧，目视地面。' },
  { id:'C6', name:'侧平板', sets:2, duration_per_set:20, score:12, category:'core', subcategory:'plank', description:'侧躺前臂支撑，髋部抬起，身体侧面成一条直线。' },
  { id:'T1', name:'矿泉水瓶推举', sets:3, duration_per_set:30, score:16, category:'strength', subcategory:'bottle', description:'双手各持一瓶水，从肩部向上推举，过顶后缓慢下放。' },
  { id:'T3', name:'矿泉水瓶弯举', sets:3, duration_per_set:30, score:14, category:'strength', subcategory:'bottle', description:'手心朝前持瓶，肘关节固定，缓慢弯举至胸前。' },
  { id:'E1', name:'眼保健操', sets:1, duration_per_set:90, score:10, category:'stretch', subcategory:'eye', description:'按摩攒竹、睛明、四白、太阳穴，最后远眺 6m 外。' },
];

const SAMPLE_TYPES = [
  { id:'work',     label:'专注',     color:'#A87FEC' },
  { id:'reset',    label:'Reset',   color:'#C8B4F0' },
  { id:'meal',     label:'用餐',     color:'#F4C77A' },
  { id:'rest',     label:'休息',     color:'#9DC4E8' },
  { id:'exercise', label:'运动',     color:'#7DC9A0' },
  { id:'social',   label:'社交',     color:'#E89BB5' },
  { id:'other',    label:'其他',     color:'#B8B8B8' },
];

// Iconography for exercises — flat line + accent fill
function getExIcon(ex) {
  const map = {
    S2: NeckIcon, S5: ShoulderIcon, S7: SpineIcon,
    C1: BreathIcon, C4: PlankIcon, C6: SidePlankIcon,
    T1: BottlePressIcon, T3: BottleCurlIcon,
    E1: EyeIcon,
  };
  return map[ex.id] || DefaultIcon;
}

function NeckIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <circle cx="16" cy="9" r="4"/>
    <path d="M16 13v8M11 17c2-1 8-1 10 0M16 21l-3 6M16 21l3 6"/>
    <path d="M19 9c2 1 4 3 4 5" strokeDasharray="2 2"/>
  </svg>;
}
function ShoulderIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <circle cx="16" cy="8" r="3"/>
    <path d="M16 11v9M9 15c3-2 11-2 14 0M16 20l-4 7M16 20l4 7"/>
    <path d="M7 13c-1 2 0 4 2 4M25 13c1 2 0 4-2 4" strokeDasharray="1.5 2"/>
  </svg>;
}
function SpineIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <circle cx="13" cy="9" r="3"/>
    <path d="M13 12c0 4 4 4 6 6M13 18l-2 9M19 18l2 9M9 22h12"/>
  </svg>;
}
function BreathIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <circle cx="16" cy="16" r="9" opacity=".4"/>
    <circle cx="16" cy="16" r="5"/>
    <path d="M16 7v3M16 22v3M7 16h3M22 16h3"/>
  </svg>;
}
function PlankIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <circle cx="6" cy="16" r="2.2"/>
    <path d="M8 17h17M25 13v4M5 19l-2 2M27 19l-1 2"/>
    <path d="M9 17l13-3" strokeDasharray="1 2"/>
  </svg>;
}
function SidePlankIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <circle cx="6" cy="20" r="2"/>
    <path d="M7 19l18-12M25 7v3M5 22v3M16 13l3 3"/>
  </svg>;
}
function BottlePressIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <circle cx="16" cy="9" r="3"/>
    <path d="M16 12v9M9 16h14M16 21l-3 6M16 21l3 6"/>
    <rect x="5" y="3" width="3" height="6" rx="1"/>
    <rect x="24" y="3" width="3" height="6" rx="1"/>
  </svg>;
}
function BottleCurlIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <circle cx="16" cy="9" r="3"/>
    <path d="M16 12v9M16 21l-3 6M16 21l3 6"/>
    <path d="M16 14l-6 4M16 14l6 4"/>
    <rect x="7" y="16" width="3" height="6" rx="1"/>
    <rect x="22" y="16" width="3" height="6" rx="1"/>
  </svg>;
}
function EyeIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6" strokeLinecap="round">
    <path d="M3 16c4-6 9-9 13-9s9 3 13 9c-4 6-9 9-13 9S7 22 3 16z"/>
    <circle cx="16" cy="16" r="3.5"/>
    <circle cx="16" cy="16" r="1" fill={c}/>
  </svg>;
}
function DefaultIcon({ c='currentColor' }) {
  return <svg viewBox="0 0 32 32" fill="none" stroke={c} strokeWidth="1.6">
    <circle cx="16" cy="16" r="10"/>
  </svg>;
}

window.SAMPLE_EX = SAMPLE_EX;
window.SAMPLE_TYPES = SAMPLE_TYPES;
window.getExIcon = getExIcon;
