const karateEdges = [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[0,8],[0,10],[0,11],[0,12],[0,13],[0,17],[0,19],[0,21],[0,31],[1,2],[1,3],[1,7],[1,13],[1,17],[1,19],[1,21],[1,30],[2,3],[2,7],[2,8],[2,9],[2,13],[2,27],[2,28],[2,32],[3,7],[3,12],[3,13],[4,6],[4,10],[5,6],[5,10],[5,16],[6,16],[8,30],[8,32],[8,33],[9,33],[13,33],[14,32],[14,33],[15,32],[15,33],[18,32],[18,33],[19,33],[20,32],[20,33],[22,32],[22,33],[23,25],[23,27],[23,29],[23,32],[23,33],[24,25],[24,27],[24,31],[25,31],[26,29],[26,33],[27,33],[28,31],[28,33],[29,32],[29,33],[30,32],[30,33],[31,32],[31,33],[32,33]]
const club = {9:'Officer',14:'Officer',15:'Officer',18:'Officer',20:'Officer',22:'Officer',23:'Officer',24:'Officer',25:'Officer',26:'Officer',27:'Officer',28:'Officer',29:'Officer',30:'Officer',31:'Officer',32:'Officer',33:'Officer'}
const LARGE_NETWORK_LIMIT = 10000
export const isLargeNetwork = network => network.nodes.length > 500 || network.links.length > LARGE_NETWORK_LIMIT

export const karate = () => ({
  name: 'Karate Club example', directed: false,
  nodes: Array.from({ length: 34 }, (_, i) => ({ id: String(i), group: club[i] || 'Mr. Hi' })),
  links: karateEdges.map(([source, target]) => ({ source: String(source), target: String(target) })),
})

export function parseNetwork(text, directed = false, name = 'Uploaded network') {
  const links = []
  const ids = new Set()
  const dot = /^\s*(?:strict\s+)?(?:graph|digraph)\b/i.test(text)
  if (dot) {
    const body = text.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*$/gm, '')
    const idPattern = String.raw`"(?:\\.|[^"])*"|[-+]?(?:\d+(?:\.\d*)?|\.\d+)|[A-Za-z_\u0080-\uffff][\w\u0080-\uffff]*`
    const unquote = value => value.startsWith('"') && value.endsWith('"') ? value.slice(1, -1).replace(/\\"/g, '"') : value
    body.split(/\r?\n/).forEach(line => {
      const clean = line.trim()
      if (!clean || /^(?:strict\s+)?(?:graph|digraph)\b/i.test(clean) || clean === '}' || clean.startsWith('[')) return
      const edge = clean.match(new RegExp(String.raw`^\s*(${idPattern})\s*(--|->)\s*(${idPattern})(?=\s|;|\[|$)`))
      if (edge) {
        const source = unquote(edge[1]), target = unquote(edge[3])
        ids.add(source); ids.add(target); links.push({ source, target })
        return
      }
      const node = clean.match(new RegExp(String.raw`^\s*(${idPattern})\s*(?:\[[^\]]*\])?\s*;\s*$`))
      if (node) ids.add(unquote(node[1]))
    })
  } else {
  text.split(/\r?\n/).forEach((line) => {
    const clean = line.trim()
    if (!clean || clean.startsWith('#') || clean.startsWith('%')) return
    const [source, target] = clean.split(/[\s,;]+/).map(v => v.trim())
    if (!source || !target || /^(source|from)$/i.test(source)) return
    ids.add(source); ids.add(target); links.push({ source, target })
  })
  }
  if (!links.length) throw new Error('No edges found. Use one source,target pair per line.')
  return { name, directed, nodes: [...ids].map(id => ({ id })), links }
}

function adjacency(network, reverse = false) {
  const map = new Map(network.nodes.map(n => [n.id, new Set()]))
  network.links.forEach(({ source, target }) => {
    map.get(reverse ? target : source)?.add(reverse ? source : target)
    if (!network.directed) map.get(reverse ? source : target)?.add(reverse ? target : source)
  })
  return map
}
function undirectedAdjacency(network) {
  const map = new Map(network.nodes.map(n => [n.id, new Set()]))
  network.links.forEach(({ source, target }) => { map.get(source)?.add(target); map.get(target)?.add(source) })
  return map
}
function bfs(adj, start) {
  const d = new Map([[start, 0]]), queue = [start]
  for (let i = 0; i < queue.length; i++) for (const next of adj.get(queue[i]) || []) if (!d.has(next)) { d.set(next, d.get(queue[i]) + 1); queue.push(next) }
  return d
}
function components(adj) {
  const unseen = new Set(adj.keys()), groups = []
  while (unseen.size) { const start = unseen.values().next().value, seen = bfs(adj, start); seen.forEach((_, node) => unseen.delete(node)); groups.push([...seen.keys()]) }
  return groups
}
function normalize(values) { const max = Math.max(...Object.values(values), 0); return Object.fromEntries(Object.entries(values).map(([k,v]) => [k, max ? v / max : 0])) }

export function analyze(network) {
  const ids = network.nodes.map(n => n.id), n = ids.length, adj = adjacency(network), undirected = undirectedAdjacency(network)
  const large = isLargeNetwork(network)
  const degree = Object.fromEntries(ids.map(id => [id, (undirected.get(id)?.size || 0) / Math.max(1, n - 1)]))
  const closeness = large ? sampledCloseness(undirected, ids) : Object.fromEntries(ids.map(id => { const d = bfs(undirected, id), reachable = d.size - 1, sum = [...d.values()].reduce((a,b) => a + b, 0); return [id, sum ? (reachable / sum) * (reachable / Math.max(1,n-1)) : 0] }))
  const betweenness = brandes(network.directed ? adj : undirected, ids, large ? sampleIds(ids, 64) : ids)
  const eigenvector = eigen(undirected, ids, large ? 50 : 200)
  const pagerank = pageRank(adj, ids)
  const groups = large ? labelPropagation(undirected, ids) : girvanNewman(undirected, ids)
  const comps = components(undirected), giant = comps.sort((a,b) => b.length-a.length)[0] || []
  const giantAdj = new Map(giant.map(id => [id, new Set([...undirected.get(id)].filter(x => giant.includes(x)))]))
  const pathStats = large ? sampledPathStats(giantAdj, giant) : exactPathStats(giantAdj, giant)
  const clusteringStats = large ? sampledClustering(undirected, ids) : exactClustering(undirected, ids, network.links)
  return { degree, closeness, betweenness, eigenvector, pagerank, groups, stats: {
    nodes:n, edges:network.links.length, density: n > 1 ? (network.directed ? network.links.length/(n*(n-1)) : 2*network.links.length/(n*(n-1))) : 0,
    components:comps.length, giant:giant.length, diameter:pathStats.diameter, path:pathStats.path,
    clustering:clusteringStats.clustering, transitivity:clusteringStats.transitivity, averageDegree: n ? 2*network.links.length/n : 0
  }, robustness: robustness(network, betweenness) }
}
function exactPathStats(adj, ids) { const distances=ids.flatMap(id=>[...bfs(adj,id).values()].filter(distance=>distance>0)); return { diameter:Math.max(...distances,0), path:distances.length ? distances.reduce((a,b)=>a+b,0)/distances.length : 0 } }
function sampledPathStats(adj, ids) { let count=0, sum=0, diameter=0; sampleIds(ids,64).forEach(id=>bfs(adj,id).forEach(distance=>{if(distance>0){count++;sum+=distance;diameter=Math.max(diameter,distance)}})); return { diameter, path:count ? sum/count : 0 } }
function exactClustering(adj, ids, links) { const clustering=ids.reduce((sum,id)=>{const ns=[...adj.get(id)];let closed=0;for(let i=0;i<ns.length;i++)for(let j=i+1;j<ns.length;j++)if(adj.get(ns[i]).has(ns[j]))closed++;return sum+(ns.length>1?(2*closed)/(ns.length*(ns.length-1)):0)},0)/ids.length; const triples=ids.reduce((s,id)=>s+adj.get(id).size*(adj.get(id).size-1)/2,0), closed=links.reduce((s,{source,target})=>s+[...adj.get(source)].filter(x=>adj.get(target).has(x)).length,0); return { clustering, transitivity:triples?closed/triples:0 } }
function sampledClustering(adj, ids) { const sample=sampleIds(ids,256), values=sample.map(id=>{const ns=[...adj.get(id)];let closed=0;for(let i=0;i<ns.length;i++)for(let j=i+1;j<ns.length;j++)if(adj.get(ns[i]).has(ns[j]))closed++;return ns.length>1?(2*closed)/(ns.length*(ns.length-1)):0}); return { clustering:values.reduce((a,b)=>a+b,0)/values.length, transitivity:values.reduce((a,b)=>a+b,0)/values.length } }
function labelPropagation(adj, ids) { const labels=Object.fromEntries(ids.map(id=>[id,id])); for(let iteration=0;iteration<20;iteration++){let changed=false;for(const id of ids){const counts={};for(const neighbor of adj.get(id)){const label=labels[neighbor];counts[label]=(counts[label]||0)+1}const best=Object.entries(counts).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))[0];if(best&&labels[id]!==best[0]){labels[id]=best[0];changed=true}}if(!changed)break}const groups={};Object.values(labels).forEach(label=>{if(groups[label]===undefined)groups[label]=Object.keys(groups).length});return Object.fromEntries(ids.map(id=>[id,groups[labels[id]]])) }
function sampleIds(ids, limit) { if (ids.length <= limit) return ids; const step = (ids.length - 1) / (limit - 1); return Array.from({ length: limit }, (_, i) => ids[Math.round(i * step)]) }
function sampledCloseness(adj, ids) { const sums=Object.fromEntries(ids.map(id=>[id,0])), reachable=Object.fromEntries(ids.map(id=>[id,0])); sampleIds(ids,64).forEach(source => bfs(adj,source).forEach((distance,id)=>{if(distance){sums[id]+=distance;reachable[id]++}})); return Object.fromEntries(ids.map(id=>[id,sums[id] ? reachable[id]/sums[id] : 0])) }
function brandes(adj, ids, sources = ids) { const out=Object.fromEntries(ids.map(id=>[id,0])); for (const s of sources) { const stack=[], pred=new Map(ids.map(v=>[v,[]])), sigma=new Map(ids.map(v=>[v,0])), dist=new Map(ids.map(v=>[v,-1])); sigma.set(s,1); dist.set(s,0); const q=[s]; for(let h=0;h<q.length;h++){const v=q[h];stack.push(v);for(const w of adj.get(v)||[]){if(dist.get(w)<0){q.push(w);dist.set(w,dist.get(v)+1)}if(dist.get(w)===dist.get(v)+1){sigma.set(w,sigma.get(w)+sigma.get(v));pred.get(w).push(v)}}}const delta=new Map(ids.map(v=>[v,0])); while(stack.length){const w=stack.pop();for(const v of pred.get(w))delta.set(v,delta.get(v)+(sigma.get(v)/sigma.get(w))*(1+delta.get(w)));if(w!==s)out[w]+=delta.get(w)}} const scale=ids.length/sources.length; return Object.fromEntries(ids.map(id=>[id,out[id]*scale/Math.max(1,(ids.length-1)*(ids.length-2))])) }
function eigen(adj, ids, iterations = 200) { let x=Object.fromEntries(ids.map(id=>[id,1/Math.sqrt(ids.length)])); for(let k=0;k<iterations;k++){let y=Object.fromEntries(ids.map(id=>[id,x[id]+[...adj.get(id)].reduce((s,v)=>s+x[v],0)]));const norm=Math.sqrt(Object.values(y).reduce((s,v)=>s+v*v,0))||1; Object.keys(y).forEach(id=>y[id]/=norm);if(Object.keys(y).reduce((s,id)=>s+Math.abs(y[id]-x[id]),0)<1e-8)return y;x=y}return x }
function pageRank(adj, ids) { let r=Object.fromEntries(ids.map(id=>[id,1/ids.length]));for(let k=0;k<150;k++){const next=Object.fromEntries(ids.map(id=>[id,.15/ids.length]));const dangling=ids.filter(id=>!adj.get(id).size).reduce((s,id)=>s+r[id],0);ids.forEach(id=>{next[id]+=.85*dangling/ids.length;if(adj.get(id).size)[...adj.get(id)].forEach(v=>next[v]+=.85*r[id]/adj.get(id).size)});if(ids.reduce((s,id)=>s+Math.abs(next[id]-r[id]),0)<1e-9)return next;r=next}return r }
function girvanNewman(original, ids) {
  // A compact Girvan--Newman implementation is robust for the small networks
  // intended for this teaching dashboard. It keeps the split with best modularity.
  const graph = new Map(ids.map(id => [id, new Set(original.get(id))]))
  const edgeCount = [...graph.values()].reduce((sum, set) => sum + set.size, 0) / 2
  let best = components(graph), bestScore = modularity(best, original, edgeCount)
  for (let iteration = 0; iteration < Math.min(30, edgeCount); iteration++) {
    const edgeScores = edgeBetweenness(graph, ids)
    const [key] = Object.entries(edgeScores).sort((a, b) => b[1] - a[1])[0] || []
    if (!key) break
    const [a, b] = key.split('\u0000')
    graph.get(a).delete(b); graph.get(b).delete(a)
    const candidate = components(graph)
    const score = modularity(candidate, original, edgeCount)
    if (score > bestScore) { best = candidate; bestScore = score }
  }
  return Object.fromEntries(best.flatMap((group, index) => group.map(id => [id, index])))
}
function edgeBetweenness(adj, ids) {
  const scores = {}
  const edgeKey = (a, b) => [a, b].sort().join('\u0000')
  for (const source of ids) {
    const stack = [], pred = new Map(ids.map(id => [id, []])), sigma = new Map(ids.map(id => [id, 0])), distance = new Map(ids.map(id => [id, -1]))
    sigma.set(source, 1); distance.set(source, 0); const queue = [source]
    for (let i = 0; i < queue.length; i++) { const node = queue[i]; stack.push(node); for (const neighbor of adj.get(node)) { if (distance.get(neighbor) < 0) { distance.set(neighbor, distance.get(node) + 1); queue.push(neighbor) } if (distance.get(neighbor) === distance.get(node) + 1) { sigma.set(neighbor, sigma.get(neighbor) + sigma.get(node)); pred.get(neighbor).push(node) } } }
    const dependency = new Map(ids.map(id => [id, 0]))
    while (stack.length) { const node = stack.pop(); for (const parent of pred.get(node)) { const contribution = (sigma.get(parent) / sigma.get(node)) * (1 + dependency.get(node)); scores[edgeKey(parent, node)] = (scores[edgeKey(parent, node)] || 0) + contribution; dependency.set(parent, dependency.get(parent) + contribution) } }
  }
  return scores
}
function modularity(groups, original, edgeCount) {
  if (!edgeCount) return 0
  return groups.reduce((score, group) => { const set = new Set(group); let internal = 0, degree = 0; for (const id of group) { degree += original.get(id).size; for (const neighbor of original.get(id)) if (set.has(neighbor)) internal++ } return score + internal / (2 * edgeCount) - (degree / (2 * edgeCount)) ** 2 }, 0)
}
function robustness(network, scores) { const ids=network.nodes.map(n=>n.id), ranked=[...ids].sort((a,b)=>scores[b]-scores[a]), steps=Math.min(12, ids.length-1); const curve=[];for(let remove=0;remove<=steps;remove++){const removed=new Set(ranked.slice(0,remove)), adj=undirectedAdjacency(network);removed.forEach(id=>adj.delete(id));adj.forEach(ns=>removed.forEach(id=>ns.delete(id)));const largest=adj.size?Math.max(...components(adj).map(c=>c.length)):0;curve.push({removed, share:largest/ids.length})}return curve }
export function metricTitle(metric) { return ({degree:'Degree',closeness:'Closeness',betweenness:'Betweenness',eigenvector:'Eigenvector',pagerank:'PageRank'})[metric] }
