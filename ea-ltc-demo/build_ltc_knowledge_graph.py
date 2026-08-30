# -*- coding: utf-8 -*-
# 构建 LTC（线索到回款）知识网络图 —— 百度 ECharts 力导向图
# 节点类型: LTC流程 / 阶段活动 / 业务功能 / 对象 / 行为方法
# 左侧列出顶层 LTC 流程(7 阶段)，点击右侧内容区显示相关 功能/对象/行为方法
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as G   # 复用已验证的三层架构数据（__main__ 已加守卫，导入无副作用）

OUT = r"C:\Users\hemin\WorkBuddy\2026-08-22-16-38-30\EA_三层架构"
HTML_PATH = os.path.join(OUT, "LTC知识网络图.html")

# 1) 能力字典
cap_map = {c[0]: {"domain": c[1], "objs": c[2], "combo": c[3]} for c in G.capabilities}

def parse_combo(combo):
    """把 'A.x + B.y' 解析为 [{'obj':'A','m':'x'}, ...]"""
    out = []
    for tok in combo.split("+"):
        tok = tok.strip()
        if "." in tok:
            obj, m = tok.split(".", 1)
            out.append({"obj": obj.strip(), "m": m.strip()})
    return out

# 2) 顶层 LTC 流程 = 7 个阶段（阶段活动）
STAGES = [
    {"idx": 0, "name": "阶段1 市场与商机",
     "desc": "品牌定位与营销获客：通过线索采集、评分与 MQL 移交，将市场机会转化为可跟进的销售线索。",
     "caps": ["品牌定位", "线索采集", "线索评分", "MQL移交"]},
    {"idx": 1, "name": "阶段2 销售与下单",
     "desc": "价格与促销校验后创建订单，经五步审核（价/促/库/信/合）与库存承诺 ATP 确认可履约。",
     "caps": ["价格体系", "促销规则", "购物车/下单", "订单审核", "库存承诺ATP", "信用额度(应收确认)"]},
    {"idx": 2, "name": "阶段3 计划与供应",
     "desc": "S&OP 供需平衡、MRP 运算与采购执行，保障物料齐套与交期。",
     "caps": ["S&OP协同", "MRP运算(供应计划)", "采购订单", "交期确认"]},
    {"idx": 3, "name": "阶段4 生产制造",
     "desc": "MPS 下达工单、SMT 贴片与包装入库，完成 IMEI/SN 绑定与单机追溯。",
     "caps": ["主生产计划MPS", "工单管理", "SMT执行", "包装入库"]},
    {"idx": 4, "name": "阶段5 物流交付",
     "desc": "仓店路由选择履约节点，拣配发货与签收确认，触发应收与售后期起算。",
     "caps": ["仓店路由", "拣配发货", "签收确认"]},
    {"idx": 5, "name": "阶段6 客户服务",
     "desc": "多渠道报修、维修诊断与 NPS 回访，质量问题回流研发/制造闭环。",
     "caps": ["多渠道报修", "维修诊断", "NPS回访"]},
    {"idx": 6, "name": "阶段7 财务回款",
     "desc": "应收确认、渠道回款核销与返利结算，完成现金闭环。",
     "caps": ["应收确认", "渠道回款", "返利结算"]},
]

# 名称解析（处理带括号的别名 / 合成项）
def resolve_cap(name):
    if name == "MRP运算(供应计划)":
        return cap_map.get("供应计划")
    if name == "信用额度(应收确认)":  # 合成：订单五步审核中的"信用"环节
        return {"domain": "D06 销售与渠道", "objs": ["应收单", "客户"],
                "combo": "应收单.确认应收 + 客户.信用额度管理"}
    return cap_map.get(name)

# 3) 组装能力数据（含对象行为方法）
CAPS = []
for st in STAGES:
    for cn in st["caps"]:
        info = resolve_cap(cn)
        if not info:
            # 兜底：保证不缺节点
            info = {"domain": "—", "objs": [], "combo": ""}
        CAPS.append({
            "id": "c::" + cn,
            "name": cn,
            "domain": info["domain"],
            "stage": st["idx"],
            "methods": parse_combo(info["combo"]),
        })

# 4) 统计唯一对象 / 方法
obj_set, meth_set = set(), set()
for c in CAPS:
    for mm in c["methods"]:
        obj_set.add(mm["obj"])
        meth_set.add(mm["obj"] + "." + mm["m"])

N_CAP = len(CAPS)
N_STAGE = len(STAGES)
N_OBJ = len(obj_set)
N_METH = len(meth_set)

LTC = {
    "id": "ltc",
    "name": "线索到回款 (LTC)",
    "desc": "Lead to Cash（线索到回款）是手机厂商的核心经营主线，覆盖从市场营销获客、销售下单、计划供应、"
            "生产制造、物流交付、客户服务到财务回款的全链路端到端价值流，是三层架构（对象→能力→场景）纵向贯通的最佳载体。",
}

DATA = {
    "ltc": LTC,
    "stages": STAGES,
    "caps": CAPS,
    "counts": {"cap": N_CAP, "stage": N_STAGE, "obj": N_OBJ, "meth": N_METH},
}

data_json = json.dumps(DATA, ensure_ascii=False)

# 5) HTML 模板
HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>手机厂商企业架构 · LTC（线索到回款）知识网络图</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"></script>
<script>window.echarts||document.write('<script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.5.1/echarts.min.js"><\\/script>')</script>
<style>
  :root{
    --c-ltc:#CC0000; --c-stage:#006393; --c-cap:#2E86C1; --c-obj:#1E8449; --c-meth:#D68910;
    --navy:#0a2540; --navy2:#103a5e; --ink:#1f2d3d; --muted:#6b7a8d; --line:#e3e8ef; --bg:#f5f7fa;
  }
  *{box-sizing:border-box;}
  html,body{margin:0;height:100%;font-family:"PingFang SC","Microsoft YaHei","Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);}
  /* 顶部 */
  header{background:linear-gradient(120deg,var(--navy),var(--navy2));color:#fff;padding:16px 26px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 10px rgba(0,0,0,.18);}
  header .title h1{margin:0;font-size:19px;font-weight:700;letter-spacing:.5px;}
  header .title p{margin:4px 0 0;font-size:12.5px;color:#bcd3e6;}
  .chips{display:flex;gap:10px;}
  .chip{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:7px 14px;text-align:center;min-width:84px;}
  .chip b{display:block;font-size:20px;font-weight:700;line-height:1.1;}
  .chip span{font-size:11px;color:#cfe0ee;}
  /* 主体 */
  .wrap{display:flex;height:calc(100% - 78px);}
  /* 左侧 */
  aside{width:268px;background:#fff;border-right:1px solid var(--line);padding:14px 12px;overflow:auto;}
  aside h2{font-size:13px;color:var(--muted);margin:2px 6px 10px;text-transform:none;letter-spacing:.5px;}
  .navitem{border:1px solid var(--line);border-left:4px solid transparent;border-radius:8px;padding:10px 12px;margin-bottom:8px;cursor:pointer;transition:.15s;background:#fbfcfe;}
  .navitem:hover{background:#eef4fb;border-left-color:var(--c-cap);}
  .navitem.active{background:#eaf3fb;border-left-color:var(--c-stage);box-shadow:0 1px 6px rgba(0,99,147,.15);}
  .navitem .nm{font-size:13.5px;font-weight:600;display:flex;justify-content:space-between;align-items:center;}
  .navitem .nm .badge{background:#eef1f5;color:var(--muted);font-size:11px;border-radius:20px;padding:1px 8px;}
  .navitem.active .nm .badge{background:var(--c-stage);color:#fff;}
  .navitem .ds{font-size:11px;color:var(--muted);margin-top:4px;line-height:1.5;}
  .navitem.all{forder:1px dashed var(--line);}
  /* 中间图 */
  .graphbox{flex:1;position:relative;min-width:0;}
  #graph{width:100%;height:100%;}
  .glegend{position:absolute;top:12px;left:14px;display:flex;gap:14px;background:rgba(255,255,255,.9);border:1px solid var(--line);border-radius:8px;padding:7px 12px;font-size:12px;box-shadow:0 1px 6px rgba(0,0,0,.06);}
  .glegend i{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px;vertical-align:middle;}
  .ghint{position:absolute;bottom:12px;left:14px;font-size:11px;color:var(--muted);background:rgba(255,255,255,.85);border:1px solid var(--line);border-radius:6px;padding:5px 10px;}
  /* 右侧 */
  section.detail{width:360px;background:#fff;border-left:1px solid var(--line);padding:16px 18px;overflow:auto;}
  section.detail h3{margin:0 0 6px;font-size:16px;}
  section.detail .sub{font-size:12px;color:var(--muted);margin-bottom:12px;line-height:1.6;}
  .sec{border-top:1px solid var(--line);padding:12px 0;}
  .sec h4{margin:0 0 8px;font-size:13px;display:flex;align-items:center;gap:7px;}
  .dot{width:9px;height:9px;border-radius:50%;display:inline-block;}
  .pill{display:inline-block;border:1px solid var(--line);background:#f7f9fc;border-radius:6px;padding:4px 9px;margin:0 6px 6px 0;font-size:12px;}
  .pill b{color:var(--c-cap);}
  .pill.obj b{color:var(--c-obj);}
  .pill.meth b{color:var(--c-meth);}
  .rel{font-size:11.5px;color:var(--muted);margin:2px 0 8px;line-height:1.6;}
  .empty{color:var(--muted);font-size:13px;line-height:1.8;}
  .kv{font-size:12px;color:var(--muted);margin:2px 0;}
  .kv b{color:var(--ink);}
  footer{font-size:11px;color:var(--muted);padding:6px 14px;background:var(--bg);border-top:1px solid var(--line);}
</style>
</head>
<body>
<header>
  <div class="title">
    <h1>手机厂商企业架构 · LTC（线索到回款）知识网络图</h1>
    <p>对象行为方法 → 业务能力 → 场景流程 的 SBR 三层语义网络 · 基于 TOGAF 业务架构 / 数据架构</p>
  </div>
  <div class="chips" id="chips"></div>
</header>

<div class="wrap">
  <aside>
    <h2>顶层 LTC 流程（点击查看明细）</h2>
    <div class="navitem all active" data-stage="all">
      <div class="nm">LTC 全链路总览 <span class="badge" id="badge-all"></span></div>
      <div class="ds">展示线索到回款完整知识网络（1 流程 · 7 阶段 · 27 功能 · 对象 · 行为方法）</div>
    </div>
    <div id="navlist"></div>
  </aside>

  <div class="graphbox">
    <div class="glegend">
      <span><i style="background:var(--c-ltc)"></i>LTC流程</span>
      <span><i style="background:var(--c-stage)"></i>阶段活动</span>
      <span><i style="background:var(--c-cap)"></i>业务功能</span>
      <span><i style="background:var(--c-obj)"></i>对象</span>
      <span><i style="background:var(--c-meth)"></i>行为方法</span>
    </div>
    <div id="graph"></div>
    <div class="ghint">拖拽平移 · 滚轮缩放 · 点击节点查看明细 · 点击左侧流程聚焦子网</div>
  </div>

  <section class="detail" id="detail"></section>
</div>

<footer>数据来源：手机厂商 TOGAF 业务架构（第2章）/ 数据架构（第3章）。力导向图由百度 ECharts 渲染，节点与边均来自已验证的三层架构数据。</footer>

<script>
const DATA = __DATA__;
const COL = {ltc:'#CC0000', stage:'#006393', cap:'#2E86C1', obj:'#1E8449', meth:'#D68910'};
const CATNAME = ['LTC流程','阶段活动','业务功能','对象','行为方法'];

// ---------- 构建图数据 ----------
function buildGraph(filterStage){
  const nodes = [], edges = [], seen = {};
  function addNode(id, name, cat, extra){
    if(seen[id]) return;
    seen[id]=true;
    const size = [70,46,24,16,10][cat];
    nodes.push(Object.assign({id, name, category:cat, symbolSize:size,
      label:{show: cat<=3}, itemStyle:{color:COL[['ltc','stage','cap','obj','meth'][cat]]}}, extra||{}));
  }
  // LTC
  addNode(DATA.ltc.id, DATA.ltc.name, 0, {desc:DATA.ltc.desc});
  // stages
  DATA.stages.forEach(st=>{
    if(filterStage!==null && st.idx!==filterStage) return;
    const sid='s::'+st.idx;
    addNode(sid, st.name, 1, {desc:st.desc, stidx:st.idx});
    edges.push({source:DATA.ltc.id, target:sid, kind:'包含',
      lineStyle:{color:COL.ltc, width:2, type:'solid', opacity:.85, curveness:0}});
  });
  // caps + methods + objects
  DATA.caps.forEach(c=>{
    if(filterStage!==null && c.stage!==filterStage) return;
    addNode(c.id, c.name, 2, {desc:'业务功能', domain:c.domain, stage:c.stage});
    edges.push({source:'s::'+c.stage, target:c.id, kind:'编排',
      lineStyle:{color:COL.stage, width:1.6, type:'solid', opacity:.65, curveness:0}});
    c.methods.forEach(mm=>{
      const mid='m::'+mm.obj+'::'+mm.m;
      const oid='o::'+mm.obj;
      addNode(mid, mm.obj+'.'+mm.m, 4, {desc:'行为方法', obj:mm.obj, m:mm.m});
      edges.push({source:c.id, target:mid, kind:'调用',
        lineStyle:{color:COL.cap, width:1, type:'dashed', opacity:.5, curveness:.05}});
      addNode(oid, mm.obj, 3, {desc:'业务对象'});
      edges.push({source:mid, target:oid, kind:'归属',
        lineStyle:{color:COL.obj, width:.8, type:'dotted', opacity:.35, curveness:0}});
    });
  });
  return {nodes, edges};
}

// ---------- ECharts ----------
const chart = echarts.init(document.getElementById('graph'));
function render(filterStage){
  const g = buildGraph(filterStage);
  chart.setOption({
    tooltip:{
      formatter:function(p){
        if(p.dataType!=='node') return '';
        const d=p.data;
        const cat=CATNAME[d.category];
        let extra='';
        if(d.category===2) extra='域：'+d.domain;
        else if(d.category===4) extra='对象：'+d.obj+' · 方法：'+d.m;
        else if(d.category===1||d.category===0) extra='';
        return '<b>'+cat+'</b><br/>'+d.name+(extra?('<br/><span style="color:#888;font-size:11px">'+extra+'</span>'):'');
      }
    },
    legend:{show:false},
    series:[{
      type:'graph', layout:'force', roam:true,
      categories:CATNAME.map((n,i)=>({name:n, itemStyle:{color:[COL.ltc,COL.stage,COL.cap,COL.obj,COL.meth][i]}})),
      data:g.nodes, links:g.edges,
      emphasis:{focus:'adjacency', label:{show:true}, lineStyle:{width:3}},
      lineStyle:{opacity:.5},
      force:{repulsion:170, edgeLength:[30,120], gravity:.06, friction:.5, layoutAnimation:true},
      label:{color:'#1f2d3d', fontSize:11, position:'right', formatter:'{b}',
             textBorderColor:'#fff', textBorderWidth:2},
      scaleLimit:{min:.4, max:3}
    }]
  }, true);
}

// ---------- 顶部统计 ----------
(function(){
  const c=DATA.counts;
  const chips=[['1','LTC流程'],['7','阶段活动'],['27','业务功能'],[''+c.obj,'业务对象'],[''+c.meth,'行为方法']];
  document.getElementById('chips').innerHTML = chips.map(x=>'<div class="chip"><b>'+x[0]+'</b><span>'+x[1]+'</span></div>').join('');
  document.getElementById('badge-all').textContent = c.obj+'对象 / '+c.meth+'方法';
})();

// ---------- 左侧导航 ----------
(function(){
  const list=document.getElementById('navlist');
  list.innerHTML = DATA.stages.map(st=>{
    const objN=new Set(), methN=new Set();
    st.caps.forEach(cn=>{const c=DATA.caps.find(x=>x.name===cn); (c?c.methods:[]).forEach(m=>{objN.add(m.obj);methN.add(m.obj+'.'+m.m);});});
    return '<div class="navitem" data-stage="'+st.idx+'">'+
      '<div class="nm">'+st.name+' <span class="badge">'+st.caps.length+'功能</span></div>'+
      '<div class="ds">'+st.desc.slice(0,42)+'…</div></div>';
  }).join('');
})();

// ---------- 右侧明细 ----------
function showStage(idx){
  const st=DATA.stages[idx];
  let capsHtml='', objSet=new Set(), methSet=new Set();
  st.caps.forEach(cn=>{
    const c=DATA.caps.find(x=>x.name===cn);
    const objs=c?c.methods.map(m=>m.obj):[];
    objs.forEach(o=>objSet.add(o));
    const meths=c?c.methods.map(m=>m.obj+'.'+m.m):[];
    meths.forEach(m=>methSet.add(m));
    capsHtml += '<span class="pill"><b>'+cn+'</b> <span style="color:#888;font-size:10.5px">'+c.domain+'</span></span>';
  });
  const objHtml=[...objSet].map(o=>'<span class="pill obj"><b>'+o+'</b></span>').join('');
  const methHtml=[...methSet].map(m=>'<span class="pill meth"><b>'+m+'</b></span>').join('');
  document.getElementById('detail').innerHTML =
    '<h3>'+st.name+'</h3>'+
    '<div class="sub">'+st.desc+'</div>'+
    '<div class="sec"><h4><span class="dot" style="background:'+COL.stage+'"></span>业务功能（'+st.caps.length+'）</h4>'+
    '<div class="rel">本阶段由以下业务能力编排而成（业务能力 = 业务对象行为方法的组合）：</div>'+capsHtml+'</div>'+
    '<div class="sec"><h4><span class="dot" style="background:'+COL.obj+'"></span>业务对象（'+objSet.size+'）</h4>'+
    '<div class="rel">本阶段能力所操作的核心业务对象：</div>'+objHtml+'</div>'+
    '<div class="sec"><h4><span class="dot" style="background:'+COL.meth+'"></span>行为方法（'+methSet.size+'）</h4>'+
    '<div class="rel">对象在本阶段被调用的行为方法（对象.方法）：</div>'+methHtml+'</div>';
}
function showNode(d){
  let html='';
  if(d.category===0){
    document.getElementById('detail').innerHTML =
      '<h3>'+d.name+'</h3><div class="sub">'+d.desc+'</div>'+
      '<div class="empty">点击左侧任意「阶段活动」可查看该流程相关的业务功能、业务对象与行为方法明细。</div>';
    return;
  }
  if(d.category===1){
    showStage(d.stidx); return;
  }
  if(d.category===2){
    const c=DATA.caps.find(x=>x.id===d.id);
    const objs=[...new Set(c.methods.map(m=>m.obj))];
    const meths=c.methods.map(m=>m.obj+'.'+m.m);
    html='<h3>'+c.name+'</h3>'+
      '<div class="sub"><b>业务功能</b> · 所属阶段：'+DATA.stages[c.stage].name+'<br/>所属业务域：'+c.domain+'</div>'+
      '<div class="sec"><h4><span class="dot" style="background:'+COL.obj+'"></span>操作的对象</h4>'+
      objs.map(o=>'<span class="pill obj"><b>'+o+'</b></span>').join('')+'</div>'+
      '<div class="sec"><h4><span class="dot" style="background:'+COL.meth+'"></span>调用的行为方法（对象.方法组合）</h4>'+
      meths.map(m=>'<span class="pill meth"><b>'+m+'</b></span>').join('')+'</div>'+
      '<div class="rel">该能力由上述「对象.方法」组合而成，是 LTC 场景在该环节的原子能力单元。</div>';
  }
  if(d.category===3){
    const obj=d.name;
    const caps=DATA.caps.filter(c=>c.methods.some(m=>m.obj===obj));
    const meths=[...new Set(caps.flatMap(c=>c.methods.filter(m=>m.obj===obj).map(m=>m.m)))];
    html='<h3>'+obj+'</h3>'+
      '<div class="sub"><b>业务对象</b> · 在 LTC 中被 '+caps.length+' 个业务能力使用</div>'+
      '<div class="sec"><h4><span class="dot" style="background:'+COL.cap+'"></span>涉及的业务功能</h4>'+
      caps.map(c=>'<span class="pill"><b>'+c.name+'</b></span>').join('')+'</div>'+
      '<div class="sec"><h4><span class="dot" style="background:'+COL.meth+'"></span>行为方法</h4>'+
      meths.map(m=>'<span class="pill meth"><b>'+obj+'.'+m+'</b></span>').join('')+'</div>';
  }
  if(d.category===4){
    const obj=d.obj, m=d.m;
    const caps=DATA.caps.filter(c=>c.methods.some(x=>x.obj===obj&&x.m===m));
    html='<h3>'+obj+'.'+m+'</h3>'+
      '<div class="sub"><b>行为方法</b> · 隶属于对象「'+obj+'」，被 '+caps.length+' 个业务能力调用</div>'+
      '<div class="sec"><h4><span class="dot" style="background:'+COL.cap+'"></span>调用该功能的方法的业务能力</h4>'+
      caps.map(c=>'<span class="pill"><b>'+c.name+'</b> <span style="color:#888;font-size:10.5px">'+DATA.stages[c.stage].name+'</span></span>').join('')+'</div>';
  }
  document.getElementById('detail').innerHTML=html;
}

// ---------- 事件 ----------
function selectStage(idx){
  document.querySelectorAll('.navitem').forEach(n=>n.classList.remove('active'));
  const sel=document.querySelector('.navitem[data-stage="'+(idx==='all'?'all':idx)+'"]');
  if(sel) sel.classList.add('active');
  render(idx==='all'?null:idx);
  if(idx==='all'){
    document.getElementById('detail').innerHTML =
      '<h3>线索到回款 (LTC) · 全链路总览</h3>'+
      '<div class="sub">'+DATA.ltc.desc+'</div>'+
      '<div class="empty">• 左侧点击「阶段活动」可聚焦该流程的子网与明细。<br/>• 图中点击任意节点（功能 / 对象 / 方法）可在本区查看其依赖关系。<br/>• 五类节点构成 SBR 三层语义网络：<br/>　LTC流程 → 阶段活动 → 业务功能 → 行为方法 → 业务对象。</div>';
  } else {
    showStage(idx);
  }
}

document.getElementById('navlist').addEventListener('click', e=>{
  const it=e.target.closest('.navitem'); if(!it) return;
  selectStage(parseInt(it.dataset.stage,10));
});
document.querySelector('.navitem.all').addEventListener('click', ()=>selectStage('all'));
chart.on('click', p=>{ if(p.dataType==='node') showNode(p.data); });
window.addEventListener('resize', ()=>chart.resize());

// 初始
selectStage('all');
</script>
</body>
</html>
"""

html = HTML.replace("__DATA__", data_json)
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("已生成:", HTML_PATH)
print("节点规模 -> 流程:1 阶段:%d 功能:%d 对象:%d 行为方法:%d" % (N_STAGE, N_CAP, N_OBJ, N_METH))
