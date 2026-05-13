const { useState, useEffect, useRef } = React;

/* ===== Variation A: Big numeral, refined dots ===== */
function CircuitA() {
  const [secs, setSecs] = useState(18);
  useEffect(() => { const i = setInterval(()=> setSecs(s => s>0?s-1:30), 1000); return ()=>clearInterval(i); }, []);
  const ex = SAMPLE_EX[6]; // T1
  const Icon = getExIcon(ex);
  const dots = [true, false, false]; // sets done state
  const fmt = s => `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar/>
      <ProgressBar/>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'20px 24px' }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:14 }}>
          <button style={{ background:'none', border:'none', color:'var(--muted)', fontSize:12, cursor:'pointer', textDecoration:'underline', fontFamily:'inherit' }}>← 返回</button>
          <div style={{ display:'flex', alignItems:'center', gap:9 }}>
            <span style={{ width:24, height:24, color:'var(--red)' }}><Icon c="var(--red)"/></span>
            <span style={{ fontFamily:'var(--mono)', fontSize:11, fontWeight:700, color:'var(--muted)', letterSpacing:'1.4px' }}>{ex.id}</span>
            <span style={{ fontSize:17, fontWeight:700 }}>{ex.name}</span>
          </div>
        </div>
        <div style={{ height:1, background:'var(--line)', margin:'10px 0 6px' }}/>
        <div style={{ fontFamily:'var(--mono)', fontSize:88, fontWeight:200, letterSpacing:'5px', textAlign:'center', color:'var(--acc2)', padding:'24px 0 14px', lineHeight:1, fontVariantNumeric:'tabular-nums' }}>{fmt(secs)}</div>
        <div style={{ display:'flex', gap:14, justifyContent:'center', padding:'4px 0 12px' }}>
          {dots.map((d,i) => (
            <span key={i} style={{
              width: i===1?12:10, height: i===1?12:10, borderRadius:'50%',
              border: `1.5px solid ${d ? 'var(--acc)' : i===1 ? 'var(--acc)' : 'var(--line)'}`,
              background: d ? 'var(--acc)' : 'transparent',
              transform: i===1 ? 'scale(1.25)' : 'scale(1)',
            }}/>
          ))}
        </div>
        <div style={{ fontSize:12, color:'var(--muted)', textAlign:'center', fontFamily:'var(--mono)', marginBottom:8 }}>第 2 组 / 共 3 组</div>
        <div style={{ fontSize:13, color:'var(--sub)', textAlign:'center', lineHeight:1.6, marginBottom:20, padding:'0 8px' }}>{ex.description}</div>
        <button style={{
          width:'100%', padding:'14px', background:'transparent',
          border:'1.5px solid var(--line)', borderRadius:10,
          color:'var(--muted)', fontWeight:600, fontSize:14, fontFamily:'inherit',
          cursor:'pointer',
        }}>✓ 完成第 2 组</button>
      </div>
    </div>
  );
}

/* ===== Variation B: Circular progress ring ===== */
function CircuitB() {
  const [secs, setSecs] = useState(22);
  useEffect(() => { const i = setInterval(()=> setSecs(s => s>0?s-1:30), 1000); return ()=>clearInterval(i); }, []);
  const ex = SAMPLE_EX[3]; // C1 breathing
  const Icon = getExIcon(ex);
  const total = 30;
  const pct = secs / total;
  const r = 110;
  const C = 2 * Math.PI * r;
  const fmt = s => `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar/>
      <ProgressBar/>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'24px' }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:8 }}>
          <button style={{ background:'none', border:'none', color:'var(--muted)', fontSize:12, cursor:'pointer', fontFamily:'inherit' }}>← 返回</button>
          <span style={{ fontFamily:'var(--mono)', fontSize:11, color:'var(--muted)', letterSpacing:'1.4px' }}>{ex.id} · 第 1 组 / 共 1 组</span>
        </div>
        <div style={{ display:'flex', justifyContent:'center', padding:'14px 0 6px' }}>
          <div style={{ position:'relative', width:260, height:260 }}>
            <svg viewBox="0 0 260 260" style={{ width:'100%', height:'100%', transform:'rotate(-90deg)' }}>
              <circle cx="130" cy="130" r={r} fill="none" stroke="var(--line)" strokeWidth="3"/>
              <circle cx="130" cy="130" r={r} fill="none" stroke="var(--acc)" strokeWidth="6" strokeLinecap="round"
                strokeDasharray={C} strokeDashoffset={C * (1-pct)} style={{ transition:'stroke-dashoffset 1s linear' }}/>
            </svg>
            <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
              <span style={{ width:42, height:42, color:'var(--amber)' }}><Icon c="var(--amber)"/></span>
              <div style={{ fontFamily:'var(--mono)', fontSize:54, fontWeight:300, letterSpacing:'2px', color:'var(--text)', lineHeight:1, fontVariantNumeric:'tabular-nums' }}>{fmt(secs)}</div>
              <div style={{ fontSize:13, fontWeight:600, color:'var(--text)' }}>{ex.name}</div>
            </div>
          </div>
        </div>
        <div style={{ fontSize:13, color:'var(--sub)', textAlign:'center', lineHeight:1.6, padding:'14px 24px 18px' }}>{ex.description}</div>
        <button style={{
          width:'100%', padding:'14px', background:'transparent',
          border:'1.5px solid var(--line)', borderRadius:10,
          color:'var(--muted)', fontWeight:600, fontSize:14, fontFamily:'inherit',
          cursor:'pointer',
        }}>✓ 完成全部动作</button>
      </div>
    </div>
  );
}

/* ===== Variation C: Breath / pulse calmer aesthetic ===== */
function CircuitC() {
  const [secs, setSecs] = useState(15);
  const [phase, setPhase] = useState('in');
  useEffect(() => {
    const i = setInterval(()=> setSecs(s => s>0?s-1:30), 1000);
    const p = setInterval(()=> setPhase(x => x==='in'?'out':'in'), 4000);
    return ()=>{ clearInterval(i); clearInterval(p); };
  }, []);
  const ex = SAMPLE_EX[3];
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar/>
      <ProgressBar/>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'30px 24px', textAlign:'center' }}>
        <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.6px', textTransform:'uppercase', color:'var(--muted)', marginBottom:6 }}>{ex.id} · 呼吸练习</div>
        <div style={{ fontSize:18, fontWeight:600, color:'var(--text)', marginBottom:24 }}>{ex.name}</div>
        <div style={{ position:'relative', width:240, height:240, margin:'0 auto 16px' }}>
          <div style={{
            position:'absolute', inset:0,
            background:'var(--acc-soft)', borderRadius:'50%',
            transform: phase==='in' ? 'scale(1.0)' : 'scale(0.65)',
            transition:'transform 4s cubic-bezier(0.4, 0, 0.6, 1)',
          }}/>
          <div style={{
            position:'absolute', inset:30,
            background:'var(--acc)', opacity:.4, borderRadius:'50%',
            transform: phase==='in' ? 'scale(1.0)' : 'scale(0.7)',
            transition:'transform 4s cubic-bezier(0.4, 0, 0.6, 1)',
          }}/>
          <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            <div style={{ fontSize:13, color:'var(--acc2)', fontWeight:600, letterSpacing:'.5px', marginBottom:4 }}>
              {phase === 'in' ? '吸 气' : '呼 气'}
            </div>
            <div style={{ fontFamily:'var(--mono)', fontSize:42, fontWeight:300, color:'var(--text)', fontVariantNumeric:'tabular-nums' }}>
              {String(Math.floor(secs/60)).padStart(2,'0')}:{String(secs%60).padStart(2,'0')}
            </div>
          </div>
        </div>
        <div style={{ fontSize:13, color:'var(--sub)', lineHeight:1.7, marginBottom:20, padding:'0 20px' }}>跟着圆圈呼吸 · 鼻吸 4 秒，口呼 4 秒</div>
        <button style={{
          width:'100%', padding:'14px', background:'transparent',
          border:'1.5px solid var(--acc)', borderRadius:10,
          color:'var(--acc2)', fontWeight:600, fontSize:14, fontFamily:'inherit',
          cursor:'pointer',
        }}>✓ 完成</button>
      </div>
    </div>
  );
}

window.CircuitA = CircuitA;
window.CircuitB = CircuitB;
window.CircuitC = CircuitC;
