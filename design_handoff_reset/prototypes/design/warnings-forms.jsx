const { useState: useS_w, useEffect: useE_w } = React;

/* ===== Warning Toast Variations ===== */
function WarningA() {
  const [s, setS] = useS_w(38);
  useE_w(()=>{ const i=setInterval(()=>setS(x=>x>0?x-1:60),1000); return ()=>clearInterval(i); }, []);
  return (
    <div className="reset-screen" style={{ width:380, padding:0, background:'var(--card)', border:'1.5px solid var(--acc)', borderRadius:14, overflow:'hidden', boxShadow:'0 18px 50px rgba(168,127,236,.25)' }}>
      <div style={{ padding:'18px 20px 14px', display:'flex', alignItems:'center', gap:12 }}>
        <div style={{ width:38, height:38, borderRadius:10, background:'var(--acc-soft)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:20 }}>☕</div>
        <div style={{ flex:1 }}>
          <div style={{ fontSize:14, fontWeight:600, color:'var(--text)' }}>该休息了</div>
          <div style={{ fontSize:12, color:'var(--muted)', marginTop:2 }}>已专注 42 分钟，眼睛该歇歇了</div>
        </div>
        <div style={{ fontFamily:'var(--mono)', fontSize:22, fontWeight:300, color:'var(--acc2)', fontVariantNumeric:'tabular-nums' }}>{String(Math.floor(s/60)).padStart(2,'0')}:{String(s%60).padStart(2,'0')}</div>
      </div>
      <div style={{ height:3, background:'var(--line)' }}>
        <div style={{ height:'100%', width:`${(s/60)*100}%`, background:'var(--acc)', transition:'width 1s linear' }}/>
      </div>
      <div style={{ display:'flex', borderTop:'1px solid var(--line)' }}>
        <button style={{ flex:1, padding:'10px', background:'none', border:'none', borderRight:'1px solid var(--line)', fontSize:12, color:'var(--muted)', cursor:'pointer', fontFamily:'inherit' }}>再等 5 分钟</button>
        <button style={{ flex:1, padding:'10px', background:'none', border:'none', fontSize:12, fontWeight:600, color:'var(--acc2)', cursor:'pointer', fontFamily:'inherit' }}>立即开始 →</button>
      </div>
    </div>
  );
}
function WarningB() {
  const [s, setS] = useS_w(45);
  useE_w(()=>{ const i=setInterval(()=>setS(x=>x>0?x-1:60),1000); return ()=>clearInterval(i); }, []);
  const r = 22, C = 2*Math.PI*r;
  return (
    <div className="reset-screen" style={{ width:340, padding:'14px 18px', background:'var(--text)', borderRadius:99, color:'var(--bg)', display:'flex', alignItems:'center', gap:14, boxShadow:'0 12px 40px rgba(0,0,0,.18)' }}>
      <div style={{ position:'relative', width:50, height:50, flexShrink:0 }}>
        <svg viewBox="0 0 50 50" style={{ width:'100%', height:'100%', transform:'rotate(-90deg)' }}>
          <circle cx="25" cy="25" r={r} fill="none" stroke="rgba(255,255,255,.2)" strokeWidth="2.5"/>
          <circle cx="25" cy="25" r={r} fill="none" stroke="var(--acc)" strokeWidth="2.5" strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C*(1-s/60)} style={{ transition:'stroke-dashoffset 1s linear' }}/>
        </svg>
        <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', fontFamily:'var(--mono)', fontSize:13, fontWeight:600, fontVariantNumeric:'tabular-nums' }}>{s}</div>
      </div>
      <div style={{ flex:1 }}>
        <div style={{ fontSize:13, fontWeight:600 }}>该休息了 ☕</div>
        <div style={{ fontSize:11, opacity:.65, marginTop:1 }}>{s} 秒后自动开始</div>
      </div>
      <button style={{ background:'var(--acc)', border:'none', borderRadius:99, color:'#fff', padding:'7px 14px', fontSize:12, fontWeight:600, cursor:'pointer', fontFamily:'inherit' }}>开始 →</button>
    </div>
  );
}
function WarningC() {
  return (
    <div className="reset-screen" style={{ width:320, padding:'18px 20px', background:'var(--card)', border:`1px solid var(--line)`, borderLeft:'4px solid var(--acc)', borderRadius:8 }}>
      <div style={{ display:'flex', alignItems:'baseline', gap:8, marginBottom:8 }}>
        <span style={{ fontSize:11, fontWeight:700, letterSpacing:'1.5px', color:'var(--muted)', textTransform:'uppercase' }}>休息提醒</span>
        <span style={{ flex:1 }}/>
        <span style={{ fontFamily:'var(--mono)', fontSize:18, color:'var(--text)', fontWeight:300, fontVariantNumeric:'tabular-nums' }}>00:32</span>
      </div>
      <div style={{ fontSize:14, color:'var(--text)', marginBottom:4, lineHeight:1.5 }}>已专注 <strong>42 分钟</strong>，给眼睛一点时间</div>
      <div style={{ fontSize:12, color:'var(--muted)', marginBottom:14 }}>0:32 后自动开始 · 完成可得 <span style={{ color:'var(--acc2)', fontWeight:600 }}>+13 分</span></div>
      <div style={{ display:'flex', gap:6 }}>
        <button style={{ flex:1, background:'var(--acc)', color:'#fff', border:'none', borderRadius:6, padding:'9px', fontSize:12, fontWeight:600, fontFamily:'inherit', cursor:'pointer' }}>立即开始</button>
        <button style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:6, padding:'9px 12px', fontSize:12, color:'var(--muted)', fontFamily:'inherit', cursor:'pointer' }}>+5 分</button>
      </div>
    </div>
  );
}
window.WarningA = WarningA; window.WarningB = WarningB; window.WarningC = WarningC;

/* ===== Away / Return Forms ===== */
function AwayFormA() {
  const [type, setType] = useS_w('meal');
  return (
    <div className="reset-screen" style={{ width:520, padding:'28px 24px' }}>
      <Topbar/>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'22px' }}>
        <div style={{ fontSize:18, fontWeight:600, color:'var(--text)', marginBottom:4 }}>要离开了吗？</div>
        <div style={{ fontSize:12, color:'var(--muted)', marginBottom:18 }}>记录一下这段时间在做什么</div>

        <label style={{ fontSize:11, fontWeight:600, color:'var(--muted)', letterSpacing:'.5px', marginBottom:8, display:'block' }}>类型</label>
        <div style={{ display:'flex', gap:6, flexWrap:'wrap', marginBottom:16 }}>
          {SAMPLE_TYPES.filter(t=>['meal','rest','exercise','social','other'].includes(t.id)).map(t => (
            <button key={t.id} onClick={()=>setType(t.id)} style={{
              fontSize:12, fontWeight:600, padding:'6px 13px', borderRadius:99,
              border: type===t.id?'1.5px solid transparent':'1.5px solid var(--line)',
              background: type===t.id?t.color:'var(--bg)', color: type===t.id?'#1a1a1a':'var(--muted)',
              cursor:'pointer', fontFamily:'inherit',
            }}>{t.label}</button>
          ))}
        </div>

        <label style={{ fontSize:11, fontWeight:600, color:'var(--muted)', letterSpacing:'.5px', marginBottom:8, display:'block' }}>备注</label>
        <input placeholder="午饭 · 公司食堂" style={{ width:'100%', background:'var(--bg)', border:'1.5px solid var(--line)', borderRadius:10, padding:'11px 14px', fontSize:14, fontFamily:'inherit', marginBottom:18 }}/>

        <div style={{ display:'flex', gap:8 }}>
          <button style={{ flex:1, padding:'13px', background:'var(--bg)', border:'1.5px solid var(--line)', borderRadius:10, color:'var(--muted)', fontWeight:600, fontSize:14, fontFamily:'inherit', cursor:'pointer' }}>取消</button>
          <button style={{ flex:2, padding:'13px', background:'var(--acc)', border:'none', borderRadius:10, color:'#fff', fontWeight:600, fontSize:14, fontFamily:'inherit', cursor:'pointer' }}>离开 →</button>
        </div>
      </div>
    </div>
  );
}
function ReturnFormA() {
  return (
    <div className="reset-screen" style={{ width:520, padding:'28px 24px' }}>
      <Topbar/>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'22px' }}>
        <div style={{ fontSize:18, fontWeight:600, color:'var(--text)', marginBottom:4 }}>欢迎回来 👋</div>
        <div style={{ fontSize:12, color:'var(--muted)', marginBottom:16 }}>你刚才离开了 <strong style={{ color:'var(--text)' }}>1 小时 23 分</strong></div>

        <div style={{ background:'var(--bg)', border:'1px solid var(--line)', borderRadius:10, padding:'14px', marginBottom:16 }}>
          <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:8 }}>
            <span style={{ fontSize:11, fontWeight:600, padding:'3px 10px', borderRadius:99, background:SAMPLE_TYPES.find(t=>t.id==='meal').color, color:'#1a1a1a' }}>用餐</span>
            <span style={{ fontFamily:'var(--mono)', fontSize:11, color:'var(--muted)' }}>13:09 → 14:32</span>
          </div>
          <div style={{ fontSize:13, color:'var(--text)' }}>午饭 · 公司食堂</div>
          <button style={{ marginTop:8, background:'none', border:'none', fontSize:11, color:'var(--acc2)', textDecoration:'underline', cursor:'pointer', fontFamily:'inherit', padding:0 }}>编辑这段记录</button>
        </div>

        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:16, fontSize:12 }}>
          <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:8, padding:'10px 12px' }}>
            <div style={{ color:'var(--muted)', fontSize:10.5, marginBottom:2 }}>今日专注</div>
            <div style={{ fontFamily:'var(--mono)', fontSize:18, fontWeight:300, color:'var(--text)' }}>3<span style={{ fontSize:11, color:'var(--muted)' }}>h</span> 12<span style={{ fontSize:11, color:'var(--muted)' }}>m</span></div>
          </div>
          <div style={{ background:'var(--acc-soft)', border:'1px solid var(--acc)', borderRadius:8, padding:'10px 12px' }}>
            <div style={{ color:'var(--muted)', fontSize:10.5, marginBottom:2 }}>积分</div>
            <div style={{ fontFamily:'var(--mono)', fontSize:18, fontWeight:300, color:'var(--acc2)' }}>★ 42</div>
          </div>
        </div>

        <button style={{ width:'100%', padding:'13px', background:'var(--acc)', border:'none', borderRadius:10, color:'#fff', fontWeight:600, fontSize:14, fontFamily:'inherit', cursor:'pointer' }}>开始新一段专注 ▶</button>
      </div>
    </div>
  );
}
window.AwayFormA = AwayFormA; window.ReturnFormA = ReturnFormA;
