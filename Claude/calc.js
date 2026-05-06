// ═════════════════════════════════════════════════════════════

const SK='biz_v10', SNAPK='biz_snaps_v6';
const NET_DEFAULT='#1D9E75';
const DEFAULT_COLORS=['#378ADD','#D85A30','#1D9E75','#BA7517','#A32D2D','#534AB7','#D4537E','#639922','#5F5E5A','#888780','#0F6E56','#993C1D'];
const TAX_BRACKETS=[{u:6790,r:.10},{u:9730,r:.14},{u:15620,r:.20},{u:21710,r:.31},{u:45180,r:.35},{u:Infinity,r:.47}];
const CREDIT_POINT_MONTHLY=242;
const FOREX_SYMBOLS={USD:'$',EUR:'€',GBP:'£',JPY:'¥',CHF:'CHF',CAD:'CA$',AUD:'A$',SEK:'SEK'};
const PALETTE_GROUPS=[
  {g:'אדום',c:[{n:'אדום בהיר מאוד',h:'#FFF0F0'},{n:'אדום בהיר',h:'#FADBD8'},{n:'אדום',h:'#E74C3C'},{n:'אדום כהה',h:'#C0392B'},{n:'אדום עמוק',h:'#641E16'}]},
  {g:'ורוד',c:[{n:'ורוד בהיר',h:'#FADADD'},{n:'ורוד',h:'#F8BBD0'},{n:'ורוד עז',h:'#D4537E'},{n:'פוקסיה',h:'#D63388'}]},
  {g:'כתום',c:[{n:'כתום בהיר',h:'#FDEBD0'},{n:'אפרסק',h:'#FFCCBC'},{n:'כתום',h:'#E67E22'},{n:'כתום עז',h:'#D35400'}]},
  {g:'צהוב',c:[{n:'צהוב בהיר',h:'#FFF9C4'},{n:'צהוב',h:'#F9E79F'},{n:'זהב',h:'#F4D03F'},{n:'אמבר',h:'#EF9F27'},{n:'חרדל',h:'#BA7517'}]},
  {g:'ירוק',c:[{n:'ירוק בהיר מאוד',h:'#F0FFF4'},{n:'מינט',h:'#D5F5E3'},{n:'פיסטוק',h:'#A5D6A7'},{n:'ירוק',h:'#27AE60'},{n:'ירוק כהה',h:'#145A32'}]},
  {g:'טורקיז',c:[{n:'קרח',h:'#E0F7FA'},{n:'טורקיז',h:'#1ABC9C'},{n:'טורקיז כהה',h:'#0F6E56'}]},
  {g:'כחול',c:[{n:'כחול בהיר מאוד',h:'#F0F8FF'},{n:'שמיים',h:'#BBDEFB'},{n:'תכלת',h:'#64B5F6'},{n:'כחול',h:'#378ADD'},{n:'כחול כהה',h:'#185FA5'},{n:'נייבי',h:'#0D47A1'}]},
  {g:'סגול',c:[{n:'לבנדר',h:'#E8DAEF'},{n:'אורכידיה',h:'#CE93D8'},{n:'סגול',h:'#8E24AA'},{n:'אינדיגו',h:'#5C6BC0'}]},
  {g:'חום / בז׳',c:[{n:'קרם',h:'#FFF8DC'},{n:'בז׳',h:'#D7CCC8'},{n:'חום',h:'#795548'},{n:'חום כהה',h:'#4E342E'}]},
  {g:'אפור',c:[{n:'לבן',h:'#FFFFFF'},{n:'אפור בהיר',h:'#F5F5F5'},{n:'כסף',h:'#E0E0E0'},{n:'אפור',h:'#888780'},{n:'פחם',h:'#2C2C2A'},{n:'שחור',h:'#1a1a1a'}]},
];
let mainChart=null,settingsChart=null,compareChart=null,taxChart=null,yoyChart=null;
let expenseRows=[],expIdCounter=0;
let hiddenFields={};
let currentChartType='doughnut',itemColors={};
let colorModalLabel='',colorModalTemp='',filteredGroups=[...PALETTE_GROUPS];
let snapshots=[],viewingSnapId=null,snapSortMode='date';
let isDark=false;
let forexRate=3.72,forexCurrency='none',forexSymbol='';
let goalAmount=0,budgetMap={};
let fixedDefs=[
  {id:'tax',name:'מס הכנסה',taxOnNet:true,maxPct:60},
  {id:'vat',name:'מע"מ',defaultPct:17,maxPct:30},
  {id:'bi', name:'ביטוח לאומי',defaultPct:12,maxPct:25},
];

// ── Tabs ──────────────────────────────────────────────────
const g$=id=>document.getElementById(id);
function switchTab(tab,btn){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  g$('page-'+tab).classList.add('active'); btn.classList.add('active');
  if(tab==='history'){renderSnapList();renderCompare();renderHeatmap();}
  if(tab==='analysis'){renderAnalysis();}
  if(tab==='planning'){renderPlanning();}
  if(tab==='settings'){syncChartBtns();renderColorGrid();renderSettingsChart();renderHideFieldsUI();}
}
// ── Helpers ───────────────────────────────────────────────
function getIncome(){return parseFloat(g$('income').value)||0;}
function getExpensesAmt(){return expenseRows.reduce((s,r)=>s+(parseFloat(g$('a_'+r.id)?.value)||0),0);}
function getTaxBase(){return Math.max(0,getIncome()-getExpensesAmt());}
function pctToAmt(pct,base){return Math.round(base*pct/100);}
function amtToPct(amt,base){return base>0?parseFloat(((amt/base)*100).toFixed(2)):0;}
function noSpin(x){return`width:62px;border:none;background:transparent;font-size:14px;color:var(--text);font-family:var(--font);text-align:right;outline:none;-moz-appearance:textfield;${x||''}`;}
function getNetLabel(){return g$('ne-net')?.value||'רווח נקי לכיס';}
function getColor(label,i){return itemColors[label]||(label===getNetLabel()?NET_DEFAULT:DEFAULT_COLORS[i%DEFAULT_COLORS.length]);}
function setText(id,val){const el=g$(id);if(el)el.textContent=val;}
function getTaxBadgeText(){return g$('ne-tax-badge')?.value||'מדרגות';}
function getBiBadgeText(){return g$('ne-bi-badge')?.value||'מדרגות ב״ל';}
function calcIsraeliTax(m){if(m<=0)return 0;let t=0,p=0;for(const b of TAX_BRACKETS){if(m<=p)break;t+=(Math.min(m,b.u)-p)*b.r;p=b.u;}return Math.round(t);}
function calcIsraeliBI(m){if(m<=0)return 0;if(m<=9430)return Math.round(m*0.0345);return Math.round(Math.min(m,44020)*0.12);}
// ── Forex ─────────────────────────────────────────────────
async function fetchForexRate(){
  if(forexCurrency==='none')return;
  const ri=g$('forex-rate-input');if(ri)ri.placeholder='טוען...';
  try{
    const res=await fetch(`https://api.frankfurter.app/latest?from=${forexCurrency}&to=ILS`);
    const data=await res.json();
    if(data?.rates?.ILS){forexRate=parseFloat(data.rates.ILS.toFixed(4));if(ri)ri.value=forexRate;refreshForexDisplay();updateAllForexExpenses();saveState();}
  }catch(e){if(ri)ri.placeholder='שגיאה';}
}
function onManualRateInput(){const v=parseFloat(g$('forex-rate-input')?.value);if(v>0){forexRate=v;refreshForexDisplay();updateAllForexExpenses();saveState();}}
function onForexCurrencyChange(val){
  forexCurrency=val;forexSymbol=FOREX_SYMBOLS[val]||val;
  const has=val!=='none';
  g$('forex-rate-row').style.display=has?'block':'none';
  g$('forex-show-income-row').style.display=has?'flex':'none';
  g$('forex-show-net-row').style.display=has?'flex':'none';
  const lb=g$('forex-rate-label');if(lb)lb.textContent=has?`שער (₪ ל-1${forexSymbol})`:'שער';
  if(!has){g$('forex-income-display').style.display='none';g$('forex-net-display').style.display='none';}
  else fetchForexRate();
  expenseRows.forEach(r=>{const b=g$('curr_'+r.id);if(b&&r.currency==='foreign')b.textContent=forexSymbol||'$';});
  saveState();
}
function refreshForexDisplay(){
  if(forexCurrency==='none'||forexRate<=0)return;
  const{netAmt}=collectItemsRaw(),income=getIncome();
  const di=g$('forex-income-display');if(g$('forex-show-income')?.checked){di.style.display='block';di.textContent=`≈ ${forexSymbol}${(income/forexRate).toFixed(2)}`;}else di.style.display='none';
  const dn=g$('forex-net-display');if(g$('forex-show-net')?.checked){dn.style.display='block';dn.textContent=`≈ ${forexSymbol}${(netAmt/forexRate).toFixed(2)}`;}else dn.style.display='none';
}
function updateAllForexExpenses(){expenseRows.forEach(r=>{if(r.currency==='foreign'){const fe=g$('foreign_'+r.id),ae=g$('a_'+r.id),pe=g$('p_'+r.id),ne=g$('note_'+r.id);if(fe&&ae){const fv=parseFloat(fe.value)||0,ils=Math.round(fv*forexRate);ae.value=ils;if(pe)pe.value=amtToPct(ils,getIncome()).toFixed(2);if(ne)ne.textContent=`1${forexSymbol}=₪${forexRate.toFixed(2)} | ≈₪${ils.toLocaleString('he-IL')}`;}}}); autoSetTax();calc();}
// ── UI Names ──────────────────────────────────────────────
function applyUINames(){
  const gv=(id,fb)=>g$(id)?.value||fb;
  setText('ui-app-title',gv('ne-app-title','מחשבון רווח נקי'));
  setText('tab-calc',gv('ne-tab-calc','מחשבון'));
  setText('tab-history',gv('ne-tab-history','היסטוריה'));
  setText('tab-analysis',gv('ne-tab-analysis','ניתוח'));
  setText('tab-planning',gv('ne-tab-planning','תכנון'));
  setText('tab-settings',gv('ne-tab-settings','הגדרות'));
  setText('ui-income-title',gv('ne-income','הכנסה חודשית ברוטו'));
  setText('ui-fixed-title',gv('ne-fixed','ניכויים חובה'));
  setText('ui-expenses-title',gv('ne-expenses','הוצאות עסקיות'));
  const ab=g$('ui-add-btn');if(ab)ab.textContent=gv('ne-add-btn','+ הוסף');
  setText('ui-chart-title',gv('ne-chart','פילוח'));
  setText('ui-net-label',gv('ne-net','רווח נקי לכיס'));
  setText('ui-history-title',gv('ne-history-title','היסטוריה חודשית'));
  const ssb=g$('ui-save-snap-btn');if(ssb)ssb.textContent=gv('ne-save-snap','+ שמור חודש');
  setText('ui-exit-view',gv('ne-exit-view','חזור לנוכחי'));
  document.querySelectorAll('.snap-view-btn').forEach(el=>el.textContent=gv('ne-view-btn','הצג'));
  saveState();
}
function applyBadgeNames(){
  document.querySelectorAll('#fixed-wrap .field[data-id="tax"] .tax-auto-badge').forEach(el=>el.textContent=getTaxBadgeText());
  document.querySelectorAll('#fixed-wrap .field[data-id="bi"]  .tax-auto-badge').forEach(el=>el.textContent=getBiBadgeText());
  saveState();
}
function applyFixedNames(){
  fixedDefs[0].name=g$('ne-tax')?.value||'מס הכנסה';
  fixedDefs[1].name=g$('ne-vat')?.value||'מע"מ';
  fixedDefs[2].name=g$('ne-bi')?.value||'ביטוח לאומי';
  document.querySelectorAll('#fixed-wrap .field').forEach((div,i)=>{const sp=div.querySelector('.field-label span');if(sp)sp.textContent=fixedDefs[i]?.name||'';});
  saveAndCalc();
}
function applyFont(val){document.documentElement.style.setProperty('--font',val);saveState();}
function toggleDark(on){
  isDark=on;
  document.body.classList.add('theme-transition');
  document.body.classList.toggle('dark',on);
  // Sync home-screen dark toggle
  var sd=document.getElementById('s-dark'); if(sd) sd.checked=on;
  var hdb=document.getElementById('home-dark-btn'); if(hdb) hdb.textContent=on?'☀️':'🌙';
  // Update theme-color meta
  var meta=document.getElementById('theme-color-meta');
  if(meta) meta.content=on?'#08090E':'#EDECEA';
  saveState();
  calc();
  setTimeout(()=>document.body.classList.remove('theme-transition'),320);
}
// ── Fixed fields ──────────────────────────────────────────
function buildFixed(){
  const fw=g$('fixed-wrap');fw.innerHTML='';
  fixedDefs.forEach(f=>{
    const isTax=f.taxOnNet,base=isTax?getTaxBase():getIncome();
    let dp,da;
    if(isTax){da=calcIsraeliTax(base);dp=parseFloat(amtToPct(da,base).toFixed(1));}
    else if(f.id==='bi'){da=calcIsraeliBI(getIncome());dp=parseFloat(amtToPct(da,getIncome()).toFixed(1));}
    else{dp=f.defaultPct;da=pctToAmt(dp,base);}
    const badge=isTax?`<span class="tax-auto-badge">${getTaxBadgeText()}</span>`:(f.id==='bi'?`<span class="tax-auto-badge">${getBiBadgeText()}</span>`:'');
    const note=isTax?`<div class="tax-note">בסיס: ₪<span id="tax-base-d">${base.toLocaleString('he-IL')}</span> | אפקטיבי: <span id="tax-eff">${dp}</span>%</div>`:
               f.id==='bi'?`<div class="tax-note">מחושב לפי מדרגות — ניתן לעקוף</div>`:'';
    const div=document.createElement('div');div.className='field';div.dataset.id=f.id;div.dataset.lock='pct';
    div.innerHTML=`<div class="field-label"><span style="flex:1;">${f.name}</span>${badge}<button class="lock-btn mode-pct" id="btn_${f.id}">% קבוע</button></div><div class="input-row"><div class="num-box"><input type="number" inputmode="decimal" min="0" max="${f.maxPct}" step="0.1" value="${dp}" id="p_${f.id}" style="${noSpin()}" oninput="onFixedPct('${f.id}')"><span class="unit">%</span></div><span class="sep">=</span><div class="num-box"><input type="number" inputmode="numeric" min="0" step="1" value="${da}" id="a_${f.id}" style="${noSpin()}" oninput="onFixedAmt('${f.id}')"><span class="unit">₪</span></div></div>${note}`;
    if(f.id!=='tax'&&fw.children.length>0){const hr=document.createElement('hr');hr.className='separator';fw.appendChild(hr);}
    fw.appendChild(div);
    g$('btn_'+f.id).addEventListener('click',e=>{e.stopPropagation();toggleFixedLock(f.id);});
  });
}
function getFixedLock(id){const el=document.querySelector(`#fixed-wrap .field[data-id="${id}"]`);return el?el.dataset.lock:'pct';}
function toggleFixedLock(id){const div=document.querySelector(`#fixed-wrap .field[data-id="${id}"]`);if(!div)return;const next=div.dataset.lock==='pct'?'amt':'pct';div.dataset.lock=next;const btn=g$('btn_'+id);btn.textContent=next==='pct'?'% קבוע':'₪ קבוע';btn.className='lock-btn '+(next==='pct'?'mode-pct':'mode-amt');saveAndCalc();}
function onFixedPct(id){const pct=parseFloat(g$('p_'+id).value)||0;g$('a_'+id).value=pctToAmt(pct,id==='tax'?getTaxBase():getIncome());if(id==='tax')updateTaxNote();saveAndCalc();}
function onFixedAmt(id){if(id==='tax'){updateTaxNote();saveAndCalc();return;}const amt=parseFloat(g$('a_'+id).value)||0;const mx=fixedDefs.find(f=>f.id===id)?.maxPct||30;let pct=amtToPct(amt,getIncome());if(pct>mx)pct=mx;g$('p_'+id).value=pct.toFixed(2);saveAndCalc();}
function refreshTax(){const base=getTaxBase(),lock=getFixedLock('tax');if(lock==='pct'){const pct=parseFloat(g$('p_tax')?.value)||0;const a=g$('a_tax');if(a)a.value=pctToAmt(pct,base);}else{const amt=parseFloat(g$('a_tax')?.value)||0;const p=g$('p_tax');if(p)p.value=amtToPct(amt,base).toFixed(2);}updateTaxNote();}
function autoSetTax(){const base=getTaxBase(),amt=calcIsraeliTax(base),pct=parseFloat(amtToPct(amt,base).toFixed(1));const p=g$('p_tax');if(p)p.value=pct;const a=g$('a_tax');if(a)a.value=amt;updateTaxNote();}
function autoSetBI(){const inc=getIncome(),amt=calcIsraeliBI(inc),pct=parseFloat(amtToPct(amt,inc).toFixed(1));const lock=getFixedLock('bi');if(lock==='pct'){const p=g$('p_bi');if(p)p.value=pct;const a=g$('a_bi');if(a)a.value=amt;}}
function updateTaxNote(){const base=getTaxBase();const d=g$('tax-base-d');if(d)d.textContent=base.toLocaleString('he-IL');const pct=parseFloat(g$('p_tax')?.value)||0;const e=g$('tax-eff');if(e)e.textContent=pct.toFixed(1);}
// ── Expenses ──────────────────────────────────────────────
function addExpense(name,pct,amt,lockMode,currency,foreignAmt){
  name=name||'הוצאה עסקית';pct=pct||0;amt=amt||0;lockMode=lockMode||'pct';currency=currency||'ils';foreignAmt=foreignAmt||0;
  const id='exp_'+(++expIdCounter);expenseRows.push({id,lockMode,currency});
  const ew=g$('expenses-wrap');
  if(ew.children.length>0){const hr=document.createElement('hr');hr.className='separator';ew.appendChild(hr);}
  const div=document.createElement('div');div.className='field';div.dataset.id=id;div.dataset.lock=lockMode;div.dataset.currency=currency;
  const isF=(currency==='foreign'),fSym=forexCurrency!=='none'?(forexSymbol||'$'):'$';
  div.innerHTML=`<div class="field-label"><span class="ename-display" id="name_${id}" contenteditable="true" onblur="saveAndCalc()">${name}</span><button class="lock-btn ${lockMode==='pct'?'mode-pct':'mode-amt'}" id="btn_${id}">${lockMode==='pct'?'% קבוע':'₪ קבוע'}</button>${forexCurrency!=='none'?`<button class="curr-btn ${isF?'foreign':''}" id="curr_${id}">${isF?fSym:'₪'}</button>`:''}<button class="remove-btn" id="rm_${id}">×</button></div><div class="input-row" id="row_${id}">${isF?`<div class="num-box"><input type="number" inputmode="decimal" min="0" step="0.01" value="${foreignAmt}" id="foreign_${id}" style="${noSpin()}"><span class="unit">${fSym}</span></div><span class="sep">=</span><div class="num-box"><input type="number" inputmode="decimal" min="0" max="100" step="0.1" value="${pct}" id="p_${id}" style="${noSpin()};color:var(--text3);" readonly><span class="unit">%</span></div><input type="hidden" id="a_${id}" value="${amt}">`:`<div class="num-box"><input type="number" inputmode="decimal" min="0" max="100" step="0.5" value="${pct}" id="p_${id}" style="${noSpin()}" oninput="onExpPct('${id}')"><span class="unit">%</span></div><span class="sep">=</span><div class="num-box"><input type="number" inputmode="numeric" min="0" step="1" value="${amt}" id="a_${id}" style="${noSpin()}" oninput="onExpAmt('${id}')"><span class="unit">₪</span></div>`}</div>${isF?`<div class="usd-rate-note" id="note_${id}">1${fSym}=₪${forexRate.toFixed(2)} | ≈₪${Math.round(foreignAmt*forexRate).toLocaleString('he-IL')}</div>`:''}`;
  ew.appendChild(div);
  g$('btn_'+id).addEventListener('click',e=>{e.stopPropagation();toggleExpLock(id);});
  g$('rm_'+id).addEventListener('click',e=>{e.stopPropagation();removeExpense(id);});
  const cb=g$('curr_'+id);if(cb)cb.addEventListener('click',e=>{e.stopPropagation();toggleExpCurrency(id);});
  if(isF){const fi=g$('foreign_'+id);if(fi)fi.addEventListener('input',()=>onExpForeign(id));}
  if(g$('page-settings')?.classList.contains('active'))renderHideFieldsUI();
  saveAndCalc();
}
function getExpName(id){const el=g$('name_'+id);return el?el.textContent.trim()||'הוצאה עסקית':'הוצאה עסקית';}
function removeExpense(id){expenseRows=expenseRows.filter(r=>r.id!==id);const f=document.querySelector(`#expenses-wrap .field[data-id="${id}"]`);if(f){const p=f.previousElementSibling;if(p&&p.tagName==='HR')p.remove();f.remove();}autoSetTax();saveAndCalc();}
function toggleExpLock(id){const div=document.querySelector(`#expenses-wrap .field[data-id="${id}"]`);if(!div)return;const next=div.dataset.lock==='pct'?'amt':'pct';div.dataset.lock=next;const row=expenseRows.find(r=>r.id===id);if(row)row.lockMode=next;const btn=g$('btn_'+id);btn.textContent=next==='pct'?'% קבוע':'₪ קבוע';btn.className='lock-btn '+(next==='pct'?'mode-pct':'mode-amt');saveAndCalc();}
function getExpLock(id){const el=document.querySelector(`#expenses-wrap .field[data-id="${id}"]`);return el?el.dataset.lock:'pct';}
function onExpPct(id){const pct=parseFloat(g$('p_'+id).value)||0;g$('a_'+id).value=pctToAmt(pct,getIncome());autoSetTax();saveAndCalc();}
function onExpAmt(id){const amt=parseFloat(g$('a_'+id).value)||0;g$('p_'+id).value=amtToPct(amt,getIncome()).toFixed(2);autoSetTax();saveAndCalc();}
function onExpForeign(id){const fe=g$('foreign_'+id),ae=g$('a_'+id),pe=g$('p_'+id),ne=g$('note_'+id);if(!fe||!ae)return;const fv=parseFloat(fe.value)||0,ils=Math.round(fv*forexRate);ae.value=ils;if(pe)pe.value=amtToPct(ils,getIncome()).toFixed(2);if(ne)ne.textContent=`1${forexSymbol}=₪${forexRate.toFixed(2)} | ≈₪${ils.toLocaleString('he-IL')}`;autoSetTax();saveAndCalc();}
function toggleExpCurrency(id){
  const div=document.querySelector(`#expenses-wrap .field[data-id="${id}"]`);if(!div)return;
  const row=expenseRows.find(r=>r.id===id);const next=div.dataset.currency==='ils'?'foreign':'ils';
  div.dataset.currency=next;if(row)row.currency=next;
  const ca=parseFloat(g$('a_'+id)?.value)||0,cp=parseFloat(g$('p_'+id)?.value)||0;
  const fSym=forexSymbol||'$',cb=g$('curr_'+id),ne=div.querySelector('.usd-rate-note'),re=g$('row_'+id);
  if(cb){cb.textContent=next==='foreign'?fSym:'₪';cb.className='curr-btn'+(next==='foreign'?' foreign':'');}
  if(next==='foreign'){
    const fAmt=parseFloat((ca/forexRate).toFixed(2));
    re.innerHTML=`<div class="num-box"><input type="number" inputmode="decimal" min="0" step="0.01" value="${fAmt}" id="foreign_${id}" style="${noSpin()}"><span class="unit">${fSym}</span></div><span class="sep">=</span><div class="num-box"><input type="number" inputmode="decimal" min="0" max="100" step="0.1" value="${cp}" id="p_${id}" style="${noSpin()};color:var(--text3);" readonly><span class="unit">%</span></div><input type="hidden" id="a_${id}" value="${ca}">`;
    if(!ne){const n=document.createElement('div');n.className='usd-rate-note';n.id='note_'+id;n.textContent=`1${fSym}=₪${forexRate.toFixed(2)} | ≈₪${ca.toLocaleString('he-IL')}`;div.appendChild(n);}
    g$('foreign_'+id).addEventListener('input',()=>onExpForeign(id));onExpForeign(id);
  }else{
    re.innerHTML=`<div class="num-box"><input type="number" inputmode="decimal" min="0" max="100" step="0.5" value="${cp}" id="p_${id}" style="${noSpin()}" oninput="onExpPct('${id}')"><span class="unit">%</span></div><span class="sep">=</span><div class="num-box"><input type="number" inputmode="numeric" min="0" step="1" value="${ca}" id="a_${id}" style="${noSpin()}" oninput="onExpAmt('${id}')"><span class="unit">₪</span></div>`;
    if(ne)ne.remove();saveAndCalc();
  }
}
function onIncome(){
  const inc=getIncome();
  ['vat','bi'].forEach(id=>{const lock=getFixedLock(id);if(lock==='pct'){const pct=parseFloat(g$('p_'+id)?.value)||0;const a=g$('a_'+id);if(a)a.value=Math.round(inc*pct/100);}else{const amt=parseFloat(g$('a_'+id)?.value)||0;const p=g$('p_'+id);if(p)p.value=amtToPct(amt,inc).toFixed(2);}});
  expenseRows.forEach(r=>{if(r.currency==='foreign'){const ils=parseFloat(g$('a_'+r.id)?.value)||0;const p=g$('p_'+r.id);if(p)p.value=amtToPct(ils,inc).toFixed(2);}else{const lock=getExpLock(r.id);if(lock==='pct'){const pct=parseFloat(g$('p_'+r.id)?.value)||0;const a=g$('a_'+r.id);if(a)a.value=Math.round(inc*pct/100);}else{const amt=parseFloat(g$('a_'+r.id)?.value)||0;const p=g$('p_'+r.id);if(p)p.value=amtToPct(amt,inc).toFixed(2);}}});
  autoSetTax();autoSetBI();saveAndCalc();
}
// ── Collect ───────────────────────────────────────────────
function getFixedAmt(id){return parseFloat(g$('a_'+id)?.value)||0;}
function getExpAmt(id){return parseFloat(g$('a_'+id)?.value)||0;}
function collectItemsRaw(){
  refreshTax();
  const income=getIncome();
  const fixedItems=fixedDefs.map(f=>({name:f.name,amt:getFixedAmt(f.id)}));
  const expItems=expenseRows.map(r=>({name:getExpName(r.id),amt:getExpAmt(r.id)})).filter(e=>e.amt>0);
  const totalAmt=fixedItems.reduce((s,f)=>s+f.amt,0)+expItems.reduce((s,e)=>s+e.amt,0);
  const netAmt=Math.max(0,income-totalAmt);
  const netLabel=getNetLabel();
  const allItems=[...fixedItems,...expItems,{name:netLabel,amt:Math.round(netAmt)}];
  return{income,totalAmt,netAmt,labels:allItems.map(i=>i.name),data:allItems.map(i=>income>0?parseFloat((i.amt/income*100).toFixed(1)):0),amts:allItems.map(i=>i.amt),colors:allItems.map((item,i)=>getColor(item.name,i))};
}
// ── Charts ────────────────────────────────────────────────
function buildConfig(labels,data,amts,colors,income,small){
  const fs=small?9:11,bdr=isDark?'#1e1e20':'#fff';
  const sc={y:{ticks:{callback:v=>'₪'+v.toLocaleString('he-IL'),font:{size:fs}},grid:{color:'rgba(128,128,128,.1)'}},x:{grid:{display:false},ticks:{font:{size:fs}}}};
  const tt={callbacks:{label:c=>' ₪'+Math.round(c.raw).toLocaleString('he-IL')}},ttp={callbacks:{label:c=>' '+c.parsed.toFixed(1)+'%'}};
  if(currentChartType==='doughnut')return{type:'doughnut',data:{labels,datasets:[{data,backgroundColor:colors,borderWidth:2,borderColor:bdr,hoverOffset:small?3:6}]},options:{responsive:true,maintainAspectRatio:false,cutout:'58%',plugins:{legend:{display:false},tooltip:ttp}}};
  if(currentChartType==='pie')return{type:'pie',data:{labels,datasets:[{data,backgroundColor:colors,borderWidth:2,borderColor:bdr}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:ttp}}};
  if(currentChartType==='bar')return{type:'bar',data:{labels,datasets:[{data:amts,backgroundColor:colors,borderRadius:4,borderSkipped:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:tt},scales:sc}};
  if(currentChartType==='horizontalBar')return{type:'bar',data:{labels,datasets:[{data:amts,backgroundColor:colors,borderRadius:4,borderSkipped:false}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:tt},scales:{x:{ticks:{callback:v=>'₪'+v.toLocaleString('he-IL'),font:{size:fs}},grid:{color:'rgba(128,128,128,.1)'}},y:{grid:{display:false},ticks:{font:{size:fs}}}}}};
  if(currentChartType==='line'){const cum=[];let run=0;amts.forEach((a,i)=>{if(i===amts.length-1)cum.push(income);else{run+=a;cum.push(run);}});return{type:'line',data:{labels,datasets:[{data:cum,borderColor:'#185FA5',backgroundColor:'rgba(24,95,165,.08)',fill:true,tension:.3,pointBackgroundColor:colors,pointRadius:small?3:5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:tt},scales:sc}};}
  if(currentChartType==='radar'){const netless=labels.slice(0,-1);const netlessD=data.slice(0,-1);const netlessC=colors.slice(0,-1);return{type:'radar',data:{labels:netless,datasets:[{data:netlessD,backgroundColor:isDark?'rgba(79,163,240,.15)':'rgba(26,111,212,.1)',borderColor:'#1A6FD4',pointBackgroundColor:netlessC,pointRadius:4,pointHoverRadius:6,fill:true}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' '+c.parsed.r.toFixed(1)+'%'}}},scales:{r:{ticks:{font:{size:fs},color:isDark?'#888':'#aaa',backdropColor:'transparent'},grid:{color:isDark?'rgba(255,255,255,.08)':'rgba(0,0,0,.08)'},pointLabels:{font:{size:fs},color:isDark?'#b0b0b0':'#555'}}}}};}
  if(currentChartType==='polarArea')return{type:'polarArea',data:{labels,datasets:[{data,backgroundColor:colors.map(c=>c+'CC'),borderWidth:2,borderColor:isDark?'#1a1a1c':'#fff'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:ttp},scales:{r:{ticks:{font:{size:fs},backdropColor:'transparent',color:isDark?'#888':'#aaa'},grid:{color:isDark?'rgba(255,255,255,.08)':'rgba(0,0,0,.08)'}}}}};
  if(currentChartType==='stackedBar')return{type:'bar',data:{labels:['פילוח'],datasets:labels.map((lbl,i)=>({label:lbl,data:[amts[i]],backgroundColor:colors[i],borderRadius:i===0?[4,4,0,0]:i===labels.length-1?[0,0,4,4]:[0,0,0,0],borderSkipped:false}))},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true,position:'bottom',labels:{font:{size:fs},color:isDark?'#e8e8e8':'#444',boxWidth:10,padding:8}},tooltip:{callbacks:{label:c=>' '+c.dataset.label+': ₪'+Math.round(c.raw).toLocaleString('he-IL')}}},scales:{x:{stacked:true,grid:{display:false},ticks:{font:{size:fs}}},y:{stacked:true,ticks:{callback:v=>'₪'+v.toLocaleString('he-IL'),font:{size:fs}},grid:{color:'rgba(128,128,128,.1)'}}}}};
    if(currentChartType==='waterfall'){const wL=['הכנסה',...labels.slice(0,-1),labels[labels.length-1]],wA=[income,...amts.slice(0,-1),amts[amts.length-1]],wC=['#1D9E75',...colors.slice(0,-1),colors[colors.length-1]];const fl=[];let rb=income;fl.push([0,income]);for(let i=1;i<wA.length-1;i++){fl.push([rb-wA[i],rb]);rb-=wA[i];}fl.push([0,wA[wA.length-1]]);return{type:'bar',data:{labels:wL,datasets:[{data:fl,backgroundColor:wC,borderRadius:3,borderSkipped:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' ₪'+(Math.abs(c.raw[1]-c.raw[0])).toLocaleString('he-IL')}}},scales:sc}};}
  return null;
}
function calc(){
  const{income,totalAmt,netAmt,labels,data,amts,colors}=collectItemsRaw();
  const netPct=income>0?netAmt/income*100:0;
  const nv=g$('net-val');if(nv){nv.classList.remove('animate-val');void nv.offsetWidth;nv.classList.add('animate-val');}
  setText('net-val','₪'+Math.round(netAmt).toLocaleString('he-IL'));
  setText('net-pct',netPct.toFixed(1)+'% מההכנסה');
  g$('warn').style.display=totalAmt>income?'block':'none';
  renderLegend('legend',labels,data,amts,colors);
  refreshForexDisplay();
  updateForecast(netAmt);
  requestAnimationFrame(()=>{
    if(mainChart)mainChart.destroy();
    const cfg=buildConfig(labels,data,amts,colors,income,false);
    if(cfg)mainChart=new Chart(g$('pie-main').getContext('2d'),cfg);
    if(g$('page-settings').classList.contains('active')){renderSettingsChart();renderColorGrid();}
    if(g$('page-analysis').classList.contains('active'))renderAnalysis();
    if(g$('page-planning').classList.contains('active'))renderPlanning();
  });
}
function renderSettingsChart(){
  const{income,labels,data,amts,colors}=collectItemsRaw();
  requestAnimationFrame(()=>{if(settingsChart)settingsChart.destroy();const cfg=buildConfig(labels,data,amts,colors,income,true);if(cfg)settingsChart=new Chart(g$('settings-chart').getContext('2d'),cfg);});
}
function renderLegend(elId,labels,data,amts,colors){
  const el=g$(elId);if(!el)return;el.innerHTML='';
  const netLabel=getNetLabel();
  labels.forEach((lbl,i)=>{const isNet=lbl===netLabel;const row=document.createElement('div');row.className='legend-row'+(isNet?' legend-net':'');row.innerHTML=`<span class="legend-left"><span class="dot" style="background:${colors[i]}"></span>${lbl}</span><span class="legend-right">₪${amts[i].toLocaleString('he-IL')} (${data[i].toFixed(1)}%)</span>`;el.appendChild(row);});
}
function setChartType(type,btn){currentChartType=type;document.querySelectorAll('.ct-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');saveState();calc();renderSettingsChart();}
function syncChartBtns(){document.querySelectorAll('.ct-btn').forEach(b=>b.classList.remove('active'));const btn=g$('ctbtn-'+currentChartType);if(btn)btn.classList.add('active');}
// ── Forecast ──────────────────────────────────────────────
function updateForecast(netAmt){
  setText('annual','₪'+(Math.round(netAmt*12)).toLocaleString('he-IL'));
  const nets=snapshots.map(s=>s.data.netAmt||0);
  setText('avg3',nets.length>=3?'₪'+Math.round((nets[0]+nets[1]+nets[2])/3).toLocaleString('he-IL'):'—');
  setText('avgAll',nets.length>0?'₪'+Math.round(nets.reduce((s,v)=>s+v,0)/nets.length).toLocaleString('he-IL'):'—');
}
// ── Analysis ──────────────────────────────────────────────
function renderAnalysis(){
  const{income,totalAmt,netAmt}=collectItemsRaw();
  const netPct=income>0?netAmt/income*100:0;
  const taxAmt=getFixedAmt('tax'),vatAmt=getFixedAmt('vat'),biAmt=getFixedAmt('bi');
  const effTax=income>0?taxAmt/income*100:0;
  const marginalRate=getMarginalRate(getTaxBase());
  // KPIs
  const kpis=[
    {label:'אחוז רווח נקי',val:netPct.toFixed(1)+'%',cls:netPct>40?'good':netPct>20?'warn':'bad',sub:'מהכנסה ברוטו'},
    {label:'מס אפקטיבי',val:effTax.toFixed(1)+'%',cls:'',sub:'מס מתוך הכנסה כוללת'},
    {label:'מס שולי',val:(marginalRate*100).toFixed(0)+'%',cls:'',sub:'על כל ₪ נוסף'},
    {label:'סה"כ ניכויים',val:'₪'+totalAmt.toLocaleString('he-IL'),cls:'',sub:'מס + ביטוח + הוצאות'},
    {label:'הכנסה שנתית',val:'₪'+(income*12).toLocaleString('he-IL'),cls:'',sub:'12 חודשים'},
    {label:'רווח נקי שנתי',val:'₪'+(netAmt*12).toLocaleString('he-IL'),cls:'good',sub:'תחזית שנתית'},
  ];
  const grid=g$('kpi-grid');grid.innerHTML='';
  kpis.forEach(k=>{const c=document.createElement('div');c.className='kpi-card';c.innerHTML=`<div class="kpi-label">${k.label}</div><div class="kpi-value ${k.cls}">${k.val}</div><div class="kpi-sub">${k.sub}</div>`;grid.appendChild(c);});
  // Tax breakdown bars
  const tbw=g$('tax-breakdown-wrap');tbw.innerHTML='';
  [{name:'מס הכנסה',amt:taxAmt,color:'#378ADD'},{name:'ביטוח לאומי',amt:biAmt,color:'#D85A30'},{name:'מע"מ (עלות)',amt:vatAmt,color:'#BA7517'}].forEach(item=>{
    const pct=income>0?item.amt/income*100:0;
    const row=document.createElement('div');row.style.marginBottom='.5rem';
    row.innerHTML=`<div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text2);margin-bottom:3px;"><span>${item.name}</span><span>₪${item.amt.toLocaleString('he-IL')} (${pct.toFixed(1)}%)</span></div><div class="tax-breakdown-bar"><div class="tax-breakdown-fill" style="width:${Math.min(100,pct*2)}%;background:${item.color};"></div></div>`;
    tbw.appendChild(row);
  });
  // Tax pie chart
  requestAnimationFrame(()=>{
    if(taxChart)taxChart.destroy();
    const tc=g$('tax-chart');if(!tc)return;
    taxChart=new Chart(tc.getContext('2d'),{type:'doughnut',data:{labels:['מס הכנסה','ביטוח לאומי','מע"מ','הוצאות','רווח נקי'],datasets:[{data:[taxAmt,biAmt,vatAmt,getExpensesAmt(),Math.round(netAmt)],backgroundColor:['#378ADD','#D85A30','#BA7517','#534AB7','#1D9E75'],borderWidth:2,borderColor:isDark?'#1e1e20':'#fff'}]},options:{responsive:true,maintainAspectRatio:false,cutout:'55%',plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' ₪'+Math.round(c.raw).toLocaleString('he-IL')}}}}});
  });
  // Break-even
  const fixedExpenses=totalAmt-netAmt;
  const breakEven=Math.round(fixedExpenses*100/(100-0));
  // Break-even = total fixed costs (tax+bi+expenses) — need income where net=0
  // Simplified: since tax depends on income, we iterate
  let be=totalAmt;for(let i=0;i<20;i++){const t=calcIsraeliTax(be-getExpensesAmt()),bi2=calcIsraeliBI(be),v=be*VAT_RATE_DEFAULT/100;be=getExpensesAmt()+t+bi2+v;}
  setText('breakeven-val','₪'+Math.round(be).toLocaleString('he-IL'));
  setText('breakeven-sub',income>be?`הכנסה הנוכחית גבוהה ב-₪${Math.round(income-be).toLocaleString('he-IL')} מנקודת האיזון`:`חסר ₪${Math.round(be-income).toLocaleString('he-IL')} להגיע לאיזון`);
  // Tax credits
  calcTaxCredits();
  // YoY
  renderYoY();
}
const VAT_RATE_DEFAULT=17;
function getMarginalRate(taxableIncome){for(const b of TAX_BRACKETS)if(taxableIncome<=b.u)return b.r;return .47;}
function calcTaxCredits(){
  const pts=parseFloat(g$('credit-points')?.value)||0;
  const monthly=Math.round(pts*CREDIT_POINT_MONTHLY);
  const taxAmt=getFixedAmt('tax');
  const afterTax=Math.max(0,taxAmt-monthly);
  const{netAmt}=collectItemsRaw();
  const newNet=netAmt+monthly;
  setText('credit-monthly','₪'+monthly.toLocaleString('he-IL'));
  setText('credit-after-tax','₪'+afterTax.toLocaleString('he-IL'));
  setText('credit-net','₪'+Math.round(newNet).toLocaleString('he-IL'));
}
function runWhatIf(){
  const newIncome=parseFloat(g$('wi-income')?.value)||getIncome();
  const expDelta=parseFloat(g$('wi-expense')?.value)||0;
  const curExpenses=getExpensesAmt();
  const newExpenses=curExpenses+expDelta;
  const newTaxBase=Math.max(0,newIncome-newExpenses);
  const newTax=calcIsraeliTax(newTaxBase);
  const newBI=calcIsraeliBI(newIncome);
  const newVAT=newIncome*VAT_RATE_DEFAULT/100;
  const newNet=Math.max(0,newIncome-newExpenses-newTax-newBI-newVAT);
  const{netAmt}=collectItemsRaw();
  const diff=Math.round(newNet-netAmt);
  const sign=diff>=0?'+':'';
  setText('wi-result',`רווח נקי חדש: ₪${Math.round(newNet).toLocaleString('he-IL')} (${sign}₪${diff.toLocaleString('he-IL')} לעומת כיום)`);
}
function renderYoY(){
  const yoyCard=g$('yoy-card');if(!yoyCard)return;
  if(snapshots.length<2){yoyCard.style.display='none';return;}
  yoyCard.style.display='block';
  // Group snaps by rough "year"
  const byYear={};snapshots.forEach(s=>{const y=new Date(s.ts).getFullYear();if(!byYear[y])byYear[y]=[];byYear[y].push(s);});
  const years=Object.keys(byYear).sort().slice(-2);
  if(years.length<2){yoyCard.style.display='none';return;}
  const [y1,y2]=years;
  const avg1=Math.round(byYear[y1].reduce((s,x)=>s+(x.data.netAmt||0),0)/byYear[y1].length);
  const avg2=Math.round(byYear[y2].reduce((s,x)=>s+(x.data.netAmt||0),0)/byYear[y2].length);
  const diff=avg2-avg1,pct=avg1>0?((diff/avg1)*100).toFixed(1):0;
  const wrap=g$('yoy-wrap');wrap.innerHTML=`<div style="display:flex;gap:1rem;margin-bottom:.75rem;flex-wrap:wrap;"><div class="kpi-card" style="flex:1;"><div class="kpi-label">${y1} ממוצע</div><div class="kpi-value">₪${avg1.toLocaleString('he-IL')}</div></div><div class="kpi-card" style="flex:1;"><div class="kpi-label">${y2} ממוצע</div><div class="kpi-value ${diff>0?'good':'bad'}">₪${avg2.toLocaleString('he-IL')}</div><div class="kpi-sub">${diff>0?'+':''}${pct}% לעומת שנה קודמת</div></div></div>`;
  requestAnimationFrame(()=>{
    if(yoyChart)yoyChart.destroy();
    const ctx=g$('yoy-chart').getContext('2d');
    yoyChart=new Chart(ctx,{type:'bar',data:{labels:[y1,y2],datasets:[{data:[avg1,avg2],backgroundColor:['#85B7EB','#1D9E75'],borderRadius:6,borderSkipped:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' ₪'+Math.round(c.raw).toLocaleString('he-IL')}}},scales:{y:{ticks:{callback:v=>'₪'+v.toLocaleString('he-IL'),font:{size:10}},grid:{color:'rgba(128,128,128,.1)'}},x:{grid:{display:false}}}}});
  });
}
// ── Planning ──────────────────────────────────────────────
function updateGoal(){
  const goal=parseFloat(g$('goal-input')?.value)||0;goalAmount=goal;
  const wrap=g$('goal-progress-wrap'),fill=g$('goal-fill'),status=g$('goal-status');
  if(!goal){wrap.style.display='none';saveState();return;}
  wrap.style.display='block';
  const{netAmt}=collectItemsRaw();
  const pct=Math.min(100,Math.round(netAmt/goal*100));
  fill.style.width=pct+'%';fill.style.background=pct>=100?'#27AE60':pct>=70?'#EF9F27':'#E74C3C';
  const diff=Math.round(netAmt-goal);
  status.textContent=pct>=100?`✓ יעד הושג! עודף ₪${Math.abs(diff).toLocaleString('he-IL')}`:`${pct}% מהיעד — חסר ₪${Math.abs(diff).toLocaleString('he-IL')}`;
  saveState();
}
function renderPlanning(){
  updateGoal();renderBudgetComparison();renderBudgetEditor();
}
function renderBudgetEditor(){
  const card=g$('budget-editor-card'),wrap=g$('budget-editor-wrap');if(!card||!wrap)return;
  card.style.display='block';wrap.innerHTML='';
  const items=[...fixedDefs.map(f=>f.name),...expenseRows.map(r=>getExpName(r.id))];
  items.forEach(name=>{
    const row=document.createElement('div');row.className='name-editor-row';
    const budgetVal=budgetMap[name]||0;
    row.innerHTML=`<span class="name-editor-label" style="max-width:110px;overflow:hidden;text-overflow:ellipsis;">${name}</span><input type="number" inputmode="numeric" min="0" step="1" class="name-editor-input" style="max-width:100px;" data-item="${name}" value="${budgetVal}" placeholder="תקציב ₪">`;
    wrap.appendChild(row);
  });
}
function saveBudget(){
  const inputs=g$('budget-editor-wrap').querySelectorAll('input');
  inputs.forEach(inp=>{const val=parseFloat(inp.value)||0;budgetMap[inp.dataset.item]=val;});
  saveState();renderBudgetComparison();
  g$('budget-editor-card').style.display='none';
}
function editBudget(){g$('budget-editor-card').style.display='block';renderBudgetEditor();}
function renderBudgetComparison(){
  const wrap=g$('budget-wrap');if(!wrap)return;wrap.innerHTML='';
  const{netAmt}=collectItemsRaw();
  const items=[
    ...fixedDefs.map(f=>({name:f.name,actual:getFixedAmt(f.id)})),
    ...expenseRows.map(r=>({name:getExpName(r.id),actual:getExpAmt(r.id)})),
    {name:getNetLabel(),actual:Math.round(netAmt)},
  ];
  const hasAnyBudget=items.some(i=>budgetMap[i.name]>0);
  if(!hasAnyBudget){wrap.innerHTML='<p style="font-size:13px;color:var(--text4);">לחץ "עריכת תקציב" כדי להגדיר תקציב מתוכנן</p>';return;}
  const header=document.createElement('div');header.className='budget-row';header.innerHTML='<span class="budget-label">פרמטר</span><span class="budget-planned">מתוכנן</span><span class="budget-actual">בפועל</span>';
  wrap.appendChild(header);
  items.forEach(item=>{
    const budget=budgetMap[item.name]||0;if(!budget&&item.name!==getNetLabel())return;
    const diff=item.actual-budget,isNet=item.name===getNetLabel();
    const diffCls=isNet?(diff>=0?'pos':'neg'):(diff<=0?'pos':'neg');
    const sign=diff>=0?'+':'';
    const row=document.createElement('div');row.className='budget-row';
    row.innerHTML=`<span class="budget-label">${item.name}</span><span class="budget-planned">${budget?'₪'+budget.toLocaleString('he-IL'):'—'}</span><span class="budget-actual ${budget?'':''}" style="color:var(--text);">₪${item.actual.toLocaleString('he-IL')} ${budget?`<span class="budget-diff ${diffCls}">${sign}₪${Math.abs(diff).toLocaleString('he-IL')}</span>`:''}</span>`;
    wrap.appendChild(row);
  });
}
function downloadReminder(){
  const day=parseInt(g$('reminder-day')?.value)||1;
  const now=new Date();const y=now.getFullYear(),m=String(now.getMonth()+1).padStart(2,'0');
  const dtStart=`${y}${m}${String(day).padStart(2,'0')}T090000`;
  const ics=`BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:שמירת נתוני חודש — מחשבון רווח נקי\nDTSTART;TZID=Asia/Jerusalem:${dtStart}\nDURATION:PT30M\nRRULE:FREQ=MONTHLY;BYMONTHDAY=${day}\nDESCRIPTION:זמן לשמור את נתוני החודש במחשבון הרווח הנקי\nEND:VEVENT\nEND:VCALENDAR`;
  const blob=new Blob([ics],{type:'text/calendar'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='תזכורת-חודשית.ics';a.click();
}
// ── Colors ────────────────────────────────────────────────
function renderColorGrid(){
  const{labels,colors}=collectItemsRaw();const grid=g$('color-grid');grid.innerHTML='';
  labels.forEach((lbl,i)=>{const row=document.createElement('div');row.className='color-row';row.onclick=()=>openColorModal(lbl,colors[i]);row.innerHTML=`<div class="color-swatch" style="background:${colors[i]}"></div><span class="color-name" title="${lbl}">${lbl}</span>`;grid.appendChild(row);});
}
function filterColors(){const q=g$('color-search').value.trim().toLowerCase();filteredGroups=q?PALETTE_GROUPS.map(g=>({g:g.g,c:g.c.filter(c=>c.n.includes(q)||c.h.toLowerCase().includes(q))})).filter(g=>g.c.length>0):[...PALETTE_GROUPS];renderPaletteScroll();}
function renderPaletteScroll(){
  const el=g$('palette-scroll');el.innerHTML='';
  filteredGroups.forEach(group=>{
    const gDiv=document.createElement('div');gDiv.className='palette-group';
    const t=document.createElement('div');t.className='palette-group-title';t.textContent=group.g;
    const grid=document.createElement('div');grid.className='preset-colors';
    group.c.forEach(c=>{const sw=document.createElement('div');sw.className='preset-swatch'+(c.h===colorModalTemp?' selected':'');sw.style.background=c.h;sw.title=c.n;sw.onclick=()=>{colorModalTemp=c.h;g$('hex-input').value=c.h;g$('hex-preview').style.background=c.h;document.querySelectorAll('.preset-swatch').forEach(s=>s.classList.remove('selected'));sw.classList.add('selected');};grid.appendChild(sw);});
    gDiv.appendChild(t);gDiv.appendChild(grid);el.appendChild(gDiv);
  });
}
function onHexInput(){const v=g$('hex-input').value.trim();if(/^#[0-9A-Fa-f]{6}$/.test(v)){g$('hex-preview').style.background=v;colorModalTemp=v;document.querySelectorAll('.preset-swatch').forEach(s=>s.classList.remove('selected'));}}
function applyHexColor(){const v=g$('hex-input').value.trim();if(!/^#[0-9A-Fa-f]{6}$/.test(v)){alert('הזן קוד תקני: #RRGGBB');return;}colorModalTemp=v;g$('hex-preview').style.background=v;document.querySelectorAll('.preset-swatch').forEach(s=>s.classList.remove('selected'));}
function openColorModal(label,cur){colorModalLabel=label;colorModalTemp=cur;filteredGroups=[...PALETTE_GROUPS];g$('color-modal-title').textContent='צבע: '+label;g$('color-search').value='';g$('hex-input').value=cur;g$('hex-preview').style.background=cur;g$('color-modal').classList.add('open');renderPaletteScroll();}
function closeColorModal(){g$('color-modal').classList.remove('open');}
function confirmColor(){if(colorModalLabel&&colorModalTemp){itemColors[colorModalLabel]=colorModalTemp;saveAndCalc();renderColorGrid();}closeColorModal();}
function resetColors(){itemColors={};saveAndCalc();renderColorGrid();}
// ── Heatmap ───────────────────────────────────────────────
function renderHeatmap(){
  const card=g$('heatmap-card'),grid=g$('heatmap-grid');if(!card||!grid)return;
  if(snapshots.length<2){card.style.display='none';return;}
  card.style.display='block';grid.innerHTML='';
  const nets=snapshots.map(s=>s.data.netAmt||0);
  const mn=Math.min(...nets),mx=Math.max(...nets);
  const MONTHS=['ינ׳','פב׳','מר׳','אפ׳','מא׳','יו׳','יל׳','אג׳','ספ׳','אוק׳','נו׳','דצ׳'];
  const byMonthYear={};snapshots.forEach(s=>{const d=new Date(s.ts);const key=`${d.getFullYear()}-${d.getMonth()}`;if(!byMonthYear[key]||s.ts>byMonthYear[key].ts)byMonthYear[key]=s;});
  const now=new Date(),entries=[];
  for(let i=11;i>=0;i--){const d=new Date(now.getFullYear(),now.getMonth()-i,1);const key=`${d.getFullYear()}-${d.getMonth()}`;entries.push({month:d.getMonth(),year:d.getFullYear(),snap:byMonthYear[key]||null});}
  entries.forEach(e=>{
    const cell=document.createElement('div');cell.className='hm-cell';
    if(e.snap){const v=e.snap.data.netAmt||0,t=(mx>mn)?(v-mn)/(mx-mn):0.5;const r=Math.round(231*t+41*(1-t)),g2=Math.round(174*t+196*(1-t)),b=Math.round(117*(1-t)+193*(1-t));cell.style.background=`hsl(${Math.round(t*120)},60%,${isDark?45:55}%)`;cell.title=`${MONTHS[e.month]} ${e.year}: ₪${Math.round(v).toLocaleString('he-IL')}`;}
    else{cell.style.background='var(--border)';cell.title=`${MONTHS[e.month]} ${e.year}: אין נתון`;}
    cell.textContent=MONTHS[e.month];grid.appendChild(cell);
  });
}
// ── Snapshots ─────────────────────────────────────────────
function captureState(){
  const st={income:getIncome(),fixed:{},expenses:[],itemColors:{...itemColors},chartType:currentChartType,isDark,forexCurrency,forexRate,goalAmount,budgetMap:{...budgetMap},hiddenFields:{...hiddenFields},uiNames:{},fixedNames:{}};
  fixedDefs.forEach(f=>{st.fixed[f.id]={pct:parseFloat(g$('p_'+f.id)?.value)||0,amt:parseFloat(g$('a_'+f.id)?.value)||0,lock:getFixedLock(f.id)};});
  expenseRows.forEach(r=>{const fe=g$('foreign_'+r.id);st.expenses.push({name:getExpName(r.id),pct:parseFloat(g$('p_'+r.id)?.value)||0,amt:parseFloat(g$('a_'+r.id)?.value)||0,lockMode:getExpLock(r.id),currency:r.currency||'ils',foreignAmt:fe?parseFloat(fe.value)||0:0});});
  ['app-title','tab-calc','tab-history','tab-analysis','tab-planning','tab-settings','income','fixed','expenses','add-btn','chart','net','history-title','save-snap','view-btn','exit-view','tax-badge','bi-badge'].forEach(k=>{const el=g$('ne-'+k);if(el)st.uiNames[k]=el.value;});
  fixedDefs.forEach(f=>{const el=g$('ne-'+f.id);if(el)st.fixedNames[f.id]=el.value;});
  const{netAmt}=collectItemsRaw();st.netAmt=netAmt;
  return st;
}
function setSortMode(mode,btn){snapSortMode=mode;document.querySelectorAll('.sort-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');renderSnapList();}
function getSortedSnaps(){const arr=[...snapshots];if(snapSortMode==='profit')arr.sort((a,b)=>(b.data.netAmt||0)-(a.data.netAmt||0));return arr;}
function openSnapModal(){
  const now=new Date();const months=['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
  g$('snap-label-input').value=months[now.getMonth()]+' '+now.getFullYear();g$('snap-note-input').value='';
  g$('snap-date-note').textContent='תאריך: '+now.toLocaleDateString('he-IL');
  g$('snap-modal').classList.add('open');setTimeout(()=>g$('snap-label-input').select(),300);
}
function closeSnapModal(){g$('snap-modal').classList.remove('open');}
function confirmSaveSnap(){
  const label=g$('snap-label-input').value.trim()||'ללא שם',note=g$('snap-note-input').value.trim();
  const now=new Date();
  const snap={id:Date.now(),label,note,date:now.toLocaleDateString('he-IL'),ts:now.getTime(),data:captureState()};
  snapshots.unshift(snap);saveSnapsToStorage();closeSnapModal();renderSnapList();renderHeatmap();renderCompare();updateForecast(collectItemsRaw().netAmt);showBadge('✓ חודש נשמר');
}
function renderSnapList(){
  const el=g$('snap-list');el.innerHTML='';
  const sorted=getSortedSnaps();
  if(!sorted.length){el.innerHTML='<div class="snap-empty">אין שמירות עדיין.</div>';g$('compare-card').style.display='none';g$('heatmap-card').style.display='none';return;}
  sorted.forEach(snap=>{
    const snapId=snap.id;
    const item=document.createElement('div');item.className='snap-item'+(viewingSnapId===snapId?' viewing':'');
    const net='₪'+Math.round(snap.data.netAmt||0).toLocaleString('he-IL');
    const fxInfo=snap.data.forexCurrency&&snap.data.forexCurrency!=='none'&&snap.data.forexRate?` · ${FOREX_SYMBOLS[snap.data.forexCurrency]||snap.data.forexCurrency}${(snap.data.netAmt/snap.data.forexRate).toFixed(0)}`:'';
    const topDiv=document.createElement('div');topDiv.className='snap-top';
    topDiv.innerHTML=`<div class="snap-dot"></div><div class="snap-info"><input class="snap-name-input" value="${snap.label.replace(/"/g,'&quot;')}"><div class="snap-date-line">${snap.date}${snap.note?` · ${snap.note}`:''}${fxInfo}</div></div><div class="snap-net">${net}</div>`;
    topDiv.querySelector('.snap-name-input').addEventListener('change',function(){snap.label=this.value.trim()||'ללא שם';saveSnapsToStorage();renderCompare();});
    const actDiv=document.createElement('div');actDiv.className='snap-actions';
    const vBtn=document.createElement('button');vBtn.className='snap-view-btn';vBtn.textContent=g$('ne-view-btn')?.value||'הצג';
    const dBtn=document.createElement('button');dBtn.className='snap-dl-btn';dBtn.textContent='הורד';
    const shBtn=document.createElement('button');shBtn.className='snap-share-btn';shBtn.textContent='שתף';
    const xBtn=document.createElement('button');xBtn.className='snap-del-btn';xBtn.textContent='מחק';
    function tap(btn,fn){let t=false;btn.addEventListener('touchstart',e=>{t=true;e.stopPropagation();},{passive:true});btn.addEventListener('touchend',e=>{if(t){t=false;e.preventDefault();e.stopPropagation();fn();}});btn.addEventListener('click',e=>{e.stopPropagation();if(!t)fn();t=false;});}
    tap(vBtn,()=>loadSnap(snapId));tap(dBtn,()=>downloadSnap(snapId));tap(shBtn,()=>shareSnap(snapId));tap(xBtn,()=>deleteSnap(snapId));
    actDiv.appendChild(vBtn);actDiv.appendChild(dBtn);actDiv.appendChild(shBtn);actDiv.appendChild(xBtn);
    item.appendChild(topDiv);item.appendChild(actDiv);el.appendChild(item);
  });
  g$('compare-card').style.display=sorted.length>=2?'block':'none';
  g$('heatmap-card').style.display=sorted.length>=2?'block':'none';
}
function loadSnap(id){const snap=snapshots.find(s=>s.id===id);if(!snap)return;viewingSnapId=id;applyState(snap.data);g$('viewing-banner').classList.add('show');g$('viewing-text').textContent='צופה בנתוני: '+snap.label;renderSnapList();switchTab('calc',g$('tab-calc'));}
function exitView(){viewingSnapId=null;g$('viewing-banner').classList.remove('show');try{const raw=localStorage.getItem(SK);if(raw)applyState(JSON.parse(raw));}catch(e){}renderSnapList();}
function deleteSnap(id){if(!confirm('למחוק שמירה זו?'))return;snapshots=snapshots.filter(s=>s.id!==id);if(viewingSnapId===id){viewingSnapId=null;g$('viewing-banner').classList.remove('show');}saveSnapsToStorage();renderSnapList();renderHeatmap();renderCompare();}
function downloadSnap(id){
  const snap=snapshots.find(s=>s.id===id);if(!snap)return;
  const d=snap.data,income=d.income||0,netAmt=d.netAmt||0;
  const netPct=income>0?(netAmt/income*100).toFixed(1):0;
  const fxLine=d.forexCurrency&&d.forexCurrency!=='none'&&d.forexRate
    ?`<div class="fx-line">שער ${FOREX_SYMBOLS[d.forexCurrency]||d.forexCurrency} בזמן השמירה: ₪${d.forexRate.toFixed(2)} &nbsp;|&nbsp; רווח נקי: ${FOREX_SYMBOLS[d.forexCurrency]||d.forexCurrency}${(netAmt/d.forexRate).toFixed(2)}</div>`:'' ;
  const fixedRows=[];
  [{id:'tax',name:'מס הכנסה',color:'#378ADD'},{id:'vat',name:'מע"מ',color:'#BA7517'},{id:'bi',name:'ביטוח לאומי',color:'#D85A30'}]
    .forEach(f=>{const s=d.fixed?.[f.id];if(s&&s.amt>0)fixedRows.push({name:f.name,amt:s.amt,pct:(income>0?s.amt/income*100:0).toFixed(1),color:f.color,type:'fixed'});});
  const expRows=[];
  if(d.expenses)d.expenses.forEach((e,i)=>{if(e.amt>0)expRows.push({name:e.name,amt:e.amt,pct:(income>0?e.amt/income*100:0).toFixed(1),color:'#534AB7',type:'exp'});});
  const allRows=[...fixedRows,...expRows];
  const totalDeductions=allRows.reduce((s,r)=>s+r.amt,0);

  const rowsHTML=allRows.map(r=>`
    <tr>
      <td><span class="dot" style="background:${r.color}"></span>${r.name}</td>
      <td class="num">₪${Math.round(r.amt).toLocaleString('he-IL')}</td>
      <td class="pct">${r.pct}%</td>
    </tr>`).join('');

  const html=`<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${snap.label} — דוח חודשי</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Heebo',Arial,sans-serif;background:#F0EEE9;color:#111;min-height:100vh;padding:2rem 1rem;-webkit-font-smoothing:antialiased;}
.page{max-width:560px;margin:0 auto;}
.header{background:#fff;border-radius:16px;padding:1.5rem;margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,.06);}
.header-top{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;}
.title{font-size:22px;font-weight:700;letter-spacing:-.02em;color:#111;}
.badge{font-size:11px;font-weight:600;background:#EAF3DE;color:#3B6D11;border-radius:20px;padding:4px 12px;border:1px solid rgba(24,168,118,.2);white-space:nowrap;margin-top:4px;}
.meta{font-size:13px;color:#888;margin-top:.4rem;}
.fx-line{font-size:12px;color:#888;margin-top:.5rem;padding-top:.5rem;border-top:1px solid #f0f0f0;}
.net-box{background:linear-gradient(135deg,#E6F6F0 0%,#f5f5f3 100%);border:1px solid rgba(24,168,118,.2);border-radius:12px;padding:1.25rem 1.1rem;margin-bottom:1rem;}
.net-label{font-size:11px;font-weight:600;color:#18A876;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.35rem;}
.net-amount{font-size:38px;font-weight:700;color:#111;letter-spacing:-.03em;line-height:1;}
.net-sub{font-size:13px;color:#888;margin-top:.35rem;}
.net-annual{font-size:13px;color:#18A876;font-weight:500;margin-top:.25rem;}
.card{background:#fff;border-radius:14px;padding:1.1rem;margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,.06);}
.card-title{font-size:10.5px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.85rem;}
table{width:100%;border-collapse:collapse;}
tr{border-bottom:1px solid #f0f0ec;}
tr:last-child{border-bottom:none;}
td{padding:9px 4px;font-size:14px;vertical-align:middle;}
td:first-child{display:flex;align-items:center;gap:8px;color:#333;}
.dot{width:9px;height:9px;border-radius:2px;flex-shrink:0;display:inline-block;}
td.num{text-align:left;font-weight:500;color:#111;white-space:nowrap;}
td.pct{text-align:left;color:#aaa;font-size:12px;white-space:nowrap;width:48px;}
.summary-row{display:flex;gap:.75rem;flex-wrap:wrap;margin-bottom:1rem;}
.summary-box{flex:1;min-width:130px;background:#fff;border-radius:10px;padding:.75rem;box-shadow:0 1px 4px rgba(0,0,0,.06);}
.summary-box .s-label{font-size:10.5px;color:#aaa;font-weight:500;margin-bottom:3px;}
.summary-box .s-val{font-size:16px;font-weight:600;color:#111;}
.footer{text-align:center;font-size:11.5px;color:#bbb;margin-top:1.5rem;padding-top:1rem;}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="header-top">
      <div>
        <div class="title">${snap.label}</div>
        <div class="meta">${snap.date}${snap.note?' &nbsp;·&nbsp; '+snap.note:''}</div>
        ${fxLine}
      </div>
      ${snap.approved?'<div class="badge">✓ מאושר</div>':''}
    </div>
  </div>

  <div class="net-box">
    <div class="net-label">רווח נקי לכיס</div>
    <div class="net-amount">₪${Math.round(netAmt).toLocaleString('he-IL')}</div>
    <div class="net-sub">${netPct}% מההכנסה הכוללת</div>
    <div class="net-annual">תחזית שנתית: ₪${Math.round(netAmt*12).toLocaleString('he-IL')}</div>
  </div>

  <div class="summary-row">
    <div class="summary-box">
      <div class="s-label">הכנסה ברוטו</div>
      <div class="s-val">₪${income.toLocaleString('he-IL')}</div>
    </div>
    <div class="summary-box">
      <div class="s-label">סה"כ ניכויים</div>
      <div class="s-val">₪${Math.round(totalDeductions).toLocaleString('he-IL')}</div>
    </div>
    <div class="summary-box">
      <div class="s-label">מס אפקטיבי</div>
      <div class="s-val">${income>0?((d.fixed?.tax?.amt||0)/income*100).toFixed(1):0}%</div>
    </div>
  </div>

  ${allRows.length?`<div class="card">
    <div class="card-title">פירוט ניכויים והוצאות</div>
    <table><tbody>${rowsHTML}</tbody></table>
  </div>`:''}

  <div class="footer">דוח זה נוצר ממחשבון הרווח הנקי &nbsp;·&nbsp; ${snap.date}</div>
</div>

<!-- Quick card modal -->
<div class="modal-overlay" id="quick-card-modal" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="modal" style="max-width:480px;">
    <div class="modal-title">כרטיס סיכום</div>
    <div id="quick-card-preview" style="background:var(--bg);border-radius:var(--radius-md);padding:1.25rem;margin-bottom:1rem;text-align:center;"></div>
    <div class="modal-actions">
      <button class="modal-cancel" onclick="g$('quick-card-modal').classList.remove('open')">סגור</button>
      <button class="modal-confirm" onclick="printQuickCard()">🖨 הדפס / שמור PDF</button>
    </div>
  </div>
</div>

</body>
</html>`;

  const blob=new Blob([html],{type:'text/html;charset=utf-8'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download=snap.label+'.html';a.click();
}

function exportAllCSV(){
  if(!snapshots.length){alert('אין שמירות לייצוא');return;}
  const headers=['שם','תאריך','הכנסה','מס הכנסה','מע"מ','ביטוח לאומי','הוצאות','רווח נקי','הערה'];
  const rows=snapshots.map(s=>{const d=s.data;return[s.label,s.date,d.income||0,d.fixed?.tax?.amt||0,d.fixed?.vat?.amt||0,d.fixed?.bi?.amt||0,(d.expenses||[]).reduce((sum,e)=>sum+e.amt,0),d.netAmt||0,s.note||''];});
  const csv=[headers,...rows].map(r=>r.map(v=>`"${String(v).replace(/"/g,'""')}"`).join(',')).join('\n');
  const blob=new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='היסטוריה-רווח.csv';a.click();
}
// ── Compare ───────────────────────────────────────────────
let compareSelected=new Set();
function renderCompare(){
  if(snapshots.length<2){g$('compare-card').style.display='none';return;}
  g$('compare-card').style.display='block';
  const cb=g$('compare-checkboxes');cb.innerHTML='';
  snapshots.forEach(snap=>{
    if(compareSelected.size===0)compareSelected.add(snap.id);
    const row=document.createElement('div');row.className='compare-check-row';const checked=compareSelected.has(snap.id);
    row.innerHTML=`<input type="checkbox" id="cmp_${snap.id}" ${checked?'checked':''} onchange="toggleCompare(${snap.id},this.checked)"><label for="cmp_${snap.id}" style="cursor:pointer;">₪${Math.round(snap.data.netAmt||0).toLocaleString('he-IL')} — ${snap.label}</label>`;
    cb.appendChild(row);
  });
  drawCompareChart();
}
function toggleCompare(id,checked){if(checked)compareSelected.add(id);else compareSelected.delete(id);drawCompareChart();}
function drawCompareChart(){
  const sel=snapshots.filter(s=>compareSelected.has(s.id)).reverse();if(!sel.length)return;
  const labels=sel.map(s=>s.label),netAmts=sel.map(s=>Math.round(s.data.netAmt||0)),incomes=sel.map(s=>s.data.income||0),colors=sel.map((_,i)=>DEFAULT_COLORS[i%DEFAULT_COLORS.length]);
  const ctx=g$('compare-chart').getContext('2d');if(compareChart)compareChart.destroy();
  const fs=10,sc={y:{ticks:{callback:v=>'₪'+v.toLocaleString('he-IL'),font:{size:fs}},grid:{color:'rgba(128,128,128,.1)'}},x:{grid:{display:false},ticks:{font:{size:fs}}}};
  requestAnimationFrame(()=>{compareChart=new Chart(ctx,{type:'bar',data:{labels,datasets:[{label:'רווח נקי',data:netAmts,backgroundColor:colors,borderRadius:4,borderSkipped:false},{label:'הכנסה',data:incomes,backgroundColor:colors.map(c=>c+'33'),borderRadius:4,borderSkipped:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true,labels:{font:{size:fs},color:isDark?'#e8e8e8':'#444'}},tooltip:{callbacks:{label:c=>' ₪'+Math.round(c.raw).toLocaleString('he-IL')}}},scales:sc}});});
  if(sel.length===2){
    const dw=g$('compare-diff-wrap');dw.innerHTML='';
    const a=sel[0].data,b=sel[1].data;
    const rows=[{label:'הכנסה',aV:a.income||0,bV:b.income||0},{label:'מס',aV:a.fixed?.tax?.amt||0,bV:b.fixed?.tax?.amt||0},{label:'ביטוח לאומי',aV:a.fixed?.bi?.amt||0,bV:b.fixed?.bi?.amt||0},{label:'רווח נקי',aV:a.netAmt||0,bV:b.netAmt||0}];
    const table=document.createElement('table');table.className='compare-diff-table';
    table.innerHTML=`<thead><tr><th>פרמטר</th><th>${sel[0].label}</th><th>${sel[1].label}</th><th>הפרש</th></tr></thead><tbody>${rows.map(r=>{const diff=Math.round(r.bV-r.aV);const cls=diff>0?'diff-pos':'diff-neg';return`<tr><td>${r.label}</td><td>₪${Math.round(r.aV).toLocaleString('he-IL')}</td><td>₪${Math.round(r.bV).toLocaleString('he-IL')}</td><td class="${cls}">${diff>=0?'+':''}₪${diff.toLocaleString('he-IL')}</td></tr>`;}).join('')}</tbody>`;
    dw.appendChild(table);
  }else{g$('compare-diff-wrap').innerHTML='';}
}
// ── Reset ─────────────────────────────────────────────────
function resetAllData(){if(!confirm('למחוק את כל הנתונים?'))return;localStorage.removeItem(SK);localStorage.removeItem(SNAPK);location.reload();}
// ── Save / Load ───────────────────────────────────────────
function buildStateObj(){
  const st=captureState();
  st.forexShowIncome=g$('forex-show-income')?.checked||false;
  st.forexShowNet=g$('forex-show-net')?.checked||false;
  st.fontVal=g$('font-select')?.value||'Arial,sans-serif';
  st.quickMode=document.body.classList.contains('quick-mode');
  st.fontSize=document.documentElement.style.fontSize||'16px';
  st.hcMode=document.body.classList.contains('hc');
  st.goalAmount=goalAmount;st.budgetMap={...budgetMap};
  return st;
}
function showBadge(msg){const b=g$('saved-badge');b.textContent=msg||'✓ נשמר';b.style.display='inline';setTimeout(()=>{b.style.display='none';b.textContent='✓ נשמר';},1800);}
function saveState(){if(viewingSnapId!==null){saveSnapChanges();return;}localStorage.setItem(SK,JSON.stringify(buildStateObj()));showBadge();}
function saveAndCalc(){saveState();calc();}
function saveSnapChanges(){const s=snapshots.find(x=>x.id===viewingSnapId);if(s){s.data=captureState();saveSnapsToStorage();}}
function saveSnapsToStorage(){localStorage.setItem(SNAPK,JSON.stringify(snapshots));}
function loadSnapsFromStorage(){try{const r=localStorage.getItem(SNAPK);if(r)snapshots=JSON.parse(r);}catch(e){}}
function applyState(state){
  expenseRows=[];expIdCounter=0;g$('expenses-wrap').innerHTML='';
  if(state.chartType){currentChartType=state.chartType;syncChartBtns();}
  if(state.isDark!==undefined){
    isDark=state.isDark;
    document.body.classList.toggle('dark',isDark);
    var sd2=document.getElementById('s-dark'); if(sd2) sd2.checked=isDark;
    var hdb2=document.getElementById('home-dark-btn'); if(hdb2) hdb2.textContent=isDark?'☀️':'🌙';
  }
  buildFixed();
  g$('income').value=state.income||20000;
  if(state.itemColors)itemColors={...state.itemColors};
  if(state.budgetMap)budgetMap={...state.budgetMap};
  if(state.hiddenFields){hiddenFields={...state.hiddenFields};setTimeout(applyHiddenFields,100);}
  if(state.goalAmount){goalAmount=state.goalAmount;const gi=g$('goal-input');if(gi)gi.value=goalAmount;}
  const fv=state.fontVal||'Arial,sans-serif';const fs=g$('font-select');if(fs)fs.value=fv;applyFont(fv);
  if(state.uiNames)Object.entries(state.uiNames).forEach(([k,v])=>{const el=g$('ne-'+k);if(el)el.value=v;});
  if(state.fixedNames)fixedDefs.forEach(f=>{if(state.fixedNames[f.id])f.name=state.fixedNames[f.id];const el=g$('ne-'+f.id);if(el&&state.fixedNames[f.id])el.value=state.fixedNames[f.id];});
  applyUINames();
  if(state.forexCurrency&&state.forexCurrency!=='none'){
    forexCurrency=state.forexCurrency;forexSymbol=FOREX_SYMBOLS[forexCurrency]||forexCurrency;
    if(state.forexRate>0)forexRate=state.forexRate;
    const sel=g$('forex-currency-select');if(sel)sel.value=forexCurrency;
    const ri=g$('forex-rate-input');if(ri)ri.value=forexRate;
    const lb=g$('forex-rate-label');if(lb)lb.textContent=`שער (₪ ל-1${forexSymbol})`;
    g$('forex-rate-row').style.display='block';g$('forex-show-income-row').style.display='flex';g$('forex-show-net-row').style.display='flex';
    if(state.forexShowIncome)g$('forex-show-income').checked=true;if(state.forexShowNet)g$('forex-show-net').checked=true;
  if(state.quickMode){document.body.classList.add('quick-mode');const qt=g$('quick-toggle');if(qt)qt.checked=true;}
  if(state.fontSize&&state.fontSize!=='16px'){document.documentElement.style.fontSize=state.fontSize;const sz=state.fontSize==='14px'?'s':state.fontSize==='18px'?'l':'m';document.querySelectorAll('.fz-btn').forEach(b=>b.classList.remove('active'));const fb=g$('fz-'+sz);if(fb)fb.classList.add('active');}
  if(state.hcMode)toggleHC(true);
    fetchForexRate();
  }
  fixedDefs.forEach(f=>{const s=state.fixed?.[f.id];if(!s)return;const p=g$('p_'+f.id);if(p)p.value=s.pct;const a=g$('a_'+f.id);if(a)a.value=s.amt;const div=document.querySelector(`#fixed-wrap .field[data-id="${f.id}"]`);if(div&&s.lock){div.dataset.lock=s.lock;const btn=g$('btn_'+f.id);if(btn){btn.textContent=s.lock==='pct'?'% קבוע':'₪ קבוע';btn.className='lock-btn '+(s.lock==='pct'?'mode-pct':'mode-amt');}}});
  if(state.expenses?.length)state.expenses.forEach(e=>addExpense(e.name,e.pct,e.amt,e.lockMode,e.currency||'ils',e.foreignAmt||0));
  autoSetTax();autoSetBI();calc();
  // Load shared snap from URL
  const params=new URLSearchParams(window.location.search);const snapParam=params.get('snap');
  if(snapParam){try{const snapData=JSON.parse(decodeURIComponent(atob(snapParam)));const shared={id:Date.now()+'_shared',label:'שמירה משותפת',note:'נטענה מקישור',date:new Date().toLocaleDateString('he-IL'),ts:Date.now(),data:snapData};snapshots.unshift(shared);saveSnapsToStorage();viewingSnapId=shared.id;applyState(snapData);g$('viewing-banner').classList.add('show');g$('viewing-text').textContent='צופה בנתונים משותפים';window.history.replaceState({},'',window.location.pathname);}catch(e){}}
}
// ── Hours simulator ───────────────────────────────────────
function runHoursCalc() {
  const rate = parseFloat(g$('wi-rate')?.value)||0;
  const hours = parseFloat(g$('wi-hours')?.value)||0;
  const res = g$('wi-hours-result');
  if (!rate || !hours || !res) { if(res) res.style.display='none'; return; }
  const grossIncome = rate * hours;
  const taxBase = Math.max(0, grossIncome - getExpensesAmt());
  const tax = calcIsraeliTax(taxBase);
  const bi = calcIsraeliBI(grossIncome);
  const vat = grossIncome * VAT_RATE_DEFAULT / 100;
  const net = Math.max(0, grossIncome - getExpensesAmt() - tax - bi - vat);
  const effRate = grossIncome > 0 ? (net/hours).toFixed(0) : 0;
  res.style.display = 'block';
  res.textContent = `${hours} שעות × ₪${rate} = ₪${Math.round(grossIncome).toLocaleString('he-IL')} ברוטו → רווח נקי: ₪${Math.round(net).toLocaleString('he-IL')} (₪${effRate}/שעה נטו)`;
}


function initCtxMenu() {
  const hide = () => { const m=g$('ctx-menu'); if(m) m.style.display='none'; };
  const cv = g$('ctx-view');   if(cv) cv.onclick   = () => { if(ctxSnapId) loadSnap(ctxSnapId); hide(); };
  const cd = g$('ctx-dup');    if(cd) cd.onclick    = () => { if(ctxSnapId) duplicateSnap(ctxSnapId); hide(); };
  const cs = g$('ctx-share');  if(cs) cs.onclick    = () => { if(ctxSnapId) shareSnap(ctxSnapId); hide(); };
  const cx = g$('ctx-del');
  if(cx) cx.onclick = () => {
    hide();
    if(!ctxSnapId) return;
    const snap=snapshots.find(s=>s.id===ctxSnapId); if(!snap) return;
    const backup=[...snapshots];
    snapshots=snapshots.filter(s=>s.id!==ctxSnapId);
    if(viewingSnapId===ctxSnapId){viewingSnapId=null;g$('viewing-banner')?.classList.remove('show');}
    saveSnapsToStorage();renderSnapList();renderHeatmap();renderCompare();
    pushUndo('"'+snap.label+'" נמחקה',()=>{snapshots=backup;saveSnapsToStorage();renderSnapList();renderHeatmap();renderCompare();});
  };
  document.addEventListener('click', e => {
    const m=g$('ctx-menu');
    if(m && m.style.display!=='none' && !m.contains(e.target)) m.style.display='none';
  });
}
// ── Init ──────────────────────────────────────────────────
loadSnapsFromStorage();
buildFixed();
let loaded=false;
try{const raw=localStorage.getItem(SK);if(raw){applyState(JSON.parse(raw));loaded=true;}}catch(e){}
if(!loaded){const inc=20000;[{name:'שכירות משרד',pct:5,lockMode:'pct'},{name:'שיווק ופרסום',pct:3,lockMode:'amt'},{name:'ציוד ותוכנות',pct:2,lockMode:'amt'},{name:'עובדים / קבלנים',pct:4,lockMode:'amt'},{name:'הוצאות רכב',pct:1,lockMode:'amt'}].forEach(e=>addExpense(e.name,e.pct,pctToAmt(e.pct,inc),e.lockMode));}
autoSetTax();autoSetBI();calc();
setInterval(()=>{if(forexCurrency!=='none')fetchForexRate();},600000);

// ══ ADDITIONAL FEATURES ══════════════════════════════════

function syncThemeColor(){const m=document.getElementById('theme-color-meta');if(m)m.content=isDark?'#1a1a1c':'#ffffff';}

document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){closeColorModal();closeSnapModal();['qr-modal','share-modal','template-modal','gsearch'].forEach(function(id){const el=document.getElementById(id);if(el)el.classList.remove('open');});}
  if((e.ctrlKey||e.metaKey)&&e.key==='s'){e.preventDefault();saveState();showBadge();}
  if((e.ctrlKey||e.metaKey)&&e.key==='k'){e.preventDefault();openGSearch();}
  if(e.key==='Enter'&&document.getElementById('snap-modal')?.classList.contains('open')){e.preventDefault();confirmSaveSnap();}
  if(e.altKey&&(e.key==='ArrowLeft'||e.key==='ArrowRight')){
    var allTabs=['calc','history','analysis','planning','tools','ds','settings'];
    // Only include visible tabs
    var tabs=allTabs.filter(function(t){var btn=document.getElementById('tab-'+t);return btn&&btn.style.display!=='none';});
    var c=tabs.findIndex(function(t){return document.getElementById('page-'+t)?.classList.contains('active');});
    if(e.key==='ArrowLeft'&&c<tabs.length-1) switchTab(tabs[c+1],document.getElementById('tab-'+tabs[c+1]));
    if(e.key==='ArrowRight'&&c>0)            switchTab(tabs[c-1],document.getElementById('tab-'+tabs[c-1]));
  }
});

(function(){
  const tabs=['calc','history','analysis','planning','settings'];
  let sx=0,sy=0;
  document.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;sy=e.touches[0].clientY;},{passive:true});
  document.addEventListener('touchend',function(e){
    const dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;
    if(Math.abs(dx)<50||Math.abs(dy)>Math.abs(dx)*.7)return;
    const cur=tabs.findIndex(t=>document.getElementById('page-'+t)?.classList.contains('active'));
    if(cur<0)return;const next=dx>0?cur-1:cur+1;
    if(next<0||next>=tabs.length)return;
    switchTab(tabs[next],document.getElementById('tab-'+tabs[next]));
  },{passive:true});
})();

let _undoItem=null,_undoTimer=null;
function pushUndo(msg,fn){
  _undoItem=fn;const t=document.getElementById('undo-toast');document.getElementById('undo-msg').textContent=msg;t.classList.add('show');
  clearTimeout(_undoTimer);_undoTimer=setTimeout(function(){t.classList.remove('show');_undoItem=null;},5000);
}
function doUndo(){if(_undoItem){_undoItem();showBadge('↩ בוטל');}document.getElementById('undo-toast').classList.remove('show');_undoItem=null;clearTimeout(_undoTimer);}

function exportBackup(){
  const b={version:'biz_v10',exported:new Date().toISOString(),state:buildStateObj(),snapshots:snapshots};
  const blob=new Blob([JSON.stringify(b,null,2)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download='גיבוי-רווח-'+new Date().toLocaleDateString('he-IL').replace(/[/]/g,'-')+'.json';a.click();showBadge('✓ גיבוי הורד');
}
function handleBackupFile(input){
  const file=input.files[0];if(!file)return;
  const reader=new FileReader();
  reader.onload=function(e){
    try{const b=JSON.parse(e.target.result);if(!b.state)throw new Error('קובץ לא תקין');
      if(!confirm('ייבא גיבוי? הנתונים הנוכחיים יוחלפו.'))return;
      if(b.snapshots){snapshots=b.snapshots.slice();saveSnapsToStorage();}
      applyState(b.state);saveState();showBadge('✓ גיבוי יובא');
    }catch(ex){alert('שגיאה: '+ex.message);}input.value='';
  };reader.readAsText(file);
}

function showQR(){
  const url=location.href.split('?')[0]+'?state='+btoa(encodeURIComponent(JSON.stringify(buildStateObj())));
  const canvas=document.getElementById('qr-canvas');const ctx=canvas.getContext('2d');
  ctx.fillStyle=isDark?'#1e1e20':'#fff';ctx.fillRect(0,0,200,200);
  const img=new Image();img.crossOrigin='anonymous';
  img.onload=function(){ctx.drawImage(img,0,0,200,200);};
  img.onerror=function(){ctx.fillStyle=isDark?'#aaa':'#555';ctx.font='12px Arial';ctx.textAlign='center';ctx.fillText('לא ניתן לטעון QR',100,100);};
  img.src='https://api.qrserver.com/v1/create-qr-code/?size=200x200&data='+encodeURIComponent(url);
  document.getElementById('qr-modal').classList.add('open');
}
function downloadQR(){const a=document.createElement('a');a.href=document.getElementById('qr-canvas').toDataURL();a.download='qr-רווח.png';a.click();}

function shareSnap(id){
  const snap=snapshots.find(function(s){return s.id===id;});if(!snap)return;
  const enc=btoa(encodeURIComponent(JSON.stringify(snap.data)));
  const url=location.href.split('?')[0]+'?snap='+enc;
  document.getElementById('share-link-box').textContent=url;
  const opts=document.getElementById('share-options');opts.innerHTML='';
  const d=snap.data,net=Math.round(d.netAmt||0),inc=d.income||0;
  function mkShare(text,fn){const b=document.createElement('button');b.className='reset-btn-sm';b.textContent=text;b.addEventListener('click',fn);return b;}
  opts.appendChild(mkShare('💬 WhatsApp',function(){const txt='📊 *'+snap.label+'*\n💰 הכנסה: ₪'+inc.toLocaleString('he-IL')+'\n✅ רווח נקי: ₪'+net.toLocaleString('he-IL');window.open('https://wa.me/?text='+encodeURIComponent(txt),'_blank');closeShareModal();}));
  opts.appendChild(mkShare('📧 מייל',function(){const s=encodeURIComponent('דוח — '+snap.label);const b2=encodeURIComponent('הכנסה: ₪'+inc.toLocaleString('he-IL')+'\nרווח נקי: ₪'+net.toLocaleString('he-IL'));window.open('mailto:?subject='+s+'&body='+b2);closeShareModal();}));
  opts.appendChild(mkShare('📄 הורד HTML',function(){downloadSnap(id);closeShareModal();}));
  document.getElementById('share-modal').classList.add('open');
}
function closeShareModal(){document.getElementById('share-modal').classList.remove('open');}
function copyShareLink(){navigator.clipboard.writeText(document.getElementById('share-link-box').textContent).then(function(){showBadge('✓ הועתק');});closeShareModal();}

function tryLoadFromURL(){
  const p=new URLSearchParams(location.search);
  const st=p.get('state'),sn=p.get('snap');
  if(st){try{if(confirm('נמצאו נתונים בקישור — לטעון?')){applyState(JSON.parse(decodeURIComponent(atob(st))));saveState();showBadge('✓ נטען');}}catch(ex){}history.replaceState({},'',location.pathname);}
  else if(sn){try{const sd=JSON.parse(decodeURIComponent(atob(sn)));const sh={id:Date.now(),label:'שמירה משותפת',note:'מקישור',date:new Date().toLocaleDateString('he-IL'),ts:Date.now(),data:sd};snapshots.unshift(sh);saveSnapsToStorage();viewingSnapId=sh.id;applyState(sd);document.getElementById('viewing-banner').classList.add('show');document.getElementById('viewing-text').textContent='צופה בנתונים משותפים';}catch(ex){}history.replaceState({},'',location.pathname);}
}

const TEMPLATES={
  tech:{income:25000,exps:[{n:'ציוד ותוכנות',p:8},{n:'שיווק',p:3},{n:'הכשרות',p:4},{n:'ביטוח מקצועי',a:300},{n:'הוצאות רכב',a:800}]},
  creative:{income:18000,exps:[{n:'ציוד יצירתי',p:6},{n:'תוכנות עיצוב',a:400},{n:'שיווק',p:5},{n:'סטודיו',a:600},{n:'חומרים',p:3}]},
  food:{income:60000,exps:[{n:'חומרי גלם',p:30},{n:'שכירות',a:8000},{n:'עובדים',p:20},{n:'חשמל וארנונה',a:2500},{n:'שיווק',p:2}]},
  retail:{income:40000,exps:[{n:'עלות סחורה',p:40},{n:'שכירות',a:5000},{n:'עובדים',p:12},{n:'חשמל וארנונה',a:1500},{n:'שיווק',p:3}]},
  ecommerce:{income:35000,exps:[{n:'עלות סחורה / ספקים',p:35},{n:'משלוחים',p:8},{n:'פרסום ממומן',p:10},{n:'פלטפורמה (Shopify/אמזון)',a:500},{n:'החזרות ופגמים',p:3},{n:'אריזות',p:2}]},
  service:{income:20000,exps:[{n:'שיווק ופרסום',p:5},{n:'ביטוח מקצועי',a:400},{n:'תוכנות וכלים',a:300},{n:'הוצאות רכב',a:600},{n:'ניהול חשבונות',a:250}]},
  photographer:{income:22000,exps:[{n:'ציוד ומצלמות',p:6},{n:'עריכה ותוכנה',a:350},{n:'נסיעות',p:4},{n:'שיווק ואתר',a:400},{n:'סטודיו / לוקיישן',a:800},{n:'גיבוי ואחסון',a:150}]},
  digital:{income:28000,exps:[{n:'פרסום ממומן (Meta/Google)',p:15},{n:'כלים ותוכנות',a:600},{n:'מנויים ופלטפורמות',a:400},{n:'הכשרות',p:3},{n:'עיצוב ותוכן',a:500}]},
};
function loadTemplate(name){
  const t=TEMPLATES[name];if(!t)return;
  document.getElementById('income').value=t.income;
  expenseRows=[];expIdCounter=0;document.getElementById('expenses-wrap').innerHTML='';
  t.exps.forEach(function(e){const amt=e.a||pctToAmt(e.p||0,t.income);const pct=e.p||amtToPct(amt,t.income);addExpense(e.n,pct,amt,e.a?'amt':'pct');});
  autoSetTax();autoSetBI();saveAndCalc();showBadge('✓ תבנית נטענה');
}

function duplicateSnap(id){
  const snap=snapshots.find(function(s){return s.id===id;});if(!snap)return;
  const copy=JSON.parse(JSON.stringify(snap));copy.id=Date.now();copy.label=snap.label+' (עותק)';copy.date=new Date().toLocaleDateString('he-IL');copy.ts=Date.now();copy.approved=false;
  snapshots.unshift(copy);saveSnapsToStorage();renderSnapList();showBadge('✓ שוכפל');
}

function renderYearlySummary(){
  const card=document.getElementById('yearly-summary-card'),wrap=document.getElementById('yearly-summary-wrap');if(!card||!wrap)return;
  if(snapshots.length<3){card.style.display='none';return;}
  const byYear={};snapshots.forEach(function(s){const y=new Date(s.ts).getFullYear();if(!byYear[y])byYear[y]=[];byYear[y].push(s);});
  const years=Object.keys(byYear).sort().reverse().slice(0,3);
  card.style.display='block';wrap.innerHTML='';
  years.forEach(function(y){
    const list=byYear[y];
    const totalNet=list.reduce(function(s,x){return s+(x.data.netAmt||0);},0);
    const avgNet=Math.round(totalNet/list.length);
    const avgInc=Math.round(list.reduce(function(s,x){return s+(x.data.income||0);},0)/list.length);
    const div=document.createElement('div');div.className='year-block';
    div.innerHTML='<div class="year-block-title">'+y+' — '+list.length+' חודשים</div><div style="display:flex;gap:8px;flex-wrap:wrap;"><div class="kpi-card" style="flex:1;"><div class="kpi-label">סה"כ רווח נקי</div><div class="kpi-value good" style="font-size:15px;">₪'+Math.round(totalNet).toLocaleString('he-IL')+'</div></div><div class="kpi-card" style="flex:1;"><div class="kpi-label">ממוצע חודשי</div><div class="kpi-value" style="font-size:15px;">₪'+avgNet.toLocaleString('he-IL')+'</div></div><div class="kpi-card" style="flex:1;"><div class="kpi-label">ממוצע הכנסה</div><div class="kpi-value" style="font-size:15px;">₪'+avgInc.toLocaleString('he-IL')+'</div></div></div>';
    wrap.appendChild(div);
  });
}

// ══ UX IMPROVEMENTS ══════════════════════════════════════

// ── Global search (Ctrl+K) ────────────────────────────────

function openGSearch() {
  document.getElementById('gsearch').classList.add('open');
  setTimeout(() => document.getElementById('gsearch-input')?.focus(), 80);
}
function closeGSearch() {
  document.getElementById('gsearch').classList.remove('open');
  document.getElementById('gsearch-input').value = '';
  document.getElementById('gsearch-results').innerHTML = '<div class="gsearch-empty">התחל להקליד לחיפוש...</div>';
}
function runGSearch(q) {
  const res = document.getElementById('gsearch-results');
  if (!q.trim()) { res.innerHTML = '<div class="gsearch-empty">התחל להקליד לחיפוש...</div>'; return; }
  const qL = q.toLowerCase();
  const matches = [];
  // Search snapshots
  if (snapshots.length) {
    const label = document.createElement('div'); label.className='gsearch-section'; label.textContent='שמירות';
    matches.push(label);
    snapshots.filter(s => s.label.toLowerCase().includes(qL)||(s.note||'').toLowerCase().includes(qL))
      .slice(0,5).forEach(s => {
        const row = document.createElement('div'); row.className='gsearch-result';
        row.innerHTML = `<span class="gsearch-result-icon">📅</span><div class="gsearch-result-main"><div class="gsearch-result-title">${s.label}</div><div class="gsearch-result-sub">${s.date}${s.note?' · '+s.note:''}</div></div><div class="gsearch-result-val">₪${Math.round(s.data.netAmt||0).toLocaleString('he-IL')}</div>`;
        row.onclick = () => { loadSnap(s.id); closeGSearch(); };
        matches.push(row);
      });
  }
  if (matches.length <= 1) { res.innerHTML = '<div class="gsearch-empty">אין תוצאות לחיפוש זה</div>'; return; }
  res.innerHTML = ''; matches.forEach(m => res.appendChild(m));
}

// ── Long-press context menu on snap items ─────────────────
let ctxSnapId = null;
function attachCtxMenu(item, snapId) {
  let pressTimer = null;
  const open = (x, y) => {
    ctxSnapId = snapId;
    const m = document.getElementById('ctx-menu');
    m.style.display = 'block';
    m.style.top = Math.min(y, window.innerHeight - 180) + 'px';
    m.style.right = Math.min(window.innerWidth - x, window.innerWidth - 190) + 'px';
    m.style.left = 'auto';
  };
  item.addEventListener('touchstart', e => { pressTimer = setTimeout(() => { e.preventDefault(); const t = e.touches[0]; open(t.clientX, t.clientY); }, 500); }, {passive:true});
  item.addEventListener('touchend', () => clearTimeout(pressTimer));
  item.addEventListener('touchmove', () => clearTimeout(pressTimer));
  item.addEventListener('contextmenu', e => { e.preventDefault(); open(e.clientX, e.clientY); });
}
document.addEventListener('click', e => {
  const m = document.getElementById('ctx-menu');
  if (m && m.style.display !== 'none' && !m.contains(e.target)) m.style.display = 'none';
});

// Patch renderSnapList to attach context menu
const _origRenderSnapList = renderSnapList;
renderSnapList = function() {
  _origRenderSnapList();
  document.querySelectorAll('.snap-item').forEach(item => {
    const net = item.querySelector('.snap-net');
    const sid = snapshots.find(s => net && '₪'+Math.round(s.data.netAmt||0).toLocaleString('he-IL') === net.textContent)?.id;
    if (sid) attachCtxMenu(item, sid);
  });
};

// ── Net profit color flash ─────────────────────────────────
let _lastNet = 0;
const _origCalc = calc;
calc = function() {
  const prev = _lastNet;
  _origCalc();
  const nv = document.getElementById('net-val');
  if (!nv) return;
  const cur = parseFloat(nv.textContent.replace(/[₪,]/g,''))||0;
  if (prev > 0 && cur !== prev) {
    nv.classList.remove('flash-green','flash-red');
    void nv.offsetWidth;
    nv.classList.add(cur > prev ? 'flash-green' : 'flash-red');
  }
  _lastNet = cur;
  renderInsightBanner(cur);
};

// ── Insight banner ─────────────────────────────────────────
function renderInsightBanner(netAmt) {
  const el = document.getElementById('insight-banner');
  if (!el) return;
  const nets = snapshots.map(s => s.data.netAmt||0);
  if (!nets.length) { el.style.display='none'; return; }
  const avg = nets.reduce((a,b)=>a+b,0)/nets.length;
  const diff = netAmt - avg;
  const pct = avg > 0 ? Math.round(Math.abs(diff)/avg*100) : 0;
  if (pct < 5) { el.style.display='none'; return; }
  el.style.display = 'flex';
  if (diff > 0) {
    el.className = 'insight-banner green';
    el.innerHTML = `🎉 &nbsp;חודש טוב! הרווח גבוה ב-${pct}% מהממוצע שלך`;
  } else {
    el.className = 'insight-banner amber';
    el.innerHTML = `📉 &nbsp;הרווח נמוך ב-${pct}% מהממוצע שלך`;
  }
}

// ── Quick mode ─────────────────────────────────────────────
function toggleQuickMode() {
  const on = !document.body.classList.contains('quick-mode');
  document.body.classList.toggle('quick-mode', on);
  document.getElementById('quick-toggle').checked = on;
  if (on) {
    const {netAmt, income} = collectItemsRaw();
    document.getElementById('quick-net-val').textContent = '₪'+Math.round(netAmt).toLocaleString('he-IL');
    document.getElementById('quick-meta').textContent = (income>0?(netAmt/income*100).toFixed(1):0)+'% מההכנסה | תחזית שנתית: ₪'+Math.round(netAmt*12).toLocaleString('he-IL');
  } else {
    // Restart background canvas after quick mode ends
    if (typeof initCalcBgCanvas === 'function') initCalcBgCanvas();
  }
  saveState();
}

// ── High contrast ──────────────────────────────────────────
function toggleHC(on) {
  document.body.classList.toggle('hc', on);
  if (on) {
    document.body.classList.add('dark');
    isDark = true;
  } else {
    // Restore the actual dark state set by home screen, not forced by HC
    var shouldDark = !!(window.homeState && window.homeState.dark);
    document.body.classList.toggle('dark', shouldDark);
    isDark = shouldDark;
  }
  document.getElementById('hc-toggle').checked = on;
  var sd=document.getElementById('s-dark'); if(sd) sd.checked=isDark;
  syncThemeColor(); saveState(); calc();
}

// ── Font size ──────────────────────────────────────────────
function setFontSize(sz) {
  const sizes = {s:'14px', m:'16px', l:'18px'};
  document.documentElement.style.fontSize = sizes[sz] || '16px';
  document.querySelectorAll('.fz-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('fz-'+sz); if(btn) btn.classList.add('active');
  saveState();
}

// ── PIN lock ───────────────────────────────────────────────
let _pinBuffer = '', _pinStored = localStorage.getItem('app_pin')||'', _pinMode = 'enter';
function buildPinGrid() {
  const grid = document.getElementById('pin-grid'); if(!grid) return;
  grid.innerHTML = '';
  [1,2,3,4,5,6,7,8,9,'',0,'⌫'].forEach(k => {
    const btn = document.createElement('button'); btn.className='pin-key';
    btn.textContent = k; btn.type='button';
    btn.onclick = () => handlePinKey(String(k));
    if(k==='') { btn.style.visibility='hidden'; }
    grid.appendChild(btn);
  });
}
function handlePinKey(k) {
  if (k==='⌫') { _pinBuffer = _pinBuffer.slice(0,-1); }
  else if (_pinBuffer.length < 4) { _pinBuffer += k; }
  // Update dots
  for(let i=0;i<4;i++) {
    const d = document.getElementById('pd'+i);
    if(d) d.classList.toggle('filled', i < _pinBuffer.length);
  }
  if (_pinBuffer.length === 4) {
    setTimeout(() => {
      if (_pinMode === 'set') { _pinStored = _pinBuffer; localStorage.setItem('app_pin',_pinStored); showBadge('✓ קוד PIN נשמר'); hidePinOverlay(); }
      else if (_pinMode === 'enter') {
        if (_pinBuffer === _pinStored) { hidePinOverlay(); }
        else { _pinBuffer=''; for(let i=0;i<4;i++){const d=document.getElementById('pd'+i);if(d)d.classList.remove('filled');} document.getElementById('pin-overlay').querySelector('.pin-title').textContent='קוד שגוי, נסה שוב'; }
      }
    }, 200);
  }
}
function hidePinOverlay() { document.getElementById('pin-overlay').classList.remove('show'); _pinBuffer=''; for(let i=0;i<4;i++){const d=document.getElementById('pd'+i);if(d)d.classList.remove('filled');} }
function togglePinSetup() {
  if (_pinStored) { if(confirm('האם לבטל את קוד ה-PIN?')) { _pinStored=''; localStorage.removeItem('app_pin'); document.getElementById('pin-toggle-btn').textContent='הגדר קוד'; showBadge('PIN בוטל'); } return; }
  _pinMode='set'; _pinBuffer=''; buildPinGrid();
  document.getElementById('pin-overlay').querySelector('.pin-title').textContent='בחר קוד PIN (4 ספרות)';
  document.getElementById('pin-overlay').classList.add('show');
}
function clearPin() { hidePinOverlay(); }
// Show PIN on load if set
window.addEventListener('DOMContentLoaded', () => {
  buildPinGrid();
  if (_pinStored) { _pinMode='enter'; document.getElementById('pin-overlay').querySelector('.pin-title').textContent='הזן קוד גישה'; document.getElementById('pin-overlay').classList.add('show'); }
});

// ── Auto-focus expense name on add ────────────────────────
const _origAddExpense = addExpense;
addExpense = function(name, pct, amt, lockMode, currency, foreignAmt) {
  _origAddExpense(name, pct, amt, lockMode, currency, foreignAmt);
  if (!name) {
    // Focus the last added expense name
    setTimeout(() => {
      const names = document.querySelectorAll('.ename-display');
      if (names.length) { const last = names[names.length-1]; last.focus(); document.execCommand('selectAll'); }
    }, 50);
  }
};

// ── Enter key moves from name → amount in expenses ────────
// expenses-wrap Enter key handler - added safely in init
function initExpensesKeyboard() {
  const ew = g$('expenses-wrap');
  if (!ew) return;
  ew.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const el = e.target;
    if (el.classList.contains('ename-display')) {
      e.preventDefault();
      const field = el.closest('.field');
      const inp = field?.querySelector('.num-box input');
      if (inp) inp.focus();
    }
  });
}

// ── Reminder if no save in 35 days ────────────────────────
function checkSaveReminder() {
  if (!snapshots.length) return;
  const last = snapshots[0].ts;
  const daysSince = (Date.now() - last) / (1000*60*60*24);
  if (daysSince > 35) {
    const banner = document.getElementById('insight-banner');
    if (banner) {
      banner.style.display = 'flex';
      banner.className = 'insight-banner amber';
      banner.innerHTML = `⏰ &nbsp;לא שמרת ${Math.round(daysSince)} ימים — זמן לשמור את נתוני החודש!`;
    }
  }
}

checkSaveReminder();

// ── Name editor accordion ─────────────────────────────────
function toggleNEGroup(id) {
  const body = document.getElementById(id);
  const chev = document.getElementById('chev-'+id);
  if (!body) return;
  const isOpen = body.classList.contains('open');
  body.classList.toggle('open', !isOpen);
  if (chev) chev.classList.toggle('open', !isOpen);
}

// ── Randomize colors ───────────────────────────────────────
function randomizeColors() {
  const {labels} = collectItemsRaw();
  const allHex = [];
  PALETTE_GROUPS.forEach(g => g.c.forEach(c => allHex.push(c.h)));
  labels.forEach(lbl => {
    const idx = Math.floor(Math.random() * allHex.length);
    itemColors[lbl] = allHex[idx];
  });
  saveAndCalc();
  renderColorGrid();
}

// ── Hide fields ───────────────────────────────────────────

function renderHideFieldsUI() {
  const wrap = document.getElementById('hide-fields-wrap');
  if (!wrap) return;
  wrap.innerHTML = '';
  const allFields = [
    ...fixedDefs.map(f => ({id: 'fixed_'+f.id, label: f.name, type:'fixed'})),
    ...expenseRows.map(r => ({id: 'exp_'+r.id, label: getExpName(r.id), type:'expense'}))
  ];
  if (!allFields.length) {
    wrap.innerHTML = '<p style="font-size:13px;color:var(--text4);">אין שדות להסתיר</p>';
    return;
  }
  allFields.forEach(field => {
    const row = document.createElement('div');
    row.className = 'dark-toggle-row';
    row.style.cssText = 'border-bottom:.5px solid var(--border);padding:.4rem 0;';
    const lbl = document.createElement('span');
    lbl.className = 'dark-toggle-label';
    lbl.style.fontSize = '13px';
    lbl.textContent = field.label;
    const tog = document.createElement('label');
    tog.className = 'toggle-switch';
    const inp = document.createElement('input');
    inp.type = 'checkbox';
    inp.checked = !hiddenFields[field.id];
    inp.addEventListener('change', () => {
      hiddenFields[field.id] = !inp.checked;
      applyHiddenFields();
      saveState();
    });
    const sl = document.createElement('span');
    sl.className = 'toggle-slider';
    tog.appendChild(inp); tog.appendChild(sl);
    row.appendChild(lbl); row.appendChild(tog);
    wrap.appendChild(row);
  });
}

function applyHiddenFields() {
  // Hide/show fixed fields
  fixedDefs.forEach(f => {
    const fieldEl = document.querySelector('#fixed-wrap .field[data-id="'+f.id+'"]');
    const sep = fieldEl?.previousElementSibling;
    if (fieldEl) {
      const hidden = hiddenFields['fixed_'+f.id];
      fieldEl.style.display = hidden ? 'none' : '';
      if (sep && sep.tagName === 'HR') sep.style.display = hidden ? 'none' : '';
    }
  });
  // Hide/show expense rows
  expenseRows.forEach(r => {
    const fieldEl = document.querySelector('#expenses-wrap .field[data-id="'+r.id+'"]');
    const sep = fieldEl?.previousElementSibling;
    if (fieldEl) {
      const hidden = hiddenFields['exp_'+r.id];
      fieldEl.style.display = hidden ? 'none' : '';
      if (sep && sep.tagName === 'HR') sep.style.display = hidden ? 'none' : '';
    }
  });
}


// ══ NEW FEATURES ═══════════════════════════════════════════

// ── Font preview ─────────────────────────────────────────────
const _origApplyFont = applyFont;
applyFont = function(val) {
  _origApplyFont(val);
  const preview = g$('font-preview-text');
  if (preview) preview.style.fontFamily = val;
};

// ── Swipe-to-reveal on snap items ─────────────────────────────
function addSwipeReveal(item, snapId) {
  let startX = 0, threshold = 60, revealed = false;
  const reveal = document.createElement('div');
  reveal.className = 'snap-swipe-reveal';
  const delBtn = document.createElement('button');
  delBtn.className = 'snap-swipe-del';
  delBtn.textContent = '🗑 מחק';
  delBtn.addEventListener('click', () => deleteSnap(snapId));
  reveal.appendChild(delBtn);
  item.appendChild(reveal);

  item.addEventListener('touchstart', e => {
    startX = e.touches[0].clientX;
  }, {passive:true});
  item.addEventListener('touchmove', e => {
    const dx = startX - e.touches[0].clientX; // RTL: swipe right reveals (negative dx)
    const rdx = e.touches[0].clientX - startX;
    if (rdx > 10) { reveal.classList.add('visible'); revealed = true; }
    else if (dx > 10) { reveal.classList.remove('visible'); revealed = false; }
  }, {passive:true});
  document.addEventListener('touchstart', e => {
    if (revealed && !item.contains(e.target)) {
      reveal.classList.remove('visible'); revealed = false;
    }
  }, {passive:true});
}

// Patch renderSnapList to attach swipe
const _origRSL2 = renderSnapList;
renderSnapList = function() {
  _origRSL2();
  document.querySelectorAll('.snap-item').forEach(item => {
    if (item.querySelector('.snap-swipe-reveal')) return; // already attached
    const net = item.querySelector('.snap-net');
    const snap = snapshots.find(s => net && ('₪'+Math.round(s.data.netAmt||0).toLocaleString('he-IL')) === net.textContent);
    if (snap) addSwipeReveal(item, snap.id);
  });
};

// ── Quick card widget ──────────────────────────────────────────
function openQuickCard() {
  const {income, netAmt} = collectItemsRaw();
  const netPct = income > 0 ? (netAmt/income*100).toFixed(1) : 0;
  const preview = g$('quick-card-preview');
  if (!preview) return;
  preview.innerHTML = `
    <div style="font-family:var(--font);padding:.5rem;">
      <div style="font-size:11px;font-weight:700;color:var(--text4);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem;">רווח נקי חודשי</div>
      <div style="font-size:44px;font-weight:900;color:var(--green);letter-spacing:-.04em;line-height:1;">₪${Math.round(netAmt).toLocaleString('he-IL')}</div>
      <div style="font-size:14px;color:var(--text3);margin-top:.4rem;font-weight:600;">${netPct}% מהכנסה ברוטו ₪${income.toLocaleString('he-IL')}</div>
      <div style="font-size:13px;color:var(--text3);margin-top:.25rem;">תחזית שנתית: ₪${Math.round(netAmt*12).toLocaleString('he-IL')}</div>
      <div style="font-size:11px;color:var(--text4);margin-top:.75rem;">${new Date().toLocaleDateString('he-IL')}</div>
    </div>`;
  g$('quick-card-modal').classList.add('open');
}
function printQuickCard() {
  const preview = g$('quick-card-preview');
  if (!preview) return;
  const w = window.open('', '_blank');
  w.document.write('<html dir="rtl"><head><meta charset="UTF-8"><link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;700;900&display=swap" rel="stylesheet"><style>body{font-family:Heebo,Arial,sans-serif;padding:2rem;background:#EDECEA;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}div{text-align:center;}</style></head><body>' + preview.innerHTML + '</body></html>');
  w.document.close();
  setTimeout(() => { w.print(); w.close(); }, 500);
}

// ── Smart insights ─────────────────────────────────────────────
function renderSmartInsights() {
  const wrap = g$('smart-insights-wrap');
  if (!wrap || snapshots.length < 2) return;
  const insights = [];
  const nets = snapshots.map(s => s.data.netAmt||0);
  const avg = nets.reduce((a,b)=>a+b,0) / nets.length;
  const latest = nets[0];
  const prev = nets[1];
  // Trend
  const trend = latest - prev;
  const trendPct = prev > 0 ? Math.round(trend/prev*100) : 0;
  if (Math.abs(trendPct) >= 5) {
    const icon = trendPct > 0 ? '📈' : '📉';
    const color = trendPct > 0 ? 'var(--green)' : 'var(--red)';
    const text = trendPct > 0
      ? `הרווח עלה ב-${trendPct}% לעומת החודש הקודם`
      : `הרווח ירד ב-${Math.abs(trendPct)}% לעומת החודש הקודם`;
    insights.push({ icon, text, color });
  }
  // Vs average
  const vsAvg = latest - avg;
  const vsAvgPct = Math.round(Math.abs(vsAvg)/avg*100);
  if (vsAvgPct >= 8) {
    const above = vsAvg > 0;
    insights.push({
      icon: above ? '🎯' : '⚠️',
      text: above
        ? `חודש זה גבוה ב-${vsAvgPct}% מהממוצע שלך — שקול לחסוך את העודף`
        : `חודש זה נמוך ב-${vsAvgPct}% מהממוצע שלך — בדוק מה השתנה`,
      color: above ? 'var(--green)' : 'var(--amber)'
    });
  }
  // Best month
  const maxNet = Math.max(...nets);
  const maxSnap = snapshots[nets.indexOf(maxNet)];
  if (maxSnap && nets.indexOf(maxNet) > 0) {
    insights.push({ icon: '🏆', text: `החודש הטוב ביותר: ${maxSnap.label} (₪${Math.round(maxNet).toLocaleString('he-IL')})`, color: 'var(--text3)' });
  }
  if (!insights.length) { wrap.innerHTML = '<p style="font-size:13px;color:var(--text4);text-align:center;padding:1rem 0;">אין תובנות חדשות</p>'; return; }
  wrap.innerHTML = insights.map(ins =>
    `<div style="display:flex;align-items:flex-start;gap:10px;padding:.6rem 0;border-bottom:1px solid var(--border);">
      <span style="font-size:18px;flex-shrink:0;">${ins.icon}</span>
      <span style="font-size:13px;color:${ins.color};font-weight:600;line-height:1.5;">${ins.text}</span>
    </div>`
  ).join('').replace(/border-bottom[^;]+;(?=[^"]*<\/div>\s*$)/, '');
}

// Patch renderAnalysis to call renderSmartInsights
const _origRA = renderAnalysis;
renderAnalysis = function() {
  _origRA();
  renderSmartInsights();
};

// ── Export to accountant ───────────────────────────────────────
function exportAccountant() {
  if (!snapshots.length) { alert('אין שמירות לייצוא'); return; }
  const now = new Date();
  const year = now.getFullYear();
  const snapsThisYear = snapshots.filter(s => new Date(s.ts).getFullYear() === year);
  const list = snapsThisYear.length ? snapsThisYear : snapshots.slice(0, 12);

  const totalIncome = list.reduce((s,x) => s+(x.data.income||0), 0);
  const totalTax = list.reduce((s,x) => s+(x.data.fixed?.tax?.amt||0), 0);
  const totalBI = list.reduce((s,x) => s+(x.data.fixed?.bi?.amt||0), 0);
  const totalVAT = list.reduce((s,x) => s+(x.data.fixed?.vat?.amt||0), 0);
  const totalExp = list.reduce((s,x) => s+(x.data.expenses||[]).reduce((e,r)=>e+r.amt,0), 0);
  const totalNet = list.reduce((s,x) => s+(x.data.netAmt||0), 0);

  const rowsHTML = list.map(s => {
    const d = s.data;
    const inc = d.income||0;
    const tax = d.fixed?.tax?.amt||0;
    const bi = d.fixed?.bi?.amt||0;
    const vat = d.fixed?.vat?.amt||0;
    const exp = (d.expenses||[]).reduce((e,r)=>e+r.amt,0);
    const net = d.netAmt||0;
    return `<tr><td>${s.label}</td><td>₪${inc.toLocaleString('he-IL')}</td><td>₪${tax.toLocaleString('he-IL')}</td><td>₪${bi.toLocaleString('he-IL')}</td><td>₪${vat.toLocaleString('he-IL')}</td><td>₪${exp.toLocaleString('he-IL')}</td><td><strong>₪${net.toLocaleString('he-IL')}</strong></td></tr>`;
  }).join('');

  const html = `<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="UTF-8"><title>דוח לחשבונאי ${year}</title>
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>body{font-family:Heebo,Arial,sans-serif;padding:2rem;max-width:900px;margin:0 auto;color:#111;}h1{font-size:22px;font-weight:800;margin-bottom:.25rem;}h2{font-size:14px;color:#888;font-weight:500;margin-bottom:1.5rem;}table{width:100%;border-collapse:collapse;margin-bottom:2rem;}th{text-align:right;background:#EDECEA;padding:10px 12px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#666;}td{padding:10px 12px;border-bottom:1px solid #eee;font-size:13px;}tr:last-child td{border-bottom:none;}.totals-row td{background:#f8f8f6;font-weight:700;border-top:2px solid #ddd;}.green{color:#0F9E6A;}.note{font-size:11px;color:#aaa;margin-top:2rem;}</style>
</head><body>
<h1>דוח הכנסות ורווח נקי — ${year}</h1>
<h2>נוצר: ${now.toLocaleDateString('he-IL')} | ${list.length} חודשים</h2>
<table><thead><tr><th>חודש</th><th>הכנסה</th><th>מס הכנסה</th><th>ביטוח לאומי</th><th>מע"מ</th><th>הוצאות</th><th>רווח נקי</th></tr></thead>
<tbody>${rowsHTML}
<tr class="totals-row"><td><strong>סה"כ</strong></td><td>₪${totalIncome.toLocaleString('he-IL')}</td><td>₪${totalTax.toLocaleString('he-IL')}</td><td>₪${totalBI.toLocaleString('he-IL')}</td><td>₪${totalVAT.toLocaleString('he-IL')}</td><td>₪${totalExp.toLocaleString('he-IL')}</td><td class="green">₪${totalNet.toLocaleString('he-IL')}</td></tr>
</tbody></table>
<p class="note">* דוח זה נוצר ממחשבון הרווח הנקי ואינו מהווה מסמך רשמי. יש לאמת מול רואה חשבון.</p>
</body></html>`;

  const blob = new Blob([html], {type:'text/html;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'דוח-לחשבונאי-' + year + '.html';
  a.click();
  showBadge('✓ דוח הורד');
}

// ── Scenario comparison ────────────────────────────────────────
function runScenario() {
  const res = g$('scenario-result');
  if (!res) return;
  const aInc = parseFloat(g$('sc-a-income')?.value) || getIncome();
  const aExp = parseFloat(g$('sc-a-exp')?.value) || 0;
  const bInc = parseFloat(g$('sc-b-income')?.value) || getIncome();
  const bExp = parseFloat(g$('sc-b-exp')?.value) || 0;
  if (!g$('sc-a-income')?.value && !g$('sc-b-income')?.value) { res.style.display='none'; return; }

  function calcNet(inc, extraExp) {
    const expBase = getExpensesAmt() + extraExp;
    const taxBase = Math.max(0, inc - expBase);
    const tax = calcIsraeliTax(taxBase);
    const bi = calcIsraeliBI(inc);
    const vat = inc * VAT_RATE_DEFAULT / 100;
    return Math.max(0, inc - expBase - tax - bi - vat);
  }

  const netA = calcNet(aInc, aExp);
  const netB = calcNet(bInc, bExp);
  const diff = netB - netA;
  const diffSign = diff >= 0 ? '+' : '';
  const betterColor = diff > 0 ? 'var(--green)' : diff < 0 ? 'var(--red)' : 'var(--text3)';

  res.style.display = 'block';
  res.innerHTML = `
    <div style="display:flex;gap:8px;margin-bottom:.6rem;">
      <div style="flex:1;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:.75rem;text-align:center;">
        <div style="font-size:10px;font-weight:700;color:var(--text4);text-transform:uppercase;margin-bottom:4px;">תרחיש א</div>
        <div style="font-size:20px;font-weight:800;color:var(--text);">₪${Math.round(netA).toLocaleString('he-IL')}</div>
        <div style="font-size:11px;color:var(--text3);">רווח נקי</div>
      </div>
      <div style="flex:1;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:.75rem;text-align:center;">
        <div style="font-size:10px;font-weight:700;color:var(--accent-text);text-transform:uppercase;margin-bottom:4px;">תרחיש ב</div>
        <div style="font-size:20px;font-weight:800;color:var(--text);">₪${Math.round(netB).toLocaleString('he-IL')}</div>
        <div style="font-size:11px;color:var(--text3);">רווח נקי</div>
      </div>
    </div>
    <div style="text-align:center;font-size:14px;font-weight:700;color:${betterColor};">
      הפרש: ${diffSign}₪${Math.round(Math.abs(diff)).toLocaleString('he-IL')} לחודש &nbsp;·&nbsp; ${diffSign}₪${Math.round(Math.abs(diff)*12).toLocaleString('he-IL')} לשנה
    </div>`;
}


// ══ DROPSHIPPING MODE ════════════════════════════════════════

let dsModeOn = false;

// Per-tab visibility toggles
function toggleTab(tabName, on) {
  var el = g$('tab-' + tabName);
  if(el) el.style.display = on ? '' : 'none';
  // If hiding and currently on this tab, go to calc
  if(!on) {
    var page = g$('page-' + tabName);
    if(page && page.classList.contains('active')) switchTab('calc', g$('tab-calc'));
  }
  if(tabName === 'ds') {
    dsModeOn = on;
    applyDSLabel();
  }
  saveState();
}

// Legacy wrapper kept for any saved-state calls
function toggleDSMode(on) { toggleTab('ds', on); }

// Collapse/expand settings sections
function toggleSettingsSection(bodyId, chevId) {
  var body = g$(bodyId);
  var chev = g$(chevId);
  if(!body) return;
  var isOpen = body.style.display !== 'none';
  body.style.display = isOpen ? 'none' : 'block';
  if(chev) chev.textContent = isOpen ? '▼' : '▲';
}

function applyDSLabel() {
  const label = g$('ne-ds-mode')?.value || 'חנות אינטרנטית';
  const btn = g$('tab-ds'); if (btn) btn.textContent = label;
  const lbl = g$('ds-mode-label'); if (lbl) lbl.textContent = label;
}

// ── Product profit ────────────────────────────────────────────
function calcDSProduct() {
  const buy   = parseFloat(g$('ds-buy')?.value)  || 0;
  const sell  = parseFloat(g$('ds-sell')?.value) || 0;
  const ship  = parseFloat(g$('ds-ship')?.value) || 0;
  const fee   = parseFloat(g$('ds-fee')?.value)  || 0;
  const ad    = parseFloat(g$('ds-ad')?.value)   || 0;
  const res   = g$('ds-product-result');
  if (!sell || !buy) { if(res) res.style.display='none'; return; }
  const feeAmt   = sell * fee / 100;
  const profit   = sell - buy - ship - feeAmt - ad;
  const margin   = sell > 0 ? (profit / sell * 100).toFixed(1) : 0;
  const roi      = buy > 0  ? (profit / buy  * 100).toFixed(0) : 0;
  const color    = profit > 0 ? 'var(--green)' : 'var(--red)';
  res.style.display = 'block';
  res.style.color = color;
  res.innerHTML = `רווח למוצר: <strong>₪${profit.toFixed(2)}</strong> &nbsp;|&nbsp; מרג׳ין: ${margin}% &nbsp;|&nbsp; ROI: ${roi}%`;
}

// ── ROAS ──────────────────────────────────────────────────────
function calcROAS() {
  const spend = parseFloat(g$('ds-roas-spend')?.value) || 0;
  const rev   = parseFloat(g$('ds-roas-rev')?.value)   || 0;
  const cogs  = parseFloat(g$('ds-roas-cogs')?.value)  || 0;
  const res   = g$('ds-roas-result');
  if (!spend || !rev) { if(res) res.style.display='none'; return; }
  const roas      = rev / spend;
  const netRev    = rev - cogs - spend;
  const breakeven = spend > 0 ? (spend / (1 - cogs/rev)).toFixed(0) : 0;
  res.style.display = 'block';
  res.style.color = netRev > 0 ? 'var(--green)' : 'var(--red)';
  res.innerHTML = `ROAS: <strong>${roas.toFixed(2)}x</strong> &nbsp;|&nbsp; רווח נקי קמפיין: ₪${netRev.toFixed(0)} &nbsp;|&nbsp; נקודת איזון: ₪${breakeven}`;
}

// ── CAC & LTV ─────────────────────────────────────────────────
function calcCAC() {
  const spend     = parseFloat(g$('ds-cac-spend')?.value)     || 0;
  const customers = parseFloat(g$('ds-cac-customers')?.value) || 0;
  const aov       = parseFloat(g$('ds-ltv-aov')?.value)       || 0;
  const freq      = parseFloat(g$('ds-ltv-freq')?.value)      || 1;
  const res       = g$('ds-cac-result');
  if (!spend || !customers) { if(res) res.style.display='none'; return; }
  const cac = spend / customers;
  const ltv = aov * freq;
  const ratio = ltv > 0 ? (ltv / cac).toFixed(2) : '—';
  const ok = ltv > cac;
  res.style.display = 'block';
  res.style.color = ok ? 'var(--green)' : 'var(--amber)';
  res.innerHTML = `CAC: <strong>₪${cac.toFixed(0)}</strong> &nbsp;|&nbsp; LTV שנתי: ₪${ltv.toFixed(0)} &nbsp;|&nbsp; יחס LTV:CAC: ${ratio}${!ok ? ' ⚠ CAC גבוה מ-LTV' : ' ✓'}`;
}

// ── Conversion ────────────────────────────────────────────────
function calcConversion() {
  const visitors = parseFloat(g$('ds-cv-visitors')?.value) || 0;
  const orders   = parseFloat(g$('ds-cv-orders')?.value)   || 0;
  const aov      = parseFloat(g$('ds-cv-aov')?.value)      || 0;
  const res      = g$('ds-cv-result');
  if (!visitors) { if(res) res.style.display='none'; return; }
  const cvr    = (orders / visitors * 100).toFixed(2);
  const rev    = orders * aov;
  const perVisitor = visitors > 0 ? (rev / visitors).toFixed(2) : 0;
  res.style.display = 'block';
  res.style.color = 'var(--text)';
  res.innerHTML = `יחס המרה: <strong>${cvr}%</strong> &nbsp;|&nbsp; הכנסה: ₪${rev.toLocaleString('he-IL')} &nbsp;|&nbsp; ₪${perVisitor} לכל מבקר`;
}

// ── Returns ───────────────────────────────────────────────────
function calcReturns() {
  const pct    = parseFloat(g$('ds-ret-pct')?.value)    || 0;
  const price  = parseFloat(g$('ds-ret-price')?.value)  || 0;
  const orders = parseFloat(g$('ds-ret-orders')?.value) || 0;
  const res    = g$('ds-ret-result');
  if (!orders || !price) { if(res) res.style.display='none'; return; }
  const retOrders = orders * pct / 100;
  const loss      = retOrders * price;
  const impact    = orders > 0 ? (loss / (orders * price) * 100).toFixed(1) : 0;
  res.style.display = 'block';
  res.style.color = pct > 10 ? 'var(--red)' : pct > 5 ? 'var(--amber)' : 'var(--green)';
  res.innerHTML = `החזרות: <strong>${retOrders.toFixed(1)}</strong> הזמנות | הפסד: ₪${loss.toFixed(0)}/חודש | השפעה: ${impact}% מההכנסה${pct > 10 ? ' ⚠ שיעור החזרה גבוה' : ''}`;
}

// ── Cash Flow ─────────────────────────────────────────────────
function calcCashFlow() {
  const supplier = parseFloat(g$('ds-cf-supplier')?.value) || 0;
  const revenue  = parseFloat(g$('ds-cf-revenue')?.value)  || 0;
  const delay    = parseFloat(g$('ds-cf-delay')?.value)    || 14;
  const res      = g$('ds-cf-result');
  if (!supplier && !revenue) { if(res) res.style.display='none'; return; }
  const gap        = revenue - supplier;
  const dailyCost  = supplier / 30;
  const delayLoss  = dailyCost * delay;
  const ok         = gap > 0;
  res.style.display = 'block';
  res.style.color = ok ? 'var(--green)' : 'var(--red)';
  res.innerHTML = `פער תזרים: <strong>${gap >= 0 ? '+' : ''}₪${gap.toFixed(0)}</strong> &nbsp;|&nbsp; עלות ${delay} ימי המתנה: ₪${delayLoss.toFixed(0)} &nbsp;|&nbsp; ${ok ? '✓ תזרים חיובי' : '⚠ דרוש מימון ביניים'}`;
}

// ── Restore DS mode on load ───────────────────────────────────
const _origApplyStatePre = applyState;
applyState = function(state) {
  _origApplyStatePre(state);
  if (state.dsModeOn) {
    dsModeOn = true;
    const tog = g$('ds-toggle'); if (tog) tog.checked = true;
    const dsTab = g$('tab-ds'); if (dsTab) dsTab.style.display = '';
    applyDSLabel();
  }
  // Restore individual tab visibility
  ['analysis','planning','tools'].forEach(function(t){
    var on = !!state['tab_'+t+'_on'];
    var el = g$('tab-'+t); if(el) el.style.display = on ? '' : 'none';
    var chk = g$('toggle-tab-'+t); if(chk) chk.checked = on;
  });
  if (state.dsLabel) {
    const inp = g$('ne-ds-mode'); if (inp) { inp.value = state.dsLabel; applyDSLabel(); }
  }
};

// ── Save DS state ─────────────────────────────────────────────
const _origBSO = buildStateObj;
buildStateObj = function() {
  const st = _origBSO();
  st.dsModeOn = dsModeOn;
  st.dsLabel  = g$('ne-ds-mode')?.value || 'חנות אינטרנטית';
  // Save individual tab states
  ['analysis','planning','tools'].forEach(function(t){
    var el = g$('tab-'+t);
    st['tab_'+t+'_on'] = el ? el.style.display !== 'none' : false;
  });
  return st;
};

// ── switchTab: add 'ds' ───────────────────────────────────────
const _origST = switchTab;
switchTab = function(tab, btn) {
  _origST(tab, btn);
  // DS tab page show/hide handled by base switchTab since page exists in DOM
};


// ══ TOOLS PAGE ═══════════════════════════════════════════════

// ── switchTab: include 'tools' ────────────────────────────────
// Already handled by base switchTab since page-tools exists in DOM

// ── #3 Real hourly rate ───────────────────────────────────────
function calcRealHourly() {
  const direct = parseFloat(g$('hr-direct')?.value) || 0;
  const admin  = parseFloat(g$('hr-admin')?.value)  || 0;
  const travel = parseFloat(g$('hr-travel')?.value)  || 0;
  const res    = g$('hr-result');
  if (!direct && !admin) { if(res) res.style.display='none'; return; }
  const totalHrsWeek = direct + admin + travel;
  const totalHrsMon  = totalHrsWeek * 4.33;
  const {netAmt} = collectItemsRaw();
  const realRate = totalHrsMon > 0 ? netAmt / totalHrsMon : 0;
  const billedRate = direct * 4.33 > 0 ? netAmt / (direct * 4.33) : 0;
  res.style.display = 'block';
  const color = realRate < 60 ? 'var(--red)' : realRate < 120 ? 'var(--amber)' : 'var(--green)';
  res.style.color = color;
  res.innerHTML = `שכר שעתי אמיתי: <strong>₪${realRate.toFixed(0)}/שעה</strong> (${totalHrsMon.toFixed(0)} שעות/חודש)<br>
    <span style="font-size:12px;font-weight:400;opacity:.8;">לפי שעות מחויבות בלבד: ₪${billedRate.toFixed(0)}/שעה — הפרש ₪${(billedRate-realRate).toFixed(0)}/שעה נעלם לניהול</span>`;
}

// ── #9 Meeting timer ──────────────────────────────────────────
let mtInterval = null, mtSeconds = 0, mtRunning = false;

function meetingStart() {
  if (mtRunning) return;
  mtRunning = true;
  g$('mt-start-btn').style.display = 'none';
  g$('mt-stop-btn').style.display  = '';
  mtInterval = setInterval(() => {
    mtSeconds++;
    const h = String(Math.floor(mtSeconds/3600)).padStart(2,'0');
    const m = String(Math.floor((mtSeconds%3600)/60)).padStart(2,'0');
    const s = String(mtSeconds%60).padStart(2,'0');
    const disp = g$('mt-display'); if(disp) disp.textContent = h+':'+m+':'+s;
    updateMeetingCost();
  }, 1000);
}

function meetingStop() {
  clearInterval(mtInterval); mtRunning = false;
  g$('mt-start-btn').style.display = '';
  g$('mt-stop-btn').style.display  = 'none';
}

function meetingReset() {
  meetingStop(); mtSeconds = 0;
  const disp = g$('mt-display'); if(disp) disp.textContent = '00:00:00';
  const cost = g$('mt-cost'); if(cost) cost.style.display = 'none';
}

function updateMeetingCost() {
  if (!mtSeconds) return;
  const participants = parseInt(g$('mt-participants')?.value) || 1;
  const {netAmt} = collectItemsRaw();
  const hourlyRate = netAmt / 160; // ~160 working hours/month
  const hours = mtSeconds / 3600;
  const cost = hourlyRate * hours * participants;
  const costEl = g$('mt-cost');
  if (costEl) {
    costEl.style.display = 'block';
    costEl.textContent = 'עלות הפגישה עד כה: ₪' + cost.toFixed(0);
  }
}

// ── #10 Pricing reminder ──────────────────────────────────────
function calcPricing() {
  const price     = parseFloat(g$('pr-price')?.value)     || 0;
  const months    = parseFloat(g$('pr-months')?.value)    || 12;
  const inflation = parseFloat(g$('pr-inflation')?.value) || 3.5;
  const res       = g$('pr-result');
  if (!price) { if(res) res.style.display='none'; return; }
  const years        = months / 12;
  const realValue    = price / Math.pow(1 + inflation/100, years);
  const recommended  = price * Math.pow(1 + inflation/100, years);
  const lossPercent  = ((price - realValue) / price * 100).toFixed(1);
  const addAmount    = (recommended - price).toFixed(0);
  res.style.display = 'block';
  const urgent = months >= 12;
  res.style.color = urgent ? 'var(--red)' : 'var(--amber)';
  res.innerHTML = `המחיר שלך שווה כיום רק <strong>₪${realValue.toFixed(0)}</strong> במונחים ריאליים (${lossPercent}% פחות)<br>
    <span style="font-size:12px;font-weight:600;">מחיר מומלץ לאחר עדכון: ₪${recommended.toFixed(0)} (+₪${addAmount})</span>${urgent ? '<br><span style="font-size:11px;">⚠ מעל שנה ללא עדכון — הגיע הזמן!</span>' : ''}`;
}

// ── #7 Invoice scanner (Claude Vision) ───────────────────────
let invoiceData = null;

function scanInvoice(input) {
  const file = input.files[0]; if(!file) return;
  const reader = new FileReader();
  g$('invoice-loading').style.display = 'block';
  g$('invoice-result').style.display  = 'none';
  g$('invoice-add-btn-wrap').style.display = 'none';
  invoiceData = null;

  reader.onload = async (e) => {
    const base64 = e.target.result.split(',')[1];
    const mediaType = file.type || 'image/jpeg';
    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 500,
          messages: [{
            role: 'user',
            content: [
              { type: 'image', source: { type: 'base64', media_type: mediaType, data: base64 } },
              { type: 'text', text: 'זוהי תמונה של חשבונית עסקית. חלץ ממנה את המידע הבא בפורמט JSON בלבד (ללא markdown, ללא טקסט נוסף):\n{"supplier":"שם הספק","amount":סכום_מספרי,"date":"תאריך","category":"קטגוריה מתוך: ציוד/שיווק/שירותים מקצועיים/הוצאות רכב/שכירות/אחר","description":"תיאור קצר"}' }
            ]
          }]
        })
      });
      const data = await response.json();
      const text = data?.content?.[0]?.text || '{}';
      try {
        invoiceData = JSON.parse(text);
      } catch(e) {
        const match = text.match(/\{[^}]+\}/s);
        invoiceData = match ? JSON.parse(match[0]) : null;
      }
      g$('invoice-loading').style.display = 'none';
      const res = g$('invoice-result');
      if (invoiceData && invoiceData.amount) {
        res.style.display = 'block';
        res.innerHTML = `
          <div class="invoice-result-row"><span class="invoice-result-label">ספק</span><span class="invoice-result-val">${invoiceData.supplier || '—'}</span></div>
          <div class="invoice-result-row"><span class="invoice-result-label">סכום</span><span class="invoice-result-val" style="color:var(--red);font-size:16px;">₪${Number(invoiceData.amount).toLocaleString('he-IL')}</span></div>
          <div class="invoice-result-row"><span class="invoice-result-label">תאריך</span><span class="invoice-result-val">${invoiceData.date || '—'}</span></div>
          <div class="invoice-result-row"><span class="invoice-result-label">קטגוריה</span><span class="invoice-result-val">${invoiceData.category || '—'}</span></div>
          <div class="invoice-result-row"><span class="invoice-result-label">תיאור</span><span class="invoice-result-val">${invoiceData.description || '—'}</span></div>`;
        g$('invoice-add-btn-wrap').style.display = 'block';
      } else {
        res.style.display = 'block';
        res.innerHTML = '<div style="color:var(--red);font-size:13px;">לא ניתן לזהות את החשבונית — נסה תמונה ברורה יותר</div>';
      }
    } catch(err) {
      g$('invoice-loading').style.display = 'none';
      const res = g$('invoice-result');
      res.style.display = 'block';
      res.innerHTML = '<div style="color:var(--red);font-size:13px;">שגיאה בניתוח — בדוק חיבור לאינטרנט</div>';
    }
    input.value = '';
  };
  reader.readAsDataURL(file);
}

function addInvoiceAsExpense() {
  if (!invoiceData || !invoiceData.amount) return;
  const name = (invoiceData.supplier || invoiceData.description || invoiceData.category || 'חשבונית').trim();
  const amt  = Number(invoiceData.amount);
  const pct  = getIncome() > 0 ? (amt / getIncome() * 100).toFixed(2) : 0;
  addExpense(name, parseFloat(pct), amt, 'amt');
  g$('invoice-result').style.display = 'none';
  g$('invoice-add-btn-wrap').style.display = 'none';
  invoiceData = null;
  switchTab('calc', g$('tab-calc'));
  showBadge('✓ הוצאה נוספה');
}

// Drag & drop for invoice
document.addEventListener('DOMContentLoaded', () => {
  const drop = g$('invoice-drop');
  if (!drop) return;
  drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('drag-over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('drag-over'));
  drop.addEventListener('drop', e => {
    e.preventDefault(); drop.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      const inp = g$('invoice-file');
      const dt = new DataTransfer(); dt.items.add(file);
      inp.files = dt.files;
      scanInvoice(inp);
    }
  });
});

// ── #8 AI Monthly advisor ─────────────────────────────────────
async function runMonthlyAdvisor() {
  const btn = g$('advisor-btn');
  const loading = g$('advisor-loading');
  const result  = g$('advisor-result');
  if (!btn || !loading || !result) return;

  btn.style.display     = 'none';
  loading.style.display = 'block';
  result.style.display  = 'none';

  const {income, netAmt} = collectItemsRaw();
  const nets = snapshots.map(s => s.data.netAmt || 0);
  const avgNet = nets.length > 0 ? Math.round(nets.reduce((a,b)=>a+b,0)/nets.length) : 0;
  const taxAmt = parseFloat(g$('a_tax')?.value) || 0;
  const expAmt = expenseRows.reduce((s,r) => s + (parseFloat(g$('a_'+r.id)?.value)||0), 0);
  const prevNet = nets[0] || 0;
  const trend   = prevNet > 0 ? ((netAmt - prevNet) / prevNet * 100).toFixed(1) : null;

  const prompt = `אתה יועץ פיננסי לעצמאים ובעלי עסקים קטנים בישראל.
הנתונים הנוכחיים:
- הכנסה חודשית ברוטו: ₪${income.toLocaleString('he-IL')}
- רווח נקי: ₪${Math.round(netAmt).toLocaleString('he-IL')} (${income > 0 ? (netAmt/income*100).toFixed(1) : 0}%)
- מס הכנסה: ₪${taxAmt.toLocaleString('he-IL')}
- סה"כ הוצאות עסקיות: ₪${expAmt.toLocaleString('he-IL')}
- ממוצע רווח נקי 12 חודשים: ₪${avgNet.toLocaleString('he-IL')}
- מגמה לעומת חודש קודם: ${trend !== null ? trend + '%' : 'אין נתון'}
- מספר שמירות בהיסטוריה: ${snapshots.length}

תן 3 המלצות ספציפיות, ממוקדות, ואקציונביליות בעברית.
כל המלצה: כותרת קצרה + משפט הסבר + פעולה מוצעת.
פורמט: JSON בלבד:
[{"title":"כותרת","insight":"תצפית על הנתונים","action":"פעולה מוצעת"}]`;

  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 800,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    const data = await res.json();
    const text = data?.content?.[0]?.text || '[]';
    let tips;
    try { tips = JSON.parse(text); }
    catch(e) { const m = text.match(/\[[\s\S]+\]/); tips = m ? JSON.parse(m[0]) : []; }

    loading.style.display = 'none';
    btn.style.display = '';

    if (!tips || !tips.length) throw new Error('empty');

    const icons = ['💡','📊','🎯'];
    result.style.display = 'block';
    result.innerHTML = tips.map((t, i) => `
      <div style="background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-md);padding:.9rem 1rem;margin-bottom:.65rem;">
        <div style="font-size:13px;font-weight:800;color:var(--text);margin-bottom:.3rem;">${icons[i]||'•'} ${t.title}</div>
        <div style="font-size:12.5px;color:var(--text3);margin-bottom:.35rem;line-height:1.5;">${t.insight}</div>
        <div style="font-size:12.5px;font-weight:600;color:var(--accent);">← ${t.action}</div>
      </div>`).join('');
  } catch(err) {
    loading.style.display = 'none';
    btn.style.display = '';
    result.style.display = 'block';
    result.innerHTML = '<div style="color:var(--red);font-size:13px;">שגיאה — בדוק חיבור לאינטרנט</div>';
  }
}



function openApp(name){
  document.body.classList.add('in-app');
  document.getElementById('app-home').style.display='none';
  ['app-calc','app-cal','app-tasks'].forEach(function(id){var el=document.getElementById(id);if(el){el.style.display='none';el.classList.remove('on');}});
  var target=document.getElementById('app-'+name);
  if(target) target.style.display='block';
  window.scrollTo(0,0);
  document.body.classList.add('in-app');
  if(name==='calc') setTimeout(function(){if(typeof calc==='function')calc();},50);
  if(name==='cal') setTimeout(function(){if(typeof calInit==='function')calInit();},50);
  if(name==='tasks') setTimeout(function(){if(typeof tkOnOpen==='function')tkOnOpen();},50);
}
function goHome(){
  document.body.classList.remove('in-app');
  document.querySelectorAll('[id^="app-"]').forEach(function(el){
    if(el.id === 'app-home'){
      el.style.display = 'flex';
    } else {
      el.style.display = 'none';
      el.classList.remove('on');
    }
  });
  window.scrollTo(0,0);
}
window.openCalc=function(){openApp('calc');};
document.addEventListener('DOMContentLoaded',function(){
  
});


// ── CALCULATOR: Privacy Mode ─────────────────────────────────────────
// ── CALCULATOR: Privacy Mode ──────────────────────────────────
var CALC_PRIVACY = false;
function calcTogglePrivacy(){
  CALC_PRIVACY = !CALC_PRIVACY;
  var btn = document.getElementById('calc-privacy-btn');
  var targets = document.querySelectorAll(
    '#net-val,#net-pct,#annual,#avg3,#avgAll,.forecast-val,.legend-right,.result-value,.result-sub,.snap-net,.income-input'
  );
  targets.forEach(function(el){
    el.style.filter = CALC_PRIVACY ? 'blur(6px)' : '';
    el.style.userSelect = CALC_PRIVACY ? 'none' : '';
  });
  if(btn){
    btn.style.background = CALC_PRIVACY ? 'var(--accent-dim)' : 'var(--surface2)';
    btn.style.color = CALC_PRIVACY ? 'var(--accent-text)' : 'var(--text3)';
    btn.style.borderColor = CALC_PRIVACY ? 'rgba(26,92,232,.3)' : 'var(--border2)';
    btn.textContent = CALC_PRIVACY ? '🙈 חשוף' : '👁 פרטיות';
  }
}

