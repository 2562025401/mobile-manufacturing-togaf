# -*- coding: utf-8 -*-
"""从4个本体模型YAML生成ECharts知识图谱HTML（黑色背景/按类型配色/对象节点更大/多布局切换）。"""
import yaml, json, os

YAML_DIR = os.path.dirname(os.path.abspath(__file__))
def load(n):
    with open(os.path.join(YAML_DIR, n), encoding='utf-8') as f:
        return yaml.safe_load(f)

obj_doc = load('objects.yaml')
beh_doc = load('behaviors.yaml')
rule_doc = load('rules.yaml')
scn_doc = load('scenarios.yaml')

agg = obj_doc['aggregates']
behs = beh_doc['behaviors']
rules = rule_doc['rules']
ucs = scn_doc['use_cases']

# ---------- 类型/颜色定义 ----------
CAT = {
    'obj':  {'name': '业务对象', 'color': '#00E5FF'},
    'beh':  {'name': '业务行为', 'color': '#FFB300'},
    'rule': {'name': '业务规则', 'color': '#B388FF'},
    'uc':   {'name': '业务场景', 'color': '#69F0AE'},
}
def cat_color(t): return CAT[t]['color']

# ---------- 构建节点 ----------
nodes = []          # ECharts nodes
node_index = {}     # id -> node
degree = {}

def add_node(nid, name, cat, detail):
    node_index[nid] = {'id': nid, 'name': name, 'category': cat, 'detail': detail}
    nodes.append(node_index[nid])
    degree[nid] = 0

# 对象节点
for a in agg:
    cat_label = a.get('categoryLabel') or a.get('objectCategory') or ''
    attrs = a.get('attributes') or []
    att_str = '；'.join([f"{x.get('label')}({x.get('type')})" for x in attrs[:12]])
    if len(attrs) > 12: att_str += ' …'
    detail = {
        'type': 'obj',
        'oid': a['id'], 'name': a['name'],
        'alias': a.get('alias') or '',
        'aggType': a.get('aggregateType') or '',
        'objCat': cat_label,
        'domain': a.get('domain') or '',
        'source': a.get('sourceSystem') or '',
        'life': a.get('lifecycle') or '',
        'desc': a.get('description') or '',
        'attrs': att_str,
    }
    add_node(a['id'], a['name'], 'obj', detail)

# 行为节点
beh_id_set = set(b['id'] for b in behs)
for b in behs:
    detail = {
        'type': 'beh',
        'bid': b['id'], 'name': b['name'],
        'btype': b.get('behaviorType') or '',
        'trigger': b.get('triggerType') or '',
        'owner': b.get('ownerEntity') or '',
        'domain': b.get('domain') or '',
        'app': b.get('supportApp') or '',
        'desc': b.get('description') or '',
        'outputs': '、'.join(b.get('outputObjects') or []),
    }
    add_node(b['id'], b['name'], 'beh', detail)

# 规则节点
for r in rules:
    detail = {
        'type': 'rule',
        'rid': r['id'], 'name': r['name'],
        'rtype': r.get('ruleType') or '',
        'rcat': r.get('ruleCategory') or '',
        'domain': r.get('domain') or '',
        'cond': r.get('condition') or '',
        'handle': r.get('violationHandling') or '',
    }
    add_node(r['id'], r['name'], 'rule', detail)

# 场景节点
for u in ucs:
    steps = u.get('primaryFlow') or []
    detail = {
        'type': 'uc',
        'uid': u['id'], 'name': u['name'],
        'domain': u.get('domain') or '',
        'actors': '、'.join(u.get('actors') or []),
        'desc': u.get('description') or '',
        'steps': len(steps),
    }
    add_node(u['id'], u['name'], 'uc', detail)

# ---------- 构建边（去重） ----------
edges = []
seen = set()
def add_edge(src, tgt, label):
    if src not in node_index or tgt not in node_index: return
    if src == tgt: return
    key = (src, tgt, label)
    if key in seen: return
    seen.add(key)
    degree[src] += 1
    degree[tgt] += 1
    edges.append({'source': src, 'target': tgt, 'label': label, 'color': cat_color(node_index[src]['category'])})

# 对象 -> 行为（拥有行为）
for a in agg:
    for b in (a.get('relatedBehaviors') or []):
        add_edge(a['id'], b, '拥有行为')
# 对象 -> 规则（受约束）
for a in agg:
    for r in (a.get('relatedRules') or []):
        add_edge(a['id'], r, '受约束')
# 行为 -> 对象（产出/修改）
for b in behs:
    for o in (b.get('outputObjects') or []):
        add_edge(b['id'], o, '产出/修改对象')
# 行为 -> 规则（应用规则）
for b in behs:
    for r in (b.get('appliedRules') or []):
        add_edge(b['id'], r, '应用规则')
# 规则 -> 对象（作用于）
for r in rules:
    for o in (r.get('appliesToObjects') or []):
        add_edge(r['id'], o, '作用于对象')
# 场景 -> 对象（读写）
for u in ucs:
    for st in (u.get('primaryFlow') or []):
        for o in (st.get('readObjects') or []):
            add_edge(u['id'], o, '读取对象')
        for o in (st.get('writeObjects') or []):
            add_edge(u['id'], o, '写入对象')
        br = st.get('behaviorRef')
        if br and br in node_index:
            add_edge(u['id'], br, '触发行为')
# 跨域对象关联
for ass in (obj_doc.get('aggregate_associations') or []):
    s = ass.get('sourceAggregate'); t = ass.get('targetAggregate')
    add_edge(s, t, '跨域关联')

# ---------- 计算节点大小（对象按度数放大，其它固定） ----------
for n in nodes:
    t = n['detail']['type']
    d = degree.get(n['id'], 0)
    if t == 'obj':
        n['symbolSize'] = 38 + min(d, 14) * 2.2      # 38~69
    elif t == 'uc':
        n['symbolSize'] = 50                          # 场景次之
    elif t == 'beh':
        n['symbolSize'] = 26 + min(d, 10) * 0.8       # 26~34
    else:
        n['symbolSize'] = 22 + min(d, 10) * 0.6       # 规则 22~28

# ---------- 组装 ECharts 数据 ----------
cat_list = [{'name': CAT[k]['name'], 'itemStyle': {'color': CAT[k]['color']}} for k in ['obj','beh','rule','uc']]
graph = {
    'nodes': [{'id': n['id'], 'name': n['name'], 'category': ['obj','beh','rule','uc'].index(n['category']),
               'symbolSize': n['symbolSize'], 'value': degree.get(n['id'],0), 'detail': n['detail']} for n in nodes],
    'links': [{'source': e['source'], 'target': e['target'],
               'lineStyle': {'color': e['color'], 'width': 1, 'opacity': 0.28, 'curveness': 0.12},
               'label': e['label']} for e in edges],
    'categories': cat_list,
}
DATA_JSON = json.dumps(graph, ensure_ascii=False)

# ---------- 写 HTML ----------
html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>手机制造行业企业架构 · 本体知识图谱</title>
<script src="echarts.min.js"></script>
<style>
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; height:100%; background:#000; color:#e6e6e6;
    font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif; overflow:hidden; }
  #app { display:flex; flex-direction:column; height:100vh; }
  #toolbar { display:flex; flex-wrap:wrap; align-items:center; gap:10px;
    padding:10px 16px; background:#0c0c10; border-bottom:1px solid #1f1f29; }
  #toolbar .group { display:flex; align-items:center; gap:6px; }
  #toolbar label { font-size:12px; color:#9aa0a6; }
  #toolbar select, #toolbar input {
    background:#15151c; color:#e6e6e6; border:1px solid #2a2a36; border-radius:6px;
    padding:5px 8px; font-size:13px; outline:none; }
  #toolbar input[type=text] { width:200px; }
  #toolbar button {
    background:#1d2836; color:#7fdfff; border:1px solid #2a4a5a; border-radius:6px;
    padding:5px 12px; font-size:13px; cursor:pointer; }
  #toolbar button:hover { background:#26405a; }
  #toolbar .chk { display:flex; align-items:center; gap:4px; font-size:12px; cursor:pointer;
    padding:3px 8px; border-radius:6px; border:1px solid #2a2a36; }
  #toolbar .chk.on { border-color:#3a3a48; }
  .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
  #stat { font-size:12px; color:#7a8088; margin-left:auto; }
  #chart { flex:1; width:100%; }
  #tip { max-width:340px; font-size:12px; line-height:1.6; }
  #tip h4 { margin:0 0 6px; font-size:13px; }
  #tip .k { color:#9aa0a6; }
  #tip .row { margin:2px 0; }
  #tip a { color:#7fdfff; }
</style>
</head>
<body>
<div id="app">
  <div id="toolbar">
    <div class="group">
      <label>布局</label>
      <select id="layout">
        <option value="force">力导向布局</option>
        <option value="circular">环形布局</option>
        <option value="grid">网格布局</option>
        <option value="cluster">分类聚类布局</option>
      </select>
    </div>
    <div class="group" id="catFilter">
      <span class="chk on" data-cat="0"><span class="dot" style="background:#00E5FF"></span>业务对象</span>
      <span class="chk on" data-cat="1"><span class="dot" style="background:#FFB300"></span>业务行为</span>
      <span class="chk on" data-cat="2"><span class="dot" style="background:#B388FF"></span>业务规则</span>
      <span class="chk on" data-cat="3"><span class="dot" style="background:#69F0AE"></span>业务场景</span>
    </div>
    <div class="group">
      <label>边</label>
      <button id="toggleEdge">隐藏关系边</button>
    </div>
    <div class="group">
      <input type="text" id="search" placeholder="搜索节点名称…"/>
      <button id="focusBtn">聚焦</button>
      <button id="resetBtn">重置</button>
    </div>
    <div id="stat"></div>
  </div>
  <div id="chart"></div>
</div>

<script>
var GRAPH = __GRAPH_DATA__;
var CAT_COLORS = ['#00E5FF','#FFB300','#B388FF','#69F0AE'];
var CAT_NAMES  = ['业务对象','业务行为','业务规则','业务场景'];
var chart = echarts.init(document.getElementById('chart'), null, {renderer:'canvas'});
var BASE_NODES = GRAPH.nodes.slice();
var BASE_LINKS = GRAPH.links.slice();
var activeCats = [true,true,true,true];
var showEdge = true;
var focusedId = null;

function tooltipFormatter(p){
  if(!p.data || !p.data.detail){ // 边
    return '<div id="tip">'+ (p.data? p.data.source+' → '+p.data.target+'<br/>关系：'+p.data.label : '') +'</div>';
  }
  var d = p.data.detail; var h = '<div id="tip">';
  if(d.type==='obj'){
    h += '<h4 style="color:'+CAT_COLORS[0]+'">◆ 业务对象：'+d.name+'</h4>';
    h += '<div class="row"><span class="k">编号：</span>'+d.oid+'</div>';
    if(d.alias) h += '<div class="row"><span class="k">别名：</span>'+d.alias+'</div>';
    h += '<div class="row"><span class="k">对象分类：</span>'+d.objCat+' ｜ <span class="k">聚合类型：</span>'+d.aggType+'</div>';
    h += '<div class="row"><span class="k">所属域：</span>'+d.domain+'</div>';
    h += '<div class="row"><span class="k">来源系统：</span>'+d.source+'</div>';
    if(d.life) h += '<div class="row"><span class="k">生命周期：</span>'+d.life+'</div>';
    if(d.desc) h += '<div class="row"><span class="k">说明：</span>'+d.desc+'</div>';
    if(d.attrs) h += '<div class="row"><span class="k">关键属性：</span>'+d.attrs+'</div>';
  } else if(d.type==='beh'){
    h += '<h4 style="color:'+CAT_COLORS[1]+'">● 业务行为：'+d.name+'</h4>';
    h += '<div class="row"><span class="k">编号：</span>'+d.bid+'</div>';
    h += '<div class="row"><span class="k">行为类型：</span>'+d.btype+' ｜ <span class="k">触发：</span>'+d.trigger+'</div>';
    h += '<div class="row"><span class="k">归属对象：</span>'+d.owner+'</div>';
    h += '<div class="row"><span class="k">所属域：</span>'+d.domain+'</div>';
    if(d.outputs) h += '<div class="row"><span class="k">产出对象：</span>'+d.outputs+'</div>';
    if(d.app) h += '<div class="row"><span class="k">支撑系统：</span>'+d.app+'</div>';
    if(d.desc) h += '<div class="row"><span class="k">说明：</span>'+d.desc+'</div>';
  } else if(d.type==='rule'){
    h += '<h4 style="color:'+CAT_COLORS[2]+'">▲ 业务规则：'+d.name+'</h4>';
    h += '<div class="row"><span class="k">编号：</span>'+d.rid+'</div>';
    h += '<div class="row"><span class="k">规则类型：</span>'+d.rtype+' ｜ <span class="k">分类：</span>'+d.rcat+'</div>';
    h += '<div class="row"><span class="k">所属域：</span>'+d.domain+'</div>';
    if(d.cond) h += '<div class="row"><span class="k">条件：</span>'+d.cond+'</div>';
    if(d.handle) h += '<div class="row"><span class="k">违规处理：</span>'+d.handle+'</div>';
  } else {
    h += '<h4 style="color:'+CAT_COLORS[3]+'">■ 业务场景：'+d.name+'</h4>';
    h += '<div class="row"><span class="k">编号：</span>'+d.uid+'</div>';
    h += '<div class="row"><span class="k">所属域：</span>'+d.domain+'</div>';
    if(d.actors) h += '<div class="row"><span class="k">参与角色：</span>'+d.actors+'</div>';
    h += '<div class="row"><span class="k">流程步骤数：</span>'+d.steps+'</div>';
    if(d.desc) h += '<div class="row"><span class="k">说明：</span>'+d.desc+'</div>';
  }
  h += '</div>';
  return h;
}

function layoutOption(mode){
  if(mode==='force') return { layout:'force', force:{ repulsion: 320, edgeLength:[50,160], gravity:0.06, friction:0.6, layoutAnimation:true } };
  if(mode==='circular') return { layout:'circular', circular:{ rotateLabel:true, sort:'desc' } };
  return { layout:'none' }; // grid / cluster 由坐标决定
}

function computePositions(mode){
  if(mode==='grid' || mode==='cluster'){
    var byCat = [[],[],[],[]];
    BASE_NODES.forEach(function(n){ byCat[n.category].push(n); });
    var W = chart.getWidth(), H = chart.getHeight();
    var pos = {};
    byCat.forEach(function(arr, ci){
      if(mode==='cluster'){
        // 四象限：对象右、行为下、规则左上、场景右上（按类型聚集）
        var cx = [W*0.5, W*0.5, W*0.27, W*0.73][ci];
        var cy = [H*0.5, H*0.78, H*0.25, H*0.25][ci];
        var n = arr.length; var cols = Math.ceil(Math.sqrt(n));
        var gap = Math.max(28, Math.min(70, (W*0.42)/cols));
        arr.forEach(function(nd, i){
          var r = Math.floor(i/cols), c = i%cols;
          pos[nd.id] = [ cx + (c-(cols-1)/2)*gap, cy + (r-(Math.ceil(n/cols)-1)/2)*gap ];
        });
      } else { // grid: 每类占一行
        var perRow = Math.ceil(Math.sqrt(arr.length));
        var gx = (W-80)/perRow;
        arr.forEach(function(nd, i){
          var r = Math.floor(i/perRow), c = i%perRow;
          pos[nd.id] = [ 60 + c*gx, 60 + ci*(H/4) + (r*( (H/4-40)/ (Math.ceil(arr.length/perRow)) )) ];
        });
      }
    });
    return pos;
  }
  return null;
}

function render(){
  var mode = document.getElementById('layout').value;
  var pos = computePositions(mode);
  var nodes = BASE_NODES.filter(function(n){ return activeCats[n.category]; }).map(function(n){
    var o = { id:n.id, name:n.name, category:n.category, symbolSize:n.symbolSize, value:n.value, detail:n.detail };
    if(pos && pos[n.id]){ o.x = pos[n.id][0]; o.y = pos[n.id][1]; o.fixed = (mode==='grid'); }
    return o;
  });
  var idset = {}; nodes.forEach(function(n){ idset[n.id]=true; });
  var links = showEdge ? BASE_LINKS.filter(function(l){ return idset[l.source] && idset[l.target]; }) : [];
  if(focusedId){
    var keep = { }; keep[focusedId]=true;
    links.forEach(function(l){ if(l.source===focusedId) keep[l.target]=true; if(l.target===focusedId) keep[l.source]=true; });
    nodes = nodes.filter(function(n){ return keep[n.id]; });
    if(!nodes.length) nodes = BASE_NODES.filter(function(n){return n.id===focusedId;}).map(function(n){return n;});
  }
  var opt = {
    backgroundColor:'#000000',
    tooltip:{ trigger:'item', backgroundColor:'#11131a', borderColor:'#2a2a36', textStyle:{color:'#e6e6e6'},
              formatter: tooltipFormatter, extraCssText:'max-width:360px;white-space:normal;' },
    legend:[{ data:CAT_NAMES, top:8, right:12, textStyle:{color:'#cfd3d8'}, icon:'circle', itemWidth:10, itemHeight:10 }],
    series:[{
      type:'graph', roam:true, draggable:true,
      categories: GRAPH.categories,
      data: nodes,
      links: links,
      label:{ show:true, position:'right', color:'#cfd3d8', fontSize:10,
              formatter:function(p){ if(p.dataType==='edge') return ''; return p.data.detail? p.data.detail.name : ''; } },
      labelLayout:{ hideOverlap:true },
      lineStyle:{ color:'source', curveness:0.12 },
      emphasis:{ focus:'adjacency', lineStyle:{width:2.4, opacity:0.95}, label:{show:true, fontSize:12, color:'#fff'} },
      scaleLimit:{ min:0.2, max:6 },
      edgeSymbol:['none','none'],
      itemStyle:{ borderColor:'#000', borderWidth:1 }
    }]
  };
  var lo = layoutOption(mode);
  for(var k in lo) opt.series[0][k] = lo[k];
  chart.setOption(opt, true);
  document.getElementById('stat').textContent =
    '节点 '+nodes.length+' / '+BASE_NODES.length+' ｜ 关系边 '+links.length+' / '+BASE_LINKS.length;
}

document.getElementById('layout').addEventListener('change', render);
document.getElementById('toggleEdge').addEventListener('click', function(){
  showEdge=!showEdge; this.textContent = showEdge? '隐藏关系边':'显示关系边'; render();
});
document.querySelectorAll('#catFilter .chk').forEach(function(el){
  el.addEventListener('click', function(){
    var c = +this.getAttribute('data-cat'); activeCats[c]=!activeCats[c];
    this.classList.toggle('on', activeCats[c]); this.style.opacity = activeCats[c]? '1':'0.4'; render();
  });
});
function doFocus(){
  var q = document.getElementById('search').value.trim();
  if(!q){ focusedId=null; render(); return; }
  var hit = BASE_NODES.filter(function(n){ return n.name && n.name.indexOf(q)>=0; });
  if(hit.length){ focusedId = hit[0].id; render(); chart.dispatchAction({type:'highlight', dataIndex: hit[0] ? BASE_NODES.indexOf(hit[0]):0}); }
  else { focusedId=null; render(); alert('未找到匹配节点：'+q); }
}
document.getElementById('focusBtn').addEventListener('click', doFocus);
document.getElementById('search').addEventListener('keydown', function(e){ if(e.key==='Enter') doFocus(); });
document.getElementById('resetBtn').addEventListener('click', function(){
  focusedId=null; document.getElementById('search').value='';
  activeCats=[true,true,true,true]; showEdge=true;
  document.querySelectorAll('#catFilter .chk').forEach(function(el){ el.classList.add('on'); el.style.opacity='1'; });
  document.getElementById('toggleEdge').textContent='隐藏关系边';
  render();
});
window.addEventListener('resize', function(){ chart.resize(); render(); });
render();
</script>
</body>
</html>
'''

html = html.replace('__GRAPH_DATA__', DATA_JSON)
out = os.path.join(YAML_DIR, '企业架构本体知识图谱.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('written:', out)
print('nodes=', len(nodes), 'edges=', len(edges))
print('by cat -> obj', sum(1 for n in nodes if n['detail']['type']=='obj'),
      'beh', sum(1 for n in nodes if n['detail']['type']=='beh'),
      'rule', sum(1 for n in nodes if n['detail']['type']=='rule'),
      'uc', sum(1 for n in nodes if n['detail']['type']=='uc'))
