# CYCLECARE — BUGS, ERRORS & TECHNICAL LIMITATIONS
## Historical Bug Register, Root Cause Analysis, Forensic Fixes & System Boundaries

---

## 1. HISTORICAL BUG REGISTER & FORENSIC RESOLUTIONS (सुलझाई गई समस्याओं का विवरण)

Development aur integration testing ke dauran jo critical bugs discover huye the, unka root-cause analysis aur implemented forensic fixes niche document kiye gaye hain:

### Bug 1: Panda Mascot White Box Artifact in Dark Mode
- **Severity:** HIGH (Visual Defect / UI Degradation)
- **Symptom:** Jab user Dark Mode activate karta tha, Panda mascot (`panda_shy.png`) ke charo taraf ek bada white rectangular boundary box dikhta tha jo dark navy background par bohot kharab lagta tha.
- **Root Cause Analysis:** Image asset uncleaned PNG format mein thi jisme boundary pixels ka alpha channel `255` (opaque white `#FFFFFF`) tha. Android framework image ko raw render karte waqt background ke sath blend nahi kar pa raha tha.
- **Forensic Solution:**
  1. Python OpenCV aur Pillow script (`make_transparent.py`) develop ki gayi.
  2. GrabCut algorithm aur color thresholding use karke background white pixels ko 100% transparent alpha (`RGBA [0, 0, 0, 0]`) mein convert kiya gaya.
  3. Image edges par anti-aliasing feathering apply ki gayi taaki dark slate card `#1E293B` ke upar mascot 100% smooth aur natural blend ho.
- **Verified Status:** **RESOLVED** (Verified on physical device in both Light and Dark themes).

---

### Bug 2: Profile Edit Input Text Invisibility in Dark Mode
- **Severity:** HIGH (Usability Failure / Accessibility Violation)
- **Symptom:** Dark mode mein profile edit dialog ke andar text enter karte waqt characters black color mein render ho rahe the, jisse dark background par typing invisible ho jati thi.
- **Root Cause Analysis:** `dialog_edit_profile.xml` ke andar `TextInputEditText` views mein explicit `android:textColor` attribute define nahi tha, jisse OS default black color apply kar raha tha.
- **Forensic Solution:**
  1. Theme-aware color resource `color/text_primary` (`#F8FAFC` in `values-night/colors.xml`) map kiya gaya.
  2. Sabhi input fields mein `android:textColor="@color/text_primary"` aur `android:textColorHint="@color/text_secondary"` explicitly assign kiya gaya.
- **Verified Status:** **RESOLVED** (Text is now crisp white `#F8FAFC` against deep slate `#1E293B`).

---

### Bug 3: Supabase Cloud Pooler DNS Resolution `ENOTFOUND` Failure
- **Severity:** CRITICAL (System Outage / Database Disconnection)
- **Symptom:** Backend server start hote waqt crash ho jata tha with error: `getaddrinfo ENOTFOUND aws-0-ap-southeast-2.pooler.supabase.com`.
- **Root Cause Analysis:** Local ISP aur default operating system DNS servers cloud pooler ke external domain name ko resolve karne mein fail ho rahe the.
- **Forensic Solution:**
  1. `backend/src/config/db.js` mein Node.js ke native `dns` module se global recursive DNS servers inject kiye gaye:
     ```javascript
     const dns = require('dns');
     dns.setServers(['8.8.8.8', '1.1.1.1', '8.8.4.4']);
     ```
  2. Connection pool options mein `connectionTimeoutMillis: 10000` set kiya gaya.
- **Verified Status:** **RESOLVED** (100% reliable pooler connection with ~40ms ping latency).

---

### Bug 4: Asymmetric Reciprocal Relationship Inconsistency
- **Severity:** HIGH (Core Feature Logic Inconsistency)
- **Symptom:** Jab User A apne partner ko "Husband" assign karta tha, toh User B ke phone par relation update nahi hota tha ya unlinked reh jata tha.
- **Root Cause Analysis:** Database mein sirf one-way tagging table structure tha aur backend mein opposite relation determine karne ka koi domain logic module nahi tha.
- **Forensic Solution:**
  1. `RelationshipMappingService.js` develop kiya gaya jo user gender aur assigned tag ke base par reverse tag (e.g. *Husband -> Wife*, *Father -> Daughter/Son*) determine karta hai.
  2. Migration `006_reciprocal_relationships.sql` execute karke `partner_connections` table mein `reciprocal_relationship_tag` column add kiya gaya.
  3. Single atomic database transaction ke andar both users ka relationship synchronized update kiya gaya.
- **Verified Status:** **RESOLVED** (Covered by 27 automated test cases in `reciprocal_relationship.test.js`).

---

### Bug 5: Rapid Button Tapping Cart Quantity Race Condition
- **Severity:** MEDIUM (E-Commerce State Drift)
- **Symptom:** Wellness Store mein item ke `+` button ko bohot tezi se multiple times tap karne par UI counter aur server cart quantity mein drift aa jata tha.
- **Forensic Solution:**
  1. UI click listener par 300ms debounce throttle implement kiya gaya.
  2. Android Room local cart store ko authoritative state sync banaya gaya jo network response aane par UI ko reactively update karta hai.
- **Verified Status:** **RESOLVED**.

---

## 2. KNOWN TECHNICAL LIMITATIONS & SCOPE BOUNDARIES (वर्तमान सीमाएं)

Industrial honesty aur academic integrity ke tehat CycleCare ke current scope limitations niche list kiye gaye hain:

1. **Medical Device Classification Disclaimer:**
   - CycleCare ek self-care wellness tracker aur partner support application hai.
   - Yeh koi certified medical diagnostic software ya medical contraceptive calculation tool nahi hai. Application ke predictions heuristic algorithms par based hain aur PCOS/irregular cycles wale users ko professional gynecologist consult karne ka disclaimer clearly display hota hai.

2. **Live Commercial Payment Gateway:**
   - Production system mein abhi `DemoPaymentProvider` integrated hai jo realistic payment workflows aur delivery OTP verification test karne ke liye perfect hai.
   - Public commercial operations ke liye live merchant accounts (Razorpay Live Keys / Stripe Webhooks) configure karne honge.

3. **Multi-Day Offline Synchronization:**
   - App daily logs ko local cache mein store kar leti hai, lekin agar user bina internet ke 15 din tak offline rehta hai, toh reconnection par server conflict resolution rule: *"Latest timestamp wins"* apply hota hai.
