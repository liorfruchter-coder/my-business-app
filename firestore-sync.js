// ═══════════════════════════════════════════════════════════════
//  firestore-sync.js — סנכרון נתונים בין מכשירים דרך Firestore
//  שומר את כל נתוני האפליקציה בענן, טוען אוטומטית במכשיר חדש
// ═══════════════════════════════════════════════════════════════
(function BizFirestoreSync() {
  'use strict';

  /* ── קבצי נתונים שמסונכרנים ── */
  var DATA_KEYS = [
    'biz_v10',       // נתוני מחשבון
    'biz_snaps_v6',  // שמירות גרסאות
    'biz_cal_v2',    // יומן
    'biz_tasks_v3',  // משימות
    'home_v1',       // בית
    'biz_clients_v1',// לקוחות
    'home_apps_v1',  // סדר אפליקציות
    'cal_prefs_v1',  // העדפות יומן
    'biz_pin_v1',    // PIN
  ];

  var _db          = null;
  var _firebaseUid = null;  // UID ב-Firebase (ללא fb_ prefix)
  var _appUid      = null;  // UID באפליקציה (עם fb_ prefix)
  var _syncTimer   = null;
  var _dirty       = false; // האם יש שינויים שלא סונכרנו

  /* ── גישה ל-localStorage (עוקף namespace proxy) ── */
  function _lsGet(k) {
    if (window._bizLS && typeof window._bizLS.get === 'function') return window._bizLS.get(k);
    return localStorage.getItem(k);
  }

  /* ── המתן עד שהאימות מוכן ── */
  function _waitForAuth() {
    var tries = 0;
    var interval = setInterval(function() {
      tries++;
      var db  = window.bizFirebaseDB && window.bizFirebaseDB();
      var uid = _lsGet('_biz_uid');

      if (db && uid && uid.indexOf('fb_') === 0) {
        clearInterval(interval);
        _db          = db;
        _appUid      = uid;
        _firebaseUid = uid.slice(3); // הסר fb_
        _start();
      } else if (tries > 90) {
        clearInterval(interval); // ויתור אחרי 90 שניות
        console.log('[BizFS] Not a Firebase session — Firestore sync skipped');
      }
    }, 1000);
  }

  /* ── התחל סנכרון ── */
  function _start() {
    console.log('[BizFS] Initializing for', _firebaseUid);

    // 1. שחזר מהענן (אם יש נתונים יותר חדשים)
    _restoreFromFirestore();

    // 2. שמור לענן כל 5 דקות
    setInterval(function() {
      if (_dirty) _saveToFirestore();
    }, 5 * 60 * 1000);

    // 3. שמור כשיוצאים מהדף
    window.addEventListener('beforeunload', function() {
      if (_dirty) _saveToFirestoreSync();
    });

    // 4. האזן לשינויים ב-localStorage
    _patchLocalStorage();
  }

  /* ── שחזר נתונים מ-Firestore ── */
  function _restoreFromFirestore() {
    // מניעת לולאת טעינה
    if (sessionStorage.getItem('_biz_fs_restored')) {
      // כבר שוחזר — רק שמור נתונים מקומיים לענן
      setTimeout(function() { _dirty = true; _saveToFirestore(); }, 5000);
      return;
    }

    var colRef = _db.collection('userdata').doc(_firebaseUid).collection('keys');

    colRef.get().then(function(snapshot) {
      sessionStorage.setItem('_biz_fs_restored', '1');

      if (snapshot.empty) {
        // משתמש חדש — שמור נתונים מקומיים לענן
        console.log('[BizFS] New user — uploading local data');
        _dirty = true;
        setTimeout(_saveToFirestore, 3000);
        return;
      }

      var restored = 0;
      var cloudData = {};

      snapshot.forEach(function(doc) {
        if (DATA_KEYS.indexOf(doc.id) !== -1 && doc.data().v) {
          cloudData[doc.id] = doc.data();
        }
      });

      DATA_KEYS.forEach(function(key) {
        if (!cloudData[key]) return;

        var lsKey    = _appUid + '_' + key;
        var localVal = localStorage.getItem(lsKey);
        var cloudVal = cloudData[key].v;

        if (!localVal) {
          // אין נתון מקומי — קח מהענן
          localStorage.setItem(lsKey, cloudVal);
          restored++;
        } else {
          // יש נתון מקומי — בדוק מה יותר חדש
          var cloudMs = cloudData[key].t ? cloudData[key].t.toMillis() : 0;
          var localMs = parseInt(localStorage.getItem('_biz_fst_' + key) || '0', 10);

          if (cloudMs > localMs + 60000) { // ענן יותר חדש ב-60+ שניות
            localStorage.setItem(lsKey, cloudVal);
            restored++;
          }
        }
      });

      if (restored > 0) {
        console.log('[BizFS] Restored', restored, 'keys from Firestore');
        // טען מחדש כדי לאמץ הנתונים
        if (!sessionStorage.getItem('_biz_fs_reloaded')) {
          sessionStorage.setItem('_biz_fs_reloaded', '1');
          location.reload();
        }
      } else {
        console.log('[BizFS] Local data is up to date ✓');
        _dirty = true;
        setTimeout(_saveToFirestore, 5000); // שמור מקומי לענן
      }

    }).catch(function(err) {
      console.warn('[BizFS] Restore error:', err.code, err.message);
      sessionStorage.setItem('_biz_fs_restored', '1');
    });
  }

  /* ── שמור נתונים ל-Firestore (async) ── */
  function _saveToFirestore() {
    if (!_db || !_firebaseUid || !_appUid) return Promise.resolve();

    var batch  = _db.batch();
    var colRef = _db.collection('userdata').doc(_firebaseUid).collection('keys');
    var ts     = firebase.firestore.FieldValue.serverTimestamp();
    var nowMs  = Date.now();
    var count  = 0;

    DATA_KEYS.forEach(function(key) {
      var val = localStorage.getItem(_appUid + '_' + key);
      if (!val) return;
      if (val.length > 950000) {
        console.warn('[BizFS] Skipping oversized key:', key, val.length + ' bytes');
        return;
      }
      batch.set(colRef.doc(key), { v: val, t: ts });
      localStorage.setItem('_biz_fst_' + key, nowMs.toString());
      count++;
    });

    if (count === 0) return Promise.resolve();

    return batch.commit().then(function() {
      _dirty = false;
      console.log('[BizFS] Synced', count, 'keys ✓', new Date().toLocaleTimeString('he-IL'));
    }).catch(function(err) {
      console.warn('[BizFS] Save error:', err.code, err.message);
    });
  }

  /* ── שמור סינכרוני (לפני סגירת דף) ── */
  function _saveToFirestoreSync() {
    if (!_db || !_firebaseUid || !_appUid) return;
    // navigator.sendBeacon לא עובד עם Firestore — נסה שמירה רגילה ונקווה שתספיק
    _saveToFirestore();
  }

  /* ── האזן לשינויים ב-localStorage ── */
  function _patchLocalStorage() {
    // בדוק אם כבר נעשתה עטיפה (על ידי cloud-backup.js)
    if (localStorage._biz_fs_patched) return;
    localStorage._biz_fs_patched = true;

    var _orig = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function(key, value) {
      _orig(key, value);

      // בדוק אם זה מפתח נתונים שלנו
      if (_appUid && key.indexOf(_appUid + '_') === 0) {
        var dataKey = key.slice(_appUid.length + 1);
        if (DATA_KEYS.indexOf(dataKey) !== -1) {
          _dirty = true;
          // debounce: שמור 4 שניות אחרי השינוי האחרון
          clearTimeout(_syncTimer);
          _syncTimer = setTimeout(_saveToFirestore, 4000);
        }
      }
    };
  }

  /* ── פונקציות חיצוניות ── */
  window.bizFirestoreSync  = function() { _dirty = true; return _saveToFirestore(); };
  window.bizFirestoreReady = function() { return !!_db; };

  /* ── התחל ── */
  document.addEventListener('DOMContentLoaded', function() {
    // המתן 2 שניות כדי לתת ל-firebase-auth.js לאתחל
    setTimeout(_waitForAuth, 2000);
  });

})();
