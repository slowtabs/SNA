import { useEffect, useMemo, useRef, useState } from 'react'
import { analyze, karate, metricTitle, parseNetwork } from './network'

const metrics = ['degree', 'betweenness', 'closeness', 'eigenvector', 'pagerank']
const colors = ['#ff385c', '#460479', '#008a70', '#f59e0b', '#2672eb', '#92174d']
const pretty = n => Number(n).toLocaleString(undefined, { maximumFractionDigits: 4 })

function Graph({ network, result, metric, selected, onSelect, colorMode }) {
  const [labels, setLabels] = useState(true)
  const makePositions = () => Object.fromEntries(network.nodes.map((node, i) => {
    const angle = (i / network.nodes.length) * Math.PI * 2 - Math.PI / 2
    const radius = 40 + ((i * 17) % 29)
    return [node.id, { x: 50 + Math.cos(angle) * radius * .56, y: 50 + Math.sin(angle) * radius * .48 }]
  }))
  const [positions, setPositions] = useState(makePositions)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const drag = useRef(null)
  const svg = useRef(null)
  useEffect(() => { setPositions(makePositions()); setPan({ x: 0, y: 0 }) }, [network])
  const pointer = event => { const box = svg.current.getBoundingClientRect(); return { x: (event.clientX - box.left) * 100 / box.width, y: (event.clientY - box.top) * 100 / box.height } }
  const startNodeDrag = (event, id) => { event.stopPropagation(); const point = pointer(event); drag.current = { type: 'node', id, start: point, origin: positions[id], moved: false }; svg.current.setPointerCapture(event.pointerId) }
  const startPan = event => { const point = pointer(event); drag.current = { type: 'pan', start: point, origin: pan, moved: false }; svg.current.setPointerCapture(event.pointerId) }
  const move = event => { if (!drag.current) return; const point = pointer(event), current = drag.current, dx = point.x - current.start.x, dy = point.y - current.start.y; if (Math.abs(dx) + Math.abs(dy) > .25) current.moved = true; if (current.type === 'node') setPositions(old => ({ ...old, [current.id]: { x: Math.max(-30, Math.min(130, current.origin.x + dx)), y: Math.max(-30, Math.min(130, current.origin.y + dy)) } })); else setPan({ x: current.origin.x + dx, y: current.origin.y + dy }) }
  const stop = event => { if (!drag.current) return; const current = drag.current; drag.current = null; if (svg.current?.hasPointerCapture(event.pointerId)) svg.current.releasePointerCapture(event.pointerId); if (current.type === 'node' && !current.moved) onSelect(current.id) }
  const resetLayout = () => { setPositions(makePositions()); setPan({ x: 0, y: 0 }) }
  const values = result[metric], max = Math.max(...Object.values(values), 0.0001)
  const nodeColor = id => colorMode === 'community' ? colors[result.groups[id] % colors.length] : `rgba(255, 56, 92, ${.28 + .72 * values[id] / max})`
  return <section className="panel graph-panel">
    <div className="section-head"><div><p className="eyebrow">Network view</p><h2>{network.name}</h2></div><div className="graph-actions"><button className="reset-layout" onClick={resetLayout}>Reset layout</button><label className="toggle"><input type="checkbox" checked={labels} onChange={e=>setLabels(e.target.checked)} /><span>Labels</span></label></div></div>
    <svg ref={svg} className="network" viewBox="0 0 100 100" role="img" aria-label="Interactive network graph. Drag nodes to arrange them and drag empty space to pan." onPointerDown={startPan} onPointerMove={move} onPointerUp={stop} onPointerCancel={stop}>
      <g transform={`translate(${pan.x} ${pan.y})`}>
      {network.links.map((link, i) => <line key={i} x1={positions[link.source].x} y1={positions[link.source].y} x2={positions[link.target].x} y2={positions[link.target].y} className="edge" />)}
      {network.nodes.map(node => <g key={node.id} className="graph-node" onPointerDown={event=>startNodeDrag(event, node.id)}>
        <circle cx={positions[node.id].x} cy={positions[node.id].y} r={1.7 + 2.8 * values[node.id] / max} fill={nodeColor(node.id)} className={selected === node.id ? 'selected' : ''} />
        {labels && <text x={positions[node.id].x} y={positions[node.id].y+.9}>{node.id}</text>}
      </g>)}
      </g>
    </svg>
    <div className="legend"><span><i className="dot coral"/> {colorMode === 'community' ? 'Detected communities' : `${metricTitle(metric)} score`}</span><span>{network.directed ? 'Directed' : 'Undirected'} · drag nodes to arrange · drag background to pan</span></div>
  </section>
}

function App() {
  const [network, setNetwork] = useState(karate)
  const [metric, setMetric] = useState('betweenness')
  const [selected, setSelected] = useState('0')
  const [directed, setDirected] = useState(false)
  const [colorMode, setColorMode] = useState('metric')
  const [message, setMessage] = useState('Showing the project’s Zachary Karate Club example.')
  const input = useRef(null)
  const result = useMemo(() => analyze(network), [network])
  const ranking = useMemo(() => network.nodes.map(n => ({ ...n, score: result[metric][n.id] })).sort((a,b)=>b.score-a.score), [network,result,metric])
  const node = network.nodes.find(n => n.id === selected) || network.nodes[0]
  const importFile = async e => { const file=e.target.files?.[0]; if(!file)return; try { const parsed=parseNetwork(await file.text(), directed, file.name); setNetwork(parsed); setSelected(parsed.nodes[0].id); setMessage(`Loaded ${file.name}. Your file stays in this browser.`) } catch(err) { setMessage(err.message) } }
  const loadExample = () => { const next=karate(); setNetwork(next); setSelected('0'); setMessage('Karate Club example loaded — the same dataset used in the notebooks.') }
  const exportResults = () => { const payload={ network:network.name, generatedAt:new Date().toISOString(), stats:result.stats, centrality:Object.fromEntries(network.nodes.map(n=>[n.id,Object.fromEntries(metrics.map(m=>[m,result[m][n.id]]))])), communities:result.groups, robustness:result.robustness }; const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'})); const a=document.createElement('a');a.href=url;a.download='network-lens-analysis.json';a.click();URL.revokeObjectURL(url) }
  return <>
    <header><div className="brand"><span className="mark"><b/> <b/> <b/></span><span>Network Lens</span></div><nav><a className="active" href="#workspace">Explore</a><a href="#ranking">Analyze</a><a href="#example" onClick={loadExample}>Example</a></nav><button className="nav-action" onClick={exportResults}>Export analysis</button></header>
    <main>
      <section className="hero"><div><p className="eyebrow">SOCIAL NETWORK ANALYSIS</p><h1>Make every connection count.</h1><p className="lead">Import an edge list or explore the Karate Club network from your group project. Compare influence, detect communities, and test network resilience — all locally.</p></div><div className="project-chip"><span>✓</span> ATSMA group project</div></section>
      <section className="importer" id="workspace"><div className="import-copy"><span className="upload-icon">↗</span><div><strong>Bring your network</strong><small>CSV, TXT, or whitespace edge list · source,target per line</small></div></div><div className="import-actions"><label className="toggle"><input type="checkbox" checked={directed} onChange={e=>setDirected(e.target.checked)} /><span>Directed graph</span></label><input ref={input} hidden type="file" accept=".csv,.txt,.edges" onChange={importFile}/><button className="secondary" onClick={loadExample}>Load example</button><button className="primary" onClick={()=>input.current?.click()}>Import network <span>→</span></button></div></section>
      <p className="status">{message}</p>
      <section className="stat-grid">{[['Nodes',result.stats.nodes],['Edges',result.stats.edges],['Density',pretty(result.stats.density)],['Components',result.stats.components],['Avg. degree',pretty(result.stats.averageDegree)]].map(([label,value])=><article className="stat" key={label}><span>{label}</span><strong>{value}</strong></article>)}</section>
      <section className="controls"><div><p className="eyebrow">ANALYSIS LENS</p><div className="metric-tabs">{metrics.map(m=><button key={m} onClick={()=>setMetric(m)} className={metric===m?'chosen':''}>{metricTitle(m)}</button>)}</div></div><div className="segmented"><button className={colorMode==='metric'?'on':''} onClick={()=>setColorMode('metric')}>Score</button><button className={colorMode==='community'?'on':''} onClick={()=>setColorMode('community')}>Communities</button></div></section>
      <section className="workspace"><Graph network={network} result={result} metric={metric} selected={selected} onSelect={setSelected} colorMode={colorMode}/><aside className="panel insights"><div className="section-head"><div><p className="eyebrow">NODE INSIGHT</p><h2>Member {node.id}</h2></div><span className="rank">#{ranking.findIndex(x=>x.id===node.id)+1}</span></div><div className="score-block"><span>{metricTitle(metric)} centrality</span><strong>{pretty(result[metric][node.id])}</strong><small>Normalized structural importance</small></div><dl><div><dt>Degree</dt><dd>{pretty(result.degree[node.id])}</dd></div><div><dt>Betweenness</dt><dd>{pretty(result.betweenness[node.id])}</dd></div><div><dt>Community</dt><dd>Group {result.groups[node.id]+1}</dd></div>{node.group&&<div><dt>Known faction</dt><dd>{node.group}</dd></div>}</dl><p className="insight-note">{ranking[0].id===node.id ? 'This node is the strongest connector for the selected lens.' : 'Select another node in the graph to compare its role.'}</p></aside></section>
      <section className="lower" id="ranking"><article className="panel ranking"><div className="section-head"><div><p className="eyebrow">INFLUENCE RANKING</p><h2>Who matters most?</h2></div><span className="metric-label">{metricTitle(metric)}</span></div><div className="table-head"><span>Node</span><span>Score</span></div>{ranking.slice(0,8).map((row,i)=><button className={'rank-row '+(selected===row.id?'highlight':'')} key={row.id} onClick={()=>setSelected(row.id)}><span><b>{i+1}</b> Member {row.id}</span><span className="bar"><i style={{width:`${Math.max(5,row.score/(ranking[0].score||1)*100)}%`}}/></span><em>{pretty(row.score)}</em></button>)}</article>
        <article className="panel resilience"><div className="section-head"><div><p className="eyebrow">ROBUSTNESS</p><h2>Removal stress test</h2></div><span className="metric-label">Top betweenness</span></div><div className="curve">{result.robustness.map((point,i)=><div key={i} className="curve-bar"><i style={{height:`${point.share*100}%`}}/><small>{point.removed}</small></div>)}</div><div className="curve-label"><span>0 nodes removed</span><span>{result.robustness.at(-1).removed} removed</span></div><p>Largest connected component after sequentially removing the highest-betweenness nodes.</p></article></section>
      <section className="method"><p className="eyebrow">WHAT IS HAPPENING?</p><h2>From a simple edge list to a clear structural story.</h2><div><article><b>01</b><h3>Map</h3><p>Draw the relationships and establish the network’s baseline structure.</p></article><article><b>02</b><h3>Measure</h3><p>Compare five centrality definitions, each revealing a different type of influence.</p></article><article><b>03</b><h3>Understand</h3><p>Find emergent groups and see how targeted removals affect cohesion.</p></article></div></section>
    </main><footer><span>Network Lens · locally processed · no data is uploaded</span><span>Built for Advanced Text and Social Media Analytics</span></footer>
  </>
}
export default App
