# 13_BUG_REGISTER_AND_TECHNICAL_DEBT.md — Bug Register, Defects, and Technical Debt

**Scope:** Formal register of resolved defects, residual technical debt, suspected edge cases, architectural workarounds, and maintenance recommendations in CycleCare.  
**Audit Date:** 2026-10-10  
**Evidence Standard:** Git commit history, code inspection, static analysis, and runtime verification.

---

## 1. Confirmed Defects Register (Resolved & Active)

| Bug ID | Title | Severity | Affected Feature | Affected Files | Observed Behavior | Root Cause | Status | Verification |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **BUG-01** | Render Startup Crash (`getQuickCareItems`) | Critical | Backend Boot / Deploy | `chatController.js`, `chatRoutes.js` | Server threw `ReferenceError: getQuickCareItems is not defined` within 21s of launch on Render. | Missing function declaration in controller while referenced in exports and router. | **RESOLVED** (Commit `bc39bcd`) | `GET /api/v1/health` HTTP 200 on Render |
| **BUG-02** | PostgREST Cross-Table Filter Failure | High | Contact Search | `chatController.js` | PostgREST `.or('email.ilike,profiles.display_name.ilike')` query failed or threw 400. | PostgREST does not support cross-table OR filtering in single query syntax. | **RESOLVED** | Refactored to direct PostgreSQL SQL query with JOIN. |
| **BUG-03** | Date Fields Unclickable in Period Log UI | High | Period Tracking | `PeriodLogActivity.java`, `activity_period_log.xml` | Tapping Start Date or End Date did nothing; dates could not be selected. | `focusable="false"` and `inputType="none"` set with no `OnClickListener` or `DatePickerDialog`. | **RESOLVED** | Attached `DatePickerDialog` to both fields. |
| **BUG-04** | Hardcoded Cycle Fallback State ("4 days left") | Medium | Home Dashboard | `HomeFragment.java` | When local Room database had no logs, UI displayed hardcoded fallback (*Day 24 of 28, 4 days left*). | Fallback math lacked dynamic calculation or clear empty-state messaging. | **RESOLVED** | Dynamic cycle math calculates actual days remaining from cycle settings. |
| **BUG-05** | Missing In-Chat Message Deletion Route | Medium | Trusted Circle Chat | `chatRoutes.js`, `CircleChatActivity.java` | Long-pressing a message bubble did not offer a delete option. | Route `DELETE /api/v1/chat/messages/:id` was unmounted; long-press listener missing in Android adapter. | **RESOLVED** | Mounted route and added long-press confirmation dialog. |
| **BUG-06** | Ineffective Language Toggle (English/Hindi) | Medium | Localization | `SettingsActivity.java`, `LocaleHelper.java` | Selecting Hindi in settings did not change UI strings. | Missing `values-hi/strings.xml` resource file and missing activity recreation. | **RESOLVED** | Created `values-hi/strings.xml` and wired `recreate()`. |
| **BUG-07** | Missing Dark Mode Theme Toggle | Low | Theming / UX | `SettingsActivity.java` | No dark mode toggle switch existed in Settings. | Lack of switch in layout and missing `values-night/` colors and themes. | **RESOLVED** | Created `values-night/*` and wired `AppCompatDelegate`. |

---

## 2. Technical Debt & Residual Concerns

### 2.1 Supabase JavaScript Client vs Direct `pg.Pool` Adapter
- **Description:** Because past Supabase PostgREST API Gateway requests intermittently failed with `401 Invalid API key`, the backend was enhanced with a direct PostgreSQL connection pooler (`pg.Pool`) wrapped in a dynamic SQL adapter (`backend/src/config/supabase.js`).
- **Impact:** High reliability, but the adapter implements a custom subset of Supabase query builder methods (`select`, `insert`, `update`, `delete`, `eq`, `or`, `in`, `ilike`).
- **Recommendation:** Maintain the direct `pg.Pool` connection as the authoritative data access layer; refactor legacy controllers to clean, standard parameterized SQL queries over time.

### 2.2 Google Maps API Key in Android Manifest
- **Description:** `AndroidManifest.xml` references `@string/google_maps_key` or `com.google.android.geo.API_KEY`.
- **Impact:** On developer machines without a configured Google Cloud Maps API key, the map tile renders as a blank grid (though courier telemetry coordinates and progress percentages function properly).
- **Recommendation:** Ensure a valid Google Cloud Maps API key is provided in `local.properties` or environment variables for production releases.

### 2.3 Android 14/15 Exact Alarm Scheduling Permissions
- **Description:** Android 14 (API 34) and Android 15 restrict `SCHEDULE_EXACT_ALARM` permissions.
- **Impact:** If `AlarmManager.canScheduleExactAlarms()` returns `false`, calling `setExactAndAllowWhileIdle()` throws a `SecurityException`.
- **Implementation:** `CycleNotificationScheduler.java` includes a defensive guard checking `canScheduleExactAlarms()`, falling back to `setAndAllowWhileIdle()` or prompting the user to grant alarm permissions.

---

## 3. High-Risk Shared Files Requiring Careful Maintenance

1. `backend/src/config/db.js` & `backend/src/config/supabase.js`:
   - Central database access point for all 17 controllers. Any syntax regression breaks the entire REST API.
2. `android/app/src/main/java/com/cyclecare/api/ApiService.java`:
   - Declares all 68 Retrofit endpoints. Changing an endpoint path or parameter type requires synchronized backend changes.
3. `android/app/src/main/java/com/cyclecare/auth/LoginActivity.java`:
   - Contains sensitive Panda mascot animation timing handlers. Any refactor must preserve mascot drawables and focus listeners untouched.
