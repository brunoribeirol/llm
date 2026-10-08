'use strict';
(() => {
  const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = x => typeof x === 'number' ? (Number.isFinite(x) ? Number(x.toFixed(4)).toLocaleString('pt-BR') : String(x)) : String(x ?? '');
  const title = x => x ? '<div class="chart-title">'+esc(x)+'</div>' : '';
  window.DEMO_H = {
    escape: esc,
    metric(label, value, detail='') { return '<div class="metric"><div class="metric-label">'+esc(label)+'</div><div class="metric-value">'+esc(fmt(value))+'</div><div class="metric-detail">'+esc(detail)+'</div></div>'; },
    cards(items) { return '<div class="cards">'+items.map(x=>'<section class="card"><h3>'+esc(x.title)+'</h3>'+x.body+'</section>').join('')+'</div>'; },
    flow(labels,active=0) { return '<div class="flow">'+labels.map((x,i)=>(i?'<span class="flow-arrow" aria-hidden="true">→</span>':'')+'<div class="flow-node '+(i===active?'active':'')+'"'+(i===active?' aria-current="step"':'')+'>'+esc(x)+'</div>').join('')+'</div>'; },
    table(headers, rows, label='') { return '<div class="table-wrap"><table>'+(label?'<caption>'+esc(label)+'</caption>':'')+'<thead><tr>'+headers.map(x=>'<th scope="col">'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+r.map(x=>'<td>'+esc(fmt(x))+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'; },
    matrix(rows, rowLabels=[], colLabels=[], label='') {
      const max = Math.max(1,...rows.flat().filter(Number.isFinite).map(Math.abs));
      return '<div class="matrix-wrap"><table class="matrix">'+(label?'<caption>'+esc(label)+'</caption>':'')+'<thead><tr><th></th>'+(colLabels.length?colLabels:rows[0]?.map((_,i)=>i+1)||[]).map(x=>'<th scope="col">'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+rows.map((r,i)=>'<tr><th scope="row">'+esc(rowLabels[i]??i+1)+'</th>'+r.map(v=>'<td style="background:rgba('+(v<0?'185,95,65':'32,77,193')+','+(Number.isFinite(v)?(.05+.28*Math.abs(v)/max):.04)+')">'+esc(fmt(v))+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
    },
    bars(labels, values, label='') {
      const max=Math.max(1e-9,...values.map(v=>Math.abs(Number(v)||0)));
      return title(label)+'<div class="bars" role="img" aria-label="'+esc(label+': '+labels.map((l,i)=>l+' '+fmt(values[i])).join('; '))+'">'+labels.map((l,i)=>'<div class="bar-column"><div class="bar-value">'+esc(fmt(values[i]))+'</div><div class="bar-track"><div class="bar '+(values[i]<0?'negative':'')+'" style="height:'+(Math.abs(Number(values[i])||0)/max*100)+'%;min-height:0"></div></div><div class="bar-label">'+esc(l)+'</div></div>').join('')+'</div>';
    },
    vectors(vectors,label='') {
      const max=Math.max(1,...vectors.flatMap(v=>[Math.abs(v.x),Math.abs(v.y)]));
      const scale=130/max, colors=['#146952','#204dc1','#b56727','#8f3d77'];
      return title(label)+'<svg class="vector-chart" viewBox="0 0 420 340" role="img" aria-label="'+esc(label)+'"><line x1="30" y1="170" x2="390" y2="170" stroke="#bdccd4"/><line x1="210" y1="15" x2="210" y2="325" stroke="#bdccd4"/><text x="395" y="166" font-size="12">x</text><text x="216" y="16" font-size="12">y</text>'+vectors.map((v,i)=>{const x=210+v.x*scale,y=170-v.y*scale;return '<line x1="210" y1="170" x2="'+x+'" y2="'+y+'" stroke="'+colors[i%4]+'" stroke-width="3"/><circle cx="'+x+'" cy="'+y+'" r="5" fill="'+colors[i%4]+'"/><text x="'+Math.min(315,Math.max(10,x+8))+'" y="'+Math.max(24,y-9)+'" font-size="12" fill="'+colors[i%4]+'">'+esc(v.label)+' ('+esc(fmt(v.x))+', '+esc(fmt(v.y))+')</text>';}).join('')+'</svg>';
    }
  };
})();
