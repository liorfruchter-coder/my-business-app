# מדריך הפצה — מערכת ניהול עסק

---

## 🌐 PWA — אתר שניתן להתקנה (הכי מהיר)

### שלב 1: העלאה לשרת
האפשרות הכי פשוטה — Netlify (חינם לגמרי):

1. כנס ל־ https://netlify.com → **Sign up** (חינם)
2. גרור את **כל תיקיית Claude** לתוך האזור שכתוב "Drop your site here"
3. תוך 30 שניות קיבלת כתובת URL כמו: `https://shiny-app-12345.netlify.app`

זהו — האפליקציה באוויר!

### שלב 2: שם דומיין מותאם (אופציונלי)
- ב-Netlify: Site Settings → Domain → Add custom domain
- דוגמה: `mybusiness.co.il`

### איך המשתמש מתקין על הטלפון:
**אנדרואיד (Chrome):**
1. פותחים את הכתובת בכרום
2. מופיעה הודעה "הוסף למסך הבית" — לוחצים עליה
3. האפליקציה מותקנת כמו אפליקציה רגילה ✓

**iPhone (Safari):**
1. פותחים את הכתובת בספארי
2. לוחצים על כפתור השיתוף (⬆)
3. "הוסף למסך הבית"

---

## 📱 Capacitor — אפליקציית אנדרואיד אמיתית (Google Play)

### דרישות מוקדמות:
- [ ] Node.js מותקן: https://nodejs.org (הורד LTS)
- [ ] Android Studio מותקן: https://developer.android.com/studio
- [ ] Java JDK 17+: מגיע עם Android Studio

### שלב 1: התקנת Capacitor

פתח Command Prompt בתיקיית Claude:
```
cd C:\Users\Owner\Downloads\Claude
npm install
```

### שלב 2: הוספת פלטפורמת אנדרואיד
```
npx cap add android
npx cap sync
```

### שלב 3: פתיחה ב-Android Studio
```
npx cap open android
```

### שלב 4: בניית APK
ב-Android Studio:
1. **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**
2. הקובץ נוצר ב: `android/app/build/outputs/apk/debug/app-debug.apk`
3. שלח את הקובץ לטלפון → התקן

### שלב 5: Google Play Store (אופציונלי)
1. יצור חשבון Developer: https://play.google.com/console ($25 חד-פעמי)
2. ב-Android Studio: **Build** → **Generate Signed Bundle/APK**
3. העלה את ה-AAB לPlay Console

---

## 🔄 עדכון האפליקציה בלי לפגוע בנתונים

### PWA:
1. ערוך את הקבצים (HTML, JS וכו')
2. העלה שוב ל-Netlify (גרור תיקייה)
3. Service Worker מתעדכן אוטומטי תוך 24 שעות
4. נתוני המשתמשים (localStorage) נשמרים ✓

### Capacitor:
1. ערוך את הקבצים
2. הרץ: `npx cap sync`
3. בנה APK חדש ב-Android Studio
4. הגש עדכון ל-Play Store
5. נתוני המשתמשים נשמרים (localStorage → WebView storage) ✓

---

## 📁 מבנה הקבצים

```
Claude/
├── מחשבון_רווח_עסקי.html   ← קובץ ראשי (HTML + CSS)
├── home.js                   ← לוגיקת מסך הבית + canvas
├── calc.js                   ← מחשבון רווח
├── calendar.js               ← יומן
├── tasks.js                  ← משימות
├── manifest.json             ← הגדרות PWA
├── sw.js                     ← Service Worker (offline)
├── index.html                ← נקודת כניסה ל-Capacitor
├── icon-192.svg              ← אייקון קטן
├── icon-512.svg              ← אייקון גדול
├── icon-maskable.svg         ← אייקון לאנדרואיד
├── package.json              ← הגדרות npm
└── capacitor.config.json     ← הגדרות Capacitor
```

---

## ⚠️ חשוב: נתוני משתמשים

הנתונים שמורים ב-**localStorage** — בנפרד מהקוד.
כל עדכון קוד **לא** פוגע בנתונים.

אך שים לב:
- **ניקוי cache** בדפדפן — עשוי למחוק נתונים
- **הסרת אפליקציה** — מוחקת נתונים

**המלצה לעתיד:** הוסף Firebase / Supabase לסנכרון נתונים בענן.
