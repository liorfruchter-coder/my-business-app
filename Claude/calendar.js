// ══ CALENDAR ══════════════════════════════════════════════════
var CAL_SK = 'biz_cal_v2';
var CAL_EVS = [];
var C_VIEW = 'month';
var C_DATE = new Date();
var C_SEL_YMD = null; // selected day in month view
var C_EDIT = null;
var C_TYPE = 'meeting';
var C_TIMERS = [];

var DAYS_HE2 = ['א','ב','ג','ד','ה','ו','ש'];
var MONTHS_HE2 = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];

function cSave(){ localStorage.setItem(CAL_SK, JSON.stringify(CAL_EVS)); }
function cLoad(){ try{ var d=localStorage.getItem(CAL_SK); if(d) CAL_EVS=JSON.parse(d); }catch(e){} }
function cYMD(d){ return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2); }
function cParse(s){ var p=s.split('-').map(Number); return new Date(p[0],p[1]-1,p[2]); }
function cSameDay(a,b){ return a.getFullYear()===b.getFullYear()&&a.getMonth()===b.getMonth()&&a.getDate()===b.getDate(); }
function cID(){ return Date.now()+'_'+Math.random().toString(36).slice(2,6); }
function cG(id){ return document.getElementById(id); }

function cV(view, btn){
  C_VIEW = view;
  document.querySelectorAll('#app-cal .c-pane').forEach(function(el){el.classList.remove('on');});
  document.querySelectorAll('#app-cal .c-tab').forEach(function(el){el.classList.remove('on');});
  var p = cG('c-pane-'+view); if(p) p.classList.add('on');
  if(btn) btn.classList.add('on');
  else {
    var b = cG('c-tab-'+(view==='month'?'m':view==='week'?'w':'s'));
    if(b) b.classList.add('on');
  }
  cDraw();
}

function cPrev(){
  if(C_VIEW==='month') C_DATE=new Date(C_DATE.getFullYear(),C_DATE.getMonth()-1,1);
  else C_DATE=new Date(C_DATE.getTime()-7*86400000);
  cDraw();
}
function cNext(){
  if(C_VIEW==='month') C_DATE=new Date(C_DATE.getFullYear(),C_DATE.getMonth()+1,1);
  else C_DATE=new Date(C_DATE.getTime()+7*86400000);
  cDraw();
}
function cToday(){ C_DATE=new Date(); cDraw(); }

function cDraw(){
  cDrawMini();
  cDrawUpcoming();
  if(C_VIEW==='month') cDrawMonth();
  else if(C_VIEW==='week') cDrawWeek();
  cReminders();
}

function cDrawMini(){
  var y=C_DATE.getFullYear(), m=C_DATE.getMonth();
  var lbl=cG('c-mini-lbl'); if(lbl) lbl.textContent=MONTHS_HE2[m]+' '+y;
  var el=cG('c-mini'); if(!el) return;
  var today=new Date();
  var fd=parseInt(cG('cs-fd')?.value||0);
  var first=new Date(y,m,1);
  var start=((first.getDay()-fd)+7)%7;
  var days=new Date(y,m+1,0).getDate();
  var html='';
  DAYS_HE2.forEach(function(d,i){ html+='<div class="c-mhdr">'+DAYS_HE2[(i+fd)%7]+'</div>'; });
  for(var i=0;i<start;i++) html+='<div class="c-mcell dim"></div>';
  for(var d=1;d<=days;d++){
    var dt=new Date(y,m,d);
    var isT=cSameDay(dt,today);
    var hasE=CAL_EVS.some(function(e){return e.date===cYMD(dt);});
    html+='<div class="c-mcell'+(isT?' today':'')+(hasE?' dot':'')+'" onclick="C_DATE=new Date('+y+','+(m)+','+d+');cDraw()">'+d+'</div>';
  }
  el.innerHTML=html;
}

function cDrawUpcoming(){
  var el=cG('c-upcoming'); if(!el) return;
  var today=cYMD(new Date());
  var list=CAL_EVS.filter(function(e){return e.date>=today;})
    .sort(function(a,b){return a.date.localeCompare(b.date)||(a.start||'').localeCompare(b.start||'');})
    .slice(0,8);
  if(!list.length){el.innerHTML='<div style="font-size:13px;color:var(--text4);text-align:center;padding:.5rem 0;">אין אירועים קרובים</div>';return;}
  el.innerHTML='';
  list.forEach(function(ev){
    var d=cParse(ev.date);
    var isT=cSameDay(d,new Date());
    var ds=isT?'היום':(d.getDate()+'/'+(d.getMonth()+1));
    var row=document.createElement('div');
    row.className='c-uitem';
    row.onclick=function(){cEditEv(ev.id);};
    var dot=document.createElement('div');
    dot.className='c-udot '+ev.type;
    var info=document.createElement('div');
    var ttl=document.createElement('div');
    ttl.style.cssText='font-size:13px;font-weight:600;'+(ev.done?'text-decoration:line-through;opacity:.5':'');
    ttl.textContent=ev.title;
    var sub=document.createElement('div');
    sub.style.cssText='font-size:11.5px;color:var(--text3);';
    sub.textContent=ds+(ev.start?' · '+ev.start:'');
    info.appendChild(ttl);info.appendChild(sub);
    row.appendChild(dot);row.appendChild(info);
    el.appendChild(row);
  });
}

function cDrawMonth(){
  var y=C_DATE.getFullYear(), m=C_DATE.getMonth();
  var today=new Date();
  var lbl=cG('c-month-lbl'); if(lbl) lbl.textContent=MONTHS_HE2[m]+' '+y;
  var fd=parseInt(cG('cs-fd')?.value||0);
  var hdrs=cG('c-hdrs');
  if(hdrs) hdrs.innerHTML=Array.from({length:7},function(_,i){return '<div class="c-hdr">'+DAYS_HE2[(i+fd)%7]+'</div>';}).join('');
  var first=new Date(y,m,1);
  var start=((first.getDay()-fd)+7)%7;
  var dim=new Date(y,m+1,0).getDate();
  var prev=new Date(y,m,0).getDate();
  var ct=Math.ceil((start+dim)/7)*7;
  var days=cG('c-days'); if(!days) return;
  var frag=document.createDocumentFragment();
  for(var i=0;i<ct;i++){
    var dt, isO=false;
    if(i<start){dt=new Date(y,m-1,prev-start+i+1);isO=true;}
    else if(i>=start+dim){dt=new Date(y,m+1,i-start-dim+1);isO=true;}
    else dt=new Date(y,m,i-start+1);
    var ymd=cYMD(dt);
    var isT=cSameDay(dt,today);
    var evs=CAL_EVS.filter(function(e){return e.date===ymd;}).sort(function(a,b){return (a.start||'').localeCompare(b.start||'');});
    var cell=document.createElement('div');
    cell.className='c-day'+(isO?' dim':'')+(isT?' today':'')+(ymd===C_SEL_YMD?' selected':'');
    cell.dataset.ymd=ymd;
    cell.innerHTML='<div class="c-dn">'+dt.getDate()+'</div><div class="c-chips"></div>';
    var chipsEl=cell.querySelector('.c-chips');
    evs.slice(0,3).forEach(function(ev){
      var chip=document.createElement('div');
      chip.className='c-chip '+ev.type+(ev.done?' done':'');
      chip.title=ev.title;
      chip.textContent=ev.title;
      chip.onclick=function(e){e.stopPropagation();cEditEv(ev.id);};
      chipsEl.appendChild(chip);
    });
    if(evs.length>3){var more=document.createElement('div');more.className='c-more';more.textContent='+'+(evs.length-3);chipsEl.appendChild(more);}
    (function(ymd2){cell.addEventListener('click',function(){cOpenModal(ymd2);});})(ymd);
    frag.appendChild(cell);
  }
  days.innerHTML='';
  days.appendChild(frag);
}

function cDrawWeek(){
  var fd=parseInt(cG('cs-fd')?.value||0);
  var h0=parseInt(cG('cs-h0')?.value||7);
  var h1=parseInt(cG('cs-h1')?.value||22);
  var today=new Date();
  var dow=C_DATE.getDay();
  var mon=new Date(C_DATE); mon.setDate(C_DATE.getDate()-((dow-fd+7)%7));
  var week=Array.from({length:7},function(_,i){var d=new Date(mon);d.setDate(mon.getDate()+i);return d;});
  var lbl=cG('c-week-lbl');
  if(lbl) lbl.textContent=week[0].getDate()+'/'+(week[0].getMonth()+1)+' – '+week[6].getDate()+'/'+(week[6].getMonth()+1)+' '+week[0].getFullYear();
  var hours=Array.from({length:h1-h0},function(_,i){return h0+i;});
  var el=cG('c-week'); if(!el) return;
  var hdr='<div class="c-week-hdr"><div class="c-wtc"></div>';
  week.forEach(function(d){ hdr+='<div class="c-wday'+(cSameDay(d,today)?' today':'')+'" style="border-right:1px solid var(--border);"><div class="c-wdname">'+DAYS_HE2[(d.getDay()+1)%7]+'</div><div class="c-wdn">'+d.getDate()+'</div></div>'; });
  hdr+='</div>';
  var body='<div class="c-week-body"><div class="c-wtc">';
  hours.forEach(function(h){body+='<div class="c-tlbl">'+h+':00</div>';});
  body+='</div>';
  week.forEach(function(d){
    var ymd=cYMD(d);
    var evs=CAL_EVS.filter(function(e){return e.date===ymd&&e.start;});
    body+='<div class="c-wcol">';
    hours.forEach(function(h){
      body+='<div class="c-wslot" data-ymd="'+ymd+'" data-h="'+('0'+h).slice(-2)+'"></div>';
    });
    evs.forEach(function(ev){
      var sh=parseInt(ev.start.split(':')[0]), sm=parseInt(ev.start.split(':')[1]||0);
      var eh=ev.end?parseInt(ev.end.split(':')[0]):sh+1;
      var em=ev.end?parseInt(ev.end.split(':')[1]||0):0;
      var top=(sh-h0)*52+Math.round(sm/60*52);
      var ht=Math.max(24,(eh*60+em-(sh*60+sm))/60*52);
      if(sh>=h0&&sh<h1) body+='<div class="c-wev '+ev.type+'" data-evid="'+ev.id+'" style="top:'+top+'px;height:'+ht+'px;">'+ev.start+' '+ev.title+'</div>';
    });
    body+='</div>';
  });
  body+='</div>';
  el.innerHTML=hdr+body;
}

function cOpenModal(ymd,startT){
  C_SEL_YMD = ymd || cYMD(new Date());
  // Highlight selected cell
  document.querySelectorAll('#app-cal .c-day.selected').forEach(function(el){el.classList.remove('selected');});
  document.querySelectorAll('#app-cal .c-day').forEach(function(el){
    if(el.dataset && el.dataset.ymd === C_SEL_YMD) el.classList.add('selected');
  });
  C_EDIT=null;
  var bg=cG('c-modal-bg'); if(!bg) return;
  cG('c-modal-ttl').textContent='אירוע חדש';
  cG('c-ev-title').value='';
  cG('c-ev-date').value=ymd||cYMD(new Date());
  cG('c-ev-s').value=startT||'';
  cG('c-ev-e').value='';
  cG('c-ev-notes').value='';
  cPickType('meeting');
  cG('c-btns').innerHTML='<button class="c-btn-x" onclick="cCloseModal()">ביטול</button><button class="c-btn-ok" onclick="cSaveModal()">שמור</button>';
  bg.classList.add('on');
  setTimeout(function(){cG('c-ev-title').focus();},80);
}
function cEditEv(id){
  var ev=CAL_EVS.find(function(e){return e.id===id;}); if(!ev) return;
  C_EDIT=id;
  var bg=cG('c-modal-bg'); if(!bg) return;
  cG('c-modal-ttl').textContent='עריכת אירוע';
  cG('c-ev-title').value=ev.title;
  cG('c-ev-date').value=ev.date;
  cG('c-ev-s').value=ev.start||'';
  cG('c-ev-e').value=ev.end||'';
  cG('c-ev-notes').value=ev.notes||'';
  cPickType(ev.type);
  var btns=cG('c-btns'); btns.innerHTML='';
  if(ev.type==='task'){var tb=document.createElement('button');tb.className='c-btn-x';tb.style='flex:none;padding:10px 12px;';tb.textContent=ev.done?'↩ בטל':'✓ בוצע';tb.onclick=function(){cToggleDone(id);};btns.appendChild(tb);}
  var db=document.createElement('button');db.className='c-btn-del';db.textContent='מחק';db.onclick=function(){cDelEv(id);};btns.appendChild(db);
  var cb=document.createElement('button');cb.className='c-btn-x';cb.textContent='ביטול';cb.onclick=cCloseModal;btns.appendChild(cb);
  var sb=document.createElement('button');sb.className='c-btn-ok';sb.textContent='שמור';sb.onclick=cSaveModal;btns.appendChild(sb);
  bg.classList.add('on');
}
function cCloseModal(){ var bg=cG('c-modal-bg'); if(bg) bg.classList.remove('on'); C_EDIT=null; }
function cPickType(t){
  C_TYPE=t;
  document.querySelectorAll('#app-cal .c-type').forEach(function(b){b.classList.remove('on');});
  var b=document.querySelector('#app-cal .c-type[data-t="'+t+'"]'); if(b) b.classList.add('on');
  var tr=cG('c-time-row'); if(tr) tr.style.display=t==='note'?'none':'';
}
function cSaveModal(){
  var title=cG('c-ev-title').value.trim(); if(!title){cG('c-ev-title').focus();return;}
  var ev={id:C_EDIT||cID(),type:C_TYPE,title:title,date:cG('c-ev-date').value||cYMD(new Date()),
    start:cG('c-ev-s').value,end:cG('c-ev-e').value,notes:cG('c-ev-notes').value.trim(),done:false};
  if(C_EDIT){ var i=CAL_EVS.findIndex(function(e){return e.id===C_EDIT;}); if(i>=0){ev.done=CAL_EVS[i].done;CAL_EVS[i]=ev;} }
  else CAL_EVS.push(ev);
  cSave(); cDraw(); cCloseModal();
}
function cDelEv(id){ if(!confirm('למחוק?')) return; CAL_EVS=CAL_EVS.filter(function(e){return e.id!==id;}); cSave();cDraw();cCloseModal(); }
function cToggleDone(id){ var ev=CAL_EVS.find(function(e){return e.id===id;}); if(ev){ev.done=!ev.done;cSave();cDraw();cCloseModal();} }

function cExport(){
  var a=document.createElement('a');
  a.href='data:application/json,'+encodeURIComponent(JSON.stringify(CAL_EVS,null,2));
  a.download='calendar.json';a.click();
}
function cImport(input){
  var file=input.files[0]; if(!file) return;
  var r=new FileReader();
  r.onload=function(e){
    try{var d=JSON.parse(e.target.result);if(Array.isArray(d)){CAL_EVS=[...CAL_EVS,...d.filter(function(ev){return !CAL_EVS.find(function(e2){return e2.id===ev.id;});})];cSave();cDraw();alert('יובאו '+d.length+' אירועים');}}
    catch(err){alert('קובץ לא תקין');}
  };r.readAsText(file);input.value='';
}

function cReminders(){
  C_TIMERS.forEach(clearTimeout);C_TIMERS=[];
}


// Event delegation for calendar week view
document.addEventListener('click', function(e) {
  var slot = e.target.closest('.c-wslot');
  if (slot) { cOpenModal(slot.dataset.ymd, slot.dataset.h + ':00'); return; }
  var wev = e.target.closest('.c-wev');
  if (wev) { e.stopPropagation(); cEditEv(wev.dataset.evid); return; }
});

// Called when calendar opens
function calInit(){
  cLoadSettings();
  var panes = document.querySelectorAll('#app-cal .c-pane');
  panes.forEach(function(p){ p.classList.remove('on'); });
  var mp = document.getElementById('c-pane-month');
  if(mp) mp.classList.add('on');
  var tabs = document.querySelectorAll('#app-cal .c-tab');
  tabs.forEach(function(t){ t.classList.remove('on'); });
  var mt = document.getElementById('c-tab-m');
  if(mt) mt.classList.add('on');
  C_VIEW = 'month';
  cLoad();
  if(typeof requestAnimationFrame !== 'undefined'){
    requestAnimationFrame(function(){ requestAnimationFrame(cDraw); });
  } else { setTimeout(cDraw, 100); }
}


// ══ CALENDAR FEATURES ════════════════════════════════════════

// ─── 1. Reminders (in-app alert 15min before) ──────────────────
var C_REM_TIMERS = [];
function cScheduleReminders(){
  C_REM_TIMERS.forEach(clearTimeout); C_REM_TIMERS = [];
  var now = Date.now();
  CAL_EVS.forEach(function(ev){
    if(!ev.start || ev.done) return;
    var parts = ev.start.split(':').map(Number);
    var dt = cParse(ev.date);
    dt.setHours(parts[0], parts[1], 0, 0);
    var fireAt = dt.getTime() - 15*60000;
    var delay = fireAt - now;
    if(delay > 0 && delay < 86400000){
      C_REM_TIMERS.push(setTimeout(function(){
        cShowAlert('🔔 בעוד 15 דקות: ' + ev.title + ' (' + ev.start + ')');
        if(typeof Notification !== 'undefined' && Notification.permission === 'granted'){
          new Notification('📅 ' + ev.title, {body: 'בעוד 15 דקות — ' + ev.start});
        }
      }, delay));
    }
  });
  // Ask for notification permission only ONCE ever
  if(typeof Notification !== 'undefined' && Notification.permission === 'default'){
    var asked = localStorage.getItem('cal_notif_asked');
    if(!asked){
      localStorage.setItem('cal_notif_asked','1');
      Notification.requestPermission();
    }
  }
}

function cShowAlert(msg){
  var old = document.getElementById('c-alert-el');
  if(old) old.remove();
  var el = document.createElement('div');
  el.id = 'c-alert-el';
  el.className = 'c-alert';
  el.innerHTML = '<span>' + msg + '</span><button onclick="this.parentElement.remove()" style="margin-right:auto;background:none;border:none;font-size:18px;cursor:pointer;color:var(--text3);">×</button>';
  document.body.appendChild(el);
  setTimeout(function(){ if(el.parentElement) el.remove(); }, 8000);
}

// ─── 2. Recurrence — expand recurring events for display ────────
function cGetExpandedEvents(startDate, endDate){
  var result = [];
  var s = cYMD(startDate), e = cYMD(endDate);
  CAL_EVS.forEach(function(ev){
    result.push(ev);
    if(!ev.recur) return;
    var base = cParse(ev.date);
    for(var i = 1; i <= 60; i++){
      var next = new Date(base);
      if(ev.recur === 'daily')   next.setDate(base.getDate() + i);
      else if(ev.recur === 'weekly')  next.setDate(base.getDate() + i*7);
      else if(ev.recur === 'monthly') next.setMonth(base.getMonth() + i);
      else if(ev.recur === 'yearly')  next.setFullYear(base.getFullYear() + i);
      var ymd = cYMD(next);
      if(ymd > e) break;
      if(ymd >= s){
        result.push(Object.assign({}, ev, {
          id: ev.id + '_r' + i,
          date: ymd,
          isRecurInstance: true
        }));
      }
    }
  });
  return result;
}

// Patch cDrawMonth and cDrawWeek to use expanded events
var _origCAL_EVS_for_draw = null;
function cWithExpanded(fn){
  var y = C_DATE.getFullYear(), m = C_DATE.getMonth();
  var start = new Date(y, m, 1);
  var end   = new Date(y, m+1, 0);
  var saved = CAL_EVS;
  CAL_EVS = cGetExpandedEvents(start, end);
  fn();
  CAL_EVS = saved;
}

var _origDrawMonth = cDrawMonth;
cDrawMonth = function(){
  var y = C_DATE.getFullYear(), m = C_DATE.getMonth();
  var start = new Date(y, m, 1), end = new Date(y, m+1, 0);
  var saved = CAL_EVS;
  CAL_EVS = cGetExpandedEvents(start, end);
  _origDrawMonth();
  CAL_EVS = saved;
};

var _origDrawWeek = cDrawWeek;
cDrawWeek = function(){
  var fd = parseInt(cG('cs-fd')?.value||0);
  var dow = C_DATE.getDay();
  var mon = new Date(C_DATE); mon.setDate(C_DATE.getDate()-((dow-fd+7)%7));
  var end = new Date(mon); end.setDate(mon.getDate()+6);
  var saved = CAL_EVS;
  CAL_EVS = cGetExpandedEvents(mon, end);
  _origDrawWeek();
  CAL_EVS = saved;
};

// ─── 3. Drag to reschedule (week view) ──────────────────────────
var C_DRAG_EV = null;
document.addEventListener('dragstart', function(e){
  var wev = e.target.closest && e.target.closest('.c-wev');
  if(wev && wev.dataset.evid && !wev.dataset.evid.includes('_r')){
    C_DRAG_EV = wev.dataset.evid;
    wev.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
  }
});
document.addEventListener('dragend', function(e){
  document.querySelectorAll('.c-wev.dragging').forEach(function(el){el.classList.remove('dragging');});
  document.querySelectorAll('.c-wslot.drag-over').forEach(function(el){el.classList.remove('drag-over');});
  C_DRAG_EV = null;
});
document.addEventListener('dragover', function(e){
  var slot = e.target.closest && e.target.closest('.c-wslot');
  if(slot && C_DRAG_EV){
    e.preventDefault();
    document.querySelectorAll('.c-wslot.drag-over').forEach(function(el){el.classList.remove('drag-over');});
    slot.classList.add('drag-over');
  }
});
document.addEventListener('drop', function(e){
  var slot = e.target.closest && e.target.closest('.c-wslot');
  if(slot && C_DRAG_EV){
    e.preventDefault();
    var ev = CAL_EVS.find(function(x){return x.id === C_DRAG_EV;});
    if(ev && slot.dataset.ymd && slot.dataset.h){
      ev.date = slot.dataset.ymd;
      var duration = 60;
      if(ev.start && ev.end){
        var s=ev.start.split(':').map(Number), en=ev.end.split(':').map(Number);
        duration = (en[0]*60+en[1]) - (s[0]*60+s[1]);
      }
      ev.start = slot.dataset.h + ':00';
      if(ev.end){
        var sh = parseInt(slot.dataset.h);
        var em = (sh*60 + duration) % 60;
        var eh = Math.floor((sh*60 + duration) / 60);
        ev.end = ('0'+eh).slice(-2) + ':' + ('0'+em).slice(-2);
      }
      cSave(); cDraw();
    }
    document.querySelectorAll('.c-wslot.drag-over').forEach(function(el){el.classList.remove('drag-over');});
    C_DRAG_EV = null;
  }
});

// Make week events draggable
var _origDrawWeek2 = cDrawWeek;
cDrawWeek = function(){
  _origDrawWeek2();
  // Add draggable to all week events
  document.querySelectorAll('#app-cal .c-wev').forEach(function(el){
    if(!el.dataset.evid.includes('_r')) el.draggable = true;
  });
};

// ─── 4. Quick add parser ─────────────────────────────────────────
function cQuickAdd(){
  var input = cG('c-quick-input');
  var text = input ? input.value.trim() : '';
  if(!text) return;

  var ev = {id: cID(), type: 'meeting', title: text, date: cYMD(new Date()), start: '', end: '', notes: '', done: false};

  // Parse type keywords
  if(/^(משימה|task|לעשות)/i.test(text))  { ev.type = 'task';     ev.title = text.replace(/^(משימה|task|לעשות)\s*/i, ''); }
  if(/^(הערה|note)/i.test(text))          { ev.type = 'note';     ev.title = text.replace(/^(הערה|note)\s*/i, ''); }
  if(/^(תזכורת|reminder)/i.test(text))    { ev.type = 'reminder'; ev.title = text.replace(/^(תזכורת|reminder)\s*/i, ''); }
  if(/^(פגישה|meeting)/i.test(text))      { ev.type = 'meeting';  ev.title = text.replace(/^(פגישה|meeting)\s*/i, ''); }

  // Parse date
  var today = new Date();
  if(/מחר|tomorrow/i.test(text)){ var d=new Date(today);d.setDate(d.getDate()+1);ev.date=cYMD(d); ev.title=ev.title.replace(/מחר|tomorrow/gi,'').trim(); }
  else if(/אתמול|yesterday/i.test(text)){ var d=new Date(today);d.setDate(d.getDate()-1);ev.date=cYMD(d); ev.title=ev.title.replace(/אתמול|yesterday/gi,'').trim(); }
  else if(/בעוד (\d+) ימים?/i.test(text)){ var m=text.match(/בעוד (\d+) ימים?/i);var d=new Date(today);d.setDate(d.getDate()+parseInt(m[1]));ev.date=cYMD(d); ev.title=ev.title.replace(m[0],'').trim(); }

  // Parse time — matches: ב-10:00 / ב-10 / at 10 / 10:00
  var timeM = text.match(/ב[- ]?(\d{1,2})(?::(\d{2}))?/) || text.match(/at (\d{1,2})(?::(\d{2}))?/) || text.match(/(\d{1,2}):(\d{2})/);
  if(timeM){
    var h = parseInt(timeM[1]), m2 = parseInt(timeM[2]||0);
    ev.start = ('0'+h).slice(-2)+':'+('0'+m2).slice(-2);
    ev.end   = ('0'+(h+1)).slice(-2)+':'+('0'+m2).slice(-2);
    ev.title = ev.title.replace(timeM[0],'').replace(/\s+/g,' ').trim();
  }

  CAL_EVS.push(ev);
  cSave(); cDraw();
  if(input) input.value = '';
  cShowAlert('✓ נוסף: ' + ev.title);
}

// ─── 5. ICS export ──────────────────────────────────────────────
function cExportICS(){
  var lines = ['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Business Calendar//HE'];
  CAL_EVS.forEach(function(ev){
    if(ev.isRecurInstance) return;
    lines.push('BEGIN:VEVENT');
    lines.push('UID:' + ev.id + '@bizcal');
    lines.push('SUMMARY:' + ev.title);
    var d = ev.date.replace(/-/g,'');
    if(ev.start){
      var t = ev.start.replace(':','') + '00';
      lines.push('DTSTART:' + d + 'T' + t);
      var et = ev.end ? ev.end.replace(':','')+'00' : (parseInt(ev.start.split(':')[0])+1)+'0000';
      lines.push('DTEND:' + d + 'T' + et);
    } else {
      lines.push('DTSTART;VALUE=DATE:' + d);
      lines.push('DTEND;VALUE=DATE:' + d);
    }
    if(ev.notes) lines.push('DESCRIPTION:' + ev.notes.replace(/\n/g,'\\\\n'));

    if(ev.recur){
      var freq = {daily:'DAILY',weekly:'WEEKLY',monthly:'MONTHLY',yearly:'YEARLY'}[ev.recur];
      if(freq) lines.push('RRULE:FREQ='+freq);
    }
    lines.push('END:VEVENT');
  });
  lines.push('END:VCALENDAR');
  var blob = new Blob([lines.join('\r\n')], {type:'text/calendar'});
  var a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = 'calendar.ics'; a.click();
}

// ─── 6. Weekly summary ──────────────────────────────────────────
function cDrawWeeklySummary(){
  var el = cG('c-weekly-summary-content'); if(!el) return;
  var today = new Date();
  var fd = parseInt(cG('cs-fd')?.value||0);
  var dow = today.getDay();
  var mon = new Date(today); mon.setDate(today.getDate()-((dow-fd+7)%7));
  var sun = new Date(mon); sun.setDate(mon.getDate()+6);

  var expanded = cGetExpandedEvents(mon, sun);
  var weekStr  = mon.getDate()+'/'+(mon.getMonth()+1)+' – '+sun.getDate()+'/'+(sun.getMonth()+1);
  var meetings = expanded.filter(function(e){return e.type==='meeting';}).length;
  var tasks    = expanded.filter(function(e){return e.type==='task';});
  var done     = tasks.filter(function(e){return e.done;}).length;
  var totalMin = 0;
  expanded.filter(function(e){return e.start&&e.end;}).forEach(function(e){
    var s=e.start.split(':').map(Number), en=e.end.split(':').map(Number);
    totalMin += (en[0]*60+en[1]) - (s[0]*60+s[1]);
  });
  var hrs = Math.floor(totalMin/60), mins = totalMin%60;

  // Link to calculator hourly rate
  var netAmt = 0;
  try{ var st=localStorage.getItem('biz_v10'); if(st){var d=JSON.parse(st);netAmt=d.netAmt||0;} }catch(e){}
  var hrRate = netAmt > 0 && hrs > 0 ? '₪' + Math.round(netAmt/160*totalMin/60) : '';

  el.innerHTML =
    '<div style="margin-bottom:.5rem;">📅 שבוע ' + weekStr + '</div>' +
    '<div>📋 פגישות: <strong>' + meetings + '</strong></div>' +
    '<div>✅ משימות: <strong>' + done + '/' + tasks.length + '</strong> הושלמו</div>' +
    '<div>⏱ שעות מתוכנות: <strong>' + hrs + ':' + ('0'+mins).slice(-2) + '</strong></div>' +
    (hrRate ? '<div>💰 ערך שעות (לפי שכר שעתי): <strong>' + hrRate + '</strong></div>' : '') +
    '<div style="margin-top:.75rem;font-size:12px;color:var(--text3);">לשבוע הבא: ' + expanded.filter(function(e){var d=cParse(e.date);return d>sun&&d<=new Date(sun.getTime()+7*86400000);}).length + ' אירועים</div>';
}

// Patch cV to render weekly summary when tab selected
var _origCV = cV;
cV = function(view, btn){
  _origCV(view, btn);
  if(view === 'weekly-summary') cDrawWeeklySummary();
};

// ─── 7. Save/restore recur + color in modal ──────────────────────
var _origSaveModal = cSaveModal;
cSaveModal = function(){
  var title = cG('c-ev-title').value.trim(); if(!title){cG('c-ev-title').focus();return;}
  var ev = {
    id: C_EDIT||cID(), type: C_TYPE, title: title,
    date: cG('c-ev-date').value||cYMD(new Date()),
    start: cG('c-ev-s').value, end: cG('c-ev-e').value,
    notes: cG('c-ev-notes').value.trim(), done: false,
    recur: cG('c-ev-recur').value||'',
    color: cG('c-ev-color').value||''
  };
  if(C_EDIT){ var i=CAL_EVS.findIndex(function(e){return e.id===C_EDIT;}); if(i>=0){ev.done=CAL_EVS[i].done;CAL_EVS[i]=ev;} }
  else CAL_EVS.push(ev);
  cSave(); cDraw(); cCloseModal();
};

var _origOpenModal = cOpenModal;
cOpenModal = function(ymd, startT){
  _origOpenModal(ymd, startT);
  var rc = cG('c-ev-recur'); if(rc) rc.value = '';
  var cl = cG('c-ev-color'); if(cl) cl.value = '#1668D0';
};

var _origEditEv = cEditEv;
cEditEv = function(id){
  _origEditEv(id);
  var ev = CAL_EVS.find(function(e){return e.id===id;});
  if(ev){
    var rc = cG('c-ev-recur'); if(rc) rc.value = ev.recur||'';
    var cl = cG('c-ev-color'); if(cl) cl.value = ev.color||'#1668D0';
  }
};

// ─── 8. Patch calInit ────────────────────────────────────────────
var _origCalInit = calInit;
calInit = function(){
  _origCalInit();
  cScheduleReminders();
  // Refresh reminders every minute
  setInterval(cScheduleReminders, 60000);
};


// ══ CALENDAR ADDITIONS ════════════════════════════════════════

// ─── Day view ──────────────────────────────────────────────────
function cDrawDay(){
  var today = new Date();
  var h0 = parseInt(cG('cs-h0')?.value||7);
  var h1 = parseInt(cG('cs-h1')?.value||22);
  var lbl = cG('c-day-lbl');
  var DAYS_FULL = ['ראשון','שני','שלישי','רביעי','חמישי','שישי','שבת'];
  var MONTHS_FULL = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
  if(lbl) lbl.textContent = DAYS_FULL[C_DATE.getDay()] + ', ' + C_DATE.getDate() + ' ' + MONTHS_FULL[C_DATE.getMonth()] + ' ' + C_DATE.getFullYear();

  var ymd = cYMD(C_DATE);
  var expanded = cGetExpandedEvents(C_DATE, C_DATE);
  var dayEvs  = expanded.filter(function(e){return e.date===ymd;});
  var allDay   = dayEvs.filter(function(e){return !e.start;});
  var timed    = dayEvs.filter(function(e){return !!e.start;});
  var hours    = Array.from({length:h1-h0}, function(_,i){return h0+i;});

  // All-day strip
  var ad = cG('c-day-allday');
  if(ad){
    ad.innerHTML = '';
    allDay.forEach(function(ev){
      var chip = document.createElement('div');
      chip.className = 'c-allday-chip c-chip ' + ev.type;
      chip.textContent = ev.title;
      chip.onclick = function(){ cEditEv(ev.id); };
      ad.appendChild(chip);
    });
    if(!allDay.length){
      ad.style.minHeight = '0';
      ad.style.padding = '0';
    }
  }

  // Timed grid
  var grid = cG('c-day-grid');
  if(!grid) return;
  var html = '';
  hours.forEach(function(h){
    html += '<div class="c-day-tlbl">' + h + ':00</div>';
    html += '<div class="c-day-col" data-ymd="' + ymd + '" data-h="' + ('0'+h).slice(-2) + '"></div>';
  });
  grid.innerHTML = html;

  // Add events as positioned elements
  timed.forEach(function(ev){
    var sh = parseInt(ev.start.split(':')[0]);
    var sm = parseInt(ev.start.split(':')[1]||0);
    var eh = ev.end ? parseInt(ev.end.split(':')[0]) : sh+1;
    var em = ev.end ? parseInt(ev.end.split(':')[1]||0) : 0;
    if(sh < h0 || sh >= h1) return;
    var top   = (sh-h0)*52 + Math.round(sm/60*52);
    var height = Math.max(26, (eh*60+em - (sh*60+sm))/60*52);
    // Find the col at row index sh-h0 (col index = (sh-h0)*2 + 1)
    var cols = grid.querySelectorAll('.c-day-col');
    var colIdx = sh - h0;
    if(colIdx < 0 || colIdx >= cols.length) return;
    var evEl = document.createElement('div');
    evEl.className = 'c-day-ev ' + ev.type;
    evEl.style.cssText = 'top:' + top + 'px;height:' + height + 'px;';
    evEl.textContent = ev.start + ' ' + ev.title;
    evEl.onclick = function(e){ e.stopPropagation(); cEditEv(ev.id); };
    // Position relative to the column
    var col = cols[colIdx];
    col.style.position = 'relative';
    col.appendChild(evEl);
  });

  // Click to add
  grid.querySelectorAll('.c-day-col').forEach(function(col){
    col.addEventListener('click', function(){
      cOpenModal(col.dataset.ymd, col.dataset.h + ':00');
    });
  });

  // Current time line
  if(cSameDay(C_DATE, today)){
    var nowH = today.getHours(), nowM = today.getMinutes();
    if(nowH >= h0 && nowH < h1){
      var topNow = (nowH-h0)*52 + Math.round(nowM/60*52);
      var cols2 = grid.querySelectorAll('.c-day-col');
      var timeCol = cols2[nowH-h0];
      if(timeCol){
        var line = document.createElement('div');
        line.style.cssText = 'position:absolute;left:0;right:0;top:' + topNow + 'px;height:2px;background:var(--red);z-index:2;pointer-events:none;';
        var dot = document.createElement('div');
        dot.style.cssText = 'position:absolute;right:-1px;top:-4px;width:10px;height:10px;border-radius:50%;background:var(--red);';
        line.appendChild(dot);
        timeCol.style.position = 'relative';
        timeCol.appendChild(line);
      }
    }
  }
}

// ─── Agenda view ───────────────────────────────────────────────
function cDrawAgenda(){
  var el = cG('c-agenda-list'); if(!el) return;
  var q = (cG('c-search-input')?.value||'').toLowerCase();
  var today = cYMD(new Date());
  var endDate = new Date(); endDate.setMonth(endDate.getMonth()+3);

  var expanded = cGetExpandedEvents(new Date(), endDate);
  var filtered = expanded.filter(function(e){
    if(q && !e.title.toLowerCase().includes(q) && !(e.notes||'').toLowerCase().includes(q)) return false;
    return e.date >= today;
  }).sort(function(a,b){return a.date.localeCompare(b.date)||(a.start||'').localeCompare(b.start||'');});

  if(!filtered.length){
    el.innerHTML='<div style="text-align:center;color:var(--text4);padding:2rem;font-size:14px;">'+(q?'אין תוצאות':'אין אירועים קרובים')+'</div>';
    return;
  }

  // Group by date
  var groups = {};
  filtered.forEach(function(ev){
    if(!groups[ev.date]) groups[ev.date]=[];
    groups[ev.date].push(ev);
  });

  var DAYS_FULL = ['ראשון','שני','שלישי','רביעי','חמישי','שישי','שבת'];
  el.innerHTML = '';
  Object.keys(groups).sort().forEach(function(date){
    var d = cParse(date);
    var isToday = cSameDay(d, new Date());
    var label = isToday ? 'היום' : (DAYS_FULL[d.getDay()] + ', ' + d.getDate() + '/' + (d.getMonth()+1));
    var grp = document.createElement('div'); grp.className = 'c-agenda-group'; el.appendChild(grp);
    var dateHdr = document.createElement('div'); dateHdr.className = 'c-agenda-date'; dateHdr.textContent = label; grp.appendChild(dateHdr);
    groups[date].forEach(function(ev){
      var tid = ev.isRecurInstance ? (ev.id.split('_r')[0]) : ev.id;
      var agEl=document.createElement('div');agEl.className='c-agenda-item';(function(eid){agEl.onclick=function(){cEditEv(eid);};})(tid);
      agEl.innerHTML='<div class="c-agenda-dot '+ev.type+'"></div><div class="c-agenda-time">'+(ev.start||'כל היום')+'</div><div style="flex:1;min-width:0;"><div style="font-size:13px;font-weight:600;color:var(--text);">'+(ev.done?'<s>':'')+ev.title+(ev.done?'</s>':'')+'</div>'+(ev.recur?'<span class="c-recur-badge">🔁 חוזר</span>':'')+(ev.notes?'<div style="font-size:11px;color:var(--text3);">'+ev.notes.slice(0,50)+'</div>':'')+'</div>';
        + '<div class="c-agenda-time">' + (ev.start||'כל היום') + '</div>'
        + '<div><div style="font-size:13px;font-weight:600;color:var(--text);' + (ev.done?'text-decoration:line-through;opacity:.5':'') + '">' + ev.title + '</div>'
        + (ev.recur?'<span class="c-recur-badge">🔁 חוזר</span>':'')
        + (ev.notes?'<div style="font-size:11px;color:var(--text3);">' + ev.notes.slice(0,50) + '</div>':'')
        + '</div></div>';
    });
  });
}

// ─── Search modal ──────────────────────────────────────────────
function cSearch(){
  var modal = cG('c-search-modal');
  if(!modal) return;
  modal.style.display = 'flex';
  setTimeout(function(){ cG('c-search-modal-input')?.focus(); }, 80);
  cSearchModal();
}

function cSearchModal(){
  var q = (cG('c-search-modal-input')?.value||'').toLowerCase();
  var el = cG('c-search-results'); if(!el) return;
  if(!q){ el.innerHTML = '<div style="padding:1.5rem;text-align:center;color:var(--text4);font-size:13px;">הקלד לחיפוש...</div>'; return; }

  var results = CAL_EVS.filter(function(e){
    return e.title.toLowerCase().includes(q) || (e.notes||'').toLowerCase().includes(q) || e.date.includes(q);
  }).slice(0,20);

  if(!results.length){ el.innerHTML='<div style="padding:1.5rem;text-align:center;color:var(--text4);font-size:13px;">אין תוצאות</div>'; return; }

  el.innerHTML = '';
  results.forEach(function(ev){
    var d = cParse(ev.date);
    var dateStr = d.getDate()+'/'+(d.getMonth()+1)+'/'+d.getFullYear();
    var colors = {meeting:'var(--accent)',task:'var(--green)',note:'var(--amber)',reminder:'#7C3AED'};
    var row = document.createElement('div'); row.className='c-search-result';
    (function(eid){row.onclick=function(){cEditEv(eid);var sm=cG('c-search-modal');if(sm)sm.style.display='none';};})(ev.id);
    row.innerHTML='<div style="width:10px;height:10px;border-radius:3px;background:'+(colors[ev.type]||'var(--text3)')+';flex-shrink:0;"></div><div><div style="font-size:13px;font-weight:600;color:var(--text);">'+ev.title+'</div><div style="font-size:11.5px;color:var(--text3);">'+dateStr+(ev.start?' · '+ev.start:'')+'</div></div>';
    el.appendChild(row);
  });
}

// ─── Check-in timer ────────────────────────────────────────────
var C_CHECKIN = null;
var C_CHECKIN_EV = null;
function cCheckin(id){
  if(C_CHECKIN){ clearInterval(C_CHECKIN); C_CHECKIN=null; }
  var ev = CAL_EVS.find(function(e){return e.id===id;});
  if(!ev) return;
  C_CHECKIN_EV = id;
  ev.checkinStart = Date.now();
  cSave();
  cShowAlert('⏱ צ\u05e7-אין: ' + ev.title + ' — השעון פועל');
  C_CHECKIN = setInterval(function(){
    var evNow = CAL_EVS.find(function(e){return e.id===C_CHECKIN_EV;});
    if(!evNow||!evNow.checkinStart){ clearInterval(C_CHECKIN); return; }
    var elapsed = Math.round((Date.now()-evNow.checkinStart)/60000);
    cG('c-checkin-time')&&(cG('c-checkin-time').textContent = elapsed + ' דקות');
  }, 30000);
}
function cCheckout(id){
  if(C_CHECKIN){ clearInterval(C_CHECKIN); C_CHECKIN=null; }
  var ev = CAL_EVS.find(function(e){return e.id===id;});
  if(!ev||!ev.checkinStart) return;
  var mins = Math.round((Date.now()-ev.checkinStart)/60000);
  ev.actualDuration = mins;
  delete ev.checkinStart;
  cSave(); cDraw();
  cShowAlert('✓ פגישה הסתיימה: ' + ev.title + ' — ' + mins + ' דקות');
}

// ─── Share via URL ──────────────────────────────────────────────
function cShareEvent(id){
  var ev = CAL_EVS.find(function(e){return e.id===id;}); if(!ev) return;
  var params = new URLSearchParams({
    type:ev.type, title:ev.title, date:ev.date,
    start:ev.start||'', end:ev.end||'', notes:ev.notes||''
  });
  var url = window.location.href.split('?')[0] + '?cal_event=' + encodeURIComponent(params.toString());
  navigator.clipboard&&navigator.clipboard.writeText(url).then(function(){
    cShowAlert('🔗 קישור הועתק!');
  });
}

// Load shared event from URL on init
function cLoadFromURL(){
  try{
    var params = new URLSearchParams(window.location.search);
    var evParam = params.get('cal_event');
    if(!evParam) return;
    var p = new URLSearchParams(decodeURIComponent(evParam));
    var ev = {
      id:cID(), type:p.get('type')||'meeting', title:p.get('title')||'',
      date:p.get('date')||cYMD(new Date()), start:p.get('start')||'',
      end:p.get('end')||'', notes:p.get('notes')||'', done:false
    };
    if(ev.title && !CAL_EVS.find(function(e){return e.date===ev.date&&e.title===ev.title;})){
      if(confirm('הוסף אירוע משותף: "' + ev.title + '"?')){
        CAL_EVS.push(ev); cSave();
      }
    }
    history.replaceState&&history.replaceState(null,'',window.location.pathname);
  }catch(e){}
}

// ─── Patch cV to draw day/agenda ──────────────────────────────
var _origCV2 = cV;
cV = function(view, btn){
  _origCV2(view, btn);
  if(view==='day') cDrawDay();
  else if(view==='agenda') cDrawAgenda();
};

// ─── Patch cDraw ──────────────────────────────────────────────
var _origCDraw = cDraw;
cDraw = function(){
  _origCDraw();
  if(C_VIEW==='day') cDrawDay();
  else if(C_VIEW==='agenda') cDrawAgenda();
};

// ─── Patch cPrev/cNext for day view ───────────────────────────
var _origCPrev = cPrev;
cPrev = function(){
  if(C_VIEW==='day'){ C_DATE=new Date(C_DATE.getTime()-86400000); cDraw(); return; }
  _origCPrev();
};
var _origCNext = cNext;
cNext = function(){
  if(C_VIEW==='day'){ C_DATE=new Date(C_DATE.getTime()+86400000); cDraw(); return; }
  _origCNext();
};

// ─── Patch calInit to load URL ─────────────────────────────────
var _origCalInit2 = calInit;
calInit = function(){
  _origCalInit2();
  cLoadFromURL();
};

// ─── Keyboard shortcut: Cmd/Ctrl+K for search ──────────────────
document.addEventListener('keydown', function(e){
  if((e.metaKey||e.ctrlKey) && e.key==='k'){
    e.preventDefault();
    cSearch();
  }
});



// ── CALENDAR: Extended features ─────────────────────────────────────
// ── CALENDAR: Extended cSaveModal ────────────────────────────
var _origCSaveModal = cSaveModal;
cSaveModal = function(){
  var title = document.getElementById('c-ev-title');
  if(!title) return;
  var t = title.value.trim(); if(!t){ title.focus(); return; }
  var ev = {
    id: C_EDIT || cID(),
    type: C_TYPE,
    title: t,
    date: (document.getElementById('c-ev-date')||{}).value || cYMD(new Date()),
    start: (document.getElementById('c-ev-s')||{}).value || '',
    end:   (document.getElementById('c-ev-e')||{}).value || '',
    notes: ((document.getElementById('c-ev-notes')||{}).value||'').trim(),
    recur: (document.getElementById('c-ev-recur')||{}).value || '',
    color: (document.getElementById('c-ev-color')||{}).value || '',
    done: false,
    // New fields
    client:  ((document.getElementById('c-ev-client')||{}).value||'').trim(),
    status:  (document.getElementById('c-ev-status')||{}).value || 'confirmed',
    travel:  (document.getElementById('c-ev-travel')||{}).value || '',
    video:   ((document.getElementById('c-ev-video')||{}).value||'').trim(),
    revenue: (document.getElementById('c-ev-revenue')||{}).value || ''
  };
  if(C_EDIT){
    var i = CAL_EVS.findIndex(function(e){ return e.id===C_EDIT; });
    if(i>=0){ ev.done = CAL_EVS[i].done; CAL_EVS[i] = ev; }
  } else {
    CAL_EVS.push(ev);
  }
  cSave(); cDraw(); cCloseModal();
};

// ── CALENDAR: Extended cEditEv / cOpenModal ───────────────────
var _origCEditEv = cEditEv;
cEditEv = function(id){
  _origCEditEv(id);
  // Fill new fields after original
  setTimeout(function(){
    var ev = CAL_EVS.find(function(e){ return e.id===id; });
    if(!ev) return;
    var fClient = document.getElementById('c-ev-client');  if(fClient)  fClient.value  = ev.client||'';
    var fStatus = document.getElementById('c-ev-status');  if(fStatus)  fStatus.value  = ev.status||'confirmed';
    var fTravel = document.getElementById('c-ev-travel');  if(fTravel)  fTravel.value  = ev.travel||'';
    var fVideo  = document.getElementById('c-ev-video');   if(fVideo)   fVideo.value   = ev.video||'';
    var fRev    = document.getElementById('c-ev-revenue'); if(fRev)     fRev.value     = ev.revenue||'';
  }, 0);
};

// ── CALENDAR: Toggle extra fields based on prefs ──────────────
function cToggleExtraFields(){
  var prefs = {};
  try { prefs = JSON.parse(localStorage.getItem('cal_prefs_v1')||'{}'); } catch(e){}
  var showClient  = !!(document.getElementById('cal-field-client')||{}).checked;
  var showStatus  = !!(document.getElementById('cal-field-status')||{}).checked;
  var showTravel  = !!(document.getElementById('cal-field-travel')||{}).checked;
  var showVideo   = !!(document.getElementById('cal-field-video')||{}).checked;
  var showRevenue = !!(document.getElementById('cal-field-revenue')||{}).checked;
  var clientRow  = document.getElementById('c-client-row');  if(clientRow)  clientRow.style.display  = showClient?'':'none';
  var statusRow  = document.getElementById('c-status-row');  if(statusRow)  statusRow.style.display  = showStatus?'':'none';
  var travelRow  = document.getElementById('c-travel-row');  if(travelRow)  travelRow.style.display  = showTravel?'':'none';
  var videoRow   = document.getElementById('c-video-row');   if(videoRow)   videoRow.style.display   = showVideo?'':'none';
  var revRow     = document.getElementById('c-revenue-row'); if(revRow)     revRow.style.display     = showRevenue?'':'none';
}

// ── CALENDAR: Extended cSaveSettings ─────────────────────────
var _origCSaveSettings = cSaveSettings;
cSaveSettings = function(){
  _origCSaveSettings();
  var prefs = {};
  try { prefs = JSON.parse(localStorage.getItem('cal_prefs_v1')||'{}'); } catch(e){}
  prefs.fieldClient  = !!(document.getElementById('cal-field-client')||{}).checked;
  prefs.fieldStatus  = !!(document.getElementById('cal-field-status')||{}).checked;
  prefs.fieldTravel  = !!(document.getElementById('cal-field-travel')||{}).checked;
  prefs.fieldVideo   = !!(document.getElementById('cal-field-video')||{}).checked;
  prefs.fieldRevenue = !!(document.getElementById('cal-field-revenue')||{}).checked;
  localStorage.setItem('cal_prefs_v1', JSON.stringify(prefs));
};

// ── CALENDAR: Extended cLoadSettings ─────────────────────────
var _origCLoadSettings = cLoadSettings;
cLoadSettings = function(){
  _origCLoadSettings();
  try {
    var prefs = JSON.parse(localStorage.getItem('cal_prefs_v1')||'{}');
    var map = {
      'cal-field-client':  prefs.fieldClient,
      'cal-field-status':  prefs.fieldStatus,
      'cal-field-travel':  prefs.fieldTravel,
      'cal-field-video':   prefs.fieldVideo,
      'cal-field-revenue': prefs.fieldRevenue
    };
    Object.keys(map).forEach(function(id){
      var el = document.getElementById(id); if(el) el.checked = !!map[id];
    });
    cToggleExtraFields();
  } catch(e){}
};

// ── CALENDAR: CSV Export ──────────────────────────────────────
function cExportCSV(){
  var headers = ['כותרת','סוג','תאריך','שעת התחלה','שעת סיום','לקוח','סטטוס','הכנסה','הערות'];
  var rows = CAL_EVS.map(function(ev){
    return [
      ev.title||'', ev.type||'', ev.date||'', ev.start||'', ev.end||'',
      ev.client||'', ev.status||'', ev.revenue||'', (ev.notes||'').replace(/[\r\n]/g,' ')
    ].map(function(v){ return '"'+String(v).replace(/"/g,'""')+'"'; }).join(',');
  });
  var csv = '﻿' + headers.join(',') + '\n' + rows.join('\n'); // BOM for Excel
  var a = document.createElement('a');
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  a.download = 'calendar-' + new Date().toISOString().split('T')[0] + '.csv';
  a.click();
}

// ── CALENDAR: Year View ───────────────────────────────────────
var C_YEAR_VIEW = new Date().getFullYear();

function cDrawYear(){
  var lbl = document.getElementById('c-year-lbl');
  if(lbl) lbl.textContent = C_YEAR_VIEW;
  var grid = document.getElementById('c-year-grid');
  if(!grid) return;
  var months = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
  var today = new Date();
  var html = '';
  for(var m=0; m<12; m++){
    var evCount = CAL_EVS.filter(function(ev){
      return ev.date && ev.date.startsWith(C_YEAR_VIEW+'-'+('0'+(m+1)).slice(-2));
    }).length;
    var revenue = CAL_EVS.reduce(function(sum,ev){
      if(ev.date && ev.date.startsWith(C_YEAR_VIEW+'-'+('0'+(m+1)).slice(-2)) && ev.revenue){
        return sum + parseFloat(ev.revenue||0);
      }
      return sum;
    }, 0);
    var isCurrentMonth = (today.getFullYear()===C_YEAR_VIEW && today.getMonth()===m);
    html += '<div onclick="C_DATE=new Date('+C_YEAR_VIEW+','+m+',1);cV(\'month\',document.getElementById(\'c-tab-m\'))" style="cursor:pointer;background:var(--cal-surface,var(--surface));border:1.5px solid '+(isCurrentMonth?'var(--accent)':'var(--cal-border,var(--border))') +';border-radius:12px;padding:.6rem .8rem;transition:transform .15s,box-shadow .15s;" onmouseover="this.style.transform=\'translateY(-2px)\';this.style.boxShadow=\'0 4px 16px rgba(0,0,0,.1)\'" onmouseout="this.style.transform=\'\';this.style.boxShadow=\'\'">' +
      '<div style="font-size:12px;font-weight:800;color:'+(isCurrentMonth?'var(--accent)':'var(--cal-text2,var(--text2))') +';">'+months[m]+'</div>' +
      '<div style="font-size:20px;font-weight:900;color:var(--cal-text,var(--text));margin:.2rem 0;">'+evCount+'</div>' +
      '<div style="font-size:10px;color:var(--cal-text3,var(--text3));">אירועים</div>' +
      (revenue>0?'<div style="font-size:11px;font-weight:700;color:var(--green);margin-top:3px;">₪'+revenue.toLocaleString()+'</div>':'') +
      '</div>';
  }
  grid.innerHTML = html;

  // Year stats
  var stats = document.getElementById('c-year-stats');
  if(stats){
    var totalEvs = CAL_EVS.filter(function(ev){ return ev.date && ev.date.startsWith(C_YEAR_VIEW+'-'); }).length;
    var totalRev = CAL_EVS.reduce(function(sum,ev){
      return (ev.date&&ev.date.startsWith(C_YEAR_VIEW+'-')&&ev.revenue) ? sum+parseFloat(ev.revenue||0) : sum;
    },0);
    stats.innerHTML = '<div style="display:flex;gap:10px;flex-wrap:wrap;">' +
      '<div style="background:var(--accent-dim);border-radius:12px;padding:.6rem 1rem;"><div style="font-size:11px;color:var(--accent-text);">סה״כ אירועים</div><div style="font-size:22px;font-weight:900;color:var(--accent);">'+totalEvs+'</div></div>' +
      (totalRev>0?'<div style="background:var(--green-dim);border-radius:12px;padding:.6rem 1rem;"><div style="font-size:11px;color:var(--green-text);">הכנסות שנתיות</div><div style="font-size:22px;font-weight:900;color:var(--green);">₪'+totalRev.toLocaleString()+'</div></div>':'') +
      '</div>';
  }
}

// Patch cV to handle year view and update C_YEAR_VIEW on nav
var _origCV2 = cV;
cV = function(view, btn){
  if(view==='year'){
    document.querySelectorAll('#app-cal .c-pane').forEach(function(el){el.classList.remove('on');});
    document.querySelectorAll('#app-cal .c-tab').forEach(function(el){el.classList.remove('on');});
    var p = document.getElementById('c-pane-year'); if(p) p.classList.add('on');
    if(btn) btn.classList.add('on');
    C_YEAR_VIEW = C_DATE.getFullYear();
    cDrawYear();
    return;
  }
  _origCV2(view, btn);
};

