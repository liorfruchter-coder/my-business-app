// ═══════════════════════════════════════════════════════════════
//  firebase-auth.js — אימות משתמשים עם Firebase
//  מחליף את מערכת ה-OAuth הישנה שדרשה מהמשתמש להזין Client ID
// ═══════════════════════════════════════════════════════════════
(function BizFirebaseAuth() {
  'use strict';

  var FIREBASE_READY = false;
  var _auth = null;
  var _db   = null;

  /* ── בדוק אם Firebase מוגדר ── */
  function isConfigured() {
    var cfg = window.BIZ_FIREBASE_CONFIG;
    return cfg && cfg.apiKey && cfg.apiKey !== 'FILL_IN';
  }

  /* ── אתחל Firebase ── */
  function initFirebase(onReady) {
    if (!isConfigured()) { onReady(false); return; }
    var cfg = window.BIZ_FIREBASE_CONFIG;

    // טען Firebase SDK אם עוד לא נטען
    if (window.firebase && window.firebase.auth) {
      _auth = firebase.auth();
      _db   = firebase.firestore ? firebase.firestore() : null;
      FIREBASE_READY = true;
      onReady(true);
      return;
    }

    var sdkBase = 'https://www.gstatic.com/firebasejs/9.22.2/';
    var scripts = [
      'https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js',
      'https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js',
      'https://www.gstatic.com/firebasejs/9.22.2/firebase-firestore-compat.js',
    ];

    var loaded = 0;
    function tryNext() {
      if (loaded >= scripts.length) {
        try {
          firebase.initializeApp(cfg);
          _auth = firebase.auth();
          _db   = firebase.firestore();
          FIREBASE_READY = true;
          onReady(true);
        } catch(e) {
          console.error('[BizAuth] Firebase init error:', e);
          onReady(false);
        }
        return;
      }
      var s = document.createElement('script');
      s.src = scripts[loaded++];
      s.onload  = tryNext;
      s.onerror = function() { onReady(false); };
      document.head.appendChild(s);
    }
    tryNext();
  }

  /* ── כניסה עם Google ── */
  window.firebaseSignInGoogle = function() {
    if (!FIREBASE_READY) { _showStatus('טוען...'); initFirebase(function(ok){ if(ok) window.firebaseSignInGoogle(); }); return; }
    _showStatus('loading', 'מתחבר עם Google...');
    var provider = new firebase.auth.GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });
    _auth.signInWithPopup(provider)
      .then(function(result) {
        _showStatus('');
        _onSignIn(result.user, 'google');
      })
      .catch(function(err) {
        if (err.code === 'auth/popup-closed-by-user') { _showStatus(''); return; }
        _showStatus('error', 'הכניסה נכשלה: ' + (err.message || err.code));
      });
  };

  /* ── כניסה עם Apple (אופציונלי) ── */
  window.firebaseSignInApple = function() {
    if (!FIREBASE_READY) return;
    _showStatus('loading', 'מתחבר עם Apple...');
    var provider = new firebase.auth.OAuthProvider('apple.com');
    provider.addScope('email');
    provider.addScope('name');
    _auth.signInWithPopup(provider)
      .then(function(result) {
        _showStatus('');
        _onSignIn(result.user, 'apple');
      })
      .catch(function(err) {
        if (err.code === 'auth/popup-closed-by-user') { _showStatus(''); return; }
        _showStatus('error', 'הכניסה נכשלה: ' + (err.message || err.code));
      });
  };

  /* ── כניסה עם Email + סיסמה ── */
  window.firebaseSignInEmail = function(email, password) {
    if (!FIREBASE_READY) return;
    _showStatus('loading', 'מתחבר...');
    _auth.signInWithEmailAndPassword(email, password)
      .then(function(result) {
        _showStatus('');
        _onSignIn(result.user, 'email');
      })
      .catch(function(err) {
        var msg = {
          'auth/user-not-found': 'משתמש לא קיים',
          'auth/wrong-password': 'סיסמה שגויה',
          'auth/invalid-email':  'כתובת מייל לא תקינה',
          'auth/too-many-requests': 'יותר מדי ניסיונות — נסה שוב מאוחר יותר',
        }[err.code] || err.message;
        _showStatus('error', msg);
      });
  };

  /* ── הרשמה עם Email + סיסמה ── */
  window.firebaseRegisterEmail = function(email, password, name) {
    if (!FIREBASE_READY) return;
    _showStatus('loading', 'יוצר חשבון...');
    _auth.createUserWithEmailAndPassword(email, password)
      .then(function(result) {
        // שמור שם משתמש
        return result.user.updateProfile({ displayName: name || email.split('@')[0] })
          .then(function() {
            _showStatus('');
            _onSignIn(result.user, 'email');
          });
      })
      .catch(function(err) {
        var msg = {
          'auth/email-already-in-use': 'כתובת המייל כבר קיימת',
          'auth/weak-password': 'הסיסמה חלשה מדי (מינימום 6 תווים)',
          'auth/invalid-email': 'כתובת מייל לא תקינה',
        }[err.code] || err.message;
        _showStatus('error', msg);
      });
  };

  /* ── שכחתי סיסמה ── */
  window.firebaseResetPassword = function(email) {
    if (!FIREBASE_READY || !email) return;
    _auth.sendPasswordResetEmail(email)
      .then(function() { _showStatus('success', 'קישור איפוס נשלח למייל ✓'); })
      .catch(function() { _showStatus('error', 'שגיאה — בדוק את כתובת המייל'); });
  };

  /* ── התנתקות ── */
  window.firebaseSignOut = function() {
    if (_auth) _auth.signOut().then(function() { location.reload(); });
    else { location.reload(); }
  };

  /* ── מה קורה אחרי כניסה מוצלחת ── */
  function _onSignIn(fbUser, provider) {
    var uid = 'fb_' + fbUser.uid;

    // שמור session במערכת הקיימת
    var session = {
      provider:    provider,
      uid:         uid,
      firebaseUid: fbUser.uid,
      email:       fbUser.email || '',
      displayName: fbUser.displayName || fbUser.email || 'משתמש',
      picture:     fbUser.photoURL  || '',
      expiresAt:   Date.now() + 30 * 86400000,
    };

    // כתוב ל-localStorage כך שמערכת ה-namespace הקיימת תעבוד
    var _raw = window._bizLS || localStorage;
    var store = typeof _raw.set === 'function' ? _raw : {
      set: function(k,v){ localStorage.setItem(k,v); },
      get: function(k){ return localStorage.getItem(k); }
    };
    store.set('_biz_auth_v1', JSON.stringify(session));
    store.set('_biz_uid',     uid);

    // עדכן Firestore עם פרטי המשתמש
    if (_db) {
      _db.collection('users').doc(fbUser.uid).set({
        displayName: session.displayName,
        email:       session.email,
        provider:    provider,
        lastLogin:   firebase.firestore.FieldValue.serverTimestamp(),
        uid:         uid,
      }, { merge: true }).catch(function(){});
    }

    // פתח את האפליקציה
    _unlockApp(session);
  }

  function _unlockApp(session) {
    var overlay = document.getElementById('auth-overlay');
    if (overlay) {
      overlay.style.animation = 'overlayFadeOut .4s ease forwards';
      setTimeout(function(){ overlay.style.display = 'none'; }, 380);
    }
    _updateUserChip(session);
    if (window.bizShowApp) {
      setTimeout(window.bizShowApp, 200);
    } else {
      var homeEl = document.getElementById('app-home');
      if (homeEl) homeEl.style.display = 'flex';
    }
  }

  function _updateUserChip(session) {
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

  function _showStatus(type, msg) {
    var spinner = document.getElementById('auth-spinner');
    var status  = document.getElementById('auth-status');
    var errEl   = document.getElementById('auth-err');   // email form error display
    var btn     = document.getElementById('auth-submit-btn');

    if (spinner) spinner.style.display = (type === 'loading') ? 'block' : 'none';
    if (status) {
      status.textContent = msg || '';
      status.className = 'auth-status-msg' + (type === 'error' ? ' error' : type === 'success' ? ' success' : '');
    }
    // Also feed email form error box
    if (errEl) {
      if (type === 'error' && msg) { errEl.textContent = msg; errEl.style.display = 'block'; }
      else { errEl.style.display = 'none'; }
    }
    // Re-enable submit button on error
    if (type === 'error' && btn) {
      btn.disabled = false;
      btn.textContent = (window._bizAuthMode === 'register') ? 'צור חשבון' : 'כניסה';
    }
  }

  /* ── בדוק אם המשתמש כבר מחובר (session קיים) ── */
  function _checkExistingSession() {
    try {
      var raw = (window._bizLS && typeof window._bizLS.get === 'function')
        ? window._bizLS.get('_biz_auth_v1')
        : localStorage.getItem('_biz_auth_v1');
      var s = JSON.parse(raw || 'null');
      if (s && s.uid && s.expiresAt > Date.now()) return s;
    } catch(e) {}
    return null;
  }

  /* ── אתחול בטעינת הדף ── */
  document.addEventListener('DOMContentLoaded', function() {
    // אם המשתמש כבר מחובר — פתח ישירות
    var existing = _checkExistingSession();
    if (existing) {
      _unlockApp(existing);
      return;
    }

    // טען Firebase ועדכן את כפתורי ההתחברות
    if (isConfigured()) {
      initFirebase(function(ok) {
        if (!ok) return;
        // האזן לשינויי מצב אימות
        _auth.onAuthStateChanged(function(user) {
          if (user) {
            var existing2 = _checkExistingSession();
            if (!existing2) {
              _onSignIn(user, user.providerData[0] ? user.providerData[0].providerId.replace('.com','') : 'firebase');
            }
          }
        });
      });
    }
  });

  /* ── חשוף מצב Firebase לבדיקות ── */
  window.bizFirebaseReady = function() { return FIREBASE_READY; };
  window.bizFirebaseDB    = function() { return _db; };

  // מסמן ל-bizAuthInit שה-Firebase auth כבר מנהל הכל — אל תפעיל את מערכת הישנה
  window.initAuth = true;

})();
