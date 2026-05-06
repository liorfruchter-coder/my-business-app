# Graph Report - C:\Users\Owner\Downloads\Claude  (2026-05-05)

## Corpus Check
- Corpus is ~26,204 words - fits in a single context window. You may not need a graph.

## Summary
- 61 nodes · 105 edges · 9 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_App Shell (HTML Document)|App Shell (HTML Document)]]
- [[_COMMUNITY_Auth Module|Auth Module]]
- [[_COMMUNITY_Namespace Proxy IIFE|Namespace Proxy IIFE]]
- [[_COMMUNITY_Calculator Module|Calculator Module]]
- [[_COMMUNITY_Main Calc State (biz_v10)|Main Calc State (biz_v10)]]
- [[_COMMUNITY_App Manager Module|App Manager Module]]
- [[_COMMUNITY_calc()|calc()]]
- [[_COMMUNITY_Israeli Tax Calculation|Israeli Tax Calculation]]
- [[_COMMUNITY_exportAccountant()|exportAccountant()]]

## God Nodes (most connected - your core abstractions)

## Surprising Connections (you probably didn't know these)
- `Auth Module` --depends_on--> `Calculator Module`  [EXTRACTED]
   →   _Bridges community 1 → community 3_
- `Auth Module` --depends_on--> `Namespace Proxy IIFE`  [EXTRACTED]
   →   _Bridges community 1 → community 2_
- `Namespace Proxy IIFE` --manages--> `Main Calc State (biz_v10)`  [EXTRACTED]
   →   _Bridges community 2 → community 4_
- `Namespace Proxy IIFE` --manages--> `Calendar Events (biz_cal_v2)`  [EXTRACTED]
   →   _Bridges community 2 → community 0_
- `Namespace Proxy IIFE` --manages--> `Apps Registry (home_apps_v1)`  [EXTRACTED]
   →   _Bridges community 2 → community 5_

## Hyperedges (group relationships)
- **Client-Side AI Feature Flow** — mre_fn_scan_invoice, mre_fn_run_monthly_advisor, mre_ext_anthropic_api, mre_ds_main_calc_state [INFERRED]
- **Home Quick-Stats Aggregation Flow** — mre_fn_load_home_quick_stats, mre_ds_main_calc_state, mre_ds_calendar_events, mre_ds_tasks, mre_ui_home_screen [INFERRED]
- **User Data Lifecycle (Auth + Namespace + Persistence)** — mre_auth_module, mre_ns_proxy_iife, mre_fn_biz_export_user_data, mre_fn_biz_import_user_data, mre_ds_user_credentials [INFERRED]

## Communities (9 total, 1 thin omitted)

### Community 0 - "App Shell (HTML Document)"
Cohesion: 0.2
Nodes (14): App Shell (HTML Document), Calendar Module, PWA Support, Calendar Events (biz_cal_v2), Tasks Store (biz_tasks_v3), cDraw(), cSaveModal(), loadHomeQuickStats() (+6 more)

### Community 1 - "Auth Module"
Cohesion: 0.36
Nodes (8): Auth Module, User Credentials (biz_pin_v1), bizExportUserData(), bizImportUserData(), bizLogin(), bizRegister(), bizSubmitAuth(), Auth Screen UI

### Community 2 - "Namespace Proxy IIFE"
Cohesion: 0.25
Nodes (9): User Namespace Isolation, Digital Sales State (biz_ds_v1), Home State (home_v1), Snapshots Store (biz_snaps_v6), captureState(), confirmSaveSnap(), homeApplyState(), renderSnapList() (+1 more)

### Community 3 - "Calculator Module"
Cohesion: 0.28
Nodes (6): Calculator Module, Frankfurter Forex API, calcCAC(), calcROAS(), switchTab(), Calculator Screen UI

### Community 4 - "Main Calc State (biz_v10)"
Cohesion: 0.47
Nodes (6): Main Calc State (biz_v10), Anthropic Claude API, applyState(), runMonthlyAdvisor(), saveState(), scanInvoice()

### Community 5 - "App Manager Module"
Cohesion: 0.5
Nodes (5): App Manager Module, Apps Registry (home_apps_v1), goHome(), launchApp(), openApp()

### Community 6 - "calc()"
Cohesion: 0.67
Nodes (4): Monkey-Patching Pattern, Chart.js Library, calc(), renderAnalysis()

### Community 7 - "Israeli Tax Calculation"
Cohesion: 0.67
Nodes (3): Israeli Tax Calculation, calcIsraeliBI(), calcIsraeliTax()

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Not enough signal to generate questions. This usually means the corpus has no AMBIGUOUS edges, no bridge nodes, no INFERRED relationships, and all communities are tightly cohesive. Add more files or run with --mode deep to extract richer edges._