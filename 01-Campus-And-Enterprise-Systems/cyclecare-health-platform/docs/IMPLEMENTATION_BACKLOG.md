# CycleCare Application — Implementation Backlog
**Date:** 2026-10-10  
**Status:** In Progress  
**Priority Hierarchy:** P0 (Broken Core / Integrity) -> P1 (Store / Checkout / Commerce) -> P2 (Admin / Notifications) -> P3 (Partner / Chat / Circle) -> P4 (UI Polish / Localization / Tooling)

---

## Backlog Tasks

### [TASK-P0-01] Fix Backend Startup Failure: `getQuickCareItems` Missing Declaration
- **Task ID:** TASK-P0-01
- **Exact Problem:** `chatController.js` exports `getQuickCareItems` and `chatRoutes.js` mounts it, but the function definition was omitted. Running `npm test` or starting the backend server fails with `ReferenceError: getQuickCareItems is not defined`.
- **Expected Behavior:** `getQuickCareItems` is defined and returns `{ success: true, items: QUICK_CARE_ITEMS }`. All tests run without ReferenceError.
- **Files Involved:** `backend/src/controllers/chatController.js`
- **Dependencies:** None
- **Implementation Steps:**
  1. Add `const getQuickCareItems = async (req, res, next) => { try { res.json({ success: true, count: QUICK_CARE_ITEMS.length, items: QUICK_CARE_ITEMS }); } catch (err) { next(err); } };` in `chatController.js`.
  2. Verify exports.
  3. Run `npm test`.
- **Acceptance Criteria:** `npm test` executes all test suites without startup ReferenceError.
- **Automated Tests:** `npm test` (Jest)
- **Manual Verification:** Request `GET /api/v1/chat/quick-items` and check JSON output.
- **Status:** READY

---

### [TASK-P0-02] Fix Broken User Search in Circle Care & Chat
- **Task ID:** TASK-P0-02
- **Exact Problem:** `searchUsers` in `chatController.js` queries `users` with `.or('email.ilike.%q%,profiles.display_name.ilike.%q%')`. Supabase PostgREST does not support this joined column `.or()` syntax, resulting in empty search results or queries failing silently.
- **Expected Behavior:** Searching for users by full or partial name or email returns matching registered users (excluding current user), including their display name, email, profile image, and follow status.
- **Files Involved:** `backend/src/controllers/chatController.js`
- **Dependencies:** Supabase `users` and `profiles` tables.
- **Implementation Steps:**
  1. Perform two distinct queries in `searchUsers`:
     - Query 1: search `profiles` matching `display_name.ilike.%q%`
     - Query 2: search `users` matching `email.ilike.%q%`
  2. Merge user IDs, fetch user details, deduplicate, and attach follow status.
- **Acceptance Criteria:** Searching for "Aastha", "Rahul", or "demo" returns matching user objects with HTTP 200.
- **Automated Tests:** Integration test via Jest/Supertest or node curl script.
- **Manual Verification:** In Android Profile screen, enter search text and tap search icon; user card appears.
- **Status:** READY

---

### [TASK-P0-03] Implement DatePickerDialog in PeriodLogActivity
- **Task ID:** TASK-P0-03
- **Exact Problem:** In `PeriodLogActivity.java`, `etStartDate` and `etEndDate` have `focusable="false"` and `inputType="none"` in `activity_period_log.xml`, but no `OnClickListener` is set. Users cannot click or change the dates.
- **Expected Behavior:** Tapping Start Date or End Date opens an Android Material `DatePickerDialog` allowing the user to select any date formatted as `yyyy-MM-dd`.
- **Files Involved:** `android/app/src/main/java/com/cyclecare/cycle/PeriodLogActivity.java`
- **Dependencies:** Android Calendar & DatePickerDialog.
- **Implementation Steps:**
  1. Create helper method `showDatePickerDialog(EditText target)`.
  2. Attach `setOnClickListener` to `etStartDate` and `etEndDate`.
  3. Validate that end date is on or after start date before saving.
- **Acceptance Criteria:** Date picker modal opens when tapping fields; selected date populates formatted text.
- **Automated Tests:** Android instrumentation test or UI click validation.
- **Manual Verification:** Open Period Log screen on connected device, tap Start Date, pick date, save log.
- **Status:** READY

---

### [TASK-P0-04] Gender Selection at Signup & Backend Persistence
- **Task ID:** TASK-P0-04
- **Exact Problem:** Users cannot specify gender during registration; `activity_register.xml` has no gender input, and `authController.js` `register()` does not accept or write `gender` to `users` or `profiles`.
- **Expected Behavior:** Registration screen offers clear Gender selection (Female / Male / Other). When submitted, `gender` is stored in both `users` and `profiles` database tables.
- **Files Involved:**
  - `android/app/src/main/res/layout/activity_register.xml`
  - `android/app/src/main/java/com/cyclecare/auth/RegisterActivity.java`
  - `backend/src/controllers/authController.js`
- **Dependencies:** Database columns `gender` in `users` and `profiles` (already verified created).
- **Implementation Steps:**
  1. Add Gender RadioGroup / Styled Segmented Buttons in `activity_register.xml`.
  2. Read selected gender in `RegisterActivity.java` and include `"gender": selectedGender` in registration body.
  3. Update `authController.js` `register()` to insert `gender` into `users` and `profiles`.
- **Acceptance Criteria:** New user registration persists selected gender in database.
- **Automated Tests:** Backend test checking registration payload with gender.
- **Manual Verification:** Register new user in app, inspect Supabase row for saved gender.
- **Status:** READY

---

### [TASK-P0-05] Home Screen Reactive Cycle State & Fallback Refresh
- **Task ID:** TASK-P0-05
- **Exact Problem:** `HomeFragment.java` falls back to hardcoded `cycleDay=24` and `daysRemaining=4` when Room database has no logs. When logs are added, `HomeFragment` does not re-query or refresh immediately.
- **Expected Behavior:** `HomeFragment.onResume()` triggers Room DB query / LiveData observation so the cycle dial immediately reflects newly saved logs. If no logs exist, UI indicates "Log your period to get cycle predictions" rather than a misleading static 4-day luteal calculation.
- **Files Involved:**
  - `android/app/src/main/java/com/cyclecare/home/HomeFragment.java`
- **Dependencies:** Room Database `PeriodLogDao`.
- **Implementation Steps:**
  1. Move `computeRealCycleEstimation()` to execute inside `onResume()` or observe Room LiveData directly.
  2. Handle empty state gracefully with informative copy.
- **Acceptance Criteria:** Saving a period log in `PeriodLogActivity` and returning to Home immediately updates the cycle day and days remaining.
- **Manual Verification:** Save a log on device, return to Home screen, observe updated counter.
- **Status:** READY

---

### [TASK-P1-01] Message Deletion Endpoint & UI Action in Circle Chat
- **Task ID:** TASK-P1-01
- **Exact Problem:** Users cannot delete circle messages. No DELETE route exists in `chatRoutes.js`, and `ChatAdapter.java` has no delete action.
- **Expected Behavior:** Long-pressing a message allows the sender to delete it. Backend deletes from `circle_messages` and returns confirmation.
- **Files Involved:**
  - `backend/src/controllers/chatController.js`
  - `backend/src/routes/chatRoutes.js`
  - `android/app/src/main/java/com/cyclecare/api/ApiService.java`
  - `android/app/src/main/java/com/cyclecare/chat/ChatAdapter.java`
  - `android/app/src/main/java/com/cyclecare/chat/CircleChatActivity.java`
- **Dependencies:** Supabase `circle_messages` table.
- **Implementation Steps:**
  1. Add `deleteMessage` in `chatController.js` verifying `sender_id === req.user.id || req.user.role === 'ADMIN'`.
  2. Add `DELETE /messages/:id` route in `chatRoutes.js`.
  3. Add `deleteMessage(@Path("id") String id)` in `ApiService.java`.
  4. Add long-press listener in `ChatAdapter.java` to prompt deletion dialog.
- **Acceptance Criteria:** Deleting a message removes it from the conversation view and the database.
- **Manual Verification:** Send message in chat, long-press, choose Delete, verify message disappears.
- **Status:** READY

---

### [TASK-P2-01] App Language Switching (English / Hindi / Hinglish)
- **Task ID:** TASK-P2-01
- **Exact Problem:** Selecting Hindi in `SettingsActivity.java` does not change application strings because `recreate()` is not called and `values-hi/strings.xml` is missing.
- **Expected Behavior:** Selecting Hindi changes the UI language across the app and immediately recreates the screen with localized strings.
- **Files Involved:**
  - `android/app/src/main/res/values-hi/strings.xml`
  - `android/app/src/main/java/com/cyclecare/utils/LocaleHelper.java`
  - `android/app/src/main/java/com/cyclecare/profile/SettingsActivity.java`
- **Dependencies:** Android resource configuration.
- **Implementation Steps:**
  1. Create `values-hi/strings.xml` with Hindi translations of core strings.
  2. In `SettingsActivity.java`, call `activity.recreate()` after setting language.
  3. Ensure `LocaleHelper.applyLocale(this)` is invoked in `MainActivity` and base activities.
- **Acceptance Criteria:** Tapping Hindi switches UI strings to Hindi immediately.
- **Manual Verification:** Change language in Settings, verify bottom navigation and headers appear in Hindi.
- **Status:** READY

---

### [TASK-P2-02] Dark Mode Toggle in Settings
- **Task ID:** TASK-P2-02
- **Exact Problem:** Settings screen does not have a Dark Mode switch, and no `values-night/` theme resources exist.
- **Expected Behavior:** Settings screen has a Dark Mode toggle switch. Turning it on switches the theme to night mode using `AppCompatDelegate.setDefaultNightMode(MODE_NIGHT_YES)` and persists the preference.
- **Files Involved:**
  - `android/app/src/main/res/layout/activity_settings.xml`
  - `android/app/src/main/java/com/cyclecare/profile/SettingsActivity.java`
  - `android/app/src/main/res/values-night/themes.xml`
- **Dependencies:** Android DayNight theme support.
- **Implementation Steps:**
  1. Add Switch/Row in `activity_settings.xml` for "Dark Mode".
  2. Implement toggle listener in `SettingsActivity.java` that saves preference and applies `AppCompatDelegate.setDefaultNightMode()`.
  3. Create `values-night/themes.xml` with dark palette overrides.
- **Acceptance Criteria:** Toggling Dark Mode inverts app background to dark and persists across launches.
- **Manual Verification:** Toggle switch on connected phone, observe instant theme change.
- **Status:** READY

---

### [TASK-P3-01] One-Click Control Panel Launcher Script
- **Task ID:** TASK-P3-01
- **Exact Problem:** No script exists to start the local backend server and open the Admin Control Panel in the default web browser.
- **Expected Behavior:** Double-clicking `start_control_panel.bat` starts the Express backend server and launches the default web browser pointing to `http://localhost:5000/admin-panel/admin.html`.
- **Files Involved:** `start_control_panel.bat`
- **Dependencies:** Node.js, Windows command shell.
- **Implementation Steps:**
  1. Create `start_control_panel.bat` in the repository root.
  2. Script will cd to backend, start server, and trigger `start http://localhost:5000/admin-panel/admin.html`.
- **Acceptance Criteria:** Running the `.bat` file successfully launches the backend and opens the Admin dashboard in the browser.
- **Manual Verification:** Execute script from command prompt.
- **Status:** READY

---
*End of Implementation Backlog.*
