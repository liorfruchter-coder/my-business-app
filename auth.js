// ═══════════════════════════════════════════════════════════════
//  AUTH MODULE — Google + Microsoft OAuth + Local mode
//  קובץ זה מנהל את מסך ההתחברות ואת מצב הזיהוי של המשתמש
// ═══════════════════════════════════════════════════════════════
(function AuthModule() {

  /* ── Storage keys (raw — bypasses namespace proxy) ── */
  var AUTH_STORE   = '_biz_auth_v1';
  var G_CID_KEY    = '_biz_gcid';
  var MS_CID_KEY   = '_biz_mcid';
  var EXPIRY_DAYS  = 30;

  /* ── Raw storage helpers (bypass namespace proxy) ── */
  function rGet(k) { return window._bizLS ? window._bizLS.get(k) : localStorage.getItem(k); }
  function rSet(k,v){ return window._bizLS ? window._bizLS.set(k,v) : localStorage.setItem(k,v); }
  function rDel(k) { return window._bizLS ? window._bizLS.remove(k) : localStorage.removeItem(k); }

  /* ── Auth session helpers ── */
  function getSession() {
    try { return JSON.parse(rGet(AUTH_STORE) || 'null'); } catch(e){ return null; }
  }
  function saveSession(data) {
    data.expiresAt = Date.now() + EXPIRY_DAYS * 86400000;
    rSet(AUTH_STORE, JSON.stringify(data));
  }
  function isValid(s) { return s && s.uid && s.expiresAt > Date.now(); }

  /* ── Provider config ── */
  function getGCid()  { return rGet(G_CID_KEY)  || ''; }
  function getMsCid() { return rGet(MS_CID_KEY) || ''; }

  /* ── Unlock app after successful auth ── */
  function unlockApp(session) {
    saveSession(session);
    rSet('_biz_uid', session.uid);
    var overlay = document.getElementById('auth-overlay');
    if (overlay) {
      overlay.style.animation = 'overlayFadeOut .4s ease forwards';
      setTimeout(function(){ overlay.style.display = 'none'; }, 380);
    }
    updateUserChip(session);
    // Show the app — works alongside the existing bizShowApp/bizAuthInit system
    if (window.bizShowApp) {
      setTimeout(window.bizShowApp, 200);
    } else {
      // Fallback: show #app-home directly
      var homeEl = document.getElementById('app-home');
      if (homeEl) homeEl.style.display = 'flex';
    }
  }

  function updateUserChip(session) {
    var chip = document.getElementById('home-user-chip');
    if (!chip) return;
    var name = session.displayName || session.email || '';
    var initials = name.split(' ').map(function(w){ return w[0]||''; }).slice(0,2).join('').toUpperCase() || '?';
    chip.innerHTML =
      (session.picture
        ? '<img src="'+session.picture+'" style="width:28px;height:28px;border-radius:50%;object-fit:cover;">'
        : '<span style="width:28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;">'+initials+'</span>')
      + '<span style="font-size:12px;font-weight:600;color:var(--text2);max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+(name.split(' ')[0]||name)+'</span>';
    chip.style.display = 'flex';
  }

  /* ══ PUBLIC: initAuth ════════════════════════════════════════
   *  סמן שה-module נטען — bizAuthInit בHTML בודק אם הפונקציה קיימת ודולג
   *  הלוגיקה האמיתית נמצאת ב-DOMContentLoaded למטה
   * ═══════════════════════════════════════════════════════════ */
  window.initAuth = function() { /* placeholder — DOMContentLoaded handles auth */ };

  /* ══ GOOGLE SIGN-IN ════════════════════════════════════════ */
  window.handleGoogleSignIn = function() {
    var cid = getGCid();
    if (!cid) { showProviderSetup('google'); return; }
    setAuthStatus('loading', 'Google…');
    if (window.google && window.google.accounts) {
      doGoogle(cid);
    } else {
      loadScript('https://accounts.google.com/gsi/client', function(){ doGoogle(cid); }, function(){
        setAuthStatus('error', 'שגיאה בטעינת Google. בדוק חיבור אינטרנט.');
      });
    }
  };

  function doGoogle(cid) {
    try {
      google.accounts.id.initialize({
        client_id: cid,
        callback: function(resp) {
          var p = parseJwt(resp.credential);
          if (!p) { setAuthStatus('error', 'שגיאה בעיבוד תשובת Google.'); return; }
          setAuthStatus('');
          unlockApp({
            provider: 'google',
            uid: 'g_' + hash(p.sub || p.email),
            name: p.name || '',
            email: p.email || '',
            picture: p.picture || '',
            displayName: p.name || p.email
          });
        },
        auto_select: false,
        cancel_on_tap_outside: true,
        ux_mode: 'popup'
      });
      google.accounts.id.prompt(function(n) {
        if (n.isNotDisplayed() || n.isSkippedMoment()) {
          // Fallback: render button inside container
          var wrap = document.getElementById('google-gis-wrap');
          if (wrap) {
            wrap.innerHTML = '';
            google.accounts.id.renderButton(wrap, {
              theme: 'outline', size: 'large', shape: 'pill',
              width: 280, locale: 'iw', text: 'signin_with'
            });
          }
          setAuthStatus('');
        }
      });
    } catch(e) {
      setAuthStatus('error', 'Client ID לא תקין. בדוק את הגדרות Google.');
      console.error('Google init error:', e);
    }
  }

  /* ══ MICROSOFT SIGN-IN ═══════════════════════════════════════ */
  window.handleMsSignIn = function() {
    var cid = getMsCid();
    if (!cid) { showProviderSetup('ms'); return; }
    setAuthStatus('loading', 'Microsoft…');
    if (window.msal) {
      doMicrosoft(cid);
    } else {
      loadScript('https://alcdn.msauth.net/browser/2.38.0/js/msal-browser.min.js', function(){ doMicrosoft(cid); }, function(){
        setAuthStatus('error', 'שגיאה בטעינת Microsoft. בדוק חיבור אינטרנט.');
      });
    }
  };

  function doMicrosoft(cid) {
    try {
      var inst = new msal.PublicClientApplication({
        auth: { clientId: cid, authority: 'https://login.microsoftonline.com/common', redirectUri: window.location.origin },
        cache: { cacheLocation: 'sessionStorage' }
      });
      inst.loginPopup({ scopes: ['User.Read','openid','profile','email'] })
        .then(function(r) {
          var acc = r.account;
          setAuthStatus('');
          unlockApp({
            provider: 'microsoft',
            uid: 'ms_' + hash(acc.homeAccountId || acc.username),
            name: acc.name || '',
            email: acc.username || '',
            displayName: acc.name || acc.username
          });
        })
        .catch(function(e) {
          if (e.errorCode !== 'user_cancelled')
            setAuthStatus('error', 'ההתחברות ל-Microsoft נכשלה. נסה שוב.');
          else
            setAuthStatus('');
        });
    } catch(e) {
      setAuthStatus('error', 'Client ID לא תקין. בדוק את הגדרות Microsoft.');
    }
  }

  /* ══ LOCAL MODE ═════════════════════════════════════════════ */
  window.continueLocally = function() {
    // תמיד צור UID חדש — לא לשאוב מהסשן הקודם
    var uid = 'local_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    unlockApp({ provider: 'local', uid: uid, displayName: 'משתמש מקומי' });
  };

  /* ══ SIGN OUT ════════════════════════════════════════════════ */
  window.bizSignOut = function() {
    // Flush all pending saves before clearing session
    try { if(typeof tkSave === 'function') tkSave(); } catch(e){}
    try { if(typeof cSave === 'function') cSave(); } catch(e){}
    try { if(typeof crmSave === 'function') crmSave(); } catch(e){}
    // נקה את כל מידע הסשן
    rDel(AUTH_STORE);          // _biz_auth_v1
    rDel('_biz_uid');          // session key
    // נקה גם את ה-legacy session של המערכת הישנה
    try { localStorage.removeItem('_biz_uid'); } catch(e) {}
    // סגור modal אם פתוח
    var m = document.getElementById('auth-settings-modal');
    if (m) m.classList.remove('show');
    // אם מחובר דרך Firebase — התנתק שם גם כן
    if (window.firebaseSignOut) {
      window.firebaseSignOut();
    } else {
      setTimeout(function(){ location.reload(); }, 100);
    }
  };

  /* ══ PROVIDER SETUP MODAL ════════════════════════════════════ */
  window.showProviderSetup = function(provider) {
    var modal = document.getElementById('auth-setup-modal');
    if (!modal) return;
    var isGoogle = (provider === 'google');
    document.getElementById('auth-setup-title').textContent = isGoogle ? 'הגדרת Google OAuth' : 'הגדרת Microsoft OAuth';
    document.getElementById('auth-setup-logo').innerHTML = isGoogle ? googleSVG(28) : msSVG(28);
    document.getElementById('auth-setup-provider-val').value = provider;
    document.getElementById('auth-setup-cid').value = isGoogle ? getGCid() : getMsCid();
    document.getElementById('auth-setup-placeholder').textContent =
      isGoogle ? '1234567890-abcd....apps.googleusercontent.com' : 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';
    document.getElementById('auth-setup-help').innerHTML = isGoogle
      ? 'השג Client ID ב: <a href="https://console.cloud.google.com/apis/credentials" target="_blank" style="color:var(--accent);">Google Cloud Console</a><br><small>צור Credentials → OAuth 2.0 Client ID → Web Application<br>הוסף את כתובת האתר שלך ל-Authorized JS Origins</small>'
      : 'השג Client ID ב: <a href="https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade" target="_blank" style="color:var(--accent);">Azure Portal</a><br><small>App Registrations → New Registration → Web<br>הוסף את כתובת האתר כ-Redirect URI</small>';
    modal.classList.add('show');
  };

  window.saveProviderSetup = function() {
    var provider = document.getElementById('auth-setup-provider-val').value;
    var cid = (document.getElementById('auth-setup-cid').value || '').trim();
    if (!cid) { alert('הזן Client ID תקין'); return; }
    if (provider === 'google') rSet(G_CID_KEY, cid);
    else rSet(MS_CID_KEY, cid);
    closeProviderSetup();
    setAuthStatus('');
    if (provider === 'google') window.handleGoogleSignIn();
    else window.handleMsSignIn();
  };

  window.closeProviderSetup = function() {
    var modal = document.getElementById('auth-setup-modal');
    if (modal) modal.classList.remove('show');
  };

  /* ── Auth settings / profile chip — פרופיל פשוט ── */
  window.openAuthSettings = function() {
    var m = document.getElementById('auth-settings-modal');
    if (!m) return;
    var sess = getSession();
    var info = document.getElementById('asm-current');
    if (info) {
      if (sess && isValid(sess)) {
        var name     = sess.displayName || sess.email || 'משתמש';
        var initials = name.split(' ').map(function(w){ return w[0]||''; }).slice(0,2).join('').toUpperCase() || '?';
        var providerHe = { google:'Google', microsoft:'Microsoft', local:'מקומי' }[sess.provider] || sess.provider;
        info.innerHTML =
          '<div style="text-align:center;padding:.6rem 0 .9rem;">'
          + (sess.picture
            ? '<img src="'+sess.picture+'" style="width:60px;height:60px;border-radius:50%;object-fit:cover;margin:0 auto .7rem;display:block;box-shadow:0 4px 14px rgba(0,0,0,.15);">'
            : '<div style="width:60px;height:60px;border-radius:50%;background:var(--accent);color:#fff;font-size:22px;font-weight:800;display:flex;align-items:center;justify-content:center;margin:0 auto .7rem;">'+initials+'</div>')
          + '<div style="font-size:17px;font-weight:800;color:var(--text);margin-bottom:.2rem;">'+name+'</div>'
          + (sess.email ? '<div style="font-size:12px;color:var(--text3);direction:ltr;margin-bottom:.25rem;">'+sess.email+'</div>' : '')
          + '<div style="display:inline-flex;align-items:center;gap:5px;background:var(--surface2);border:1px solid var(--border);border-radius:20px;padding:3px 10px 3px 8px;font-size:11.5px;font-weight:700;color:var(--text3);">'
          + (sess.provider==='google' ? '<svg width="13" height="13" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>'
            : sess.provider==='microsoft' ? '<svg width="13" height="13" viewBox="0 0 21 21"><rect x="1" y="1" width="9" height="9" fill="#F25022"/><rect x="11" y="1" width="9" height="9" fill="#7FBA00"/><rect x="1" y="11" width="9" height="9" fill="#00A4EF"/><rect x="11" y="11" width="9" height="9" fill="#FFB900"/></svg>'
            : '⚡')
          + ' מחובר עם '+providerHe+'</div>'
          + '</div>';
      } else {
        info.innerHTML = '<div style="text-align:center;padding:.8rem 0;font-size:14px;color:var(--text3);">לא מחובר</div>';
      }
    }
    m.classList.add('show');
  };

  /* ── Helpers ── */
  function setAuthStatus(type, msg) {
    var el = document.getElementById('auth-status');
    var spinner = document.getElementById('auth-spinner');
    if (!el) return;
    el.textContent = msg || '';
    el.className = 'auth-status-msg' + (type === 'error' ? ' auth-error' : '');
    if (spinner) spinner.style.display = (type === 'loading') ? 'block' : 'none';
  }

  function showToast(msg) {
    var t = document.createElement('div');
    t.style.cssText = 'position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);background:var(--surface);border:1px solid var(--border2);border-radius:20px;padding:8px 20px;font-size:13px;font-weight:600;color:var(--text);box-shadow:var(--shadow-md);z-index:9999;animation:floatUp .25s ease;';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function(){ t.remove(); }, 2500);
  }

  function loadScript(src, onload, onerror) {
    var s = document.createElement('script');
    s.src = src;
    s.onload = onload;
    s.onerror = onerror;
    document.head.appendChild(s);
  }

  function parseJwt(token) {
    try { return JSON.parse(atob(token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/'))); }
    catch(e){ return null; }
  }

  function hash(s) {
    var h = 0;
    for (var i = 0; i < s.length; i++) { h = ((h << 5) - h) + s.charCodeAt(i); h = h & h; }
    return Math.abs(h).toString(36);
  }

  /* ── SVG icons ── */
  function googleSVG(size) {
    var s = size || 20;
    return '<svg width="'+s+'" height="'+s+'" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>';
  }

  function msSVG(size) {
    var s = size || 20;
    return '<svg width="'+s+'" height="'+s+'" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg"><rect x="1" y="1" width="9" height="9" fill="#F25022"/><rect x="11" y="1" width="9" height="9" fill="#7FBA00"/><rect x="1" y="11" width="9" height="9" fill="#00A4EF"/><rect x="11" y="11" width="9" height="9" fill="#FFB900"/></svg>';
  }

  // Expose SVGs for inline use in HTML
  window._authSVG = { google: googleSVG, ms: msSVG };

  /* ── Init on DOM ready ── */
  document.addEventListener('DOMContentLoaded', function(){
    var sess = getSession();

    if (isValid(sess)) {
      // ── Session OAuth תקפה — הצג אפליקציה ישירות ──
      var authOverlay = document.getElementById('auth-overlay');
      if (authOverlay) authOverlay.style.display = 'none';
      var authScreen  = document.getElementById('biz-auth-screen');
      if (authScreen)  authScreen.style.display  = 'none';
      // כתוב גם ב-legacy key כדי ש-bizAuthInit ידלג על ה-else branch שלו
      if (window._bizLS) window._bizLS.set('_biz_uid', sess.uid);
      updateUserChip(sess);
      if (window.bizShowApp) {
        window.bizShowApp();
      } else {
        var homeEl = document.getElementById('app-home');
        if (homeEl) homeEl.style.display = 'flex';
        var fabEl  = document.getElementById('home-fab');
        if (fabEl)  fabEl.classList.add('visible');
      }
    } else {
      // ── אין session OAuth תקפה ──
      var oldUid = window._bizLS && window._bizLS.get('_biz_uid');
      if (oldUid) {
        // יש session username/password ישן — הצג את האפליקציה ישירות
        var authScreen2 = document.getElementById('biz-auth-screen');
        if (authScreen2) authScreen2.style.display = 'none';
        if (window.bizShowApp) {
          window.bizShowApp();
        } else {
          var homeEl2 = document.getElementById('app-home');
          if (homeEl2) homeEl2.style.display = 'flex';
          var fabEl2  = document.getElementById('home-fab');
          if (fabEl2)  fabEl2.classList.add('visible');
        }
        return;
      }
      // אין שום session → הצג overlay כניסה
      var overlay = document.getElementById('auth-overlay');
      if (overlay) {
        overlay.style.display = 'flex';
        overlay.style.animation = 'overlayFadeIn .4s ease forwards';
      }
    }
  });

})();
