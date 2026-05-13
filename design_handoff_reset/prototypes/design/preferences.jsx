const { useState: useS_p } = React;

function PreferencesA() {
  const [interval, setInterval_] = useS_p(45);
  const [warning, setWarning] = useS_p(60);
  const [enabled, setEnabled] = useS_p(true);
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar/>
      <div style={{ display:'flex', alignItems:'baseline', gap:10, marginBottom:16 }}>
        <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.4px', color:'var(--muted)', textTransform:'uppercase' }}>偏好设置</div>
      </div>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'4px 22px' }}>
        {/* Section 1: Reminder */}
        <div style={{ padding:'18px 0', borderBottom:'1px solid var(--line)' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <div>
              <div style={{ fontSize:14, fontWeight:600, color:'var(--text)' }}>休息提醒</div>
              <div style={{ fontSize:12, color:'var(--muted)', marginTop:2 }}>专注一段时间后提醒你休息</div>
            </div>
            <button onClick={()=>setEnabled(!enabled)} style={{
              width:42, height:24, borderRadius:99, border:'none',
              background: enabled?'var(--acc)':'var(--line)',
              position:'relative', cursor:'pointer', transition:'all .15s',
            }}>
              <span style={{
                position:'absolute', top:2, left: enabled?20:2,
                width:20, height:20, borderRadius:'50%', background:'#fff',
                transition:'left .15s', boxShadow:'0 1px 3px rgba(0,0,0,.2)',
              }}/>
            </button>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:18, marginTop:14 }}>
            <div>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'baseline', marginBottom:6 }}>
                <span style={{ fontSize:11, color:'var(--muted)', fontWeight:600 }}>专注间隔</span>
                <span style={{ fontFamily:'var(--mono)', fontSize:13, color:'var(--text)', fontVariantNumeric:'tabular-nums' }}>{interval} 分钟</span>
              </div>
              <input type="range" min="20" max="90" step="5" value={interval} onChange={e=>setInterval_(+e.target.value)} style={{ width:'100%', accentColor:'var(--acc)' }}/>
            </div>
            <div>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'baseline', marginBottom:6 }}>
                <span style={{ fontSize:11, color:'var(--muted)', fontWeight:600 }}>预警时长</span>
                <span style={{ fontFamily:'var(--mono)', fontSize:13, color:'var(--text)', fontVariantNumeric:'tabular-nums' }}>{warning} 秒</span>
              </div>
              <input type="range" min="15" max="120" step="5" value={warning} onChange={e=>setWarning(+e.target.value)} style={{ width:'100%', accentColor:'var(--acc)' }}/>
            </div>
          </div>
        </div>

        {/* Section 2: Theme */}
        <div style={{ padding:'18px 0', borderBottom:'1px solid var(--line)' }}>
          <div style={{ fontSize:14, fontWeight:600, color:'var(--text)', marginBottom:12 }}>外观</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:8 }}>
            {[
              ['薰衣草', '#A87FEC', '#F7F4FB'],
              ['鼠尾草', '#7BA888', '#F4F6F2'],
              ['雾蓝', '#7B9CC4', '#F2F5F8'],
              ['赭石', '#C8856B', '#F8F4F1'],
            ].map(([n,c,bg], i)=>(
              <button key={i} style={{
                background:bg, border: i===0?`2px solid ${c}`:'1px solid var(--line)',
                borderRadius:10, padding:'12px 10px', cursor:'pointer', fontFamily:'inherit', textAlign:'left',
              }}>
                <div style={{ display:'flex', gap:3, marginBottom:8 }}>
                  <div style={{ width:14, height:14, borderRadius:'50%', background:c }}/>
                  <div style={{ width:14, height:14, borderRadius:'50%', background:'#1a1a1a' }}/>
                  <div style={{ width:14, height:14, borderRadius:'50%', background:'#fff', border:'1px solid var(--line)' }}/>
                </div>
                <div style={{ fontSize:12, fontWeight:600, color:'#1a1a1a' }}>{n}</div>
              </button>
            ))}
          </div>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginTop:14 }}>
            <span style={{ fontSize:13, color:'var(--text)' }}>深色模式</span>
            <div style={{ display:'flex', gap:0, fontSize:11, fontFamily:'var(--mono)' }}>
              {['浅色','深色','跟随系统'].map((l,i)=>(
                <button key={i} style={{
                  background: i===0?'var(--text)':'var(--card)', color: i===0?'var(--bg)':'var(--muted)',
                  border:'1px solid var(--line)', borderRight: i===2?'1px solid var(--line)':'none',
                  borderRadius: i===0?'6px 0 0 6px':i===2?'0 6px 6px 0':0,
                  padding:'5px 11px', cursor:'pointer', fontFamily:'inherit', fontWeight:600,
                }}>{l}</button>
              ))}
            </div>
          </div>
        </div>

        {/* Section 3: Language */}
        <div style={{ padding:'18px 0', borderBottom:'1px solid var(--line)', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <div>
            <div style={{ fontSize:14, fontWeight:600, color:'var(--text)' }}>语言</div>
            <div style={{ fontSize:12, color:'var(--muted)', marginTop:2 }}>Language</div>
          </div>
          <div style={{ display:'flex', gap:0 }}>
            {['中文','English'].map((l,i)=>(
              <button key={l} style={{
                background: i===0?'var(--acc)':'var(--card)', color: i===0?'#fff':'var(--muted)',
                border: i===0?'none':'1px solid var(--line)',
                borderRadius: i===0?'6px 0 0 6px':'0 6px 6px 0',
                padding:'7px 14px', cursor:'pointer', fontFamily:'inherit', fontWeight:600, fontSize:12,
              }}>{l}</button>
            ))}
          </div>
        </div>

        {/* Section 4: Sound */}
        <div style={{ padding:'18px 0', borderBottom:'1px solid var(--line)' }}>
          <div style={{ fontSize:14, fontWeight:600, color:'var(--text)', marginBottom:12 }}>声音</div>
          {[
            ['提醒铃声', '清亮 ▾'],
            ['完成音效', '柔和 ▾'],
          ].map(([k,v])=>(
            <div key={k} style={{ display:'flex', justifyContent:'space-between', padding:'8px 0', alignItems:'center' }}>
              <span style={{ fontSize:13, color:'var(--sub)' }}>{k}</span>
              <button style={{ background:'var(--bg)', border:'1px solid var(--line)', borderRadius:8, padding:'5px 12px', fontSize:12, color:'var(--text)', cursor:'pointer', fontFamily:'inherit' }}>{v}</button>
            </div>
          ))}
        </div>

        {/* Section 5: Data */}
        <div style={{ padding:'18px 0' }}>
          <div style={{ fontSize:14, fontWeight:600, color:'var(--text)', marginBottom:12 }}>数据</div>
          <div style={{ display:'flex', gap:8 }}>
            <button style={{ flex:1, background:'var(--bg)', border:'1px solid var(--line)', borderRadius:8, padding:'10px', fontSize:12, color:'var(--text)', cursor:'pointer', fontFamily:'inherit' }}>导出 JSON</button>
            <button style={{ flex:1, background:'var(--bg)', border:'1px solid var(--line)', borderRadius:8, padding:'10px', fontSize:12, color:'var(--text)', cursor:'pointer', fontFamily:'inherit' }}>导出 CSV</button>
            <button style={{ flex:1, background:'var(--card)', border:'1px solid var(--red)', borderRadius:8, padding:'10px', fontSize:12, color:'var(--red)', cursor:'pointer', fontFamily:'inherit' }}>清空数据</button>
          </div>
        </div>
      </div>
    </div>
  );
}
window.PreferencesA = PreferencesA;
