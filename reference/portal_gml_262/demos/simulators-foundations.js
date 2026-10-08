'use strict';
(() => {
  window.DEMO_SIMULATORS ||= {};
  const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
  const norm=a=>Math.sqrt(dot(a,a));
  const sigmoid=x=>1/(1+Math.exp(-x));
  const softmax=a=>{const m=Math.max(...a),e=a.map(x=>Math.exp(x-m)),z=e.reduce((a,b)=>a+b,0);return e.map(x=>x/z);};
  const cosine=(a,b)=>dot(a,b)/(norm(a)*norm(b)||1);
  const f=(x,n=4)=>Number(x.toFixed(n));
  const sum=a=>a.reduce((a,b)=>a+b,0);
  const words=t=>String(t).trim().toLowerCase().split(/\s+/u).filter(Boolean);
  const textOf=(s,key='text')=>String(s[key]??'').slice(0,240);
  const normalized=s=>{let t=textOf(s);if(s.normalize==='NFC'||s.normalize==='lower')t=t.normalize('NFC');return s.normalize==='lower'?t.toLowerCase():t;};
  const note=(H,t)=>'<p class="simulation-note">'+H.escape(t)+'</p>';
  const cards=(H,items)=>H.cards(items.map(([title,body])=>({title,body:H.escape(body)})));
  const metrics=(H,items)=>'<div class="cards">'+items.map(x=>H.metric(...x)).join('')+'</div>';
  const register=(id,fn)=>{window.DEMO_SIMULATORS[id]=fn;window.DEMO_SIMULATORS[String(id).padStart(2,'0')]=fn;};
  const vocabVectors=[{label:'carro',x:1,y:.15},{label:'automóvel',x:.9,y:.3},{label:'gato',x:-.3,y:1},{label:'banco',x:.1,y:-.9}];
  function mergeSequence(seq,a,b){const out=[];for(let i=0;i<seq.length;i++){if(seq[i]===a&&seq[i+1]===b){out.push(a+b);i++;}else out.push(seq[i]);}return out;}
  function pairsOf(corpus){const counts=new Map();for(const w of corpus)for(let i=0;i<w.seq.length-1;i++){const k=JSON.stringify([w.seq[i],w.seq[i+1]]);counts.set(k,(counts.get(k)||0)+w.count);}return [...counts].map(([k,count])=>({pair:JSON.parse(k),count})).sort((a,b)=>b.count-a.count||JSON.stringify(a.pair).localeCompare(JSON.stringify(b.pair),'en'));}
  function bpe(n,text){
    let corpus=[['casa',5],['casas',3],['casaco',2],['caso',2]].map(([word,count])=>({word,count,seq:[...word,'▁']}));
    const base=[...new Set(corpus.flatMap(x=>x.seq))].sort();const rules=[],history=[];
    for(let i=0;i<n;i++){const pairs=pairsOf(corpus);if(!pairs.length)break;const best=pairs[0];rules.push(best.pair);history.push({pair:best.pair,count:best.count});corpus=corpus.map(w=>({...w,seq:mergeSequence(w.seq,...best.pair)}));}
    const pieces=[];for(const part of String(text).split(/(\s+)/u)){if(!part)continue;if(/^\s+$/u.test(part)){pieces.push(...part);continue;}let seq=[...part,'▁'];for(const r of rules)seq=mergeSequence(seq,...r);for(const p of seq){const cleaned=p.replaceAll('▁','');if(cleaned)pieces.push(cleaned);}}
    const vocab=[...new Set([...base,...rules.map(r=>r.join('')),...base.map(x=>x.replaceAll('▁','')),...rules.map(r=>r.join('').replaceAll('▁','')),' '].filter(Boolean))];
    return {corpus,rules,history,pairs:pairsOf(corpus),pieces,vocab,ids:pieces.map(p=>vocab.indexOf(p)),base};
  }
  function trainVector(steps,lr,neg=2){
    const positive=[1,.3],negative=[[-.7,.8],[-.5,-.7],[.1,-1],[-1,.1],[.3,-.9]].slice(0,neg);let v=[.2,.4];const history=[];
    const loss=v=>-Math.log(sigmoid(dot(v,positive)))-sum(negative.map(u=>Math.log(sigmoid(-dot(v,u)))));
    history.push(loss(v));for(let i=0;i<steps;i++){const grad=positive.map(x=>(sigmoid(dot(v,positive))-1)*x);for(const u of negative){const p=sigmoid(dot(v,u));for(let j=0;j<2;j++)grad[j]+=p*u[j];}v=v.map((x,j)=>x-lr*grad[j]);history.push(loss(v));}
    return {v,positive,negative,history,initial:[.2,.4],loss:history.at(-1)};
  }
  function trainHead(steps,lr){let logits=[.3,-.2,.1,0];const history=[];const target=1;history.push(-Math.log(softmax(logits)[target]));for(let i=0;i<steps;i++){const p=softmax(logits);logits=logits.map((x,j)=>x-lr*(p[j]-(j===target?1:0)));history.push(-Math.log(softmax(logits)[target]));}return {logits,p:softmax(logits),history,target};}
  function attention(T,d,scaled=true,causal=true){
    const Q=Array.from({length:T},(_,i)=>Array.from({length:d},(_,j)=>Math.sin((i+1)*.7+j*.3)));
    const K=Array.from({length:T},(_,i)=>Array.from({length:d},(_,j)=>Math.cos((i+1)*.4-j*.2)));
    const V=Array.from({length:T},(_,i)=>Array.from({length:d},(_,j)=>Math.sin(i+1+j*.5)));
    const scores=Q.map(q=>K.map(k=>dot(q,k)/(scaled?Math.sqrt(d):1)));
    const masked=scores.map((r,i)=>r.map((v,j)=>causal&&j>i?-Infinity:v));const weights=masked.map(softmax);
    const output=weights.map(r=>Array.from({length:d},(_,c)=>sum(r.map((a,j)=>a*V[j][c]))));return {Q,K,V,scores,masked,weights,output};
  }
  window.DEMO_FOUNDATION_MATH={softmax,bpe,trainVector,trainHead,attention,cosine};

  register(0,(s,step,H)=>{
    const labs=['Tokenizadores e embeddings','Mini-GPT','Decodificação e prompting','LoRA/QLoRA','Pipeline RAG','Tool calling e MCP','Agente autônomo','Harness de avaliação'];
    const next=labs[Math.min(7,s.done)];
    switch(step.view){
      case 'map':return H.flow(['Texto','Transformer','Adaptação','RAG','Ferramentas','Agente','Avaliação'],Math.min(6,Math.floor(s.done*.85)))+H.metric('Artefatos de laboratório concluídos',s.done,'Meta completa: oito produtos progressivos');
      case 'diagnosis':return H.bars(['Python','Álgebra'],[s.python,s.math],'Autoavaliação: 0 a 4')+cards(H,[['Python',s.python<2?'Revisar listas, funções e operações com arrays; executar um exemplo pequeno.':'Executar o exemplo de matrizes e explicar os shapes.'],['Álgebra',s.math<2?'Revisar vetor, produto interno e soma ponderada com três números.':'Calcular cosseno e uma linha de softmax à mão.']]);
      case 'layers':return H.table(['Camada','Evidência construída'],[['Representação','Segmentação e vetores'],['Arquitetura','Atenção e mini-GPT'],['Treino','Perda e validação'],['Adaptação','Modelo ajustado e comparação'],['Recuperação','Documentos, citações e métricas'],['Agentes','Trajetória de ações e limites'],['Avaliação','Conjunto de testes e relatório']],'O mapa técnico do semestre')+H.metric('Próximo laboratório',next);
      case 'time':return H.bars(['Leitura','Implementação','Análise'],[s.hours*.25,s.hours*.5,s.hours*.25],'Sugestão de horas semanais')+H.metric('Tempo semanal disponível',s.hours,'Divisão ilustrativa 25% / 50% / 25%');
      case 'grades':return H.bars(['Labs × 0,3','Prova × 0,3','Projeto × 0,4'],[s.labs*.3,s.exam*.3,s.project*.4],'Contribuições para a nota ponderada')+H.metric('Nota simulada',s.labs*.3+s.exam*.3+s.project*.4,'Média de labs já deve considerar o descarte da menor nota.');
      case 'labs':return H.table(['Laboratório','Produto','Situação simulada'],labs.map((x,i)=>[i+1,x,i<s.done?'Concluído':i===s.done?'Próximo':'A seguir']));
      case 'materials':return cards(H,[['Plano de aula','O que aprender e qual evidência demonstra isso.'],['Demonstração','Alterar uma condição e observar um mecanismo.'],['Notebook','Executar o experimento completo e registrar a configuração.'],['Guia de estudo','Revisar conceitos, perguntas e critérios de conclusão.']]);
      case 'evidence':return H.flow(['Registrar ajuda','Executar verificação','Explicar resultado','Documentar limites'],Math.min(3,s.done))+cards(H,[['Artefato atual',next],['Registro que acompanha','Entradas, configuração, versões, saída observada e explicação própria.'],['Responsabilidade','Conferir a política do curso e declarar o uso de ferramentas de IA conforme o contrato.']]);
      case 'setup':return H.flow(['Criar ambiente','Instalar dependências','Importar bibliotecas','Rodar exemplo','Registrar versões'],Math.min(4,s.python))+note(H,'Checklist de preparação; nenhum comando do seu computador é executado por esta visualização.');
      default:return cards(H,[['Próximo passo',s.done<8?'Preparar '+next:'Consolidar os oito artefatos e o relatório final.'],['Tempo reservado',s.hours+' horas por semana; '+f(s.hours*.25,1)+' para revisão e interpretação.'],['Critério de conclusão','Outra pessoa consegue reproduzir o exemplo e você consegue explicar um resultado.']]);
    }
  });

  register(1,(s,step,H)=>{
    const tp=+s.tp,fp=+s.fp,fn=100-tp,tn=9900-fp,P=tp+fp?tp/(tp+fp):null,R=tp/100,F=P&&R?(1+s.beta*s.beta)*P*R/(s.beta*s.beta*P+R):0;
    const c=words(textOf(s,'candidate')),r=words(textOf(s,'reference')),cm=new Map(),rm=new Map();c.forEach(x=>cm.set(x,(cm.get(x)||0)+1));r.forEach(x=>rm.set(x,(rm.get(x)||0)+1));const hit=sum([...cm].map(([x,n])=>Math.min(n,rm.get(x)||0))),prec=c.length?hit/c.length:0,rec=r.length?hit/r.length:0,bp=c.length?Math.exp(Math.min(0,1-r.length/c.length)):0;
    const task={sentiment:['texto → rótulo','O aplicativo ficou ótimo.','positivo'],entities:['texto → entidades','Ana visitou Recife.','Ana: pessoa; Recife: local'],translation:['texto → texto','O gato dorme.','The cat sleeps.'],summary:['texto → texto','A equipe corrigiu a falha e publicou uma versão.','Equipe lança correção.']}[s.task];
    switch(step.view){
      case 'history':return H.flow(['Regras','Contagens','Vetores','Atenção','Instruções'],['sentiment','entities','translation','summary'].indexOf(s.task))+cards(H,[['Tarefa escolhida',task[0]],['Progresso conceitual','Representações e mecanismos mais flexíveis transferem trabalho para dados, computação e avaliação.']]);
      case 'task':return cards(H,[['Assinatura',task[0]],['Entrada ilustrativa',task[1]],['Saída escrita para a aula',task[2]]]);
      case 'next':return H.bars(['Token correto','Alternativa A','Alternativa B','Alternativa C'],[s.prob,...Array(3).fill((1-s.prob)/3)],'Uma distribuição ilustrativa')+H.metric('Probabilidade de três acertos condicionais iguais',s.prob**3);
      case 'confusion':return H.table(['Real / previsto','Alerta','Liberado'],[['Fraude',tp,fn],['Legítima',fp,tn]],'Matriz de confusão — N = 10.000');
      case 'baseline':return metrics(H,[['Acurácia atual',(tp+tn)/10000],['Piso de nunca alertar',.99],['Revocação atual',R]])+H.bars(['Fraudes detectadas','Fraudes perdidas'],[tp,fn],'A função do detector');
      case 'pr':return metrics(H,[['Precisão',P===null?'Indefinida: nenhum alerta':P,'Denominador: TP + FP'],['Revocação',R,'Denominador: 100 fraudes']])+H.table(['Grupo','Quantidade'],[['Alertas emitidos',tp+fp],['Fraudes reais',100]]);
      case 'fscore':return H.bars(['Precisão','Revocação','Fβ'],[P??0,R,F],'Média harmônica ponderada')+note(H,P===null?'Sem alertas: precisão indefinida; Fβ reportado como zero por convenção.':'β² = '+s.beta*s.beta+' é o peso relativo de revocação nesta combinação.');
      case 'cost':return H.bars(['Atual','Nunca alertar','Alertar tudo'],[fp+s.cost*fn,s.cost*100,9900],'Custo em unidades de falso positivo')+H.metric('Custo de um falso negativo',s.cost);
      case 'overlap':return H.table(['Palavra','No candidato','Na referência','Correspondências'],[...new Set([...c,...r])].map(x=>[x,cm.get(x)||0,rm.get(x)||0,Math.min(cm.get(x)||0,rm.get(x)||0)]),'Contagem truncada por palavra');
      case 'generation':return metrics(H,[['Precisão de unigramas',prec],['Penalidade BP',bp],['BLEU-1 didático',bp*prec],['ROUGE-1 (revocação)',rec]])+note(H,'Divisão por espaços e minúsculas; sem BLEU-4, stemming ou comparação semântica. Textos limitados a 240 caracteres nesta miniatura.');
      case 'perplexity':return H.bars(['p','Surpresa −ln(p)','PPL'],[s.prob,-Math.log(s.prob),1/s.prob],'Números em unidades diferentes — leia os rótulos')+H.table(['p','H','PPL'],[.1,.25,.5,.9].map(p=>[p,-Math.log(p),1/p]));
      default:return cards(H,[['Sobreposição medida','BLEU-1 = '+f(bp*prec)+'; ROUGE-1 = '+f(rec)+'.'],['Inspeção humana necessária','O candidato afirma o mesmo fato? Há negação, número ou entidade trocada?'],['Critério da aplicação','Registre a falha que esta métrica consegue detectar e aquela que exige uma avaliação complementar.']]);
    }
  });

  register(2,(s,step,H)=>{
    const t=normalized(s),b=bpe(s.merges,t),w=words(t).length,n=b.pieces.length,F=w?n/w:0,bytes=[...new TextEncoder().encode(t)];
    const chips=H=>'<div class="flow">'+b.pieces.map(p=>'<span class="flow-node">'+H.escape(p===' '?'␠':p)+'</span>').join('')+'</div>';
    switch(step.view){
      case 'text':return cards(H,[['Texto observado',t||'(vazio)']])+metrics(H,[['Pontos de código',[...t].length],['Palavras',w],['Bytes UTF-8',bytes.length]]);
      case 'unicode':return H.table(['Símbolo','Código Unicode'],[...t].slice(0,40).map(c=>[c===' '?'␠':c,'U+'+c.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')]),'Primeiros 40 pontos de código após normalização');
      case 'units':return H.bars(['Palavras','Caracteres','Mini-BPE','Bytes'],[w,[...t].length,n,bytes.length],'Unidades diferentes sobre a mesma entrada')+note(H,'Mini-BPE preserva espaços; caracteres contam pontos de código. As fronteiras, portanto, também importam.');
      case 'corpus':return H.table(['Palavra','Frequência','Símbolos atuais'],b.corpus.map(x=>[x.word,x.count,x.seq.join(' · ')]),'Corpus fixo de treinamento');
      case 'pairs':return H.table(['Par candidato','Contagem ponderada'],b.pairs.map(x=>[x.pair.join(' + '),x.count]),'Pares disponíveis para o próximo merge')+H.metric('Regras já aprendidas',b.rules.length);
      case 'merge':return H.table(['Ordem','Par fundido','Frequência no momento'],b.history.map((x,i)=>[i+1,x.pair.join(' + '),x.count]),'Histórico ordenado de treinamento')+H.table(['Palavra','Estado após as fusões'],b.corpus.map(x=>[x.word,x.seq.join(' · ')]));
      case 'encode':return H.flow(['Corpus fixo','Lista ordenada de regras','Texto novo','Aplicação das regras'],3)+chips(H)+note(H,'Fronteira ▁ auxilia as regras; espaços reais são preservados na saída. Alfabeto básico restrito ao corpus didático.');
      case 'ids':return H.table(['Peça','ID no vocabulário didático'],b.pieces.map((p,i)=>[p===' '?'␠':p,b.ids[i]<0?'UNK (fora do alfabeto)':b.ids[i]]))+note(H,'IDs são estáveis para a mesma lista de regras; desconhecidos não são apresentados como tokens de um sistema byte-level.');
      case 'bytes':return H.table(['Caractere','Bytes UTF-8 em hexadecimal'],[...t].slice(0,30).map(c=>[c===' '?'␠':c,[...new TextEncoder().encode(c)].map(x=>x.toString(16).padStart(2,'0')).join(' ')]),'Representação UTF-8 real')+H.metric('Total de bytes',bytes.length);
      case 'families':return H.table(['Família','Ideia','O que esta tela executa'],[['BPE','Fusões por frequência',b.rules.length+' regras aprendidas'],['WordPiece','Construção de vocabulário e segmentação compatível','Comparação conceitual'],['Unigram','Modelo probabilístico de peças e seleção de vocabulário','Comparação conceitual']]);
      case 'budget':return metrics(H,[['Fertilidade',F||'Sem palavras'],['Custo hipotético',n*s.repeats*s.price/1e6,'Unidades monetárias; somente entrada'],['Palavras aproximadas na janela',F?Math.floor(s.window/F):'Sem texto'],['Tokens por requisição',n]])+H.table(['Entrada','Valor'],[['Requisições',s.repeats],['Preço por milhão',s.price],['Janela em tokens',s.window]]);
      default:return chips(H)+cards(H,[['Segmentação observada',n+' peças em '+w+' palavras.'],['Aritmética','IDs identificam peças; operações numéricas dependem de comportamento aprendido ou ferramentas.'],['Registro','Corpus fixo, '+b.rules.length+' merges, normalização '+s.normalize+'. Limite didático: primeiros 240 caracteres.']]);
    }
  });

  register(3,(s,step,H)=>{
    const a=s.angle*Math.PI/180,q=[s.scale*Math.cos(a),s.scale*Math.sin(a)],vec=[...vocabVectors,{label:'consulta',x:q[0],y:q[1]}],rank=vocabVectors.map(v=>[v.label,cosine(q,[v.x,v.y]),dot(q,[v.x,v.y])]).sort((a,b)=>b[1]-a[1]);
    const sentence=['o','gato','dorme','na','casa'],pairs=[];for(let i=0;i<sentence.length;i++)for(let j=Math.max(0,i-s.window);j<=Math.min(sentence.length-1,i+s.window);j++)if(i!==j)pairs.push([sentence[i],sentence[j],j-i]);const tr=trainVector(1,s.lr,s.negatives);
    switch(step.view){
      case 'lexical':return H.table(['Documento','Busca literal carro','Cosseno da consulta'],[['carro',1,rank.find(x=>x[0]==='carro')[1]],['automóvel',0,rank.find(x=>x[0]==='automóvel')[1]],['gato',0,rank.find(x=>x[0]==='gato')[1]]],'Duas formas de selecionar candidatos');
      case 'onehot':return H.matrix(Array.from({length:4},(_,i)=>Array.from({length:4},(_,j)=>+(i===j))),vocabVectors.map(v=>v.label),vocabVectors.map(v=>v.label),'Produto interno dos vetores one-hot');
      case 'contexts':return H.table(['Centro','Contexto','Deslocamento'],pairs,'Pares da frase: o gato dorme na casa')+H.metric('Quantidade de pares',pairs.length);
      case 'vectors':return H.vectors(vec,'Espaço 2D construído manualmente');
      case 'cosine':return H.vectors(vec.slice(0,2).concat(vec.at(-1)),'Direção e magnitude')+H.table(['Candidato','Cosseno','Produto interno'],rank)+H.metric('Norma da consulta',norm(q));
      case 'ranking':return H.bars(rank.map(r=>r[0]),rank.map(r=>r[1]),'Ranking por cosseno')+note(H,'A relevância não é medida: estes vetores são uma construção didática.');
      case 'proxy':return H.flow(['Contexto','CBOW: prever centro'],1)+H.flow(['Centro','Skip-gram: prever contextos'],1)+metrics(H,[['Pares skip-gram',pairs.length],['Centros CBOW',sentence.length]]);
      case 'softmax':return H.table(['Palavra','Score','Probabilidade'],vocabVectors.map((v,i)=>[v.label,dot(q,[v.x,v.y]),softmax(vocabVectors.map(x=>dot(q,[x.x,x.y])))[i]]),'Softmax completo do vocabulário didático');
      case 'negative':return H.table(['Exemplo','Alvo','Score inicial','Perda logística'],[['Contexto positivo',1,dot(tr.initial,tr.positive),-Math.log(sigmoid(dot(tr.initial,tr.positive)))],...tr.negative.map((u,i)=>['Negativo '+(i+1),0,dot(tr.initial,u),-Math.log(sigmoid(-dot(tr.initial,u)))])])+H.metric('Perda total antes',tr.history[0]);
      case 'update':return H.vectors([{label:'Antes',x:tr.initial[0],y:tr.initial[1]},{label:'Depois',x:tr.v[0],y:tr.v[1]},{label:'Contexto positivo',x:1,y:.3}],'Um passo real de SGD')+H.bars(['Antes','Depois'],tr.history,'Perda logística calculada');
      case 'analogy':return H.vectors([{label:'rei',x:1,y:1},{label:'homem',x:1,y:0},{label:'mulher',x:0,y:1},{label:'resultado/rainha',x:0,y:2}],'Analogia construída: (1,1) − (1,0) + (0,1) = (0,2)')+note(H,'Pontos escolhidos para ilustrar a operação; não são um teste empírico de analogias.');
      default:return H.vectors([{label:'banco estático',x:.1,y:-.9},{label:'contexto ilustrativo',x:s.sense==='money'?1:-1,y:s.sense==='money'?.2:.7}],'Mesmo token, contextos diferentes')+cards(H,[['Frase',s.sense==='money'?'banco aprova o crédito':'banco fica na praça'],['Limite','A posição estática não muda; o vetor contextual é uma ilustração manual de uma propriedade desejada.']]);
    }
  });

  register(4,(s,step,H)=>{
    const t=textOf(s),en=textOf(s,'english'),ptb=bpe(s.merges,t),enb=bpe(s.merges,en),wp=words(t).length,we=words(en).length,fp=wp?ptb.pieces.length/wp:0,fe=we?enb.pieces.length/we:0,tr=trainVector(s.epochs,s.lr,2);
    const cfg=[['Corpus','casa×5, casas×3, casaco×2, caso×2'],['Merges efetivos',ptb.rules.length],['Normalização','Preservar Unicode'],['Limite da entrada','240 caracteres por texto'],['Treino','Vetor central 2D; contextos fixos; SGD']];
    switch(step.view){
      case 'hypothesis':return cards(H,[['Hipótese de tokenização','Os textos terão quantidades diferentes de peças sob as mesmas regras.'],['Par português',t||'(vazio)'],['Par inglês',en||'(vazio)']]);
      case 'setup':return H.table(['Configuração','Valor'],cfg,'Ficha reproduzível')+H.metric('Regras aprendidas',ptb.rules.length);
      case 'tokenizers':return H.table(['Unidade','Português','Inglês'],[['Palavras',wp,we],['Pontos de código',[...t].length,[...en].length],['Bytes UTF-8',new TextEncoder().encode(t).length,new TextEncoder().encode(en).length],['Mini-BPE',ptb.pieces.length,enb.pieces.length]],'Comparação de algoritmos didáticos; não são tokenizadores comerciais');
      case 'pieces':return H.table(['Entrada','Peças'],[['PT',ptb.pieces.map(p=>p===' '?'␠':p).join(' · ')],['EN',enb.pieces.map(p=>p===' '?'␠':p).join(' · ')]])+note(H,'O alfabeto foi treinado num corpus minúsculo de português; esta comparação não estima a qualidade de tokenizadores de produção.');
      case 'fertility':return H.bars(['Fertilidade PT','Fertilidade EN'],[fp,fe],'Tokens por palavra')+H.table(['Texto','Tokens','Palavras'],[['PT',ptb.pieces.length,wp],['EN',enb.pieces.length,we]]);
      case 'cost':return metrics(H,[['Razão de tokens PT/EN',enb.pieces.length?ptb.pieces.length/enb.pieces.length:'Sem denominador'],['Tokens PT totais',ptb.pieces.length*s.requests],['Palavras PT na janela',fp?Math.floor(s.budget/fp):'Sem texto'],['Palavras EN na janela',fe?Math.floor(s.budget/fe):'Sem texto']]);
      case 'pairs':return H.vectors([{label:'Centro inicial',x:.2,y:.4},{label:'Positivo',x:1,y:.3},...tr.negative.map((v,i)=>({label:'Negativo '+(i+1),x:v[0],y:v[1]}))],'Dados do objetivo de contraste');
      case 'training':return H.bars(tr.history.map((_,i)=>String(i)),tr.history,'Perda por passo real de SGD')+H.metric('Perda atual',tr.loss,'Somente o vetor central recebe atualização');
      case 'learning':return H.table(['Taxa','Passos','Perda final','Vetor final'],[.05,.1,.5,1].map(lr=>{const x=trainVector(s.epochs,lr,2);return [lr,s.epochs,x.loss,x.v.map(v=>f(v)).join(', ')];}),'Mesmos dados e inicialização')+H.metric('Taxa selecionada',s.lr);
      case 'projection':{const a=s.projection*Math.PI/180,points=[['A',1,0,0],['B',1,0,2],['C',-1,1,0]];return H.vectors(points.map(([label,x,y,z])=>({label,x:x*Math.cos(a)+z*Math.sin(a),y})),'Projeção explícita 3D → 2D; não é PCA/t-SNE')+H.table(['Par','Distância 3D original'],[['A–B',2],['A–C',Math.sqrt(5)],['B–C',3]]);}
      case 'neighbors':return H.vectors([{label:'Centro treinado',x:tr.v[0],y:tr.v[1]},{label:'Positivo',x:1,y:.3},...tr.negative.map((u,i)=>({label:'Negativo '+i,x:u[0],y:u[1]}))],'Geometria após as atualizações')+H.table(['Candidato','Cosseno atual'],[['Positivo',cosine(tr.v,tr.positive)],...tr.negative.map((u,i)=>['Negativo '+i,cosine(tr.v,u)])]);
      default:return H.table(['Resultado','Valor'],[['Tokens PT / EN',ptb.pieces.length+' / '+enb.pieces.length],['Fertilidade PT / EN',f(fp)+' / '+f(fe)],['Passos / taxa',s.epochs+' / '+s.lr],['Perda antes / depois',f(tr.history[0])+' / '+f(tr.loss)],['Limite','Corpus pequeno, um vetor treinado, sem métricas externas']])+cards(H,[['Interpretação solicitada','Explique uma diferença de contagem e uma mudança da geometria usando os dados e a configuração acima.']]);
    }
  });

  register(5,(s,step,H)=>{
    const seq=s.order==='forward'?[1,-1,.5]:[.5,-1,1];let h=0;const states=seq.map((x,i)=>{const old=h;h=Math.tanh(.8*h+x);return [i+1,x,old,h];});
    const keys=[-.8,.1,1],values=[-1,.5,2],score=q=>keys.map(k=>s.scale*Math.tanh(q+k)),scores=score(s.query),p=softmax(scores),context=dot(p,values);
    switch(step.view){
      case 'symptoms':return metrics(H,[['Transições sequenciais',s.length],['Ganho acumulado',s.gain**s.length],['Caminho primeira origem → primeiro destino',s.length]])+cards(H,[['Experimento','Produtos escalares e caminhos são calculados; nenhuma qualidade de tradução está sendo estimada.']]);
      case 'unroll':return H.flow(['h₀=0',...states.map(r=>'h'+r[0]+'='+f(r[3],3))],3)+H.table(['Passo','Entrada x','Estado anterior','Estado novo'],states);
      case 'state':return H.bars(states.map(r=>'h'+r[0]),states.map(r=>r[3]),'Estados da sequência '+seq.join(', '))+H.metric('Estado final',h);
      case 'gradient':return H.table(['T','ganho^T','log₁₀ da magnitude'],[2,10,20,50,100].map(t=>[t,(s.gain**t).toExponential(4),t*Math.log10(s.gain)]),'Produto escalar isolado')+H.metric('Para T escolhido',(s.gain**s.length).toExponential(4));
      case 'regimes':return H.bars(['0,9','1','1,1'],[s.length*Math.log10(.9),0,s.length*Math.log10(1.1)],'log₁₀ da magnitude após T passos')+note(H,'Barras negativas representam ordens de grandeza abaixo de 1; não são gradientes negativos.');
      case 'parallel':return H.flow(['Entrada conhecida','h₁ calculado','h₂ depende de h₁','...','h_T disponível'],4)+H.table(['Quantidade','Valor'],[['Entradas conhecidas no treino',s.length],['Etapas na cadeia recorrente',s.length],['Peso compartilhado por transição',.8]]);
      case 'lstm':return H.bars(['Memória inicial','Memória após T'],[1,s.forget**s.length],'Caminho c_t = f c_(t−1), sem nova escrita')+H.table(['Porta f','Retenção após T'],[.9,.95,.99,1].map(x=>[x,x**s.length]));
      case 'bottleneck':return H.flow(['x₁…x_T','Encoder recorrente','Resumo h_T','Decoder'],2)+H.table(['Origem j','Passo destino t','Caminho sem atenção'],[[1,1,s.length],[Math.ceil(s.length/2),1,s.length-Math.ceil(s.length/2)+1],[s.length,1,1]]);
      case 'scores':return H.table(['Origem','Key','q + key','score = escala × tanh(q+key)'],keys.map((k,i)=>[i+1,k,s.query+k,scores[i]]));
      case 'attention':return H.bars(['Origem 1','Origem 2','Origem 3'],p,'Pesos de atenção calculados')+H.table(['α','Valor','Contribuição αv'],p.map((a,i)=>[a,values[i],a*values[i]]))+metrics(H,[['Soma dos pesos',sum(p)],['Contexto',context]]);
      case 'alignment':return H.matrix([s.query-.5,s.query,s.query+.5].map(q=>softmax(score(q))),['Passo 1','Passo 2','Passo 3'],['Origem 1','Origem 2','Origem 3'],'Alinhamento didático: scores fixados, não aprendidos');
      default:return H.table(['Mecanismo','Memória','Acesso direto à origem','Treino sem recorrência'],[['RNN','Resumo vulnerável','Não','Não'],['LSTM','Gates aprendidos','Não por si só','Não'],['RNN + atenção','Estados recorrentes','Sim','Não'],['Transformer','Atenção e blocos','Sim','Sim']])+H.metric('Distância de acesso por atenção',1,'Após os estados da origem estarem disponíveis.');
    }
  });

  register(7,(s,step,H)=>{
    const m=s.position,n=m+s.distance,a=m*s.frequency,b=n*s.frequency,rotate=(v,t)=>[v[0]*Math.cos(t)-v[1]*Math.sin(t),v[0]*Math.sin(t)+v[1]*Math.cos(t)],q=[1,.5],k=[.3,1],qr=rotate(q,a),kr=rotate(k,b),sc=dot(qr,kr);
    const x=[1,2,3,4].map(v=>v+s.offset),mean=sum(x)/4,variance=sum(x.map(v=>(v-mean)**2))/4,rms=Math.sqrt(sum(x.map(v=>v*v))/4+1e-5),ln=x.map(v=>(v-mean)/Math.sqrt(variance+1e-5)),rn=x.map(v=>v/rms),output=s.norm==='layer'?ln:rn;
    const pe=pos=>[Math.sin(pos),Math.cos(pos),Math.sin(pos/100),Math.cos(pos/100)];
    switch(step.view){
      case 'permutation':return H.table(['Token','Conteúdo antes','Conteúdo após reordenar'],[['gato','[1, 0]','[1, 0]'],['persegue','[0, 1]','[0, 1]'],['rato','[1, 1]','[1, 1]']],'Conteúdo sozinho não codifica posição')+cards(H,[['Posição selecionada',String(m)],['Informação ausente','O vetor do token permanece o mesmo até receber contexto ou informação posicional.']]);
      case 'sinusoidal':return H.matrix([pe(m),[.2,.4,.1,.3],pe(m).map((v,i)=>v+[.2,.4,.1,.3][i])],['PE(m)','Embedding','Soma'],['sin(m)','cos(m)','sin(m/100)','cos(m/100)'],'Quatro canais, d = 4')+H.metric('Posição m',m);
      case 'learned':return H.table(['Índice','Vetor ilustrativo de tabela'],Array.from({length:8},(_,i)=>[i,[Math.sin(i*.3),Math.cos(i*.6)].map(v=>f(v,3)).join(', ')]),'Tabela fixa ilustrativa: oito posições')+H.metric('Consulta na posição '+m,m<8?'Entrada existente':'Fora da tabela','Valores não treinados; tabela usada para exibir o domínio.');
      case 'rope':return H.vectors([{label:'q',x:q[0],y:q[1]},{label:'R(mθ)q',x:qr[0],y:qr[1]},{label:'R(nθ)k',x:kr[0],y:kr[1]}],'Rotação de um par de coordenadas')+H.table(['Posição','Ângulo'],[['m',a],['n',b]]);
      case 'relative':return H.table(['m','n','n−m','Produto interno'],[0,3,10,20].map(shift=>[m+shift,n+shift,s.distance,dot(rotate(q,(m+shift)*s.frequency),rotate(k,(n+shift)*s.frequency))]),'Deslocamento comum preserva o score')+H.metric('Score pela distância relativa',dot(q,rotate(k,s.distance*s.frequency)));
      case 'extrapolation':return H.bars(Array.from({length:11},(_,i)=>String(i*2)),Array.from({length:11},(_,i)=>dot(q,rotate(k,i*2*s.frequency))),'Score por distância: periodicidade de um par')+H.metric('Score na distância selecionada',sc,'Não é uma curva de qualidade de contexto longo.');
      case 'residual':return H.bars(['Sem identidade','Com identidade'],[s.depth*Math.log10(s.gain),s.depth*Math.log10(1+s.gain)],'log₁₀ da magnitude do produto escalar')+H.table(['Caminho','Ganho total'],[['g^L',(s.gain**s.depth).toExponential(4)],['(1+g)^L',((1+s.gain)**s.depth).toExponential(4)]])+note(H,'Exemplo de derivada escalar com ganho positivo; residual cria caminho direto, mas não garante gradiente estável.');
      case 'layernorm':return H.table(['Canal','x','x − média','LayerNorm'],x.map((v,i)=>[i,v,v-mean,ln[i]]))+metrics(H,[['Média original',mean],['Média após LN',sum(ln)/4],['Variância original',variance]]);
      case 'rmsnorm':return H.bars(['Canal 1','Canal 2','Canal 3','Canal 4'],output,'Saída: '+(s.norm==='layer'?'LayerNorm':'RMSNorm'))+H.table(['Métrica','LN','RMSNorm'],[['Média',sum(ln)/4,sum(rn)/4],['RMS',Math.sqrt(sum(ln.map(v=>v*v))/4),Math.sqrt(sum(rn.map(v=>v*v))/4)]]);
      case 'prenorm':return H.flow(['x','Norm(x)','F(Norm(x))','+ x'],3)+H.flow(['x','F(x)','x + F(x)','Norm da soma'],3)+cards(H,[['Norma escolhida',s.norm==='layer'?'LayerNorm':'RMSNorm'],['Pré-norm','O caminho identidade contorna a norma; pós-norm transforma a soma completa.'],['Escala do bloco','Profundidade selecionada: '+s.depth+'; este painel é um diagrama, não treino de estabilidade.']]);
      case 'ffn':return H.table(['Componente','Dimensão intermediária','Pesos sem bias'],[['FFN convencional',4*s.width,8*s.width*s.width],['FFN com gate',f(8*s.width/3,2),8*s.width*s.width],['Projeções de atenção (Q,K,V,O)',s.width,4*s.width*s.width]],'Contagem idealizada: dimensão do gate pode exigir arredondamento')+H.metric('Fração dos pesos na FFN convencional',2/3,'Ignora embeddings, normas e biases.');
      default:return H.flow(['x','Norma '+s.norm,'Atenção + RoPE','+ x','Norma','FFN','+ residual'],2)+metrics(H,[['Largura preservada',s.width],['FFN convencional',8*s.width*s.width,'Pesos sem bias'],['Distância usada no RoPE',s.distance]]);
    }
  });

  register(8,(s,step,H)=>{
    const T=s.length,Hq=s.heads,Hkv=Array.from({length:Hq},(_,i)=>i+1).filter(x=>Hq%x===0&&x<=s.kv).at(-1)||1,L=s.layers,bytes=2*L*T*Hkv*64*2,N=Math.min(T,12),mask=Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>+(s.family!=='decoder'||j<=i))),local=Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>+(Math.abs(i-j)<=s.radius)));
    const localPairs=sum(Array.from({length:T},(_,i)=>Math.min(T-1,i+s.radius)-Math.max(0,i-s.radius)+1));
    switch(step.view){
      case 'mask':return H.matrix(mask,[],[],'Máscara da família '+s.family+' — recorte de até 12 posições')+H.metric('Comprimento total configurado',T);
      case 'encoder':return H.flow(['Texto completo','Atenção bidirecional','Estado por posição','Cabeça da tarefa'],1)+H.matrix(Array.from({length:Math.min(T,6)},()=>Array(Math.min(T,6)).fill(1)),[],[],'Todos os pares do recorte podem interagir');
      case 'mlm':return H.flow(['o','gato','[MASK]','no','sofá'],2)+cards(H,[['Tarefa','Reconstruir a lacuna usando os dois lados.'],['Exemplos ilustrativos','dorme / deita / brinca; sem execução de modelo ou probabilidade real.'],['Entrada configurada',T+' posições disponíveis no exemplo de orçamento.']]);
      case 'classification':return H.flow(['Texto com '+T+' tokens','Encoder','Vetor agregado','Scores de classes','Rótulo'],3)+H.table(['Tarefa','Objeto de saída'],[['Classificação','Um rótulo por entrada'],['Rotulagem','Um rótulo por posição'],['Geração','Sequência de comprimento variável']]);
      case 'seq2seq':return H.flow(['Origem completa','Encoder','Memória da origem'],2)+H.flow(['Prefixo do destino','Self-attention causal','Cross-attention à memória','Próximo token'],2)+H.table(['Relação','Máscara'],[['Origem → origem','Bidirecional'],['Destino → destino','Causal'],['Destino → origem','Toda a origem disponível']])+H.metric('Comprimento de origem no orçamento',T);
      case 'decoder':return H.matrix(Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>+(j<=i))),[],[],'Acesso causal')+H.flow(['Prefixo','Distribuição final','Token escolhido','Prefixo ampliado'],2);
      case 'cacheflow':return H.flow(['K,V de '+T+' posições','Novo token gera Q,K,V','Q consulta cache ampliado','Guardar novo K,V'],2)+H.table(['Recurso','Dimensões'],[['K por camada','[1, '+Hkv+', '+T+', 64]'],['V por camada','[1, '+Hkv+', '+T+', 64]'],['Cache completo',L+' camadas × 2 tensores']]);
      case 'cache':return metrics(H,[['Cache KV em bytes',bytes],['Cache KV em KiB',bytes/1024],['Cabeças KV efetivas',Hkv],['Cabeças de query',Hq]])+note(H,'B=1, d_head=64, 2 bytes/elemento. Ajuste para o maior divisor de H_Q não maior que KV solicitado; sem pesos ou temporários.');
      case 'local':return H.matrix(local,[],[],'Janela local bidirecional — recorte')+metrics(H,[['Pares densos',T*T],['Pares locais exatos',localPairs],['Alcance por lado após L camadas (limite)',Math.min(T-1,L*s.radius)]])+note(H,'Atenção global não incluída nesta matriz; o alcance é um limite estrutural, não qualidade garantida.');
      case 'gqa':return H.table(['Cabeça query','Grupo KV compartilhado'],Array.from({length:Hq},(_,i)=>[i,Math.floor(i*Hkv/Hq)]),'Agrupamento uniforme válido')+H.bars(['Cache MHA','Cache escolhido'],[2*L*T*Hq*64*2,bytes],'Bytes nas mesmas condições');
      case 'distillation':return H.table(['Classe','Logit docente','p(T=1)','p(T escolhido)'],[4,2,1,0].map((x,i)=>['Classe '+(i+1),x,softmax([4,2,1,0])[i],softmax([4,2,1,0].map(x=>x/s.temperature))[i]]),'Distribuições calculadas de logits didáticos');
      default:return H.table(['Família','Uso natural','Leitura'],[['Encoder','Representações e classificação','Entrada completa'],['Encoder–decoder','Transformar uma origem em destino','Origem inteira; destino causal'],['Decoder','Continuação e interface gerativa','Prefixo causal']])+cards(H,[['Escolha atual',s.family+'; contexto '+T+'; cache hipotético '+f(bytes/1024,1)+' KiB.'],['Próxima evidência','Medir qualidade na tarefa e memória/latência com implementação e carga reais.']]);
    }
  });

  register(9,(s,step,H)=>{
    const T=s.length,d=s.dim,heads=s.heads,dh=d/heads,A=attention(T,dh,s.scaled,s.causal),labels=Array.from({length:T},(_,i)=>String(i)),tr=trainHead(s.updates,s.lr),sampleText=[...'o gato dorme'],next=softmax(tr.logits.map(x=>x/s.temperature));
    switch(step.view){
      case 'dataset':return H.table(['Posição','Entrada x','Alvo y (deslocado)'],Array.from({length:T},(_,i)=>[i,sampleText[i]===' '?'␠':sampleText[i],sampleText[i+1]===' '?'␠':sampleText[i+1]]),'Uma posição, um alvo de próximo caractere');
      case 'shapes':return H.table(['Tensor','Shape'],[['X','[1, '+T+', '+d+']'],['Q/K/V após reshape','[1, '+heads+', '+T+', '+dh+']'],['Scores','[1, '+heads+', '+T+', '+T+']'],['Concatenação','[1, '+T+', '+d+']']])+H.metric('d_head = d/H',dh);
      case 'qkv':return H.matrix(A.Q,labels,[],'Q determinístico — primeira cabeça')+H.matrix(A.K,labels,[],'K determinístico — primeira cabeça')+note(H,'Q, K e V são preenchidos por fórmulas trigonométricas para permitir inspeção, com d_head canais cada. Não são projeções de embeddings treinados. Shapes do modelo completo estão na etapa anterior.');
      case 'scores':return H.matrix(A.scores,labels,labels,'QKᵀ'+(s.scaled?'/√d_head':''))+H.metric('d_head',dh);
      case 'mask':return H.table(['Query',...labels.map(x=>'Key '+x)],A.masked.map((r,i)=>[i,...r.map(v=>Number.isFinite(v)?f(v):'−∞')]),'Scores após máscara; futuro removido antes do softmax')+note(H,s.causal?'Causal ligado: todas as posições futuras recebem −∞.':'Máscara desligada: este modo demonstra vazamento e não é um treino causal válido.');
      case 'weights':return H.matrix(A.weights,labels,labels,'Softmax por linha')+H.table(['Linha','Soma'],A.weights.map((r,i)=>[i,sum(r)]));
      case 'values':return H.matrix(A.V,labels,Array.from({length:dh},(_,i)=>'v'+i),'Valores ilustrativos')+H.matrix(A.output,labels,Array.from({length:dh},(_,i)=>'saída'+i),'Mistura AV calculada')+H.flow(['Cabeças: '+heads,'Concatenar: '+d+' canais','Projetar W_O'],1);
      case 'block':return H.flow(['X [1,T,d]','Norma','Atenção','+ X','Norma','FFN','+ residual'],3)+H.table(['Grandeza','Valor'],[['T',T],['d',d],['Cabeças',heads],['Pesos aproximados por bloco sem bias',12*d*d]])+note(H,'Contagem para FFN com expansão 4d; sem embeddings nem parâmetros de norma.');
      case 'loss':return H.table(['Classe','Logit','p','Gradiente p − alvo'],tr.logits.map((x,i)=>[i+(i===tr.target?' (alvo)':''),x,tr.p[i],tr.p[i]-(i===tr.target?1:0)]))+H.metric('Entropia cruzada do alvo',tr.history.at(-1));
      case 'training':return H.bars(tr.history.map((_,i)=>String(i)),tr.history,'Perda real de uma cabeça com quatro logits')+metrics(H,[['Perda atual',tr.history.at(-1)],['Perplexidade deste exemplo',Math.exp(tr.history.at(-1))],['Passos',s.updates]])+note(H,'Somente quatro logits aprendidos; não é treinamento do Transformer completo nem uma métrica de validação.');
      case 'evaluation':return cards(H,[['Separação','Reservar dados de validação e evitar janelas que vazem o mesmo trecho entre partições.'],['Modo de avaliação','Desativar dropout e cálculo de gradiente onde apropriado; agregar vários lotes.'],['Comparação','Registrar configuração atual d='+d+', H='+heads+', T='+T+' e repetir com sementes no notebook.']]);
      default:return H.flow(['Prefixo de até '+T+' tokens','Última posição','Softmax com T='+s.temperature,'Escolher e anexar','Recortar a janela'],2)+H.bars(['Classe 0','Classe 1 (alvo)','Classe 2','Classe 3'],next,'Distribuição da cabeça didática após temperatura')+note(H,'O objetivo aqui é inspecionar a escolha, sem apresentar uma continuação como texto de um mini-GPT treinado.');
    }
  });

  register(10,(s,step,H)=>{
    const E=s.experts,k=Math.min(s.active,E),shared=s.params,total=shared+E,active=shared+k,logits=[3,2.2,1.5,.8,.2,-.5],labels=['gato','cão','pássaro','peixe','robô','árvore'],p=softmax(logits.map(x=>x/s.temperature));
    const topk=p.map((x,i)=>i<s.topk?x:0),topP=[];let mass=0;for(const x of p){topP.push(mass<s.topp?x:0);mass+=x;}const renorm=a=>{const z=sum(a);return a.map(x=>x/z);},pk=renorm(topk),pp=renorm(topP),sample=a=>{let cum=0;for(let i=0;i<a.length;i++){cum+=a[i];if(s.draw<=cum)return labels[i];}return labels.at(-1);};
    const dispatch=Array.from({length:8},(_,t)=>{const scores=Array.from({length:E},(_,e)=>({e,v:Math.cos((t+1)*(e+1)*.4)+(e===0?.8:0)}));const chosen=scores.sort((a,b)=>b.v-a.v).slice(0,k).map(x=>x.e);return Array.from({length:E},(_,e)=>+chosen.includes(e));}),loads=Array.from({length:E},(_,e)=>sum(dispatch.map(r=>r[e])));
    const prompt={bare:'Resuma isso.',instruction:'Resuma o texto em duas frases. Preserve datas e valores. Responda somente com o resumo.',examples:'Exemplo: entrada “O evento foi adiado para sexta.” → saída “Evento adiado para sexta.”\nAgora resuma a nova entrada no mesmo formato.',evidence:'Tarefa: quando será a entrega?\nDocumento: a entrega será em 14 de outubro.\nResponda usando o documento e cite o trecho de apoio.'}[s.prompt];
    switch(step.view){
      case 'tickets':return cards(H,[['Custo','Compare '+total+' bilhões totais com '+active+' bilhões ativos no orçamento didático.'],['Repetição','Examine a distribuição e o algoritmo de seleção: T='+s.temperature+'.'],['Variabilidade','Separe logits, filtros e sorteio; u='+s.draw+'.'],['Documento ignorado','Teste evidência e posição no contexto antes de concluir falta de capacidade.']]);
      case 'compute':return metrics(H,[['N denso',shared+' bilhões'],['D',s.tokens+' bilhões'],['6ND aproximado',(6*shared*s.tokens*1e18).toExponential(3)+' FLOPs']])+H.table(['Alteração','Multiplicador de FLOPs'],[['Dobrar N',2],['Dobrar D',2],['Dobrar N e D',4]])+note(H,'Aproximação para modelo denso; não prevê duração, custo monetário ou qualidade.');
      case 'moe':return H.bars(['Compartilhados','Especialistas totais','Especialistas ativos'],[shared,E,k],'Bilhões de parâmetros na miniatura')+metrics(H,[['Total armazenável',total+' B'],['Ativos por token',active+' B'],['Pesos a 2 bytes, sem overhead',total*2+' GB decimais']]);
      case 'router':return H.matrix(dispatch,Array.from({length:8},(_,i)=>'Token '+i),Array.from({length:E},(_,i)=>'E'+i),'Despacho top-k calculado: 1 = especialista escolhido')+H.metric('Especialistas ativos efetivos',k);
      case 'balance':return H.bars(loads.map((_,i)=>'E'+i),loads,'Tokens recebidos por especialista')+metrics(H,[['Despachos totais',sum(loads)],['Máximo / média',Math.max(...loads)/(sum(loads)/E)],['Carga média',sum(loads)/E]]);
      case 'logits':return H.table(['Token','Logit fixo','Probabilidade após T'],labels.map((x,i)=>[x,logits[i],p[i]]),'Nenhum peso é atualizado ao mover temperatura');
      case 'greedy':return H.flow(['Início','A: 0,55 → melhor 0,51','Prob. A1 = 0,2805'],1)+H.flow(['Início','B: 0,45 → melhor 0,99','Prob. B1 = 0,4455'],2)+cards(H,[['Greedy','Escolhe A no primeiro passo e alcança A1.'],['Busca com largura 2','Mantém A e B; B1 é a sequência de maior probabilidade neste grafo de dois passos.'],['Decisão diferente','Na distribuição de seis palavras, argmax atual: '+labels[p.indexOf(Math.max(...p))]+'.']]);
      case 'temperature':return H.bars(labels,p,'Softmax(logits / T)')+metrics(H,[['Entropia em nats',-sum(p.map(x=>x*Math.log(x)))],['Massa no mais provável',Math.max(...p)],['Temperatura',s.temperature]]);
      case 'filter':return H.table(['Token','Original','Top-k renormalizado','Top-p renormalizado'],labels.map((x,i)=>[x,p[i],pk[i],pp[i]]))+metrics(H,[['Itens em top-k',topk.filter(x=>x>0).length],['Itens em top-p',topP.filter(x=>x>0).length],['Massa original retida por top-p',sum(topP)]]);
      case 'sample':{let cum=0;return H.table(['Token','Início do intervalo','Fim do intervalo'],pp.map((x,i)=>{const start=cum;cum+=x;return [labels[i],start,cum];}),'Intervalos acumulados após top-p')+metrics(H,[['Sorteio u',s.draw],['Completa',sample(p)],['Top-k',sample(pk)],['Top-p',sample(pp)]]);}
      case 'prompt':return cards(H,[['Prompt escolhido',prompt],['O que muda','A entrada condiciona a previsão; esta tela exibe a estrutura sem chamar um modelo.'],['Configuração de saída','T='+s.temperature+', top-k='+s.topk+', top-p='+s.topp+'.']]);
      case 'context':return H.flow(['Instrução','Documento/evidência','Pergunta','Formato da resposta'],s.prompt==='evidence'?1:0)+cards(H,[['Entrada atual',prompt],['Teste controlado','Mover a mesma evidência de posição e conferir a resposta correta, mantendo tarefa e decodificação.'],['Sem inferência automática','O portal não executa um LLM nesta miniatura; nenhum acerto de recuperação é inventado.']]);
      case 'serving':return H.flow(['Fila e lote','Prefill do prefixo','Primeiro token','Decode sequencial','Resposta'],2)+H.table(['Orçamento didático','Valor'],[['Pesos totais em GB a 2 bytes',total*2],['Parâmetros ativos por token em B',active],['Fases a medir','Tempo até primeiro token; tempo por token; throughput']]);
      default:return H.table(['Sintoma','Hipótese','Evidência a coletar'],[['Custo inesperado','Total e ativo foram confundidos',total+' B totais; '+active+' B ativos na miniatura'],['Repetição','Distribuição concentrada','Entropia atual '+f(-sum(p.map(x=>x*Math.log(x))))],['Saídas diferentes','Amostragem','Sorteio atual '+s.draw+' → '+sample(pp)],['Fato ignorado','Uso insuficiente da evidência','Comparar posições e contextos com resposta verificável']]);
    }
  });
})();
