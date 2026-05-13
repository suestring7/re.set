const { useState: useState_ci, useEffect: useEffect_ci } = React;

/* ===== Check-in Variation A: Current refined ===== */
function CheckinA() {
  const [type, setType] = useState_ci('work');
  const [eyeDone, setEyeDone] = useState_ci(false);
  const [eyeS, setEyeS] = useState_ci(20);
  useEffect_ci(()=>{ const i = setInterval(()=> setEyeS(s => { if(s<=1){ setEyeDone(true); clearInterval(i); return 0; } return s-1; }), 1000); return ()=>clearInterval(i); }, []);
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar/>
      <ProgressBar/>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'22px 24px' }}>
        <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.6px', textTransform:'uppercase', color:'var(--muted)', marginBottom:14 }}>记录这段专注</div>

        {/* Eye row */}
        <div style={{ display:'flex', alignItems:'center', gap:10, padding:'8px 0' }}>
          <span style={{ fontSize:18 }}>👁</span>
          <span style={{ fontSize:13, color:'var(--sub)', flex:1 }}>眺望 6m 外</span>
          {!eyeDone ? (
            <>
              <span style={{ fontFamily:'var(--mono)', fontSize:18, color:'var(--text)' }}>00:{String(eyeS).padStart(2,'0')}</span>
              <button onClick={()=>setEyeDone(true)} style={{ background:'none', border:'none', fontSize:12, color:'var(--muted)', textDecoration:'underline', cursor:'pointer', fontFamily:'inherit' }}>跳过 →</button>
            </>
          ) : (
            <span style={{ fontSize:11, fontWeight:600, color:'var(--green)', background:'rgba(5,150,105,.1)', padding:'3px 10px', borderRadius:99 }}>✓ 完成</span>
          )}
        </div>
        <div style={{ height:1, background:'var(--line)', margin:'14px 0' }}/>

        {/* Activity types */}
        <div style={{ marginBottom:14 }}>
          <label style={{ fontSize:11, fontWeight:600, color:'var(--muted)', letterSpacing:'.5px', marginBottom:7, display:'block' }}>活动类型</label>
          <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
            {SAMPLE_TYPES.filter(t=>!t.parent_id).map(t => (
              <button key={t.id} onClick={()=>setType(type===t.id?null:t.id)} style={{
                fontSize:12, fontWeight:600, padding:'5px 12px', borderRadius:99,
                border: type===t.id ? '1.5px solid transparent' : '1.5px solid var(--line)',
                background: type===t.id ? t.color : 'var(--bg)',
                color: type===t.id ? '#1a1a1a' : 'var(--muted)',
                cursor:'pointer', fontFamily:'inherit',
              }}>{t.label}</button>
            ))}
          </div>
        </div>

        {/* Work content */}
        <div style={{ marginBottom:14 }}>
          <label style={{ fontSize:11, fontWeight:600, color:'var(--muted)', letterSpacing:'.5px', marginBottom:7, display:'block' }}>这段时间在做什么</label>
          <input defaultValue="重构会话状态管理" style={{
            width:'100%', background:'var(--bg)', border:'1.5px solid var(--line)',
            borderRadius:10, padding:'11px 14px', fontSize:14, fontFamily:'inherit',
          }}/>
        </div>

        {/* Focus + score */}
        <div style={{ display:'flex', alignItems:'flex-end', gap:14, marginBottom:18 }}>
          <div>
            <label style={{ fontSize:11, fontWeight:600, color:'var(--muted)', letterSpacing:'.5px', marginBottom:7, display:'block' }}>专注时长</label>
            <div style={{ display:'flex', alignItems:'center', gap:9 }}>
              <input type="number" defaultValue={42} style={{ width:72, textAlign:'center', background:'var(--bg)', border:'1.5px solid var(--line)', borderRadius:10, padding:'11px 0', fontSize:14, fontFamily:'inherit' }}/>
              <span style={{ fontSize:13, color:'var(--muted)' }}>分钟</span>
            </div>
          </div>
          <div style={{ marginLeft:'auto', background:'var(--acc-soft)', border:'1px solid var(--acc)', borderRadius:10, padding:'10px 16px', textAlign:'right' }}>
            <div style={{ fontSize:10.5, color:'var(--muted)', marginBottom:2 }}>预计获得</div>
            <div style={{ fontFamily:'var(--mono)', fontSize:20, fontWeight:600, color:'var(--acc2)' }}>+13</div>
          </div>
        </div>

        <button style={{
          width:'100%', padding:'14px', background:'var(--acc)', border:'none', borderRadius:10,
          color:'#fff', fontWeight:600, fontSize:14, fontFamily:'inherit', cursor:'pointer',
        }}>完成打卡 ✓</button>
      </div>
    </div>
  );
}

/* ===== Check-in Variation B: Conversational / playful ===== */
function CheckinB() {
  const [type, setType] = useState_ci('work');
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar/>
      <ProgressBar/>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:14, padding:'22px 24px' }}>
        {/* Header line */}
        <div style={{ display:'flex', alignItems:'baseline', gap:10, marginBottom:18 }}>
          <div style={{ fontSize:22, lineHeight:1 }}>👋</div>
          <div>
            <div style={{ fontSize:18, fontWeight:600, color:'var(--text)' }}>欢迎回来</div>
            <div style={{ fontSize:12, color:'var(--muted)', marginTop:2 }}>你刚专注了 <strong style={{ color:'var(--acc2)' }}>42 分钟</strong>，来记录一下</div>
          </div>
        </div>

        <div style={{ marginBottom:16 }}>
          <div style={{ fontSize:13, color:'var(--text)', marginBottom:10 }}>这段时间是在 <span style={{ color:'var(--muted)', fontStyle:'italic' }}>...?</span></div>
          <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
            {SAMPLE_TYPES.filter(t=>!t.parent_id).map(t => (
              <button key={t.id} onClick={()=>setType(t.id)} style={{
                fontSize:13, fontWeight:600, padding:'7px 14px', borderRadius:99,
                border: type===t.id ? `1.5px solid ${t.color}` : '1.5px solid var(--line)',
                background: type===t.id ? t.color : 'var(--card)',
                color: type===t.id ? '#1a1a1a' : 'var(--sub)',
                cursor:'pointer', fontFamily:'inherit',
                boxShadow: type===t.id ? `0 2px 8px ${t.color}55` : 'none',
                transition:'all .15s',
              }}>{t.label}</button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom:16 }}>
          <div style={{ fontSize:13, color:'var(--text)', marginBottom:8 }}>具体做了什么？</div>
          <input defaultValue="重构会话状态管理" placeholder="一句话就够..." style={{
            width:'100%', background:'transparent', border:'none',
            borderBottom:'2px solid var(--acc)',
            padding:'8px 2px', fontSize:18, fontFamily:'inherit', color:'var(--text)',
            outline:'none',
          }}/>
        </div>

        {/* Eye + duration combined */}
        <div style={{ display:'flex', gap:12, marginBottom:18, alignItems:'stretch' }}>
          <div style={{ flex:1, background:'var(--bg)', borderRadius:10, padding:'10px 14px', display:'flex', alignItems:'center', gap:10 }}>
            <span style={{ fontSize:18 }}>👁</span>
            <div style={{ flex:1 }}>
              <div style={{ fontSize:11, color:'var(--muted)' }}>眺望 6m 外</div>
              <div style={{ fontFamily:'var(--mono)', fontSize:14, color:'var(--green)', fontWeight:600 }}>✓ 已完成</div>
            </div>
          </div>
          <div style={{ flex:1, background:'var(--acc-soft)', border:'1px solid var(--acc)', borderRadius:10, padding:'10px 14px' }}>
            <div style={{ fontSize:11, color:'var(--muted)' }}>预计获得</div>
            <div style={{ fontFamily:'var(--mono)', fontSize:22, fontWeight:600, color:'var(--acc2)', lineHeight:1 }}>+13 <span style={{ fontSize:11, color:'var(--muted)' }}>分</span></div>
          </div>
        </div>

        <button style={{
          width:'100%', padding:'14px', background:'var(--acc2)', border:'none', borderRadius:10,
          color:'#fff', fontWeight:600, fontSize:14, fontFamily:'inherit', cursor:'pointer',
          letterSpacing:'.3px',
        }}>记下来 ✨</button>
      </div>
    </div>
  );
}

/* ===== Check-in Variation C: Compact card ===== */
function CheckinC() {
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar/>
      <ProgressBar/>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 200px', gap:12 }}>
        <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'18px 20px' }}>
          <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.4px', textTransform:'uppercase', color:'var(--muted)', marginBottom:14 }}>记录</div>
          <div style={{ marginBottom:14 }}>
            <div style={{ fontSize:11, color:'var(--muted)', marginBottom:6, fontWeight:600 }}>类型</div>
            <div style={{ display:'flex', gap:5, flexWrap:'wrap' }}>
              {SAMPLE_TYPES.filter(t=>!t.parent_id).map(t => (
                <span key={t.id} style={{
                  fontSize:11, fontWeight:600, padding:'4px 10px', borderRadius:99,
                  border: t.id==='work' ? '1.5px solid transparent' : '1.5px solid var(--line)',
                  background: t.id==='work' ? t.color : 'var(--bg)',
                  color: t.id==='work' ? '#1a1a1a' : 'var(--muted)',
                  cursor:'pointer',
                }}>{t.label}</span>
              ))}
            </div>
          </div>
          <input defaultValue="重构会话状态管理" style={{ width:'100%', background:'var(--bg)', border:'1.5px solid var(--line)', borderRadius:8, padding:'9px 12px', fontSize:13, fontFamily:'inherit', marginBottom:10 }}/>
          <div style={{ display:'flex', alignItems:'center', gap:8, fontSize:12, color:'var(--muted)' }}>
            <input type="number" defaultValue={42} style={{ width:60, background:'var(--bg)', border:'1.5px solid var(--line)', borderRadius:8, padding:'7px 0', textAlign:'center', fontSize:13, fontFamily:'var(--mono)' }}/>
            <span>分钟专注</span>
            <span style={{ flex:1 }}/>
            <span>👁 ✓</span>
          </div>
        </div>
        <div style={{ background:'var(--acc-soft)', border:'1.5px solid var(--acc)', borderRadius:12, padding:'18px', display:'flex', flexDirection:'column', justifyContent:'space-between' }}>
          <div>
            <div style={{ fontSize:10, color:'var(--muted)', textTransform:'uppercase', letterSpacing:'.6px', fontWeight:600 }}>预计获得</div>
            <div style={{ fontFamily:'var(--mono)', fontSize:48, fontWeight:300, color:'var(--acc2)', lineHeight:1, margin:'6px 0' }}>+13</div>
            <div style={{ fontSize:11, color:'var(--muted)' }}>今日累计 55 分</div>
          </div>
          <button style={{ background:'var(--acc2)', border:'none', borderRadius:8, color:'#fff', padding:'10px', fontSize:13, fontWeight:600, fontFamily:'inherit', cursor:'pointer' }}>打卡 ✓</button>
        </div>
      </div>
    </div>
  );
}

window.CheckinA = CheckinA;
window.CheckinB = CheckinB;
window.CheckinC = CheckinC;
