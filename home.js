(function(){

var _HOME_SK = 'home_v1';

const LOGOS = ['🏪','🛒','💼','🏬','🍽️','📷','🔧','💻','🎨','📣','🚗','💎','🌿','⚡','🏋️','📚','🎵','🍕','✂️','🏠'];

// ── State ─────────────────────────────────────
var homeState = {
  businessName: 'שם העסק שלי',
  logo: '🏪',
  tagline: '',
  calcLabel: 'מחשבון רווח נקי',
  calLabel: 'יומן',
  tasksLabel: 'משימות',
  dark: false,
  fabLabel: '🏠',
  fabSize: '52',
  fabPosition: 'center',
  fabBg: '',
  userName: '',
  logoImage: '',
  logoBg: '',
};

// ── Init ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', function(){
  try {
    const saved = JSON.parse(localStorage.getItem(_HOME_SK));
    if (saved) homeState = Object.assign({}, homeState, saved);
  } catch(e){}
  homeApplyState();
  buildEmojiPicker();
  loadHomeQuickStats();
  initHomeBgCanvas();
  initCalcBgCanvas();
  initCalBgCanvas();
  initTasksBgCanvas();
});

function loadHomeQuickStats(){
  try {
    var bizData = JSON.parse(localStorage.getItem('biz_v10')||'null');
    if(!bizData) return;
    var snaps = JSON.parse(localStorage.getItem('biz_snaps_v6')||'[]');
    var wrap = document.getElementById('home-quick-stats');
    if(!wrap) return;
    var chips = [];
    // Last saved month net
    if(snaps.length > 0){
      var last = snaps[snaps.length-1];
      if(last && last.net != null){
        var net = Math.round(last.net);
        chips.push('<div class="home-stat-chip">💰 רווח אחרון: <strong>₪' + net.toLocaleString() + '</strong></div>');
      }
    }
    // Number of snapshots
    if(snaps.length > 0){
      chips.push('<div class="home-stat-chip">📊 <strong>' + snaps.length + '</strong> חודשים שמורים</div>');
    }
    // Tasks count
    try {
      var tasks = JSON.parse(localStorage.getItem('biz_tasks_v3')||'[]');
      var openTasks = tasks.filter(function(t){ return !t.done; }).length;
      if(openTasks > 0){
        chips.push('<div class="home-stat-chip">📋 <strong>' + openTasks + '</strong> משימות פתוחות</div>');
      }
    } catch(e){}
    if(chips.length > 0){
      wrap.innerHTML = chips.join('');
      wrap.style.display = 'flex';
    }
  } catch(e){}
}

function homeApplyState(){
  const g = function(id){ return document.getElementById(id); };
  const n = g('business-name');    if(n) n.textContent = homeState.businessName;
  const l = g('business-logo');
  if(l){
    if(homeState.logoImage){
      l.innerHTML = '<img src="' + homeState.logoImage + '" style="width:100%;height:100%;object-fit:cover;border-radius:26px;" alt="לוגו">';
    } else {
      l.textContent = homeState.logo;
    }
    if(homeState.logoBg){
      l.style.background = homeState.logoBg;
    } else {
      l.style.background = '';
    }
  }
  const t = g('business-tagline'); if(t){ t.textContent = homeState.tagline || ''; t.style.display = homeState.tagline ? '' : 'none'; }
  const c = g('calc-label');       if(c) c.textContent = homeState.calcLabel;
  const calLbl = g('cal-label');   if(calLbl) calLbl.textContent = homeState.calLabel || 'יומן';
  const tkLbl  = g('tasks-label'); if(tkLbl)  tkLbl.textContent  = homeState.tasksLabel || 'משימות';
  if(document.body) document.body.classList.toggle('dark', homeState.dark);
  if(typeof isDark !== 'undefined') isDark = !!homeState.dark;
  var fab = document.getElementById('home-fab');
  if(fab){
    fab.textContent = homeState.fabLabel || '🏠';
    var sz = parseInt(homeState.fabSize)||52;
    fab.style.width  = sz+'px';
    fab.style.height = sz+'px';
    fab.style.fontSize = Math.round(sz*0.42)+'px';
    fab.style.borderRadius = (sz/2)+'px';
    // Position
    var pos = homeState.fabPosition || 'center';
    if(pos==='left'){ fab.style.left='1.5rem'; fab.style.right=''; fab.style.transform=''; }
    else if(pos==='right'){ fab.style.right='1.5rem'; fab.style.left=''; fab.style.transform=''; }
    else { fab.style.left='50%'; fab.style.right=''; fab.style.transform='translateX(-50%)'; }
    // Background
    if(homeState.fabBg){ fab.style.background=homeState.fabBg; }
    else { fab.style.background=''; }
  }
  // Greeting with name
  var greetEl = document.getElementById('home-greeting');
  if(greetEl){
    var h = new Date().getHours();
    var greet = h<5?'לילה טוב':h<12?'בוקר טוב':h<17?'צהריים טובים':h<21?'ערב טוב':'לילה טוב';
    var nm = homeState.userName ? ', ' + homeState.userName : '';
    greetEl.textContent = greet + nm;
  }
  const m = g('theme-color-meta'); if(m) m.content = homeState.dark ? '#101012' : '#EDECEA';
}


function previewFab(val){
  var lbl = document.getElementById('s-fab-size-label');
  if(lbl) lbl.textContent = val+'px';
  var fab = document.getElementById('home-fab');
  if(fab){
    fab.style.width  = val+'px';
    fab.style.height = val+'px';
    fab.style.fontSize = Math.round(parseInt(val)*0.42)+'px';
  }
}

function setFabPositionPreview(pos){
  var inp = document.getElementById('s-fab-position'); if(inp) inp.value = pos;
  var fab = document.getElementById('home-fab');
  if(fab){
    fab.dataset.fabPos = pos;
    if(pos==='left'){ fab.style.setProperty('left','1.5rem','important'); fab.style.setProperty('right','auto','important'); fab.style.setProperty('transform','','important'); }
    else if(pos==='right'){ fab.style.setProperty('right','1.5rem','important'); fab.style.setProperty('left','auto','important'); fab.style.setProperty('transform','','important'); }
    else { fab.style.setProperty('left','50%','important'); fab.style.setProperty('right','auto','important'); fab.style.setProperty('transform','translateX(-50%)','important'); }
  }
  document.querySelectorAll('.fab-pos-btn').forEach(function(b){
    var isActive = b.getAttribute('data-pos') === pos;
    b.style.background = isActive ? 'var(--accent-dim)' : 'var(--surface2)';
    b.style.borderColor = isActive ? 'var(--accent)' : 'var(--border)';
    b.style.color = isActive ? 'var(--accent)' : 'var(--text2)';
  });
}
function homeSave(){
  localStorage.setItem(_HOME_SK, JSON.stringify(homeState));
}

// ── Logo cycle ────────────────────────────────

// ── Settings ──────────────────────────────────
function openSettings(){
  const fabL = document.getElementById('s-fab-label'); if(fabL) fabL.value = homeState.fabLabel||'🏠';
  const fabS = document.getElementById('s-fab-size');  if(fabS){ fabS.value = homeState.fabSize||'52'; }
  const fabSL= document.getElementById('s-fab-size-label'); if(fabSL) fabSL.textContent=(homeState.fabSize||'52')+'px';
  const name = document.getElementById('s-business-name').value;
  document.getElementById('s-business-name').value = homeState.businessName;
  document.getElementById('s-tagline').value        = homeState.tagline;
  document.getElementById('s-calc-label').value     = homeState.calcLabel;
  var sCalEl = document.getElementById('s-cal-label');   if(sCalEl)   sCalEl.value   = homeState.calLabel   || 'יומן';
  var sTkEl  = document.getElementById('s-tasks-label'); if(sTkEl)    sTkEl.value    = homeState.tasksLabel || 'משימות';
  document.getElementById('s-dark').checked         = homeState.dark;
  var snEl = document.getElementById('s-user-name'); if(snEl) snEl.value = homeState.userName||'';
  var slBg = document.getElementById('s-logo-bg'); if(slBg) slBg.value = homeState.logoBg||'#1668D0';
  var sRemBtn = document.getElementById('s-remove-img-btn'); if(sRemBtn) sRemBtn.style.display = homeState.logoImage ? '' : 'none';
  var fpEl = document.getElementById('s-fab-position'); if(fpEl){ fpEl.value = homeState.fabPosition||'center'; setFabPositionPreview(homeState.fabPosition||'center'); }
  var fbEl = document.getElementById('s-fab-bg'); if(fbEl) fbEl.value = homeState.fabBg||'#1668D0';
  highlightSelected();
  document.getElementById('settings-overlay').classList.add('open');
}

function closeSettings(){
  saveSettings();
  document.getElementById('settings-overlay').classList.remove('open');
}

function saveSettings(){
  const name = document.getElementById('s-business-name').value.trim();
  if (name) homeState.businessName = name;
  homeState.tagline   = document.getElementById('s-tagline').value.trim();
  const cl = document.getElementById('s-calc-label').value.trim();
  if (cl) homeState.calcLabel = cl;
  var sCalEl = document.getElementById('s-cal-label');   if(sCalEl && sCalEl.value.trim()) homeState.calLabel   = sCalEl.value.trim();
  var sTkEl  = document.getElementById('s-tasks-label'); if(sTkEl  && sTkEl.value.trim())  homeState.tasksLabel = sTkEl.value.trim();
  const fl = document.getElementById('s-fab-label');  if(fl && fl.value.trim()) homeState.fabLabel = fl.value.trim();
  const fs = document.getElementById('s-fab-size');   if(fs) homeState.fabSize = fs.value;
  var snEl2 = document.getElementById('s-user-name'); if(snEl2) homeState.userName = snEl2.value.trim();
  var slBg2 = document.getElementById('s-logo-bg'); if(slBg2) homeState.logoBg = slBg2.value;
  var fpEl2 = document.getElementById('s-fab-position'); if(fpEl2) homeState.fabPosition = fpEl2.value;
  var fbEl2 = document.getElementById('s-fab-bg'); if(fbEl2) homeState.fabBg = fbEl2.value;
  homeSave();
  homeApplyState();
}

function homeAutoSave(){
  saveSettings();
}

function homeToggleDark(on){
  homeState.dark = on;
  isDark = on;
  // Smooth transition across all elements
  document.body.classList.add('theme-transition');
  document.body.classList.toggle('dark', on);
  // Update theme-color meta (status bar)
  var m = document.getElementById('theme-color-meta'); if(m) m.content = on ? '#08090E' : '#EDECEA';
  // Sync home-screen toggle + topbar icon
  var sDark = document.getElementById('s-dark'); if(sDark) sDark.checked = on;
  var darkBtn = document.getElementById('home-dark-btn'); if(darkBtn) darkBtn.textContent = on ? '☀️' : '🌙';
  // Clear calendar color-theme inline vars so body.dark CSS fully takes control
  var calEl = document.getElementById('app-cal');
  if(calEl){
    ['--cal-bg','--cal-surface','--cal-surface2','--cal-border','--cal-border2','--cal-text','--cal-text2','--cal-text3'].forEach(function(k){
      calEl.style.removeProperty(k);
    });
    var sel = document.getElementById('cal-theme'); if(sel) sel.value = 'default';
  }
  homeSave();
  setTimeout(function(){ document.body.classList.remove('theme-transition'); }, 320);
}

// ── Logo cycle ────────────────────────────────
function cycleLogo(){
  var cur = LOGOS.indexOf(homeState.logo);
  homeState.logo = LOGOS[(cur + 1) % LOGOS.length];
  var el = document.getElementById('business-logo'); if(el) el.textContent = homeState.logo;
  homeSave();
  highlightSelected();
}

// ── Emoji picker ──────────────────────────────
function buildEmojiPicker(){
  const picker = document.getElementById('emoji-picker');
  if (!picker) return;
  picker.innerHTML = '';
  LOGOS.forEach(function(em) {
    const btn = document.createElement('span');
    btn.className = 'emoji-opt' + (em === homeState.logo ? ' selected' : '');
    btn.textContent = em;
    btn.onclick = function() {
      homeState.logo = em;
      var el = document.getElementById('business-logo'); if(el) el.textContent = em;
      highlightSelected();
      homeSave();
    };
    picker.appendChild(btn);
  });
}

function highlightSelected(){
  document.querySelectorAll('.emoji-opt').forEach(function(el) {
    el.classList.toggle('selected', el.textContent === homeState.logo);
  });
}

function openLogoOptions(){
  var overlay = document.getElementById('logo-modal-overlay');
  if(!overlay) return;
  var removeBtn = document.getElementById('logo-remove-img-btn');
  if(removeBtn) removeBtn.style.display = homeState.logoImage ? '' : 'none';
  overlay.style.display = 'flex';
}

function closeLogo(){
  var overlay = document.getElementById('logo-modal-overlay');
  if(overlay) overlay.style.display = 'none';
}

function showEmojiInLogo(){
  openSettings();
}

function removeLogo(){
  homeState.logoImage = '';
  var l = document.getElementById('business-logo');
  if(l){ l.textContent = homeState.logo; if(homeState.logoBg) l.style.background=homeState.logoBg; }
  var btn = document.getElementById('s-remove-img-btn'); if(btn) btn.style.display='none';
  homeSave();
}

function previewLogoBg(val){
  var l = document.getElementById('business-logo'); if(l) l.style.background = val;
}

function resetLogoBg(){
  homeState.logoBg = '';
  var inp = document.getElementById('s-logo-bg'); if(inp) inp.value = '#1668D0';
  var l = document.getElementById('business-logo'); if(l) l.style.background = '';
}

function handleLogoImageUpload(inp){
  var file = inp.files[0]; if(!file) return;
  var reader = new FileReader();
  reader.onload = function(e){
    homeState.logoImage = e.target.result;
    var l = document.getElementById('business-logo');
    if(l) l.innerHTML = '<img src="' + homeState.logoImage + '" style="width:100%;height:100%;object-fit:cover;border-radius:26px;" alt="לוגו">';
    homeSave();
  };
  reader.readAsDataURL(file);
  inp.value = '';
}

// ── Keyboard ──────────────────────────────────
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeSettings();
  if ((e.ctrlKey||e.metaKey) && e.key === 's'){ e.preventDefault(); saveSettings(); }
});

window.homeToggleDark        = homeToggleDark;
window.openSettings          = openSettings;
window.closeSettings         = closeSettings;
window.saveSettings          = saveSettings;
window.cycleLogo             = cycleLogo;
window.previewFab            = previewFab;
window.setFabPositionPreview = setFabPositionPreview;
})();

// ══ APP MANAGER ══════════════════════════════════════════════

var appsRegistry = [];
var APP_REG_KEY = 'home_apps_v1';

// Built-in apps — all auto-connected
var BUILTIN_APPS = [
  { id: 'calc', name: 'מחשבון רווח נקי', icon: '💰', sub: 'הכנסות, מסים, הוצאות' },
  { id: 'cal',  name: 'יומן עסקי',       icon: '📅', sub: 'פגישות, משימות, תזכורות' },
];

function loadAppsRegistry() {
  try {
    var d = localStorage.getItem(APP_REG_KEY);
    if (d) appsRegistry = JSON.parse(d);
  } catch(e) {}
  // Ensure all builtins exist and are connected
  BUILTIN_APPS.forEach(function(b) {
    if (!appsRegistry.find(function(a){ return a.id === b.id; })) {
      appsRegistry.push({ id: b.id, name: b.name, icon: b.icon, sub: b.sub, builtin: true });
    }
  });
}

function saveAppsRegistry() {
  localStorage.setItem(APP_REG_KEY, JSON.stringify(appsRegistry));
}

function renderAppManager() {
  var list = document.getElementById('app-manager-list');
  if (!list) return;
  list.innerHTML = appsRegistry.map(function(a) {
    return '<div class="app-manager-row">' +
      '<div class="app-manager-icon">' + a.icon + '</div>' +
      '<div class="app-manager-info">' +
        '<div class="app-manager-name">' + a.name + '</div>' +
        '<div class="app-manager-sub">'  + a.sub  + '</div>' +
      '</div>' +
      '<span style="font-size:11px;font-weight:700;color:var(--green-text);background:var(--green-dim);padding:3px 10px;border-radius:20px;border:1px solid rgba(15,158,106,.2);">✓ מחובר</span>' +
    '</div>';
  }).join('');
}

function launchApp(id) {
  openApp(id);
}

function renderHomeGrid() {
  // static HTML
}


function getCalHTML() {
  try {
    return decodeURIComponent(escape(atob(_calB64)));
  } catch(e) { return ''; }
}




// Override openSettings to also render app manager
var _origOpenSettings = window.openSettings;
window.openSettings = function() {
  _origOpenSettings();
  renderAppManager();
};

// Init
loadAppsRegistry();
renderHomeGrid();

;



// ── HOME: Privacy Mode ──────────────────────────────────────────────
// ── HOME: Privacy Mode ────────────────────────────────────────
var HOME_PRIVACY = false;
function homeTogglePrivacy(){
  HOME_PRIVACY = !HOME_PRIVACY;
  var btn = document.getElementById('home-privacy-btn');
  var targets = document.querySelectorAll('.home-stat-chip strong,#home-today-widget .hw-rev');
  targets.forEach(function(el){
    el.style.filter = HOME_PRIVACY ? 'blur(5px)' : '';
  });
  if(btn){
    btn.style.background = HOME_PRIVACY ? 'var(--accent-dim)' : '';
    btn.textContent = HOME_PRIVACY ? '🙈' : '👁';
  }
}

// ── HOME: Today Widget ────────────────────────────────────────
function homeRenderTodayWidget(){
  var wrap = document.getElementById('home-today-widget');
  if(!wrap) return;

  // Load homeState
  var showWidget = window.homeState && homeState.todayWidget;
  // Also check the checkbox
  var chk = document.getElementById('s-today-widget');
  if(chk) chk.checked = !!showWidget;
  if(!showWidget){ wrap.style.display='none'; return; }

  var today = new Date();
  var todayYMD = today.getFullYear()+'-'+('0'+(today.getMonth()+1)).slice(-2)+'-'+('0'+today.getDate()).slice(-2);

  // Get today's meetings from calendar
  var calEvs = [];
  try { calEvs = JSON.parse(localStorage.getItem('biz_cal_v2')||'[]'); } catch(e){}
  var todayEvs = calEvs.filter(function(ev){ return ev.date===todayYMD && !ev.done; })
    .sort(function(a,b){ return (a.start||'').localeCompare(b.start||''); });

  // Get urgent tasks
  var tasks = [];
  try { tasks = JSON.parse(localStorage.getItem('biz_tasks_v3')||'[]'); } catch(e){}
  var urgentTasks = tasks.filter(function(t){ return !t.done && !t.archived && t.priority==='high'; }).slice(0,3);

  var html = '<div style="font-size:11px;font-weight:800;color:var(--text4);letter-spacing:.08em;text-transform:uppercase;margin-bottom:.6rem;">📋 היום — '+
    today.getDate()+'/'+(today.getMonth()+1)+'</div>';

  if(todayEvs.length){
    html += '<div style="margin-bottom:.5rem;">';
    todayEvs.slice(0,3).forEach(function(ev){
      var dot = ev.type==='meeting'?'📅':ev.type==='task'?'✅':'📝';
      html += '<div style="display:flex;align-items:center;gap:6px;font-size:12.5px;padding:3px 0;">'+
        '<span>'+dot+'</span>'+
        '<span style="font-weight:600;color:var(--text);">'+ev.title+'</span>'+
        (ev.start?'<span style="color:var(--text3);margin-right:auto;">'+ev.start+'</span>':'')+
        (ev.revenue?'<span class="hw-rev" style="color:var(--green);font-weight:700;">₪'+Number(ev.revenue).toLocaleString()+'</span>':'')+
        '</div>';
    });
    html += '</div>';
  } else {
    html += '<div style="font-size:12px;color:var(--text4);margin-bottom:.5rem;">אין פגישות היום 🎉</div>';
  }

  if(urgentTasks.length){
    html += '<div style="border-top:1px solid var(--border);padding-top:.5rem;margin-top:.3rem;">';
    urgentTasks.forEach(function(t){
      html += '<div style="display:flex;align-items:center;gap:5px;font-size:12px;padding:2px 0;">'+
        '<span style="color:var(--red);">🔴</span><span style="color:var(--text2);">'+t.title+'</span></div>';
    });
    html += '</div>';
  }

  wrap.innerHTML = html;
  wrap.style.display = 'block';
}

// ── HOME: Keyboard Shortcuts ──────────────────────────────────
document.addEventListener('keydown', function(e){
  if(!window.homeState || !homeState.kbdShortcuts) return;
  if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA'||e.target.isContentEditable) return;
  if(e.ctrlKey||e.metaKey||e.altKey) return;
  var homeEl = document.getElementById('app-home');
  if(!homeEl || homeEl.style.display==='none') return;
  if(e.key==='c'||e.key==='C') { e.preventDefault(); openCalc(); }
  if(e.key==='j'||e.key==='J') { e.preventDefault(); openApp('cal'); }
  if(e.key==='t'||e.key==='T') { e.preventDefault(); openApp('tasks'); }
});

// Patch homeApplyState to also sync new settings
var _origHomeApplyState = homeApplyState;
homeApplyState = function(){
  _origHomeApplyState();
  var chkW = document.getElementById('s-today-widget');
  if(chkW) chkW.checked = !!(homeState.todayWidget);
  var chkK = document.getElementById('s-kbd-shortcuts');
  if(chkK) chkK.checked = !!(homeState.kbdShortcuts);
  homeRenderTodayWidget();
};

// Also patch openSettings to init new toggles
var _origOpenSettings = openSettings;
openSettings = function(){
  _origOpenSettings();
  var chkW = document.getElementById('s-today-widget');
  if(chkW) chkW.checked = !!(homeState.todayWidget);
  var chkK = document.getElementById('s-kbd-shortcuts');
  if(chkK) chkK.checked = !!(homeState.kbdShortcuts);
};


// ── HOME: Patch DOMContentLoaded ────────────────────────────────────
// ── HOME: Patch DOMContentLoaded to render today widget ───────
document.addEventListener('DOMContentLoaded', function(){
  setTimeout(function(){
    homeRenderTodayWidget();
    tkLoadPrefs();
    // Sync new homeState fields to settings
    if(window.homeState){
      var chkW = document.getElementById('s-today-widget');
      if(chkW) chkW.checked = !!homeState.todayWidget;
      var chkK = document.getElementById('s-kbd-shortcuts');
      if(chkK) chkK.checked = !!homeState.kbdShortcuts;
    }
  }, 300);
});

// Keyboard shortcut hint in home footer
(function addKbdHint(){
  document.addEventListener('DOMContentLoaded', function(){
    setTimeout(function(){
      var footer = document.getElementById('footer-text');
      if(footer && !document.getElementById('kbd-hint')){
        var hint = document.createElement('div');
        hint.id = 'kbd-hint';
        hint.style.cssText = 'font-size:10.5px;color:var(--text4);margin-top:.3rem;opacity:0;transition:opacity .3s;';
        hint.innerHTML = '<kbd style="background:var(--surface2);border:1px solid var(--border2);border-radius:4px;padding:1px 5px;font-family:monospace;font-size:10px;">C</kbd> מחשבון &nbsp; <kbd style="background:var(--surface2);border:1px solid var(--border2);border-radius:4px;padding:1px 5px;font-family:monospace;font-size:10px;">J</kbd> יומן &nbsp; <kbd style="background:var(--surface2);border:1px solid var(--border2);border-radius:4px;padding:1px 5px;font-family:monospace;font-size:10px;">T</kbd> משימות';
        footer.parentNode.insertBefore(hint, footer.nextSibling);
        // Show hint only when kbdShortcuts enabled
        function syncHint(){
          if(window.homeState && homeState.kbdShortcuts){
            hint.style.opacity='1';
          } else {
            hint.style.opacity='0';
          }
        }
        setInterval(syncHint, 1000);
      }
    }, 600);
  });
})();

// ── 12. Smooth focus rings & global UX polish ─────────────────
(function globalUXPolish(){
  // Add :focus-visible ring to all interactive elements
  var style = document.createElement('style');
  style.textContent = [
    ':focus-visible{outline:2.5px solid var(--accent);outline-offset:2px;border-radius:4px;}',
    'button:focus:not(:focus-visible){outline:none;}',
    'a:focus:not(:focus-visible){outline:none;}',
    /* Smooth scroll everywhere */
    '*{scroll-behavior:smooth;}',
    /* Better touch callout */
    'img,button,a{-webkit-touch-callout:none;}',
    /* Prevent text selection on buttons */
    'button{user-select:none;-webkit-user-select:none;}',
    /* Better placeholder opacity */
    '::placeholder{opacity:.55;}',
    /* Scrollbar styling */
    '::-webkit-scrollbar{width:4px;height:4px;}',
    '::-webkit-scrollbar-track{background:transparent;}',
    '::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px;}',
    '::-webkit-scrollbar-thumb:hover{background:var(--text4);}',
    /* Home FAB improved */
    '#home-fab{',
      'position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%);',
      'z-index:500;',
      'height:44px;padding:0 20px;',
      'border-radius:22px;',
      'background:var(--surface);',
      'color:var(--text2);',
      'border:1.5px solid var(--border2);',
      'font-size:14px;font-weight:700;font-family:var(--font);',
      'cursor:pointer;',
      'box-shadow:var(--shadow-md);',
      'transition:transform .2s cubic-bezier(.34,1.56,.64,1),box-shadow .18s,opacity .15s;',
      'display:none;align-items:center;gap:6px;',
      'white-space:nowrap;',
      'touch-action:manipulation;',
    '}',
    '#home-fab.visible{display:flex;}',
    '#home-fab:hover{box-shadow:var(--shadow-lg);}',
    '#home-fab:active{opacity:.85;}',
    /* Modal overlay improved */
    '.modal-overlay{',
      'display:none;position:fixed;inset:0;',
      'background:rgba(0,0,0,.48);',
      'backdrop-filter:blur(10px);',
      '-webkit-backdrop-filter:blur(10px);',
      'z-index:500;',
      'align-items:center;justify-content:center;',
      'padding:1rem;',
    '}',
    '.modal-overlay.open{display:flex;animation:fadeIn .18s ease;}',
    '@keyframes fadeIn{from{opacity:0;}to{opacity:1;}}',
    '.modal{',
      'background:var(--surface);',
      'border-radius:20px;',
      'padding:1.5rem 1.4rem;',
      'width:100%;max-width:380px;',
      'box-shadow:var(--shadow-lg);',
      'animation:scaleIn .2s cubic-bezier(.34,1.2,.64,1);',
    '}',
    '@keyframes scaleIn{from{opacity:0;transform:scale(.94);}to{opacity:1;transform:scale(1);}}',
    '.modal-title{font-size:17px;font-weight:800;color:var(--text);margin-bottom:1rem;letter-spacing:-.025em;}',
    '.modal-input{',
      'width:100%;border:1.5px solid var(--border2);',
      'border-radius:10px;padding:10px 13px;',
      'font-size:14px;font-family:var(--font);',
      'background:var(--surface2);color:var(--text);',
      'outline:none;margin-bottom:.65rem;',
      'transition:border-color .15s,box-shadow .15s;',
    '}',
    '.modal-input:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow);}',
    '.modal-actions{display:flex;gap:8px;margin-top:.5rem;}',
    '.modal-cancel{',
      'flex:1;padding:11px;border:1.5px solid var(--border2);',
      'border-radius:10px;background:var(--surface2);',
      'font-size:14px;font-weight:600;cursor:pointer;',
      'font-family:var(--font);color:var(--text);',
      'touch-action:manipulation;',
      'transition:background .15s;',
    '}',
    '.modal-cancel:hover{background:var(--surface3,var(--surface2));}',
    '.modal-confirm{',
      'flex:2;padding:11px;border:none;',
      'border-radius:10px;background:var(--accent);color:#fff;',
      'font-size:14px;font-weight:700;cursor:pointer;',
      'font-family:var(--font);',
      'touch-action:manipulation;',
      'transition:opacity .15s,transform .12s;',
    '}',
    '.modal-confirm:hover{opacity:.9;}',
    '.modal-confirm:active{opacity:.8;transform:scale(.97);}',
  ].join('');
  document.head.appendChild(style);
})();

// ── Home Background Canvas (3D Business) ──────────────────────
function initHomeBgCanvas() {
  var canvas = document.getElementById('home-bg-canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var W, H, t = 0;
  var networkNodes = [], cubes = [], particles = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function initAll() {
    networkNodes = [];
    for (var i = 0; i < 14; i++) {
      networkNodes.push({
        x: Math.random() * W,
        y: Math.random() * H * 0.42,
        vx: (Math.random() - 0.5) * 0.32,
        vy: (Math.random() - 0.5) * 0.32,
        r: 1.5 + Math.random() * 2.5
      });
    }
    cubes = [];
    for (var j = 0; j < 7; j++) {
      cubes.push({
        x: Math.random() * W,
        y: Math.random() * H,
        size: 16 + Math.random() * 34,
        rx: Math.random() * Math.PI * 2,
        ry: Math.random() * Math.PI * 2,
        drx: (Math.random() - 0.5) * 0.008,
        dry: (Math.random() - 0.5) * 0.010,
        vy: -(0.18 + Math.random() * 0.30),
        alpha: 0.04 + Math.random() * 0.07
      });
    }
    particles = [];
    for (var k = 0; k < 30; k++) {
      particles.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: 0.8 + Math.random() * 1.8,
        vy: -(0.22 + Math.random() * 0.48),
        a: 0.12 + Math.random() * 0.30,
        blue: Math.random() > 0.4
      });
    }
  }

  function isDark() { return document.body.classList.contains('dark'); }

  function proj(px, py, pz, cx, cy) {
    var fov = 500, scale = fov / (fov + pz);
    return { x: cx + px * scale, y: cy + py * scale };
  }

  function drawCube(c, dark) {
    var s = c.size;
    var cosX = Math.cos(c.rx), sinX = Math.sin(c.rx);
    var cosY = Math.cos(c.ry), sinY = Math.sin(c.ry);
    var verts = [[-s,-s,-s],[s,-s,-s],[s,s,-s],[-s,s,-s],[-s,-s,s],[s,-s,s],[s,s,s],[-s,s,s]];
    var rot = verts.map(function(p) {
      var x1 = p[0]*cosY - p[2]*sinY, z1 = p[0]*sinY + p[2]*cosY;
      var y1 = p[1]*cosX - z1*sinX,   z2 = p[1]*sinX + z1*cosX;
      return [x1, y1, z2];
    });
    var pr = rot.map(function(p) { return proj(p[0], p[1], p[2] + 350, c.x, c.y); });
    var edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
    ctx.save();
    ctx.strokeStyle = dark ? 'rgba(79,142,247,' + c.alpha + ')' : 'rgba(22,104,208,' + c.alpha + ')';
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    edges.forEach(function(e) {
      ctx.moveTo(pr[e[0]].x, pr[e[0]].y);
      ctx.lineTo(pr[e[1]].x, pr[e[1]].y);
    });
    ctx.stroke();
    ctx.restore();
  }

  function frame() {
    t += 0.016;
    ctx.clearRect(0, 0, W, H);
    var dark = isDark();

    // Perspective grid floor
    var gridY = H * 0.70;
    var vpX = W / 2, vpY = gridY - H * 0.16;
    ctx.save();
    ctx.globalAlpha = dark ? 0.05 : 0.035;
    ctx.strokeStyle = dark ? '#4F8EF7' : '#1668D0';
    ctx.lineWidth = 0.7;
    for (var i = 0; i <= 9; i++) {
      var gy = gridY - i * (H * 0.055);
      var hw = (W * 0.58) * (1 - (i / 9) * 0.65);
      ctx.beginPath(); ctx.moveTo(vpX - hw, gy); ctx.lineTo(vpX + hw, gy); ctx.stroke();
    }
    for (var vi = -7; vi <= 7; vi++) {
      ctx.beginPath(); ctx.moveTo(vpX + vi * (W / 7.2), gridY); ctx.lineTo(vpX, vpY); ctx.stroke();
    }
    ctx.restore();

    // 3D rising bar chart
    var barY = gridY, nBars = 7, barAreaW = W * 0.50, barAreaX = W * 0.25;
    var barW = (barAreaW / nBars) * 0.50;
    ctx.save();
    for (var b = 0; b < nBars; b++) {
      var bx = barAreaX + (barAreaW / nBars) * b + ((barAreaW / nBars) - barW) / 2;
      var targetH = H * (0.09 + (b / (nBars - 1)) * 0.25);
      var progress = Math.min(1, Math.max(0, t * 0.55 - b * 0.11));
      var wave = Math.sin(t * 1.1 + b * 0.8) * (targetH * 0.025);
      var bH = targetH * progress + wave;
      if (bH < 0) bH = 0;
      var grad = ctx.createLinearGradient(bx, barY, bx, barY - bH);
      if (dark) {
        grad.addColorStop(0, 'rgba(79,142,247,0.65)');
        grad.addColorStop(0.5, 'rgba(99,102,241,0.45)');
        grad.addColorStop(1, 'rgba(139,92,246,0.10)');
      } else {
        grad.addColorStop(0, 'rgba(22,104,208,0.38)');
        grad.addColorStop(0.5, 'rgba(79,70,229,0.22)');
        grad.addColorStop(1, 'rgba(109,40,217,0.05)');
      }
      ctx.fillStyle = grad;
      var br = Math.min(5, barW / 2);
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(bx, barY - bH, barW, bH, [br, br, 0, 0]);
      else { ctx.rect(bx, barY - bH, barW, bH); }
      ctx.fill();
      if (bH > 2) {
        ctx.fillStyle = dark ? 'rgba(79,142,247,0.9)' : 'rgba(22,104,208,0.6)';
        ctx.fillRect(bx, barY - bH - 1.5, barW, 2);
      }
      // Right face 3D
      var depth = barW * 0.32;
      ctx.fillStyle = dark ? 'rgba(79,142,247,0.11)' : 'rgba(22,104,208,0.09)';
      ctx.beginPath();
      ctx.moveTo(bx + barW, barY - bH);
      ctx.lineTo(bx + barW + depth, barY - bH - depth * 0.5);
      ctx.lineTo(bx + barW + depth, barY - depth * 0.5);
      ctx.lineTo(bx + barW, barY); ctx.closePath(); ctx.fill();
      // Top face 3D
      ctx.fillStyle = dark ? 'rgba(139,92,246,0.22)' : 'rgba(109,40,217,0.13)';
      ctx.beginPath();
      ctx.moveTo(bx, barY - bH);
      ctx.lineTo(bx + depth, barY - bH - depth * 0.5);
      ctx.lineTo(bx + barW + depth, barY - bH - depth * 0.5);
      ctx.lineTo(bx + barW, barY - bH); ctx.closePath(); ctx.fill();
    }
    ctx.restore();

    // Trend line + arrow
    ctx.save();
    var pts = [];
    for (var lp = 0; lp < nBars; lp++) {
      var lpx = barAreaX + (barAreaW / nBars) * lp + (barAreaW / nBars) / 2;
      var lpH = H * (0.09 + (lp / (nBars - 1)) * 0.25);
      var lpProg = Math.min(1, Math.max(0, t * 0.55 - lp * 0.11));
      var lpWave = Math.sin(t * 1.1 + lp * 0.8) * (lpH * 0.025);
      pts.push({ x: lpx, y: barY - (lpH * lpProg + lpWave) - 9 });
    }
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (var li = 1; li < pts.length; li++) {
      var cpx = (pts[li-1].x + pts[li].x) / 2;
      ctx.bezierCurveTo(cpx, pts[li-1].y, cpx, pts[li].y, pts[li].x, pts[li].y);
    }
    ctx.strokeStyle = dark ? 'rgba(52,211,153,0.78)' : 'rgba(15,158,106,0.58)';
    ctx.lineWidth = 2.2;
    ctx.stroke();
    var last = pts[pts.length-1], prev = pts[pts.length-2];
    var angle = Math.atan2(last.y - prev.y, last.x - prev.x);
    ctx.fillStyle = dark ? 'rgba(52,211,153,0.92)' : 'rgba(15,158,106,0.72)';
    ctx.beginPath();
    ctx.moveTo(last.x, last.y);
    ctx.lineTo(last.x - 9*Math.cos(angle-0.45), last.y - 9*Math.sin(angle-0.45));
    ctx.lineTo(last.x - 9*Math.cos(angle+0.45), last.y - 9*Math.sin(angle+0.45));
    ctx.closePath(); ctx.fill();
    ctx.restore();

    // Floating 3D cubes
    cubes.forEach(function(c) {
      c.rx += c.drx; c.ry += c.dry; c.y += c.vy;
      if (c.y < -80) { c.y = H + 40; c.x = Math.random() * W; }
      drawCube(c, dark);
    });

    // Rising particles
    particles.forEach(function(p) {
      p.y += p.vy;
      if (p.y < -5) { p.y = H + 5; p.x = Math.random() * W; }
      ctx.save();
      ctx.globalAlpha = p.a * (0.5 + 0.5 * Math.sin(t * 1.8 + p.x * 0.01));
      ctx.fillStyle = p.blue ? (dark ? 'rgba(79,142,247,1)' : 'rgba(22,104,208,1)') : (dark ? 'rgba(139,92,246,1)' : 'rgba(109,40,217,1)');
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    });

    // Network nodes
    networkNodes.forEach(function(n) {
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H * 0.42) n.vy *= -1;
    });
    ctx.save();
    var maxD = 125;
    for (var ni = 0; ni < networkNodes.length; ni++) {
      for (var nj = ni + 1; nj < networkNodes.length; nj++) {
        var ndx = networkNodes[ni].x - networkNodes[nj].x;
        var ndy = networkNodes[ni].y - networkNodes[nj].y;
        var nd = Math.sqrt(ndx*ndx + ndy*ndy);
        if (nd < maxD) {
          var na = (1 - nd/maxD) * (dark ? 0.15 : 0.09);
          ctx.strokeStyle = dark ? 'rgba(79,142,247,' + na + ')' : 'rgba(22,104,208,' + na + ')';
          ctx.lineWidth = 0.7;
          ctx.beginPath();
          ctx.moveTo(networkNodes[ni].x, networkNodes[ni].y);
          ctx.lineTo(networkNodes[nj].x, networkNodes[nj].y);
          ctx.stroke();
        }
      }
    }
    networkNodes.forEach(function(n) {
      ctx.fillStyle = dark ? 'rgba(79,142,247,0.42)' : 'rgba(22,104,208,0.30)';
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2); ctx.fill();
    });
    ctx.restore();

    // ── Bottom zone: horizon glow + wave lines ─────────────────
    ctx.save();
    // Horizon glow line at grid floor
    var hgY = H * 0.705;
    var hgGrad = ctx.createLinearGradient(0, hgY, W, hgY);
    hgGrad.addColorStop(0,   'transparent');
    hgGrad.addColorStop(0.2, dark ? 'rgba(79,142,247,0.22)' : 'rgba(22,104,208,0.14)');
    hgGrad.addColorStop(0.5, dark ? 'rgba(139,92,246,0.32)' : 'rgba(109,40,217,0.20)');
    hgGrad.addColorStop(0.8, dark ? 'rgba(79,142,247,0.22)' : 'rgba(22,104,208,0.14)');
    hgGrad.addColorStop(1,   'transparent');
    ctx.fillStyle = hgGrad;
    ctx.fillRect(0, hgY - 1.5, W, 3);

    // Floor reflection glow below horizon
    var flGrad = ctx.createLinearGradient(0, hgY, 0, H);
    flGrad.addColorStop(0, dark ? 'rgba(79,142,247,0.07)' : 'rgba(22,104,208,0.045)');
    flGrad.addColorStop(0.4, dark ? 'rgba(139,92,246,0.04)' : 'rgba(109,40,217,0.025)');
    flGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = flGrad;
    ctx.fillRect(0, hgY, W, H - hgY);

    // Animated sine waves at bottom
    var waveColors = dark
      ? ['rgba(79,142,247,0.12)', 'rgba(139,92,246,0.09)', 'rgba(52,211,153,0.07)']
      : ['rgba(22,104,208,0.09)', 'rgba(109,40,217,0.06)', 'rgba(15,158,106,0.05)'];
    var waveParams = [
      { amp: H*0.022, freq: 0.012, speed: 0.6,  yBase: H*0.82 },
      { amp: H*0.016, freq: 0.016, speed: -0.45, yBase: H*0.88 },
      { amp: H*0.012, freq: 0.020, speed: 0.35,  yBase: H*0.93 }
    ];
    waveParams.forEach(function(wp, wi) {
      ctx.beginPath();
      ctx.lineWidth = 1.2;
      ctx.strokeStyle = waveColors[wi];
      for (var wx = 0; wx <= W; wx += 4) {
        var wy = wp.yBase + Math.sin(wx * wp.freq + t * wp.speed) * wp.amp;
        wx === 0 ? ctx.moveTo(wx, wy) : ctx.lineTo(wx, wy);
      }
      ctx.stroke();
      // Fill under wave
      ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath();
      ctx.fillStyle = waveColors[wi].replace(/[\d.]+\)$/, (parseFloat(waveColors[wi].match(/[\d.]+\)$/)[0])*0.35) + ')');
      ctx.fill();
    });

    // Bottom corner accent orbs
    var orbData = [
      { x: W*0.08, y: H*0.92, r: W*0.09 },
      { x: W*0.92, y: H*0.88, r: W*0.07 }
    ];
    orbData.forEach(function(orb) {
      var og = ctx.createRadialGradient(orb.x, orb.y, 0, orb.x, orb.y, orb.r);
      og.addColorStop(0, dark ? 'rgba(139,92,246,0.10)' : 'rgba(109,40,217,0.065)');
      og.addColorStop(1, 'transparent');
      ctx.fillStyle = og;
      ctx.beginPath(); ctx.arc(orb.x, orb.y, orb.r, 0, Math.PI*2); ctx.fill();
    });
    ctx.restore();

    canvas._raf = requestAnimationFrame(frame);
  }

  window.addEventListener('resize', function() { resize(); initAll(); });
  resize(); initAll(); frame();
}

// ── CALC Background Canvas (Money / Finance theme) ─────────────
function initCalcBgCanvas() {
  var canvas = document.getElementById('calc-bg-canvas');
  if (!canvas) return;
  if (canvas._raf) { cancelAnimationFrame(canvas._raf); canvas._raf = null; }
  var ctx = canvas.getContext('2d');
  var W, H, t = 0;
  var coins = [], symParticles = [], chartPts = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    buildChart();
  }

  function buildChart() {
    chartPts = [];
    var n = 11;
    var baseY = H * 0.66;
    var h = 0.08;
    for (var i = 0; i < n; i++) {
      h = Math.max(0.06, Math.min(0.48, h + (Math.random() - 0.42) * 0.09));
      chartPts.push({ x: W * (0.08 + i * (0.84 / (n-1))), y: baseY - H * h });
    }
    // Force final points to trend upward
    for (var j = n-4; j < n; j++) {
      chartPts[j].y = Math.min(chartPts[j].y, H * 0.66 - H * (0.14 + (j-(n-4)) * 0.07));
    }
  }

  function initCoins() {
    coins = [];
    for (var i = 0; i < 11; i++) {
      coins.push({
        x: Math.random() * W, y: Math.random() * H,
        r: 11 + Math.random() * 20,
        rx: Math.random() * Math.PI * 2,
        drx: (Math.random() > 0.5 ? 1 : -1) * (0.009 + Math.random() * 0.013),
        vy: -(0.14 + Math.random() * 0.28),
        alpha: 0.06 + Math.random() * 0.10,
        gold: Math.random() > 0.35
      });
    }
    symParticles = [];
    for (var k = 0; k < 18; k++) {
      symParticles.push({
        x: Math.random() * W, y: Math.random() * H,
        vy: -(0.28 + Math.random() * 0.45),
        a: 0.08 + Math.random() * 0.18,
        size: 9 + Math.random() * 10,
        sym: ['₪','%','+','$'][Math.floor(Math.random() * 4)]
      });
    }
  }

  function isDark() { return document.body.classList.contains('dark'); }

  function drawCoin(c, dark) {
    var sq = Math.cos(c.rx);
    ctx.save();
    ctx.translate(c.x, c.y);
    ctx.scale(sq, 1);
    var g = ctx.createRadialGradient(-c.r*0.3, -c.r*0.3, 0, 0, 0, c.r);
    if (c.gold) {
      g.addColorStop(0, 'rgba(255,215,0,' + (c.alpha*2.8) + ')');
      g.addColorStop(0.6, 'rgba(212,175,55,' + (c.alpha*2) + ')');
      g.addColorStop(1, 'rgba(139,109,0,' + c.alpha + ')');
    } else {
      var a1 = c.alpha*2.5, a2 = c.alpha;
      g.addColorStop(0, dark ? 'rgba(79,142,247,'+a1+')' : 'rgba(22,104,208,'+a1+')');
      g.addColorStop(1, dark ? 'rgba(30,80,180,'+a2+')' : 'rgba(10,60,160,'+a2+')');
    }
    ctx.beginPath(); ctx.arc(0, 0, c.r, 0, Math.PI*2);
    ctx.fillStyle = g; ctx.fill();
    if (Math.abs(sq) > 0.28) {
      ctx.fillStyle = c.gold ? 'rgba(255,240,100,'+(c.alpha*4)+')' : (dark ? 'rgba(160,210,255,'+(c.alpha*4)+')' : 'rgba(80,150,255,'+(c.alpha*4)+')');
      ctx.font = 'bold ' + Math.round(c.r*0.95) + 'px sans-serif';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('₪', 0, 0);
    }
    ctx.restore();
  }

  function frame() {
    t += 0.016;
    ctx.clearRect(0, 0, W, H);
    var dark = isDark();

    // Soft gold glow center
    var gl = ctx.createRadialGradient(W/2, H*0.5, 0, W/2, H*0.5, W*0.48);
    gl.addColorStop(0, 'rgba(255,200,50,' + (dark?0.022:0.015) + ')');
    gl.addColorStop(1, 'transparent');
    ctx.fillStyle = gl; ctx.fillRect(0,0,W,H);

    // Financial chart line
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(chartPts[0].x, chartPts[0].y);
    for (var i = 1; i < chartPts.length; i++) {
      var cpx = (chartPts[i-1].x + chartPts[i].x) / 2;
      ctx.bezierCurveTo(cpx, chartPts[i-1].y, cpx, chartPts[i].y, chartPts[i].x, chartPts[i].y);
    }
    ctx.strokeStyle = dark ? 'rgba(52,211,153,0.48)' : 'rgba(15,158,106,0.38)';
    ctx.lineWidth = 1.8; ctx.stroke();
    // Fill under line
    var fillG = ctx.createLinearGradient(0, H*0.18, 0, H*0.66);
    fillG.addColorStop(0, dark?'rgba(52,211,153,0.10)':'rgba(15,158,106,0.07)');
    fillG.addColorStop(1, 'transparent');
    ctx.lineTo(chartPts[chartPts.length-1].x, H*0.66);
    ctx.lineTo(chartPts[0].x, H*0.66);
    ctx.closePath(); ctx.fillStyle = fillG; ctx.fill();
    ctx.restore();

    // Candlestick bars
    ctx.save();
    for (var ci = 0; ci < chartPts.length-1; ci++) {
      var up = chartPts[ci+1].y < chartPts[ci].y;
      ctx.fillStyle = up ? (dark?'rgba(52,211,153,0.42)':'rgba(15,158,106,0.32)') : (dark?'rgba(248,113,113,0.32)':'rgba(210,60,60,0.24)');
      var bw = (chartPts[1].x - chartPts[0].x) * 0.38;
      var bh = Math.max(3, Math.abs(chartPts[ci+1].y - chartPts[ci].y) * 0.55);
      ctx.fillRect(chartPts[ci].x - bw/2, Math.min(chartPts[ci].y, chartPts[ci+1].y), bw, bh);
    }
    ctx.restore();

    // Donut chart (lower right)
    var dcx = W*0.84, dcy = H*0.74, dcr = Math.min(W,H)*0.07;
    var sA = -Math.PI/2 + Math.sin(t*0.25)*0.04;
    ctx.save();
    ctx.lineWidth = dcr*0.38;
    // segments: profit 65% green, tax 22% red, expenses 13% amber
    var segs = [
      {a:Math.PI*2*0.65, c:dark?'rgba(52,211,153,':  'rgba(15,158,106,', op:dark?0.22:0.16},
      {a:Math.PI*2*0.22, c:dark?'rgba(248,113,113,': 'rgba(210,60,60,',  op:dark?0.18:0.13},
      {a:Math.PI*2*0.13, c:dark?'rgba(251,191,36,':  'rgba(200,140,0,',  op:dark?0.20:0.14}
    ];
    var cur = sA;
    segs.forEach(function(s) {
      ctx.strokeStyle = s.c + s.op + ')';
      ctx.beginPath(); ctx.arc(dcx, dcy, dcr, cur, cur + s.a); ctx.stroke();
      cur += s.a;
    });
    ctx.restore();

    // Floating coins
    coins.forEach(function(c) {
      c.rx += c.drx; c.y += c.vy;
      if (c.y < -c.r*2) { c.y = H+c.r; c.x = Math.random()*W; }
      drawCoin(c, dark);
    });

    // ₪ symbol particles
    symParticles.forEach(function(p) {
      p.y += p.vy;
      if (p.y < -30) { p.y = H+20; p.x = Math.random()*W; }
      ctx.save();
      ctx.globalAlpha = p.a * (0.5 + 0.5*Math.sin(t*1.4 + p.x*0.02));
      ctx.fillStyle = dark ? 'rgba(255,215,0,1)' : 'rgba(160,110,0,1)';
      ctx.font = 'bold '+p.size+'px sans-serif';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(p.sym, p.x, p.y);
      ctx.restore();
    });

    // Perspective grid floor (subtle)
    var gy0 = H*0.72, vpX2 = W/2, vpY2 = gy0-H*0.12;
    ctx.save();
    ctx.globalAlpha = dark?0.04:0.028;
    ctx.strokeStyle = dark?'#FFD700':'#B8860B';
    ctx.lineWidth = 0.6;
    for (var gi=0; gi<=7; gi++) {
      var gy = gy0 - gi*(H*0.05);
      var hw = (W*0.55)*(1-(gi/7)*0.65);
      ctx.beginPath(); ctx.moveTo(vpX2-hw,gy); ctx.lineTo(vpX2+hw,gy); ctx.stroke();
    }
    for (var gv=-6; gv<=6; gv++) {
      ctx.beginPath(); ctx.moveTo(vpX2+gv*(W/6.5),gy0); ctx.lineTo(vpX2,vpY2); ctx.stroke();
    }
    ctx.restore();

    canvas._raf = requestAnimationFrame(frame);
  }

  window.addEventListener('resize', function() { resize(); initCoins(); });
  resize(); initCoins(); frame();
}

// ── CALENDAR Background Canvas (Orbit / Time theme) ────────────
function initCalBgCanvas() {
  var canvas = document.getElementById('cal-bg-canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var W, H, t = 0;
  var orbitDots = [], calCards = [], particles = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    initAll();
  }

  function initAll() {
    orbitDots = [];
    for (var o = 0; o < 3; o++) {
      var n = 3 + o*2;
      for (var d = 0; d < n; d++) {
        orbitDots.push({
          orbit: o, angle: (Math.PI*2/n)*d,
          speed: (0.003+Math.random()*0.002)*(o%2===0?1:-1),
          r: 2.5+Math.random()*2,
          alpha: 0.22+Math.random()*0.30
        });
      }
    }
    calCards = [];
    for (var i = 0; i < 9; i++) {
      calCards.push({
        x: Math.random()*W, y: Math.random()*H,
        w: 26+Math.random()*18, h: 30+Math.random()*20,
        ry: Math.random()*Math.PI*2,
        dry: (Math.random()-0.5)*0.009,
        vy: -(0.14+Math.random()*0.24),
        alpha: 0.055+Math.random()*0.075,
        day: Math.floor(Math.random()*28)+1
      });
    }
    particles = [];
    for (var k = 0; k < 24; k++) {
      particles.push({
        x: Math.random()*W, y: Math.random()*H,
        r: 0.8+Math.random()*1.7, vy: -(0.2+Math.random()*0.38),
        a: 0.1+Math.random()*0.22
      });
    }
  }

  function isDark() { return document.body.classList.contains('dark'); }

  function frame() {
    t += 0.016;
    ctx.clearRect(0, 0, W, H);
    var dark = isDark();
    var ar = dark?79:22, ag = dark?142:104, ab = dark?247:208;
    var acc = 'rgba('+ar+','+ag+','+ab+',';

    // Orbit center
    var cx = W/2, cy = H*0.42;
    var orbitRadii = [W*0.12, W*0.21, W*0.30];
    var orbitTilts = [0.30, 0.42, 0.52];

    // Orbit ellipses (3D rings)
    ctx.save();
    ctx.setLineDash([4,9]);
    orbitRadii.forEach(function(or, oi) {
      ctx.strokeStyle = acc+(dark?0.065:0.045)+')';
      ctx.lineWidth = 0.7;
      ctx.beginPath();
      ctx.ellipse(cx, cy, or, or*Math.sin(orbitTilts[oi]), 0, 0, Math.PI*2);
      ctx.stroke();
    });
    ctx.setLineDash([]);
    ctx.restore();

    // Clock face at center
    var sunR = Math.min(W,H)*0.038;
    ctx.save();
    var sg = ctx.createRadialGradient(cx,cy,0,cx,cy,sunR*1.8);
    sg.addColorStop(0, dark?'rgba(79,142,247,0.20)':'rgba(22,104,208,0.14)');
    sg.addColorStop(0.5, dark?'rgba(139,92,246,0.10)':'rgba(109,40,217,0.06)');
    sg.addColorStop(1,'transparent');
    ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(cx,cy,sunR*1.8,0,Math.PI*2); ctx.fill();
    // Tick marks
    for (var m = 0; m < 12; m++) {
      var ma = (Math.PI*2/12)*m;
      var major = m%3===0;
      ctx.strokeStyle = acc+(major?0.45:0.20)+')';
      ctx.lineWidth = major?1.4:0.7;
      ctx.beginPath();
      ctx.moveTo(cx+Math.cos(ma)*sunR*0.6, cy+Math.sin(ma)*sunR*0.6);
      ctx.lineTo(cx+Math.cos(ma)*(sunR*0.6+(major?sunR*0.38:sunR*0.22)), cy+Math.sin(ma)*(sunR*0.6+(major?sunR*0.38:sunR*0.22)));
      ctx.stroke();
    }
    // Hands (real time)
    var now = new Date();
    var ha = (Math.PI*2/12)*(now.getHours()%12) + (Math.PI*2/12/60)*now.getMinutes() - Math.PI/2;
    var mina = (Math.PI*2/60)*now.getMinutes() - Math.PI/2;
    ctx.strokeStyle = acc+'0.52)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(cx+Math.cos(ha)*sunR*0.44, cy+Math.sin(ha)*sunR*0.44); ctx.stroke();
    ctx.strokeStyle = dark?'rgba(139,92,246,0.52)':'rgba(109,40,217,0.40)'; ctx.lineWidth = 1.4;
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(cx+Math.cos(mina)*sunR*0.58, cy+Math.sin(mina)*sunR*0.58); ctx.stroke();
    ctx.restore();

    // Orbit dots
    orbitDots.forEach(function(dot) {
      dot.angle += dot.speed;
      var or = orbitRadii[dot.orbit], tilt = orbitTilts[dot.orbit];
      var x = cx + or*Math.cos(dot.angle);
      var y = cy + or*Math.sin(dot.angle)*Math.sin(tilt);
      var zd = Math.sin(dot.angle);
      var dr = dot.r*(0.6+0.4*(1+zd)/2);
      ctx.save();
      ctx.globalAlpha = dot.alpha*(0.5+0.5*(1+zd)/2);
      ctx.fillStyle = dot.orbit===0 ? acc+'1)' : dot.orbit===1 ? 'rgba(139,92,246,1)' : 'rgba(52,211,153,1)';
      ctx.beginPath(); ctx.arc(x,y,dr,0,Math.PI*2); ctx.fill();
      ctx.restore();
    });

    // Floating 3D calendar cards
    calCards.forEach(function(c) {
      c.ry += c.dry; c.y += c.vy;
      if (c.y < -c.h*2) { c.y = H+c.h; c.x = Math.random()*W; }
      var sq = Math.cos(c.ry);
      if (Math.abs(sq) < 0.04) return;
      var cw = c.w*Math.abs(sq);
      ctx.save();
      ctx.globalAlpha = c.alpha;
      var rx = c.x-cw/2, ry2 = c.y-c.h/2;
      ctx.fillStyle = dark?'rgba(79,142,247,0.28)':'rgba(22,104,208,0.18)';
      ctx.strokeStyle = dark?'rgba(79,142,247,0.48)':'rgba(22,104,208,0.38)';
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      if(ctx.roundRect) ctx.roundRect(rx,ry2,cw,c.h,3); else ctx.rect(rx,ry2,cw,c.h);
      ctx.fill(); ctx.stroke();
      ctx.fillStyle = dark?'rgba(79,142,247,0.50)':'rgba(22,104,208,0.40)';
      ctx.beginPath();
      if(ctx.roundRect) ctx.roundRect(rx,ry2,cw,c.h*0.27,[3,3,0,0]); else ctx.rect(rx,ry2,cw,c.h*0.27);
      ctx.fill();
      if (cw > 8) {
        ctx.fillStyle = dark?'rgba(200,225,255,0.65)':'rgba(10,60,180,0.55)';
        ctx.font = 'bold '+Math.round(c.h*0.36)+'px sans-serif';
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(c.day, c.x, c.y+c.h*0.14);
      }
      ctx.restore();
    });

    // Subtle time spiral at bottom
    ctx.save();
    ctx.strokeStyle = dark?'rgba(79,142,247,0.055)':'rgba(22,104,208,0.038)';
    ctx.lineWidth = 0.9; ctx.beginPath();
    var scx = W/2, scy = H*0.86;
    for (var s = 0; s < 220; s++) {
      var sa = (s/220)*Math.PI*7 + t*0.04;
      var sr = s*(W*0.0011);
      var sx = scx+Math.cos(sa)*sr, sy = scy+Math.sin(sa)*sr*0.32;
      s===0 ? ctx.moveTo(sx,sy) : ctx.lineTo(sx,sy);
    }
    ctx.stroke(); ctx.restore();

    // Rising particles
    particles.forEach(function(p) {
      p.y += p.vy;
      if (p.y < -5) { p.y = H+5; p.x = Math.random()*W; }
      ctx.save();
      ctx.globalAlpha = p.a*(0.5+0.5*Math.sin(t*1.5+p.x*0.02));
      ctx.fillStyle = acc+'1)';
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill();
      ctx.restore();
    });

    requestAnimationFrame(frame);
  }

  window.addEventListener('resize', resize);
  resize(); frame();
}

// ── TASKS Background Canvas (Productivity / Flow theme) ─────────
function initTasksBgCanvas() {
  var canvas = document.getElementById('tasks-bg-canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var W, H, t = 0;
  var checkboxes = [], rings = [], flowNodes = [], particles = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    initAll();
  }

  function initAll() {
    checkboxes = [];
    for (var i = 0; i < 10; i++) {
      checkboxes.push({
        x: Math.random()*W, y: Math.random()*H,
        size: 13+Math.random()*18,
        ry: Math.random()*Math.PI*2,
        dry: (Math.random()-0.5)*0.011,
        vy: -(0.17+Math.random()*0.30),
        alpha: 0.06+Math.random()*0.09,
        checked: Math.random()>0.38
      });
    }
    rings = [];
    for (var j = 0; j < 6; j++) {
      rings.push({
        x: Math.random()*W, y: Math.random()*H,
        r: 16+Math.random()*26,
        prog: 0.2+Math.random()*0.72,
        rot: Math.random()*Math.PI*2,
        drot: (Math.random()-0.5)*0.005,
        vy: -(0.14+Math.random()*0.24),
        alpha: 0.07+Math.random()*0.09
      });
    }
    // Kanban flow nodes
    flowNodes = [];
    var cols = [[248,113,113],[251,191,36],[52,211,153]];
    for (var s = 0; s < 3; s++) {
      for (var n = 0; n < 3; n++) {
        flowNodes.push({
          x: W*(0.16+s*0.34) + (Math.random()-0.5)*W*0.07,
          y: H*(0.38+n*0.11) + (Math.random()-0.5)*H*0.04,
          r: 4+Math.random()*4,
          alpha: 0.11+Math.random()*0.12,
          col: cols[s]
        });
      }
    }
    particles = [];
    for (var k = 0; k < 22; k++) {
      particles.push({
        x: Math.random()*W, y: Math.random()*H,
        r: 0.8+Math.random()*1.5,
        vy: -(0.20+Math.random()*0.38),
        a: 0.10+Math.random()*0.20,
        green: Math.random()>0.40
      });
    }
  }

  function isDark() { return document.body.classList.contains('dark'); }

  function frame() {
    t += 0.016;
    ctx.clearRect(0, 0, W, H);
    var dark = isDark();

    // Subtle green glow (productivity / success)
    var gl = ctx.createRadialGradient(W/2,H*0.5,0,W/2,H*0.5,W*0.46);
    gl.addColorStop(0,'rgba(52,211,153,'+(dark?0.022:0.015)+')');
    gl.addColorStop(1,'transparent');
    ctx.fillStyle = gl; ctx.fillRect(0,0,W,H);

    // Kanban pipeline columns (bottom zone)
    ctx.save();
    var pY = H*0.82, pColW = W*0.20, pH = H*0.16;
    var stageClrs = [
      dark?'rgba(248,113,113,0.09)':'rgba(220,60,60,0.06)',
      dark?'rgba(251,191,36,0.09)':'rgba(200,140,0,0.06)',
      dark?'rgba(52,211,153,0.09)':'rgba(15,158,106,0.06)'
    ];
    for (var s = 0; s < 3; s++) {
      var px = W*(0.16+s*0.34)-pColW/2;
      ctx.fillStyle = stageClrs[s];
      ctx.beginPath();
      if(ctx.roundRect) ctx.roundRect(px,pY-pH,pColW,pH,[6,6,0,0]); else ctx.rect(px,pY-pH,pColW,pH);
      ctx.fill();
    }
    // Dashed arrows between stages
    ctx.setLineDash([4,7]);
    ctx.lineWidth = 0.9;
    for (var ai = 0; ai < 2; ai++) {
      var ax1 = W*(0.16+ai*0.34)+pColW/2, ax2 = W*(0.16+(ai+1)*0.34)-pColW/2;
      var ay = pY - pH*0.5 + Math.sin(t*1.4+ai)*2.5;
      ctx.strokeStyle = dark?'rgba(148,163,184,0.11)':'rgba(100,120,150,0.08)';
      ctx.beginPath(); ctx.moveTo(ax1,ay); ctx.lineTo(ax2,ay); ctx.stroke();
    }
    ctx.setLineDash([]);
    ctx.restore();

    // Flow node connections
    ctx.save();
    ctx.setLineDash([3,7]); ctx.lineWidth = 0.7;
    for (var ni = 0; ni < flowNodes.length-3; ni++) {
      var nj = ni+3;
      if (nj < flowNodes.length && flowNodes[ni].col !== flowNodes[nj].col) {
        ctx.strokeStyle = dark?'rgba(148,163,184,0.055)':'rgba(100,120,150,0.045)';
        var dx = flowNodes[nj].x-flowNodes[ni].x, dy = flowNodes[nj].y-flowNodes[ni].y;
        ctx.beginPath(); ctx.moveTo(flowNodes[ni].x,flowNodes[ni].y);
        ctx.bezierCurveTo(flowNodes[ni].x+dx*0.4,flowNodes[ni].y,flowNodes[nj].x-dx*0.4,flowNodes[nj].y,flowNodes[nj].x,flowNodes[nj].y);
        ctx.stroke();
      }
    }
    ctx.setLineDash([]);
    flowNodes.forEach(function(n) {
      ctx.fillStyle = 'rgba('+n.col[0]+','+n.col[1]+','+n.col[2]+','+n.alpha+')';
      ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,Math.PI*2); ctx.fill();
    });
    ctx.restore();

    // Floating 3D checkboxes
    checkboxes.forEach(function(cb) {
      cb.ry += cb.dry; cb.y += cb.vy;
      if (cb.y < -cb.size*2) { cb.y = H+cb.size; cb.x = Math.random()*W; }
      var sq = Math.cos(cb.ry), sw = cb.size*Math.abs(sq);
      if (sw < 1) return;
      ctx.save();
      ctx.globalAlpha = cb.alpha;
      var sx = cb.x-sw/2, sy = cb.y-cb.size/2;
      ctx.strokeStyle = dark?'rgba(79,142,247,0.72)':'rgba(22,104,208,0.52)';
      ctx.lineWidth = 1.2;
      ctx.fillStyle = dark?'rgba(79,142,247,0.09)':'rgba(22,104,208,0.06)';
      ctx.beginPath();
      if(ctx.roundRect) ctx.roundRect(sx,sy,sw,cb.size,2); else ctx.rect(sx,sy,sw,cb.size);
      ctx.fill(); ctx.stroke();
      if (cb.checked && sw > cb.size*0.28) {
        ctx.strokeStyle = dark?'rgba(52,211,153,0.92)':'rgba(15,158,106,0.78)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(sx+sw*0.18, sy+cb.size*0.52);
        ctx.lineTo(cb.x-sw*0.05, sy+cb.size*0.74);
        ctx.lineTo(sx+sw*0.85, sy+cb.size*0.26);
        ctx.stroke();
      }
      ctx.restore();
    });

    // Progress rings
    rings.forEach(function(ring) {
      ring.rot += ring.drot; ring.y += ring.vy;
      if (ring.y < -ring.r*3) { ring.y = H+ring.r; ring.x = Math.random()*W; }
      ctx.save();
      ctx.globalAlpha = ring.alpha;
      ctx.lineWidth = ring.r*0.30; ctx.lineCap = 'round';
      ctx.strokeStyle = dark?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.04)';
      ctx.beginPath(); ctx.arc(ring.x,ring.y,ring.r,0,Math.PI*2); ctx.stroke();
      ctx.strokeStyle = dark?'rgba(52,211,153,0.78)':'rgba(15,158,106,0.62)';
      var sa = ring.rot-Math.PI/2;
      ctx.beginPath(); ctx.arc(ring.x,ring.y,ring.r,sa,sa+Math.PI*2*ring.prog); ctx.stroke();
      ctx.restore();
    });

    // Rising particles (green = done, blue = doing)
    particles.forEach(function(p) {
      p.y += p.vy;
      if (p.y < -5) { p.y = H+5; p.x = Math.random()*W; }
      ctx.save();
      ctx.globalAlpha = p.a*(0.5+0.5*Math.sin(t*1.6+p.x*0.02));
      ctx.fillStyle = p.green ? (dark?'rgba(52,211,153,1)':'rgba(15,158,106,1)') : (dark?'rgba(79,142,247,1)':'rgba(22,104,208,1)');
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill();
      ctx.restore();
    });

    // Perspective grid
    var gY = H*0.72, gvpX = W/2, gvpY = gY-H*0.13;
    ctx.save();
    ctx.globalAlpha = dark?0.048:0.032;
    ctx.strokeStyle = dark?'#10B981':'#0F9E6A';
    ctx.lineWidth = 0.6;
    for (var gi = 0; gi <= 8; gi++) {
      var gy = gY-gi*(H*0.05);
      var hw = (W*0.56)*(1-(gi/8)*0.64);
      ctx.beginPath(); ctx.moveTo(gvpX-hw,gy); ctx.lineTo(gvpX+hw,gy); ctx.stroke();
    }
    for (var gv=-6; gv<=6; gv++) {
      ctx.beginPath(); ctx.moveTo(gvpX+gv*(W/6.8),gY); ctx.lineTo(gvpX,gvpY); ctx.stroke();
    }
    ctx.restore();

    requestAnimationFrame(frame);
  }

  window.addEventListener('resize', resize);
  resize(); frame();
}

