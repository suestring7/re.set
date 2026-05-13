const { useState: useS_r } = React;

/* ===== Records: Timeline (refined hero) ===== */
function RecordsTimeline() {
  // Build sample data
  const events = [
    { type:'work', start:'09:15', end:'09:58', label:'设计原型 · re.set 卡片视图', mins:43 },
    { type:'reset', start:'09:58', end:'10:01', label:'肩颈拉伸 · S2', mins:3, score:'+12' },
    { type:'work', start:'10:01', end:'10:47', label:'重构会话状态管理', mins:46 },
    { type:'reset', start:'10:47', end:'10:51', label:'眼保健操 · E1', mins:4, score:'+10' },
    { type:'meal', start:'10:51', end:'11:08', label:'喝水、看窗外', mins:17 },
    { type:'work', start:'11:08', end:'11:54', label:'API 文档', mins:46 },
    { type:'reset', start:'11:54', end:'11:58', label:'矿泉水瓶推举 · S4', mins:4, score:'+18' },
    { type:'meal', start:'11:58', end:'13:09', label:'午饭 · 公司食堂', mins:71 },
    { type:'work', start:'13:09', end:'13:49', label:'代码评审', mins:40 },
    { type:'reset', start:'13:49', end:'13:53', label:'呼吸练习 · C1', mins:4, score:'+13' },
  ];
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar score={92}/>
      <div style={{ display:'flex', alignItems:'baseline', gap:10, marginBottom:16 }}>
        <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.4px', color:'var(--muted)', textTransform:'uppercase' }}>今日时间线</div>
        <span style={{ flex:1 }}/>
        <div style={{ display:'flex', gap:0, fontSize:11, fontFamily:'var(--mono)' }}>
          {[
            ['时间线', true], ['24h', false], ['趋势', false], ['热图', false]
          ].map(([l,a],i)=>(
            <button key={i} style={{
              background: a?'var(--text)':'transparent', color: a?'var(--bg)':'var(--muted)',
              border:'1px solid var(--line)', borderRight: i===3?'1px solid var(--line)':'none',
              borderRadius: i===0?'6px 0 0 6px':i===3?'0 6px 6px 0':0,
              padding:'5px 11px', cursor:'pointer', fontFamily:'inherit', fontWeight:600,
            }}>{l}</button>
          ))}
        </div>
      </div>

      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'18px 22px' }}>
        {/* Stats strip */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, paddingBottom:16, marginBottom:16, borderBottom:'1px solid var(--line)' }}>
          {[
            ['专注', '4h 12m', 'var(--text)'],
            ['Reset', '4 次', 'var(--acc2)'],
            ['积分', '★ 92', 'var(--acc2)'],
            ['连续', '7 天', 'var(--green)'],
          ].map(([l,v,c])=>(
            <div key={l}>
              <div style={{ fontSize:10.5, color:'var(--muted)', marginBottom:3, letterSpacing:'.4px' }}>{l}</div>
              <div style={{ fontFamily:'var(--mono)', fontSize:20, fontWeight:300, color:c, fontVariantNumeric:'tabular-nums' }}>{v}</div>
            </div>
          ))}
        </div>

        {/* Timeline */}
        <div style={{ position:'relative', paddingLeft:64 }}>
          <div style={{ position:'absolute', left:54, top:6, bottom:6, width:1, background:'var(--line)' }}/>
          {events.map((e,i)=>{
            const t = SAMPLE_TYPES.find(x=>x.id===e.type) || {color:'var(--acc)', label:'?'};
            const isReset = e.type==='reset';
            return (
              <div key={i} style={{ display:'flex', alignItems:'flex-start', gap:14, padding:'7px 0', position:'relative' }}>
                <div style={{ position:'absolute', left:-64, top:8, fontFamily:'var(--mono)', fontSize:10.5, color:'var(--muted)', width:50, textAlign:'right', letterSpacing:'.3px' }}>{e.start}</div>
                <div style={{ position:'absolute', left:-15, top:11, width:9, height:9, borderRadius:'50%', background: isReset?'var(--card)':t.color, border: `1.5px solid ${isReset?'var(--acc)':t.color}` }}/>
                <div style={{ flex:1, display:'flex', alignItems:'center', gap:8, minHeight:22 }}>
                  {isReset && <span style={{ fontSize:11, color:'var(--acc2)', fontWeight:700, letterSpacing:'.5px' }}>RESET</span>}
                  <span style={{ fontSize:13, color:'var(--text)' }}>{e.label}</span>
                  <span style={{ flex:1 }}/>
                  <span style={{ fontFamily:'var(--mono)', fontSize:11, color:'var(--muted)' }}>{e.mins}m</span>
                  {e.score && <span style={{ fontFamily:'var(--mono)', fontSize:11, color:'var(--acc2)', fontWeight:600 }}>{e.score}</span>}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/* ===== Records: 24h proportional bar ===== */
function Records24h() {
  const segs = [
    { t:'work', start:9.25, end:9.97, label:'设计' },
    { t:'reset', start:9.97, end:10.02, label:'' },
    { t:'work', start:10.02, end:10.78 },
    { t:'reset', start:10.78, end:10.85 },
    { t:'meal', start:10.85, end:11.13, label:'喝水' },
    { t:'work', start:11.13, end:11.9, label:'API' },
    { t:'reset', start:11.9, end:11.97 },
    { t:'meal', start:11.97, end:13.15, label:'午饭' },
    { t:'work', start:13.15, end:13.82, label:'评审' },
    { t:'reset', start:13.82, end:13.88 },
    { t:'work', start:13.88, end:14.53 },
  ];
  const startH = 9, endH = 18;
  const range = endH - startH;
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar score={92}/>
      <div style={{ display:'flex', alignItems:'baseline', gap:10, marginBottom:16 }}>
        <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.4px', color:'var(--muted)', textTransform:'uppercase' }}>今日 · 9 时 — 18 时</div>
      </div>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'22px' }}>
        <div style={{ position:'relative', height:54, display:'flex', borderRadius:6, overflow:'hidden', background:'var(--bg)', border:'1px solid var(--line)' }}>
          {segs.map((s,i)=>{
            const t = SAMPLE_TYPES.find(x=>x.id===s.t) || {color:'var(--acc)'};
            const w = ((s.end-s.start)/range)*100;
            const left = ((s.start-startH)/range)*100;
            return (
              <div key={i} title={s.label} style={{
                position:'absolute', left:`${left}%`, width:`${w}%`,
                top:s.t==='reset'?6:0, bottom:s.t==='reset'?6:0,
                background: s.t==='reset'?'var(--acc)':t.color,
                borderRadius: s.t==='reset'?3:0,
                display:'flex', alignItems:'center', paddingLeft:6,
                fontSize:10, color:'#1a1a1a', fontWeight:600, overflow:'hidden', whiteSpace:'nowrap',
              }}>{s.label}</div>
            );
          })}
        </div>
        <div style={{ display:'flex', justifyContent:'space-between', marginTop:6, fontFamily:'var(--mono)', fontSize:10, color:'var(--muted)' }}>
          {Array.from({length: range+1}, (_,i)=> <span key={i}>{startH+i}:00</span>)}
        </div>

        {/* Stacked breakdown */}
        <div style={{ marginTop:24 }}>
          <div style={{ fontSize:10.5, fontWeight:700, color:'var(--muted)', textTransform:'uppercase', letterSpacing:'1.3px', marginBottom:10 }}>占比</div>
          <div style={{ display:'flex', borderRadius:6, overflow:'hidden', height:20, marginBottom:12 }}>
            {[
              ['work', 60, '专注 4h 12m'],
              ['meal', 18, '用餐 1h 28m'],
              ['rest', 12, '休息 50m'],
              ['exercise', 6, '运动 30m'],
              ['social', 4, '社交 15m'],
            ].map(([t, pct, label])=>{
              const ty = SAMPLE_TYPES.find(x=>x.id===t);
              return <div key={t} style={{ width:`${pct}%`, background: ty.color, display:'flex', alignItems:'center', paddingLeft:7, fontSize:10, fontWeight:600, color:'#1a1a1a' }}>{label}</div>;
            })}
          </div>
          <div style={{ display:'flex', flexWrap:'wrap', gap:'8px 16px', fontSize:11 }}>
            {SAMPLE_TYPES.filter(t=>!t.parent_id).map(t => (
              <div key={t.id} style={{ display:'flex', alignItems:'center', gap:6 }}>
                <span style={{ width:9, height:9, borderRadius:2, background:t.color }}/>
                <span style={{ color:'var(--sub)' }}>{t.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ===== Records: Trend bars (week) ===== */
function RecordsBars() {
  const days = [
    { d:'周一', focus:5.2, score:78 },
    { d:'周二', focus:4.5, score:65 },
    { d:'周三', focus:6.1, score:96 },
    { d:'周四', focus:3.8, score:52 },
    { d:'周五', focus:4.2, score:92, today:true },
    { d:'周六', focus:1.0, score:8, ghost:true },
    { d:'周日', focus:0, score:0, ghost:true },
  ];
  const maxF = 7;
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar score={92}/>
      <div style={{ display:'flex', alignItems:'baseline', gap:10, marginBottom:16 }}>
        <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.4px', color:'var(--muted)', textTransform:'uppercase' }}>本周趋势</div>
        <span style={{ flex:1 }}/>
        <span style={{ fontSize:11, color:'var(--muted)' }}>← 上周 · 下周 →</span>
      </div>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'22px' }}>
        {/* Top headline */}
        <div style={{ display:'flex', alignItems:'baseline', gap:14, marginBottom:18 }}>
          <div>
            <div style={{ fontSize:10.5, color:'var(--muted)', marginBottom:3, letterSpacing:'.5px' }}>本周专注</div>
            <div style={{ fontFamily:'var(--mono)', fontSize:32, fontWeight:300, color:'var(--text)', lineHeight:1, fontVariantNumeric:'tabular-nums' }}>23.8<span style={{ fontSize:14, color:'var(--muted)', marginLeft:3 }}>h</span></div>
          </div>
          <div style={{ marginLeft:14 }}>
            <div style={{ fontSize:10.5, color:'var(--muted)', marginBottom:3, letterSpacing:'.5px' }}>本周积分</div>
            <div style={{ fontFamily:'var(--mono)', fontSize:32, fontWeight:300, color:'var(--acc2)', lineHeight:1, fontVariantNumeric:'tabular-nums' }}>★ 391</div>
          </div>
          <div style={{ marginLeft:'auto', fontSize:11, color:'var(--green)', fontWeight:600 }}>↑ 18% 比上周</div>
        </div>

        {/* Bars */}
        <div style={{ display:'flex', alignItems:'flex-end', gap:14, height:160, padding:'0 8px', borderBottom:'1px solid var(--line)' }}>
          {days.map((day, i)=>(
            <div key={i} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:4, height:'100%' }}>
              <div style={{ flex:1, display:'flex', flexDirection:'column', justifyContent:'flex-end', width:'100%', alignItems:'center' }}>
                <div style={{ fontFamily:'var(--mono)', fontSize:10, color: day.today?'var(--acc2)':'var(--muted)', marginBottom:4, fontWeight: day.today?700:400 }}>{day.focus.toFixed(1)}h</div>
                <div style={{
                  width:'72%', height:`${(day.focus/maxF)*100}%`,
                  background: day.today?'var(--acc)' : day.ghost?'var(--line)':'var(--text)',
                  opacity: day.ghost?.5:1,
                  borderRadius:'4px 4px 0 0',
                  position:'relative',
                }}>
                  {day.score>0 && !day.ghost && (
                    <div style={{ position:'absolute', top:4, left:0, right:0, textAlign:'center', fontSize:10, color: day.today?'#fff':'rgba(255,255,255,.7)', fontFamily:'var(--mono)' }}>★{day.score}</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        <div style={{ display:'flex', gap:14, padding:'8px 8px 0' }}>
          {days.map((day,i)=>(<div key={i} style={{ flex:1, textAlign:'center', fontSize:11, fontWeight: day.today?700:400, color: day.today?'var(--acc2)':'var(--muted)' }}>{day.d}</div>))}
        </div>
      </div>
    </div>
  );
}

/* ===== Records: Heatmap ===== */
function RecordsHeatmap() {
  const data = []; // 12 weeks x 7 days
  for (let w=0; w<12; w++) for (let d=0; d<7; d++) {
    const v = (w*7+d) > 79 ? 0 : Math.floor(Math.random()*5);
    data.push({ w, d, v });
  }
  const colors = ['var(--bg)', 'rgba(168,127,236,.18)', 'rgba(168,127,236,.4)', 'rgba(168,127,236,.65)', 'var(--acc)'];
  const labels = ['一','二','三','四','五','六','日'];
  return (
    <div className="reset-screen" style={{ width:660, padding:'28px 24px' }}>
      <Topbar score={92}/>
      <div style={{ display:'flex', alignItems:'baseline', gap:10, marginBottom:16 }}>
        <div style={{ fontSize:11, fontWeight:700, letterSpacing:'1.4px', color:'var(--muted)', textTransform:'uppercase' }}>近 12 周热图</div>
        <span style={{ flex:1 }}/>
        <span style={{ fontFamily:'var(--mono)', fontSize:11, color:'var(--muted)' }}>当前 · 7 天连续</span>
      </div>
      <div style={{ background:'var(--card)', border:'1px solid var(--line)', borderRadius:12, padding:'22px' }}>
        <div style={{ display:'flex', gap:8, alignItems:'flex-start' }}>
          <div style={{ display:'flex', flexDirection:'column', gap:3, paddingTop:18 }}>
            {labels.map((l,i)=> <div key={i} style={{ height:14, fontSize:9.5, color:'var(--muted)', fontFamily:'var(--mono)' }}>{l}</div>)}
          </div>
          <div style={{ flex:1 }}>
            <div style={{ display:'flex', justifyContent:'space-between', fontSize:9, color:'var(--muted)', fontFamily:'var(--mono)', marginBottom:6, paddingLeft:4, paddingRight:4 }}>
              <span>12 周前</span><span>9 周前</span><span>6 周前</span><span>3 周前</span><span>本周</span>
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(12, 1fr)', gridTemplateRows:'repeat(7, 14px)', gap:3, gridAutoFlow:'column' }}>
              {data.map((cell,i)=>(
                <div key={i} style={{
                  background: colors[cell.v],
                  border: cell.v===0?'1px solid var(--line)':'1px solid transparent',
                  borderRadius:3,
                }}/>
              ))}
            </div>
          </div>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:10, marginTop:14, justifyContent:'flex-end', fontSize:10, color:'var(--muted)', fontFamily:'var(--mono)' }}>
          <span>少</span>
          {colors.map((c,i)=>(<div key={i} style={{ width:14, height:14, background:c, borderRadius:3, border: i===0?'1px solid var(--line)':'1px solid transparent' }}/>))}
          <span>多</span>
        </div>

        {/* Achievements */}
        <div style={{ marginTop:20, paddingTop:16, borderTop:'1px solid var(--line)' }}>
          <div style={{ fontSize:10.5, fontWeight:700, color:'var(--muted)', textTransform:'uppercase', letterSpacing:'1.3px', marginBottom:10 }}>本月里程碑</div>
          <div style={{ display:'flex', gap:10, flexWrap:'wrap' }}>
            {[
              ['🌱', '坚持一周', '7 天连续打卡'],
              ['👁', '眼明手快', '完成 30 次眺望'],
              ['💪', '小有所成', '累计 100 次 reset'],
            ].map(([i,t,s], k)=>(
              <div key={k} style={{ flex:1, minWidth:140, background:'var(--bg)', border:'1px solid var(--line)', borderRadius:10, padding:'10px 12px', display:'flex', alignItems:'center', gap:10 }}>
                <div style={{ fontSize:24 }}>{i}</div>
                <div>
                  <div style={{ fontSize:12, fontWeight:600, color:'var(--text)' }}>{t}</div>
                  <div style={{ fontSize:10.5, color:'var(--muted)', marginTop:1 }}>{s}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

window.RecordsTimeline = RecordsTimeline;
window.Records24h = Records24h;
window.RecordsBars = RecordsBars;
window.RecordsHeatmap = RecordsHeatmap;
