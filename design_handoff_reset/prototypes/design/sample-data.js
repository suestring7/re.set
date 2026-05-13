// Sample exercise + activity data for design previews
window.SAMPLE_EX = [
  { id:'S1', name:'颈侧拉伸', name_en:'Neck Side Stretch', category:'stretch', sets:2, duration_per_set:15, score:1, description:'右手轻放左耳上方，头缓慢向右侧倾斜，感受左侧拉伸。左右各 15 秒' },
  { id:'S4', name:'门框开胸', name_en:'Doorway Chest Stretch', category:'stretch', sets:2, duration_per_set:20, score:2, description:'手肘 90° 撑门框两侧，身体前倾，感受胸肌拉开' },
  { id:'S8', name:'坐姿翘腿髋拉伸', name_en:'Seated Figure-4', category:'stretch', sets:2, duration_per_set:20, score:2, description:'一脚脚踝放另一膝盖上，上身前倾' },
  { id:'C1', name:'坐姿腹式呼吸', name_en:'Diaphragmatic Breathing', category:'core', sets:1, duration_per_set:80, score:3, description:'双手放腹部，鼻吸 4 秒腹部隆起，口呼 6 秒收腹' },
  { id:'C4', name:'坐姿斜向抬膝', name_en:'Oblique Knee Lift', category:'core', sets:2, duration_per_set:30, score:4, description:'坐直，右膝抬向左肘方向，交替进行' },
  { id:'C6', name:'坐姿自行车', name_en:'Bicycle Crunch', category:'core', sets:2, duration_per_set:30, score:4, description:'微后倾，双脚离地，对侧肘膝交替碰触' },
  { id:'T1', name:'扶桌深蹲', name_en:'Desk Squat', category:'strength', sets:3, duration_per_set:30, score:5, description:'双手轻扶桌边，慢蹲慢起' },
  { id:'T9', name:'爬楼梯', name_en:'Stair Climb', category:'strength', sets:1, duration_per_set:180, score:6, description:'出门正常速度上楼，缓慢下楼，3–5 层' },
  { id:'B1', name:'坐姿肩上推举', name_en:'Shoulder Press', category:'strength', subcategory:'bottle', sets:3, duration_per_set:25, score:5, description:'坐直，双手各握一重物，从肩部两侧向上推举' },
];

window.SAMPLE_TYPES = [
  { id:'work', label:'工作', color:'#b1dd8c', weight:1.0 },
  { id:'entertainment', label:'娱乐', color:'#f9d3e0', weight:0.1 },
  { id:'life', label:'生活', color:'#caf0fe', weight:1.0 },
  { id:'self_improvement', label:'自我提升', color:'#d9cafe', weight:2.0 },
  { id:'restroom', label:'洗手间', color:'#B794F4', weight:0, parent_id:'life' },
];

window.SAMPLE_CHECKINS = [
  { time:'09:12', exercise:{id:'S1',name:'颈侧拉伸',name_en:'Neck Stretch',category:'stretch',sets:2,duration_per_set:15}, work_content:'回邮件，整理周报', focus_minutes:42, activity_type:'work', score:9 },
  { time:'09:48', event_type:'restroom', work_content:'倒水', score:1, activity_type:'life' },
  { time:'10:35', exercise:{id:'C4',name:'坐姿斜向抬膝',name_en:'Oblique Knee Lift',category:'core',sets:2,duration_per_set:30}, work_content:'写设计稿', focus_minutes:38, activity_type:'work', score:11 },
  { time:'11:20', exercise:{id:'T1',name:'扶桌深蹲',name_en:'Desk Squat',category:'strength',sets:3,duration_per_set:30}, work_content:'读一篇论文', focus_minutes:35, activity_type:'self_improvement', score:19 },
  { time:'14:05', exercise:{id:'S4',name:'门框开胸',name_en:'Doorway Chest',category:'stretch',sets:2,duration_per_set:20}, work_content:'下午会议', focus_minutes:60, activity_type:'work', score:14 },
  { time:'15:30', exercise:{id:'C1',name:'坐姿腹式呼吸',name_en:'Breathing',category:'core',sets:1,duration_per_set:80}, work_content:'看 B 站', focus_minutes:30, activity_type:'entertainment', score:3 },
  { time:'16:40', exercise:{id:'T9',name:'爬楼梯',name_en:'Stair Climb',category:'strength',sets:1,duration_per_set:180}, work_content:'写代码', focus_minutes:45, activity_type:'work', score:15 },
];
