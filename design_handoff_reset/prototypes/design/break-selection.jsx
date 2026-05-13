// Variation A: Lavender refined — current direction, polished
// Variation B: Editorial — serif headings, monospace details
// Variation C: Card-stack — large illustrated exercise tiles
const { useState, useEffect } = React;

/* ======= COMMON PRIMITIVES ======= */

const Pill = ({ children, color, soft, mono, style = {} }) => (
  <span style={{
    display:'inline-flex', alignItems:'center',
    fontSize: mono ? 10 : 10.5, fontWeight: 700,
    letterSpacing: '.06em', textTransform: 'uppercase',
    padding: '2px 8px', borderRadius: 99,
    background: soft || `${color}1a`, color: color,
    fontFamily: mono ? 'var(--mono)' : 'inherit',
    ...style,
  }}>{children}</span>
);

const ProgDots = ({ done, total, color }) => (
  <span style={{ display:'inline-flex', gap:3 }}>
    {Array.from({length: total}, (_, i) => (
      <span key={i} style={{
        width:6, height:6, borderRadius:'50%',
        background: i < done ? color : 'transparent',
        border: `1px solid ${i < done ? color : 'var(--line)'}`,
      }}/>
    ))}
  </span>
);

const Topbar = ({ score=42, theme='lavender' }) => (
  <div style={{ display:'flex', alignItems:'baseline', gap:12, marginBottom:18 }}>
    <span style={{ fontSize:32, fontWeight:700, color:'var(--text)', letterSpacing:'-.02em', fontVariantNumeric:'tabular-nums' }}>14:32</span>
    <span style={{ fontSize:12, color:'var(--muted)' }}>3月7日 周五</span>
    <span style={{ flex:1 }}/>
    <span style={{
      fontSize:12, fontWeight:600, color:'var(--acc2)',
      background:'var(--acc-soft)', border:'1px solid var(--acc)',
      borderRadius:99, padding:'3px 11px',
    }}>★ {score} 分</span>
    <button style={{ background:'none', border:'1px solid var(--line)', borderRadius:6, fontSize:11, fontWeight:700, color:'var(--muted)', padding:'3px 9px' }}>EN</button>
  </div>
);

const ProgressBar = () => (
  <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:14, fontSize:11 }}>
    <span style={{ color:'var(--muted)' }}>今日保底</span>
    <div style={{ display:'inline-flex', alignItems:'center', gap:5 }}>
      <Pill color="var(--green)">拉伸</Pill>
      <ProgDots done={2} total={3} color="var(--acc)" />
      <span style={{ color:'var(--muted)', fontSize:10 }}>2/3</span>
    </div>
    <span style={{ color:'var(--line)' }}>·</span>
    <div style={{ display:'inline-flex', alignItems:'center', gap:5 }}>
      <Pill color="var(--amber)">核心</Pill>
      <ProgDots done={1} total={3} color="var(--acc)" />
      <span style={{ color:'var(--muted)', fontSize:10 }}>1/3</span>
    </div>
    <span style={{ color:'var(--line)' }}>·</span>
    <div style={{ display:'inline-flex', alignItems:'center', gap:5 }}>
      <Pill color="var(--red)">力量</Pill>
      <ProgDots done={1} total={2} color="var(--acc)" />
      <span style={{ color:'var(--muted)', fontSize:10 }}>1/2</span>
    </div>
  </div>
);

/* ======= VARIATION A: LAVENDER REFINED (selection) ======= */
function BreakSelectionA() {
  const [sel, setSel] = useState('C4');
  const cats = { stretch:'var(--green)', core:'var(--amber)', strength:'var(--red)' };
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar />
      <ProgressBar />
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'22px 24px' }}>
        <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.6px', textTransform:'uppercase', color:'var(--muted)', marginBottom:18 }}>选择本次动作</div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:10, marginBottom:16 }}>
          {SAMPLE_EX.map(ex => {
            const Icon = getExIcon(ex);
            const c = cats[ex.category];
            const selected = sel === ex.id;
            return (
              <button key={ex.id} onClick={() => setSel(ex.id)} style={{
                textAlign:'left', cursor:'pointer',
                border:`1.5px solid ${selected ? 'var(--acc)' : 'var(--line)'}`,
                background: selected ? 'var(--acc-soft)' : 'var(--card)',
                borderRadius:10, padding:'14px 12px',
                fontFamily:'inherit', transition:'all .15s',
                display:'flex', flexDirection:'column', gap:6,
              }}>
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                  <span style={{ fontFamily:'var(--mono)', fontSize:9.5, color:'var(--muted)', fontWeight:700, letterSpacing:'1px' }}>{ex.id}</span>
                  <span style={{ width:32, height:32, color:c, opacity:.85 }}>
                    <Icon c={c}/>
                  </span>
                </div>
                <div style={{ fontSize:13.5, fontWeight:600, color:'var(--text)', lineHeight:1.3 }}>{ex.name}</div>
                <div style={{ fontSize:11, color:'var(--muted)', fontFamily:'var(--mono)' }}>{ex.sets}×{ex.duration_per_set}s</div>
                <div style={{ display:'flex', alignItems:'center', gap:6, marginTop:2 }}>
                  <Pill color={c}>{ex.category === 'stretch' ? '拉伸' : ex.category === 'core' ? '核心' : (ex.subcategory==='bottle'?'矿泉水瓶':'力量')}</Pill>
                  <span style={{ fontSize:10.5, color:'var(--muted)', fontFamily:'var(--mono)' }}>+{ex.score}</span>
                </div>
              </button>
            );
          })}
        </div>
        <div style={{ display:'flex', gap:14, alignItems:'center', fontSize:12 }}>
          <button style={{ background:'none', border:'none', color:'var(--muted)', textDecoration:'underline', textUnderlineOffset:2, cursor:'pointer', fontSize:12, fontFamily:'inherit' }}>跳过动作</button>
          <span style={{ color:'var(--line)' }}>·</span>
          <button style={{ background:'none', border:'none', color:'var(--acc2)', textDecoration:'underline', textUnderlineOffset:2, cursor:'pointer', fontSize:12, fontFamily:'inherit' }}>暂停 / 去洗手间</button>
        </div>
      </div>
    </div>
  );
}

/* ======= VARIATION B: EDITORIAL ======= */
function BreakSelectionB() {
  const [sel, setSel] = useState('S4');
  const cats = { stretch:'var(--green)', core:'var(--amber)', strength:'var(--red)' };
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px', fontFamily:'"Source Serif 4", "Iowan Old Style", Georgia, serif' }}>
      <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', marginBottom:6 }}>
        <div>
          <div style={{ fontSize:42, fontWeight:400, fontStyle:'italic', color:'var(--text)', lineHeight:1, letterSpacing:'-.02em' }}>Re.set</div>
          <div style={{ fontSize:11, color:'var(--muted)', marginTop:4, fontFamily:'var(--mono)', letterSpacing:'.5px' }}>14:32 · 周五 · 第 6 次休息</div>
        </div>
        <span style={{ fontSize:11, color:'var(--acc2)', fontFamily:'var(--mono)', letterSpacing:'.5px' }}>★ 42 分</span>
      </div>
      <div style={{ height:1, background:'var(--text)', opacity:.15, margin:'18px 0' }}/>
      <ProgressBar/>
      <div style={{ marginTop:8 }}>
        <div style={{ fontSize:13, color:'var(--muted)', marginBottom:14, fontStyle:'italic' }}>Pick something for your body —</div>
        {SAMPLE_EX.slice(0,6).map(ex => {
          const Icon = getExIcon(ex);
          const c = cats[ex.category];
          const selected = sel === ex.id;
          return (
            <button key={ex.id} onClick={()=>setSel(ex.id)} style={{
              display:'flex', alignItems:'center', gap:14, width:'100%',
              padding:'14px 6px', background:'none', cursor:'pointer',
              border:'none', borderBottom:'1px solid var(--line)',
              fontFamily:'inherit', textAlign:'left',
              opacity: selected ? 1 : .85,
            }}>
              <span style={{ width:36, height:36, color:c, flexShrink:0 }}><Icon c={c}/></span>
              <div style={{ flex:1 }}>
                <div style={{ display:'flex', alignItems:'baseline', gap:8 }}>
                  <span style={{ fontSize:18, fontWeight:500, color:'var(--text)' }}>{ex.name}</span>
                  <span style={{ fontSize:11, color:'var(--muted)', fontFamily:'var(--mono)' }}>{ex.id}</span>
                </div>
                <div style={{ fontSize:12, color:'var(--sub)', marginTop:2, fontFamily:'inherit' }}>{ex.description.slice(0, 40)}…</div>
              </div>
              <div style={{ textAlign:'right', flexShrink:0 }}>
                <div style={{ fontFamily:'var(--mono)', fontSize:13, color:'var(--text)' }}>{ex.sets}×{ex.duration_per_set}s</div>
                <div style={{ fontSize:11, color:c, fontFamily:'var(--mono)', marginTop:2 }}>+{ex.score}</div>
              </div>
              {selected && <span style={{ width:6, height:6, background:'var(--acc2)', borderRadius:'50%' }}/>}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/* ======= VARIATION C: CARD STACK with one big "recommended" ======= */
function BreakSelectionC() {
  const cats = { stretch:'var(--green)', core:'var(--amber)', strength:'var(--red)' };
  const featured = SAMPLE_EX[3]; // C1 breathing
  const FeaturedIcon = getExIcon(featured);
  const fc = cats[featured.category];
  const others = SAMPLE_EX.filter(x => x.id !== featured.id).slice(0, 4);
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar/>
      <ProgressBar/>
      <div style={{
        background:'var(--card)', border:`1.5px solid ${fc}`,
        borderRadius:14, padding:'22px 24px', position:'relative', overflow:'hidden',
        marginBottom:14,
      }}>
        <div style={{
          position:'absolute', right:-30, top:-20, width:160, height:160,
          color: fc, opacity:.10,
        }}>
          <FeaturedIcon c={fc}/>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8 }}>
          <Pill color="var(--acc2)" soft="var(--acc-soft)">为你推荐 ✨</Pill>
          <Pill color={fc}>核心</Pill>
        </div>
        <div style={{ fontSize:24, fontWeight:700, color:'var(--text)', marginBottom:6, letterSpacing:'-.01em' }}>{featured.name}</div>
        <div style={{ fontSize:13, color:'var(--sub)', lineHeight:1.55, marginBottom:14, maxWidth:'72%' }}>{featured.description}</div>
        <div style={{ display:'flex', alignItems:'center', gap:14 }}>
          <button style={{
            background:'var(--acc)', color:'#fff', border:'none',
            borderRadius:10, padding:'10px 22px', fontWeight:600, fontSize:14,
            fontFamily:'inherit', cursor:'pointer',
          }}>开始 ▶</button>
          <span style={{ fontSize:12, color:'var(--muted)', fontFamily:'var(--mono)' }}>
            {featured.sets}×{featured.duration_per_set}s · +{featured.score} 分
          </span>
        </div>
      </div>
      <div style={{ fontSize:11, color:'var(--muted)', textTransform:'uppercase', letterSpacing:'1.4px', fontWeight:600, marginBottom:8 }}>或选择其他</div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:8 }}>
        {others.map(ex => {
          const Icon = getExIcon(ex);
          const c = cats[ex.category];
          return (
            <button key={ex.id} style={{
              border:'1px solid var(--line)', background:'var(--card)',
              borderRadius:10, padding:'12px 10px', cursor:'pointer',
              fontFamily:'inherit', textAlign:'left',
            }}>
              <div style={{ width:28, height:28, color:c, marginBottom:6 }}><Icon c={c}/></div>
              <div style={{ fontSize:12, fontWeight:600, color:'var(--text)', lineHeight:1.25, marginBottom:3 }}>{ex.name}</div>
              <div style={{ fontSize:10, color:'var(--muted)', fontFamily:'var(--mono)' }}>{ex.sets}×{ex.duration_per_set}s</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

window.BreakSelectionA = BreakSelectionA;
window.BreakSelectionB = BreakSelectionB;
window.BreakSelectionC = BreakSelectionC;
