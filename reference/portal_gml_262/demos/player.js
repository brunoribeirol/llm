'use strict';
(() => {
  const data=JSON.parse(document.getElementById('demo-data').textContent), H=window.DEMO_H;
  const $=id=>document.getElementById(id);
  let current=0, state=Object.fromEntries(data.controls.map(c=>[c.key,c.value]));
  const defaults=()=>Object.fromEntries(data.controls.map(c=>[c.key,c.value]));
  const initial=location.hash.match(/^#etapa-(\d+)$/);
  if(initial) current=Math.max(0,Math.min(data.steps.length-1,Number(initial[1])-1));
  $('lesson-label').textContent='Aula '+String(data.id).padStart(2,'0')+' · Laboratório visual';
  $('lesson-title').textContent=data.title;
  $('lesson-subtitle').textContent=data.subtitle;
  $('outline-label').textContent=data.steps.length+' etapas · navegação livre';
  $('outline').innerHTML=data.steps.map((s,i)=>'<button class="navstep" data-step="'+i+'"><span>'+String(i+1).padStart(2,'0')+'</span>'+H.escape(s.title)+'</button>').join('');
  $('controls').innerHTML=data.controls.map(c=>{
    const id='control-'+c.key, label='<label for="'+H.escape(id)+'">'+H.escape(c.label)+(c.type==='range'?'<output id="output-'+H.escape(c.key)+'">'+H.escape(c.value)+'</output>':'')+'</label>';
    let input;
    if(c.type==='select') input='<select id="'+H.escape(id)+'" data-key="'+H.escape(c.key)+'">'+c.options.map(o=>'<option value="'+H.escape(o.value)+'"'+(o.value===c.value?' selected':'')+'>'+H.escape(o.label)+'</option>').join('')+'</select>';
    else if(c.type==='checkbox') input='<input type="checkbox" id="'+H.escape(id)+'" data-key="'+H.escape(c.key)+'"'+(c.value?' checked':'')+'>';
    else if(c.type==='range') input='<input type="range" id="'+H.escape(id)+'" data-key="'+H.escape(c.key)+'" min="'+c.min+'" max="'+c.max+'" step="'+(c.step??1)+'" value="'+c.value+'">';
    else input='<input type="text" id="'+H.escape(id)+'" data-key="'+H.escape(c.key)+'" value="'+H.escape(c.value)+'" maxlength="'+(c.maxLength??500)+'">';
    return '<div class="control" data-control="'+H.escape(c.key)+'">'+label+input+'</div>';
  }).join('');
  if(!data.teacher) $('teacher').remove();
  if(data.references?.length) $('references').innerHTML='<strong>Referências da aula</strong><ul>'+data.references.map(r=>{
    if(typeof r==='string')return '<li>'+H.escape(r)+'</li>';
    return /^https:\/\//.test(r.url||'')?'<li><a href="'+H.escape(r.url)+'" target="_blank" rel="noopener noreferrer">'+H.escape(r.title||r.label||r.url)+'</a></li>':'<li>'+H.escape(r.title||r.label||'')+'</li>';
  }).join('')+'</ul>';
  function renderVisual(){
    const s=data.steps[current];
    $('visual').innerHTML=window.DEMO_SIMULATORS[data.id](state,s,H);
    document.querySelectorAll('[data-control]').forEach(el=>el.classList.toggle('relevant',(s.controls||[]).includes(el.dataset.control)));
    $('control-hint').textContent=s.controls?.length?'Os valores são mantidos entre etapas. Comece pelos controles destacados.':'Altere os controles e compare os resultados. Os valores são mantidos entre etapas.';
    window.lessonSnapshot={lesson:data.id,step:current,view:s.view,state:{...state}};
  }
  function render(){
    const s=data.steps[current];
    $('title').textContent=s.title;
    $('stage-path').textContent='Etapa '+(current+1)+' de '+data.steps.length+' · '+(data.nodes[s.focus]||'Síntese');
    for(const key of ['explanation','action','question','answer']) $(key).textContent=s[key];
    if(data.teacher){$('speech').textContent=s.speech;$('board').textContent=s.board;}
    $('process').innerHTML=H.flow(data.nodes,s.focus);
    const mechanism=data.flowcharts.mechanisms[s.flowchart];
    $('flowchart').innerHTML=mechanism||data.flowcharts.overview[s.focus]||data.flowcharts.overview[0];
    $('flowchart-label').textContent=mechanism?'Fluxograma do mecanismo · abrir para acompanhar':'Fluxograma do percurso · abrir para se localizar';
    $('overview-box').hidden=!mechanism;
    $('flowchart-overview').innerHTML=mechanism?(data.flowcharts.overview[s.focus]||data.flowcharts.overview[0]):'';
    $('counter').textContent=(current+1)+' / '+data.steps.length;
    $('progress').style.width=((current+1)/data.steps.length*100)+'%';
    $('progress-track').setAttribute('aria-valuemax',String(data.steps.length));
    $('progress-track').setAttribute('aria-valuenow',String(current+1));
    $('back').disabled=current===0;$('next').disabled=current===data.steps.length-1;
    $('answer-box').open=false;
    document.querySelectorAll('[data-step]').forEach(b=>{if(Number(b.dataset.step)===current)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');});
    renderVisual();
  }
  function go(index,focus=false){
    current=Math.max(0,Math.min(data.steps.length-1,Number(index)||0));render();
    // Sandboxed srcdoc frames may reject History API updates; navigation must still work.
    try{history.replaceState(null,'','#etapa-'+String(current+1).padStart(2,'0'));}catch{}
    if(focus){$('title').focus({preventScroll:true});$('title').scrollIntoView({block:'start',behavior:'instant'});}
  }
  function syncControls(){
    for(const c of data.controls){const el=$('control-'+c.key);if(c.type==='checkbox')el.checked=state[c.key];else el.value=state[c.key];if(c.type==='range')$('output-'+c.key).textContent=state[c.key];}
  }
  function updateControl(e){
    const el=e.target,c=data.controls.find(c=>c.key===el.dataset.key);if(!c)return;
    state[c.key]=c.type==='checkbox'?el.checked:typeof c.value==='number'?Number(el.value):el.value;
    if(c.type==='range')$('output-'+c.key).textContent=state[c.key];
    renderVisual();
  }
  $('controls').addEventListener('input',updateControl);
  $('outline').addEventListener('click',e=>{const b=e.target.closest('[data-step]');if(b)go(Number(b.dataset.step),true);});
  $('flowchart-box').addEventListener('click',e=>{const b=e.target.closest('[data-flow-focus]');if(!b)return;const index=data.steps.findIndex(s=>s.focus===Number(b.dataset.flowFocus));if(index>=0)go(index,true);});
  $('back').addEventListener('click',()=>go(current-1,true));$('next').addEventListener('click',()=>go(current+1,true));
  $('reset').addEventListener('click',()=>{state=defaults();syncControls();renderVisual();});
  $('begin').addEventListener('click',()=>go(0,true));
  function presentation(on){document.body.classList.toggle('present',on);$('presentation').setAttribute('aria-pressed',String(on));$('presentation').textContent=on?'Sair da projeção':'Modo projeção';}
  $('presentation').addEventListener('click',()=>presentation(!document.body.classList.contains('present')));
  $('print').addEventListener('click',()=>window.print());
  document.addEventListener('keydown',e=>{if(e.ctrlKey||e.altKey||e.metaKey||['INPUT','SELECT','TEXTAREA','SUMMARY'].includes(e.target.tagName))return;if(e.key==='ArrowRight'){e.preventDefault();go(current+1,true);}if(e.key==='ArrowLeft'){e.preventDefault();go(current-1,true);}});
  window.addEventListener('hashchange',()=>{const m=location.hash.match(/^#etapa-(\d+)$/);if(m)go(Number(m[1])-1);});
  window.lesson={steps:data.steps,go,resetAll(){state=defaults();syncControls();go(0);},setControl(key,value){if(!data.controls.some(c=>c.key===key))throw Error('Controle desconhecido');state[key]=value;syncControls();renderVisual();}};
  presentation(Boolean(data.presentation));render();
})();
