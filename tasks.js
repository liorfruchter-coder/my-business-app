// ══ TASKS APP ════════════════════════════════════════════════


// ══ TASKS APP ════════════════════════════════════════════════
var TK_SK = 'biz_tasks_v3';
var tkTasks = [];
var tkCurrentFilter = 'all';
var tkEditId = null;

function tkSave(){ localStorage.setItem(TK_SK, JSON.stringify(tkTasks)); }
function tkLoad(){
  try { var d = localStorage.getItem(TK_SK); if(d) tkTasks = JSON.parse(d); }
  catch(e){ tkTasks = []; }
}
function tkID(){ return 'tk_' + Date.now() + '_' + Math.random().toString(36).slice(2,5); }
function tkYMD(d){ return (d||new Date()).toISOString().split('T')[0]; }

// ─── Render ───────────────────────────────────────────────────
function tkDrawAll(){
  tkDrawStats();
  tkDrawList();
}

function tkDrawStats(){
  var el = document.getElementById('tk-stats-row'); if(!el) return;
  var total  = tkTasks.length;
  var done   = tkTasks.filter(function(t){ return t.done; }).length;
  var open   = total - done;
  var urgent = tkTasks.filter(function(t){ return t.priority==='high' && !t.done; }).length;
  var today  = tkYMD();
  var overdue= tkTasks.filter(function(t){ return t.date && t.date < today && !t.done; }).length;

  el.innerHTML = [
    ['סה"כ',  total,  'blue'],
    ['פתוחות', open,  'amber'],
    ['הושלמו', done,  'green'],
    urgent  ? ['דחופות', urgent, 'red']  : null,
    overdue ? ['באיחור', overdue,'red']  : null,
  ].filter(Boolean).map(function(s){
    return '<div class="tk-stat">' +
      '<div class="tk-stat-num ' + s[2] + '">' + s[1] + '</div>' +
      '<div class="tk-stat-lbl">' + s[0] + '</div></div>';
  }).join('');
}

function tkGetFiltered(){
  if(tkCurrentFilter === 'done') return tkTasks.filter(function(t){ return t.done; });
  if(tkCurrentFilter === 'open') return tkTasks.filter(function(t){ return !t.done; });
  return tkTasks;
}

function tkDrawList(){
  var el = document.getElementById('tk-list'); if(!el) return;
  el.innerHTML = '';
  var list = tkGetFiltered();

  // Sort: undone first by priority, then done at bottom
  list.sort(function(a,b){
    if(a.done !== b.done) return a.done ? 1 : -1;
    var pri = {high:0, med:1, low:2};
    return (pri[a.priority]||1) - (pri[b.priority]||1);
  });

  if(!list.length){
    var empty = document.createElement('div');
    empty.className = 'tk-empty';
    empty.innerHTML = '<span class="tk-empty-icon">' +
      (tkCurrentFilter==='done' ? '🎉' : '✅') + '</span>' +
      (tkCurrentFilter==='done' ? 'אין משימות שהושלמו עדיין' : 'אין משימות! לחץ + כדי להוסיף');
    el.appendChild(empty);
    return;
  }

  var today = tkYMD();
  list.forEach(function(t){
    var item = document.createElement('div');
    var priClass = 'pri-' + (t.priority || 'low');
    item.className = 'tk-item ' + priClass + (t.done ? ' done-item' : '');
    item.onclick = function(){ tkEditTask(t.id); };

    // Checkbox
    var chk = document.createElement('div');
    chk.className = 'tk-chk' + (t.done ? ' done' : '');
    chk.onclick = function(e){ e.stopPropagation(); tkToggle(t.id); };
    item.appendChild(chk);

    // Body
    var body = document.createElement('div');
    body.className = 'tk-body';

    var ttl = document.createElement('div');
    ttl.className = 'tk-ttl' + (t.done ? ' done' : '');
    ttl.textContent = t.title;
    body.appendChild(ttl);

    if(t.desc){
      var desc = document.createElement('div');
      desc.className = 'tk-desc';
      desc.textContent = t.desc.slice(0, 80) + (t.desc.length > 80 ? '...' : '');
      body.appendChild(desc);
    }

    var meta = document.createElement('div');
    meta.className = 'tk-meta';
    if(t.cat){
      var tag = document.createElement('span');
      tag.className = 'tk-tag'; tag.textContent = t.cat; meta.appendChild(tag);
    }
    if(t.date){
      var dspan = document.createElement('span');
      var overdue = !t.done && t.date < today;
      dspan.className = 'tk-date' + (overdue ? ' overdue' : '');
      dspan.textContent = (overdue ? '⚠️ ' : '📅 ') + t.date;
      meta.appendChild(dspan);
    }
    body.appendChild(meta);
    item.appendChild(body);

    // Delete
    var del = document.createElement('button');
    del.className = 'tk-del'; del.textContent = '🗑';
    del.onclick = function(e){ e.stopPropagation(); tkDelete(t.id); };
    item.appendChild(del);

    el.appendChild(item);
  });
}

// ─── Actions ──────────────────────────────────────────────────
function tkToggle(id){
  var t = tkTasks.find(function(x){ return x.id===id; }); if(!t) return;
  t.done = !t.done;
  tkSave(); tkDrawAll();
}

function tkDelete(id){
  if(!confirm('למחוק משימה זו?')) return;
  tkTasks = tkTasks.filter(function(x){ return x.id!==id; });
  tkSave(); tkDrawAll();
}

function tkQaAdd(){
  var inp = document.getElementById('tk-qa-inp');
  var title = (inp && inp.value || '').trim();
  if(!title) return;
  tkTasks.unshift({ id:tkID(), title:title, done:false, priority:'med', cat:'', desc:'', date:'', created:Date.now() });
  if(inp) inp.value = '';
  tkSave(); tkDrawAll();
}

function tkFilter(f, btn){
  tkCurrentFilter = f;
  document.querySelectorAll('#app-tasks .tk-filter-btn').forEach(function(b){ b.classList.remove('on'); });
  if(btn) btn.classList.add('on');
  tkDrawList();
  tkDrawStats();
}

// ─── Modal ────────────────────────────────────────────────────
function tkOpenModal(){
  tkEditId = null;
  var el = document.getElementById('tk-modal-title'); if(el) el.textContent = 'משימה חדשה';
  var t = document.getElementById('tk-m-title');   if(t) t.value = '';
  var d = document.getElementById('tk-m-desc');    if(d) d.value = '';
  var p = document.getElementById('tk-m-pri');     if(p) p.value = 'med';
  var dt= document.getElementById('tk-m-date');    if(dt) dt.value = '';
  var c = document.getElementById('tk-m-cat');     if(c) c.value = '';
  var bg= document.getElementById('tk-modal-bg');  if(bg) bg.classList.add('on');
  setTimeout(function(){ var t2=document.getElementById('tk-m-title'); if(t2) t2.focus(); }, 80);
}

function tkEditTask(id){
  var t = tkTasks.find(function(x){ return x.id===id; }); if(!t) return;
  tkEditId = id;
  var el = document.getElementById('tk-modal-title'); if(el) el.textContent = 'עריכת משימה';
  var ti = document.getElementById('tk-m-title');  if(ti) ti.value = t.title;
  var d  = document.getElementById('tk-m-desc');   if(d)  d.value  = t.desc||'';
  var p  = document.getElementById('tk-m-pri');    if(p)  p.value  = t.priority||'med';
  var dt = document.getElementById('tk-m-date');   if(dt) dt.value = t.date||'';
  var c  = document.getElementById('tk-m-cat');    if(c)  c.value  = t.cat||'';
  var bg = document.getElementById('tk-modal-bg'); if(bg) bg.classList.add('on');
}

function tkCloseModal(){
  var bg = document.getElementById('tk-modal-bg'); if(bg) bg.classList.remove('on');
  tkEditId = null;
}

function tkSaveModal(){
  var titleEl = document.getElementById('tk-m-title');
  var title = (titleEl && titleEl.value || '').trim();
  if(!title){ if(titleEl) titleEl.focus(); return; }
  var ev = {
    id: tkEditId || tkID(),
    title: title,
    done: false,
    priority: document.getElementById('tk-m-pri')?.value  || 'med',
    desc:     document.getElementById('tk-m-desc')?.value || '',
    date:     document.getElementById('tk-m-date')?.value || '',
    cat:      document.getElementById('tk-m-cat')?.value  || '',
    created:  Date.now()
  };
  if(tkEditId){
    var i = tkTasks.findIndex(function(x){ return x.id===tkEditId; });
    if(i>=0){ ev.done = tkTasks[i].done; tkTasks[i] = ev; }
  } else {
    tkTasks.unshift(ev);
  }
  tkSave(); tkCloseModal(); tkDrawAll();
}

// ─── Keyboard ─────────────────────────────────────────────────
document.addEventListener('keydown', function(e){
  var bg = document.getElementById('tk-modal-bg');
  if(!bg || !bg.classList.contains('on')) return;
  if(e.key === 'Escape') tkCloseModal();
});

// ─── On open/close ────────────────────────────────────────────
function tkOnOpen(){
  tkLoad();
  tkDrawAll();
}
function tkOnClose(){}


// ─── Handle goHomeFromTasks ────────────────────────────────────
function goHomeFromTasks(){ goHome(); }


// Sub-view switcher (week/day inside month tab)
function cSubView(view, btn) {
  // Update active button
  document.querySelectorAll('#app-cal .c-svbtn').forEach(function(b){ b.classList.remove('on'); });
  if(btn) btn.classList.add('on');

  var panes = {
    month: document.getElementById('c-main-month'),
    week:  document.getElementById('c-main-week'),
    day:   document.getElementById('c-main-day'),
  };
  Object.keys(panes).forEach(function(k){
    if(panes[k]) panes[k].style.display = k===view ? '' : 'none';
  });

  // Sync C_VIEW for prev/next/draw functions
  if(view==='week') { C_VIEW='week'; cDrawWeek(); }
  else if(view==='day') { C_VIEW='day'; cDrawDay(); }
  else { C_VIEW='month'; cDrawMonth(); }
}


// ── Quick checkbox tasks in calendar settings ──────────────────
var CAL_TASKS = JSON.parse(localStorage.getItem('cal_quick_tasks')||'[]');
function cRenderQuickTasks(){
  var el=document.getElementById('c-quick-task-list'); if(!el) return;
  el.innerHTML='';
  CAL_TASKS.forEach(function(t,i){
    var row=document.createElement('div');
    row.style.cssText='display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--cal-border);';
    var chk=document.createElement('input'); chk.type='checkbox'; chk.checked=t.done;
    chk.style.cssText='width:18px;height:18px;accent-color:var(--accent);cursor:pointer;flex-shrink:0;';
    chk.onchange=(function(idx){return function(){ CAL_TASKS[idx].done=this.checked; localStorage.setItem('cal_quick_tasks',JSON.stringify(CAL_TASKS)); cRenderQuickTasks(); };})(i);
    var lbl=document.createElement('span');
    lbl.textContent=t.title;
    lbl.style.cssText='flex:1;font-size:13px;'+(t.done?'text-decoration:line-through;opacity:.5;':'');
    var del=document.createElement('button');
    del.textContent='×'; del.style.cssText='background:none;border:none;font-size:16px;cursor:pointer;color:var(--cal-text3);padding:0 4px;';
    del.onclick=(function(idx){return function(){ CAL_TASKS.splice(idx,1); localStorage.setItem('cal_quick_tasks',JSON.stringify(CAL_TASKS)); cRenderQuickTasks(); };})(i);
    row.appendChild(chk); row.appendChild(lbl); row.appendChild(del);
    el.appendChild(row);
  });
}
function cQuickTask(){
  var inp=document.getElementById('c-quick-task-inp'); if(!inp) return;
  var title=(inp.value||'').trim(); if(!title) return;
  CAL_TASKS.push({title:title,done:false});
  localStorage.setItem('cal_quick_tasks',JSON.stringify(CAL_TASKS));
  inp.value=''; cRenderQuickTasks();
}

// ── Calendar theme ─────────────────────────────────────────────
// One-time migration: convert old standalone "dark" theme to global dark mode
(function(){
  try {
    var prefs = JSON.parse(localStorage.getItem('cal_prefs_v1') || '{}');
    if(prefs.theme === 'dark') {
      prefs.theme = 'light'; // let global dark mode handle it
      localStorage.setItem('cal_prefs_v1', JSON.stringify(prefs));
    }
  } catch(e){}
})();

var CAL_THEMES = {
  light:  {'--cal-bg':'#F0EEE9','--cal-surface':'#FFFFFF','--cal-text':'#0D0D0D','--cal-surface2':'#F8F8F6','--cal-border':'rgba(0,0,0,.08)','--cal-text2':'#3D3D3D','--cal-text3':'#808080'},
  dark:   {'--cal-bg':'#101012','--cal-surface':'#18181B','--cal-text':'#F0F0F0','--cal-surface2':'#1F1F23','--cal-border':'rgba(255,255,255,.08)','--cal-text2':'#ABABAB','--cal-text3':'#626262'},
  blue:   {'--cal-bg':'#EEF4FF','--cal-surface':'#FFFFFF','--cal-text':'#0D1A33','--cal-surface2':'#E0EDFF','--cal-border':'rgba(0,0,0,.08)','--cal-text2':'#1A3066','--cal-text3':'#4A6A99'},
  green:  {'--cal-bg':'#EDFBF4','--cal-surface':'#FFFFFF','--cal-text':'#0A2118','--cal-surface2':'#D5F5E3','--cal-border':'rgba(0,0,0,.08)','--cal-text2':'#145A32','--cal-text3':'#1E8449'},
  purple: {'--cal-bg':'#F3EEFF','--cal-surface':'#FFFFFF','--cal-text':'#1A0A33','--cal-surface2':'#EDE9FE','--cal-border':'rgba(0,0,0,.08)','--cal-text2':'#4A1A99','--cal-text3':'#7C3AED'},
};
var CAL_THEME_VARS = ['--cal-bg','--cal-surface','--cal-surface2','--cal-border','--cal-border2','--cal-text','--cal-text2','--cal-text3'];
// Dark-adapted variants for calendar color themes
var CAL_THEMES_DARK = {
  blue:   {'--cal-bg':'#0D1829','--cal-surface':'#111E33','--cal-surface2':'#172440','--cal-border':'rgba(79,142,247,.18)','--cal-text':'#E8F0FF','--cal-text2':'#8BB4FF','--cal-text3':'#4F8EF7'},
  green:  {'--cal-bg':'#091A12','--cal-surface':'#0E2218','--cal-surface2':'#132B1E','--cal-border':'rgba(16,185,129,.18)','--cal-text':'#EAFAF4','--cal-text2':'#6EE7B7','--cal-text3':'#10B981'},
  purple: {'--cal-bg':'#120A2A','--cal-surface':'#1A1030','--cal-surface2':'#21153A','--cal-border':'rgba(139,92,246,.2)','--cal-text':'#F0EAFF','--cal-text2':'#C4B5FD','--cal-text3':'#8B5CF6'},
};
function cApplyTheme(name){
  var el=document.getElementById('app-cal'); if(!el) return;
  // Always clear inline vars first
  CAL_THEME_VARS.forEach(function(k){ el.style.removeProperty(k); });
  if(name==='default' || !CAL_THEMES[name]){ cSaveSettings(); return; }
  // Use dark or light variant based on current global mode
  var darkMode = document.body.classList.contains('dark');
  var theme = darkMode ? (CAL_THEMES_DARK[name] || CAL_THEMES[name]) : CAL_THEMES[name];
  Object.keys(theme).forEach(function(k){ el.style.setProperty(k,theme[k]); });
  cSaveSettings();
}

// ── Calendar font size ─────────────────────────────────────────
function cSetCalFont(size, btn){
  var el=document.getElementById('app-cal'); if(!el) return;
  el.style.fontSize=size+'px';
  document.querySelectorAll('#app-cal .c-svbtn').forEach(function(b){ if(b.parentElement===btn.parentElement) b.classList.remove('on'); });
  if(btn) btn.classList.add('on');
  cSaveSettings();
}

// Render tasks when settings opens
var _origCV_extra = cV;
cV = function(view, btn){
  _origCV_extra(view, btn);
  if(view==='settings') setTimeout(cRenderQuickTasks, 50);
};


function cSaveSettings(){
  // Save visual preferences
  var prefs = {
    theme:       (document.getElementById('cal-theme')       || {}).value || 'default',
    showTime:    (document.getElementById('cal-show-time')   || {}).checked !== false,
    showMini:    (document.getElementById('cal-show-mini')   || {}).checked !== false,
    showUpcoming:(document.getElementById('cal-show-upcoming')|| {}).checked !== false,
  };
  localStorage.setItem('cal_prefs_v1', JSON.stringify(prefs));
}

function cLoadSettings(){
  try {
    var prefs = JSON.parse(localStorage.getItem('cal_prefs_v1') || '{}');
    // Clear any stale inline --cal-* vars before applying theme
    var calEl = document.getElementById('app-cal');
    if(calEl) CAL_THEME_VARS.forEach(function(k){ calEl.style.removeProperty(k); });
    if(prefs.theme) {
      // Migrate old dark/light values to default
      var t = (prefs.theme === 'dark' || prefs.theme === 'light') ? 'default' : prefs.theme;
      var sel = document.getElementById('cal-theme'); if(sel) sel.value = t;
      cApplyTheme(t); // always call — handles dark/light variant + 'default' clears vars
    }
    var showMini = prefs.showMini !== false;
    var showUpcoming = prefs.showUpcoming !== false;
    var miniWrap = document.getElementById('c-mini-wrap');
    var upcoming = document.querySelector('#app-cal .c-card:has(#c-upcoming)');
    if(miniWrap) miniWrap.style.display = showMini ? '' : 'none';
    var el = document.getElementById('cal-show-mini'); if(el) el.checked = showMini;
    var el2 = document.getElementById('cal-show-upcoming'); if(el2) el2.checked = showUpcoming;
  } catch(e){}
}


// ── TASKS: Extended features ────────────────────────────────────────
// ── TASKS: Preferences ────────────────────────────────────────
var TK_PREFS_KEY = 'tasks_prefs_v1';
var tkPrefs = {};

function tkLoadPrefs(){
  try { tkPrefs = JSON.parse(localStorage.getItem(TK_PREFS_KEY)||'{}'); } catch(e){ tkPrefs = {}; }
  // Apply UI
  var map = ['client','time','color','subtasks','drag','kanban','archive'];
  map.forEach(function(k){
    var el = document.getElementById('tk-pref-'+k); if(el) el.checked = !!tkPrefs[k];
  });
  tkApplyPrefs();
}

function tkSavePrefs(){
  var map = ['client','time','color','subtasks','drag','kanban','archive'];
  map.forEach(function(k){
    var el = document.getElementById('tk-pref-'+k); if(el) tkPrefs[k] = el.checked;
  });
  localStorage.setItem(TK_PREFS_KEY, JSON.stringify(tkPrefs));
  tkApplyPrefs();
}

function tkApplyPrefs(){
  // Show/hide archive and kanban filter buttons
  var archBtn = document.getElementById('tf-archive');
  if(archBtn) archBtn.style.display = tkPrefs.archive ? '' : 'none';
  var kanBtn = document.getElementById('tf-kanban');
  if(kanBtn) kanBtn.style.display = tkPrefs.kanban ? '' : 'none';
  // Extra modal fields
  var fields = {
    'tk-client-field':   tkPrefs.client,
    'tk-time-field':     tkPrefs.time,
    'tk-color-field':    tkPrefs.color,
    'tk-subtasks-field': tkPrefs.subtasks
  };
  Object.keys(fields).forEach(function(id){
    var el = document.getElementById(id);
    if(el) el.style.display = fields[id] ? '' : 'none';
  });
}

function tkOpenSettings(){
  tkLoadPrefs();
  var ov = document.getElementById('tk-settings-overlay');
  if(ov) ov.style.display = 'flex';
}

function tkCloseSettings(){
  var ov = document.getElementById('tk-settings-overlay');
  if(ov) ov.style.display = 'none';
}

// ── TASKS: Extended tkSaveModal ───────────────────────────────
var _origTkSaveModal = tkSaveModal;
tkSaveModal = function(){
  var titleEl = document.getElementById('tk-m-title');
  var title = (titleEl&&titleEl.value||'').trim();
  if(!title){ if(titleEl) titleEl.focus(); return; }

  var subs = [];
  document.querySelectorAll('#tk-sub-list .tk-sub-row').forEach(function(row){
    var txt = row.dataset.text;
    var done = row.querySelector('input[type=checkbox]').checked;
    if(txt) subs.push({text:txt, done:done});
  });

  var ev = {
    id:       tkEditId || tkID(),
    title:    title,
    done:     false,
    priority: (document.getElementById('tk-m-pri')||{}).value || 'med',
    desc:     (document.getElementById('tk-m-desc')||{}).value || '',
    date:     (document.getElementById('tk-m-date')||{}).value || '',
    cat:      (document.getElementById('tk-m-cat')||{}).value  || '',
    client:   ((document.getElementById('tk-m-client')||{}).value||'').trim(),
    time:     (document.getElementById('tk-m-time')||{}).value   || '',
    est:      (document.getElementById('tk-m-est')||{}).value    || '',
    color:    (document.getElementById('tk-m-color')||{}).value  || '',
    subtasks: subs,
    created:  Date.now()
  };

  if(tkEditId){
    var i = tkTasks.findIndex(function(x){ return x.id===tkEditId; });
    if(i>=0){
      ev.done = tkTasks[i].done;
      ev.archived = tkTasks[i].archived;
      ev.created = tkTasks[i].created;
      tkTasks[i] = ev;
    }
  } else {
    tkTasks.unshift(ev);
  }
  tkSave(); tkCloseModal(); tkDrawAll();
};

// ── TASKS: Extended tkEditTask ────────────────────────────────
var _origTkEditTask = tkEditTask;
tkEditTask = function(id){
  _origTkEditTask(id);
  setTimeout(function(){
    var t = tkTasks.find(function(x){ return x.id===id; });
    if(!t) return;
    var fClient = document.getElementById('tk-m-client'); if(fClient) fClient.value = t.client||'';
    var fTime   = document.getElementById('tk-m-time');   if(fTime)   fTime.value   = t.time||'';
    var fEst    = document.getElementById('tk-m-est');    if(fEst)    fEst.value    = t.est||'';
    var fColor  = document.getElementById('tk-m-color');  if(fColor)  fColor.value  = t.color||'';
    tkHighlightColor(t.color||'');
    tkRenderSubList(t.subtasks||[]);
    tkApplyPrefs();
  }, 0);
};

// ── TASKS: Color Picker ───────────────────────────────────────
document.addEventListener('click', function(e){
  var btn = e.target.closest('.tk-color-opt');
  if(!btn) return;
  var color = btn.dataset.color || '';
  document.querySelectorAll('.tk-color-opt').forEach(function(b){
    b.style.outline = '';
    b.style.transform = '';
  });
  btn.style.outline = '2.5px solid var(--accent)';
  btn.style.transform = 'scale(1.2)';
  var inp = document.getElementById('tk-m-color');
  if(inp) inp.value = color;
});

function tkHighlightColor(color){
  document.querySelectorAll('.tk-color-opt').forEach(function(b){
    b.style.outline = (b.dataset.color === color) ? '2.5px solid var(--accent)' : '';
    b.style.transform = (b.dataset.color === color) ? 'scale(1.2)' : '';
  });
}

// ── TASKS: Sub-tasks ──────────────────────────────────────────
var TK_TEMP_SUBS = [];

function tkAddSub(){
  var inp = document.getElementById('tk-sub-inp'); if(!inp) return;
  var txt = (inp.value||'').trim(); if(!txt) return;
  TK_TEMP_SUBS.push({text:txt, done:false});
  tkRenderSubList(TK_TEMP_SUBS);
  inp.value = '';
}

function tkRenderSubList(subs){
  TK_TEMP_SUBS = subs.slice();
  var el = document.getElementById('tk-sub-list'); if(!el) return;
  el.innerHTML = '';
  subs.forEach(function(s, i){
    var row = document.createElement('div');
    row.className = 'tk-sub-row';
    row.dataset.text = s.text;
    row.style.cssText = 'display:flex;align-items:center;gap:6px;padding:4px 0;';
    var chk = document.createElement('input');
    chk.type = 'checkbox'; chk.checked = s.done;
    chk.style.cssText = 'width:16px;height:16px;accent-color:var(--accent);cursor:pointer;flex-shrink:0;';
    chk.onchange = (function(idx){ return function(){ TK_TEMP_SUBS[idx].done = this.checked; }; })(i);
    var lbl = document.createElement('span');
    lbl.textContent = s.text;
    lbl.style.cssText = 'flex:1;font-size:13px;color:var(--cal-text,#F0F2FF);'+(s.done?'text-decoration:line-through;opacity:.5;':'');
    var del = document.createElement('button');
    del.textContent = '×';
    del.style.cssText = 'background:none;border:none;color:#9494A8;cursor:pointer;font-size:15px;padding:0 3px;';
    del.onclick = (function(idx){ return function(){ TK_TEMP_SUBS.splice(idx,1); tkRenderSubList(TK_TEMP_SUBS); }; })(i);
    row.appendChild(chk); row.appendChild(lbl); row.appendChild(del);
    el.appendChild(row);
  });
}

// ── TASKS: Archive ────────────────────────────────────────────
window.tkArchiveTask = function(id){
  var t = tkTasks.find(function(x){ return x.id===id; });
  if(t){ t.archived = true; tkSave(); tkDrawAll(); }
};

// Override filter to handle archive
var _origTkGetFiltered = tkGetFiltered;
tkGetFiltered = function(){
  if(window.tkCurrentFilter === 'archive') return tkTasks.filter(function(t){ return !!t.archived; });
  // Normal filters exclude archived tasks
  var base = tkTasks.filter(function(t){ return !t.archived; });
  if(window.tkCurrentFilter === 'done') return base.filter(function(t){ return t.done; });
  if(window.tkCurrentFilter === 'open') return base.filter(function(t){ return !t.done; });
  return base;
};

// ── TASKS: Kanban View ────────────────────────────────────────
var TK_KANBAN_MODE = false;

function tkToggleKanban(btn){
  TK_KANBAN_MODE = !TK_KANBAN_MODE;
  var listWrap   = document.getElementById('tk-list');
  var kanbanWrap = document.getElementById('tk-kanban-wrap');
  if(listWrap)   listWrap.style.display   = TK_KANBAN_MODE ? 'none' : '';
  if(kanbanWrap) kanbanWrap.style.display = TK_KANBAN_MODE ? 'block' : 'none';
  if(btn) btn.style.background = TK_KANBAN_MODE ? 'rgba(79,142,247,.25)' : '';
  if(TK_KANBAN_MODE) tkDrawKanban();
}

function tkDrawKanban(){
  var active = tkTasks.filter(function(t){ return !t.archived; });
  var cols = {high:[], med:[], low:[], done:[]};
  active.forEach(function(t){
    if(t.done) cols.done.push(t);
    else cols[t.priority||'med'].push(t);
  });
  ['high','med','low','done'].forEach(function(key){
    var el = document.getElementById('tk-k-'+key+'-items');
    if(!el) return;
    el.innerHTML = '';
    cols[key].forEach(function(t){
      var card = document.createElement('div');
      card.style.cssText = 'background:rgba(255,255,255,.06);border-radius:8px;padding:8px 10px;margin-bottom:6px;cursor:pointer;font-size:13px;';
      if(t.color) card.style.borderRight = '3px solid '+t.color;
      card.textContent = t.title;
      card.onclick = function(){ tkEditTask(t.id); };
      el.appendChild(card);
    });
  });
}

// ── TASKS: Drag & Drop ────────────────────────────────────────
var TK_DRAG_ID = null;

function tkEnableDrag(){
  if(!tkPrefs.drag) return;
  var items = document.querySelectorAll('.tk-item');
  items.forEach(function(item){
    item.draggable = true;
    item.style.cursor = 'grab';
    item.addEventListener('dragstart', function(){
      TK_DRAG_ID = item.dataset.tkid;
      item.style.opacity = '0.5';
    });
    item.addEventListener('dragend', function(){
      item.style.opacity = '';
      TK_DRAG_ID = null;
    });
    item.addEventListener('dragover', function(e){
      e.preventDefault();
      item.style.background = 'rgba(79,142,247,.15)';
    });
    item.addEventListener('dragleave', function(){
      item.style.background = '';
    });
    item.addEventListener('drop', function(e){
      e.preventDefault();
      item.style.background = '';
      if(!TK_DRAG_ID || TK_DRAG_ID === item.dataset.tkid) return;
      var fromIdx = tkTasks.findIndex(function(t){ return t.id===TK_DRAG_ID; });
      var toIdx   = tkTasks.findIndex(function(t){ return t.id===item.dataset.tkid; });
      if(fromIdx<0||toIdx<0) return;
      var moved = tkTasks.splice(fromIdx,1)[0];
      tkTasks.splice(toIdx,0,moved);
      tkSave(); tkDrawAll();
    });
  });
}

// ── TASKS: Extend tkDrawList to support new fields + drag ─────
var _origTkDrawList = tkDrawList;
tkDrawList = function(){
  _origTkDrawList();
  // Add data-tkid attribute and color bar to items
  var list = tkGetFiltered();
  // Re-sort same as original
  list.sort(function(a,b){
    if(a.done!==b.done) return a.done?1:-1;
    var pri={high:0,med:1,low:2};
    return (pri[a.priority]||1)-(pri[b.priority]||1);
  });
  var items = document.querySelectorAll('#tk-list .tk-item');
  items.forEach(function(item, i){
    var t = list[i];
    if(!t) return;
    item.dataset.tkid = t.id;
    // Color bar
    if(t.color){
      item.style.borderRight = '3px solid '+t.color;
    }
    // Sub-tasks progress
    if(t.subtasks && t.subtasks.length){
      var doneSubs = t.subtasks.filter(function(s){ return s.done; }).length;
      var subBar = document.createElement('div');
      subBar.style.cssText = 'font-size:10px;color:#9494A8;margin-top:3px;';
      subBar.textContent = '✓ '+doneSubs+'/'+t.subtasks.length+' משימות משנה';
      var body = item.querySelector('.tk-body');
      if(body && !body.querySelector('.tk-subprog')) {
        subBar.className = 'tk-subprog';
        body.appendChild(subBar);
      }
    }
    // Client badge
    if(t.client && tkPrefs.client){
      var meta = item.querySelector('.tk-meta');
      if(meta && !meta.querySelector('.tk-client-badge')){
        var badge = document.createElement('span');
        badge.className = 'tk-client-badge';
        badge.textContent = '👤 '+t.client;
        badge.style.cssText = 'font-size:10.5px;color:#9494A8;background:rgba(255,255,255,.06);border-radius:20px;padding:2px 7px;';
        meta.appendChild(badge);
      }
    }
    // Archive button (if archive pref on and task not done)
    if(tkPrefs.archive && !t.done && !t.archived){
      var existingArchBtn = item.querySelector('.tk-arch-btn');
      if(!existingArchBtn){
        var archBtn = document.createElement('button');
        archBtn.className = 'tk-arch-btn';
        archBtn.textContent = '📦';
        archBtn.title = 'העבר לארכיון';
        archBtn.style.cssText = 'background:none;border:none;font-size:14px;cursor:pointer;opacity:.4;padding:4px;flex-shrink:0;transition:opacity .15s;';
        archBtn.onmouseenter = function(){ this.style.opacity='1'; };
        archBtn.onmouseleave = function(){ this.style.opacity='.4'; };
        archBtn.onclick = (function(id){ return function(e){ e.stopPropagation(); tkArchiveTask(id); }; })(t.id);
        item.appendChild(archBtn);
      }
    }
  });
  tkEnableDrag();
};

// Patch tkOnOpen to also load prefs
var _origTkOnOpen = tkOnOpen;
tkOnOpen = function(){
  _origTkOnOpen();
  tkLoadPrefs();
};

