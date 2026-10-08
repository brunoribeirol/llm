// Execute every view at defaults, control boundaries and combinations, offline.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../demos');
const context={window:{},console,TextEncoder,TextDecoder};vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,'helpers.js'),'utf8'),context);
const groups=process.argv.slice(2).length?process.argv.slice(2):['foundations','training','systems'];
for(const file of groups) vm.runInContext(fs.readFileSync(path.join(root,`simulators-${file}.js`),'utf8'),context);
const H=context.window.DEMO_H;
if(context.window.DEMO_FOUNDATION_MATH){
  const M=context.window.DEMO_FOUNDATION_MATH;
  const probabilities=M.softmax([1000,999,998]);
  assert(Math.abs(probabilities.reduce((a,b)=>a+b,0)-1)<1e-12);
  const a=M.attention(4,2,true,true);
  a.weights.forEach((row,i)=>{assert(Math.abs(row.reduce((x,y)=>x+y,0)-1)<1e-12);row.forEach((w,j)=>{if(j>i)assert.equal(w,0);});});
  assert.equal(a.output.length,4);assert.equal(a.output[0].length,2);
  const training=M.trainHead(20,.2);
  assert(training.history.at(-1)<training.history[0]);
  for(let i=1;i<training.history.length;i++)assert(training.history[i]<=training.history[i-1]+1e-12);
  const text='casa casas';assert.equal(M.bpe(5,text).pieces.join(''),text);
  assert(M.bpe(5,text).pieces.length<=M.bpe(0,text).pieces.length);
  assert(/height:0%;min-height:0/.test(H.bars(['zero'],[0])));
}
let renders=0;const summaries=[];
for(let id=0;id<=30;id++){
  if(id===6)continue;
  if(!groups.includes(id<11?'foundations':id<21?'training':'systems'))continue;
  const data=JSON.parse(fs.readFileSync(path.join(root,'lessons',`${String(id).padStart(2,'0')}.json`),'utf8'));
  const simulate=context.window.DEMO_SIMULATORS[id];assert.equal(typeof simulate,'function',`Missing simulator ${id}`);
  const defaults=Object.fromEntries(data.controls.map(c=>[c.key,c.value]));
  const scenarios=[defaults];
  for(const c of data.controls){
    const values=c.type==='range'?[c.min,c.max]:c.type==='checkbox'?[false,true]:c.type==='select'?c.options.map(o=>o.value):['','baixo baixo alta','<img src=x onerror=alert(1)>'];
    for(const value of values)scenarios.push({...defaults,[c.key]:value});
  }
  scenarios.push(Object.fromEntries(data.controls.map(c=>[c.key,c.type==='range'?c.min:c.value])));
  scenarios.push(Object.fromEntries(data.controls.map(c=>[c.key,c.type==='range'?c.max:c.value])));
  const unique=new Set(), responsive=new Set();
  for(const [index,step] of data.steps.entries()){
    const original=simulate(defaults,step,H);unique.add(original);
    for(const state of scenarios){
      const html=simulate(state,step,H);renders++;
      assert.equal(typeof html,'string',`Lesson ${id}, step ${index}`);
      assert(html.length>60,`Empty visualization ${id}/${index}`);
      assert(!/\bNaN\b|\bundefined\b/.test(html),`Non-finite/missing output ${id}/${index}: ${html}`);
      assert(!/<img\s+src=x\s+onerror=alert/.test(html),`Unescaped user input ${id}/${index}`);
      if(html!==original)responsive.add(index);
    }
  }
  assert(unique.size>=5,`Lesson ${id}: only ${unique.size} distinct visualizations`);
  assert(responsive.size>=5,`Lesson ${id}: only ${responsive.size} responsive steps`);
  summaries.push({id,steps:data.steps.length,distinct_visuals:unique.size,responsive_steps:responsive.size,scenarios:scenarios.length});
}
fs.writeFileSync(path.resolve(__dirname,'../verification/demo-simulators'+(groups.length===3?'':'-'+groups.join('-'))+'.json'),JSON.stringify({renders,lessons:summaries},null,2));
console.log(`${renders} simulation renders validated across ${summaries.length} new demonstrations.`);
