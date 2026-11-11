# CYCLECARE — UI/UX SCREEN-BY-SCREEN CATALOG
## Complete Visual Interface Inventory, Components, Layouts & Assets

---

## 1. VISUAL IDENTITY & DESIGN SYSTEM (डिज़ाइन सिस्टम और थीम)

CycleCare ka design system **Modern Neumorphic & Flat Hybrid Material 3** aesthetic par based hai. Iska primary focus clinical coldness ko avoid karke ek warm, compassionate, aur comforting experience create karna hai.

### Color Palette (कलर पैलेट)

| Role | Color Name | Hex Code | Purpose & Application |
| :--- | :--- | :--- | :--- |
| **Primary Accent** | Rose Pink | `#F43F5E` | Primary buttons, active tab indicators, high-priority badges |
| **Secondary Accent** | Soft Blush | `#FB7185` | Subtle gradient highlights, floating action buttons |
| **Background (Light)** | Cloud White | `#F8FAFC` | Daylight screen backgrounds, clean reading surface |
| **Background (Dark)** | Midnight Navy | `#0F172A` | Dark mode primary window background |
| **Surface Card (Dark)** | Deep Slate | `#1E293B` | Dark mode cards, dialog containers, bottom sheets |
| **Text Primary (Dark)** | Crisp White | `#F8FAFC` | Dark mode headers, titles, high-contrast editable text |
| **Text Secondary** | Slate Gray | `#94A3B8` | Subtitles, timestamps, placeholder text, hints |
| **Phase: Menstrual** | Crimson Rose | `#E11D48` | Menstrual bleed days highlight on calendar & dials |
| **Phase: Follicular** | Emerald Mint | `#10B981` | Energy boost & fertile preparation indicator |
| **Phase: Ovulation** | Amber Sun | `#F59E0B` | Peak ovulation & fertility window indicator |
| **Phase: Luteal** | Soft Violet | `#8B5CF6` | Pre-menstrual syndrome (PMS) & self-care phase |

---

## 2. PANDA COMPANION MASCOT SYSTEM (पांडा मैस्कॉट सिस्टम)

CycleCare mein ek intelligent, emotionally responsive **Panda Mascot** integrated hai jo app ke alag-alag states ke according dynamically react karta hai.

```
+-----------------------------------------------------------------------------------+
|                        PANDA MASCOT VISUAL POSE MATRIX                            |
+-------------------+-----------------------+---------------------------------------+
| Pose Name         | Asset File            | Emotional Context & Screen Trigger    |
+-------------------+-----------------------+---------------------------------------+
| 1. Panda Idle     | mascot_idle.png       | Neutral state, calm breathing, home   |
|                   |                       | dashboard, user reading content.      |
| 2. Panda Blink    | mascot_blink.png      | Interactive loop, natural life-like   |
|                   |                       | blinking every 3-5 seconds.           |
| 3. Panda Wave     | mascot_wave.png       | Friendly greeting, app launch,        |
|                   |                       | successful sign-in, order confirmed.  |
| 4. Panda Shy      | mascot_shy.png        | Password entry, sensitive symptom     |
|                   |                       | logging, intimate question prompt.    |
+-------------------+-----------------------+---------------------------------------+
```

### Forensic Technical Fix on Panda Assets
- **The Issue:** Dark mode mein Panda mascot ke charo taraf ek ugly rectangular white box dikhta tha kyunki JPEG/uncleaned PNG background alpha channel zero nahi tha.
- **The Solution:** Custom OpenCV & PIL transparency pipeline (`make_transparent.py`) run karke mascot ke outer pixels ko 100% transparent alpha (`RGBA [0,0,0,0]`) mein convert kiya gaya aur dark-slate container ke sath perfectly blend kiya gaya.

---

## 3. SCREEN-BY-SCREEN CATALOG (समस्त स्क्रीन और कम्पोनेंट्स का विस्तृत कैटलॉग)

Niche application ki har ek activity, fragment, aur interactive modal ka detailed technical breakdown diya gaya hai:

### Screen 1: Splash & Launch Screen
- **Java Class:** `SplashActivity.java`
- **Layout File:** `activity_splash.xml`
- **Visual Asset:** `screen_login.png`
- **Functionality:** App load hone par SharedPreferences se saved JWT session token check karta hai. Agar valid token present hai toh direct `MainActivity` par navigate karta hai; otherwise `LoginActivity` open karta hai.

---

### Screen 2: Login & Authentication Screen
- **Java Class:** `LoginActivity.java`
- **Layout File:** `activity_login.xml`
- **Visual Asset:** `assets/screen_login.png`
- **Key UI Elements:**
  - Interactive Animated Panda Mascot (Blinks naturally, waves on focus, covers eyes in Shy pose when password field is active).
  - Material TextInputEditText fields for Email & Password.
  - Primary button: `btn_login` ("Sign In to CycleCare").
  - Quick action text: "Don't have an account? Sign Up".
  - Dedicated secondary demo action button: `btn_demo_delivery_login` ("🚴 Demo Delivery Agent Mode").
- **Dark Mode Verification:** Input text and hints remain `#FFFFFF` against `#1E293B` container.

---

### Screen 3: Registration Screen
- **Java Class:** `RegisterActivity.java`
- **Layout File:** `activity_register.xml`
- **Functionality:** New user onboarding with Full Name, Email, Password, Gender selection (Female, Male, Non-binary), and Optional Partner Invite Code. Calls `POST /api/v1/auth/register`.

---

### Screen 4: Home Wellness Dashboard
- **Java Class:** `HomeFragment.java` (hosted inside `MainActivity.java`)
- **Layout File:** `fragment_home.xml`
- **Visual Asset:** `assets/screen_home_dashboard.png`
- **Key UI Elements:**
  - Circular Animated Cycle Dial: Displaying current cycle day (e.g., "Day 14") and estimated days remaining until next period.
  - Phase Badge: High-contrast pill showing current phase (`Menstrual Phase`, `Follicular Phase`, `Ovulation Window`, `Luteal Phase`).
  - Today's Wellness Tip Card: Dynamically generated self-care guidance based on current cycle phase.
  - Quick Symptom Logging FAB: Floating button to quickly open symptom logger.
  - Bottom Navigation Bar with 5 tabs: [Home], [Calendar], [Store], [Partner], [Profile].

---

### Screen 5: Cycle Calendar & Date Selection
- **Java Class:** `CalendarFragment.java`
- **Layout File:** `fragment_calendar.xml`
- **Visual Asset:** `assets/screen_cycle_calendar.png`
- **Key UI Elements:**
  - Interactive Monthly Grid Calendar with color-coded dot badges for past periods, predicted periods, and fertile windows.
  - Clicking any date opens the date picker dialog and shows historical logged symptoms for that day.

---

### Screen 6: Symptom & Period Logging Modal
- **Java Class:** `PeriodLogDialogFragment.java`
- **Layout File:** `dialog_period_log.xml`
- **Visual Asset:** `assets/screen_period_log_modal.png`
- **Key UI Elements:**
  - Date Selector (Start Date & End Date).
  - Bleeding Flow Selector Chips: [Spotting], [Light], [Medium], [Heavy].
  - Cramp Pain Intensity Slider (1 to 5 scale with descriptive labels: Mild, Manageable, Severe).
  - Mood Tag Chips: [Happy], [Calm], [Tired], [Irritable], [Anxious], [Crying Spells].
  - Intimate Notes input area.
  - Action buttons: [Cancel] and [Save Period Log]. Synchronizes immediately with `POST /api/v1/cycle/logs`.

---

### Screen 7: Wellness E-Commerce Store
- **Java Class:** `StoreFragment.java`
- **Layout File:** `fragment_store.xml`
- **Visual Asset:** `assets/screen_wellness_store.png`
- **Key UI Elements:**
  - Category Carousel: [All], [Pads & Tampons], [Cramp Relief], [Herbal Teas], [Heating Bags].
  - 2-Column Staggered Grid of Product Cards showing thumbnail, name, rating, price, and "+ Add to Cart" button.
  - Floating Shopping Cart badge with live item count and subtotal.

---

### Screen 8: Product Detail View
- **Java Class:** `ProductDetailActivity.java`
- **Layout File:** `activity_product_detail.xml`
- **Visual Asset:** `assets/screen_product_detail.png`
- **Key UI Elements:**
  - Full-width product image banner.
  - Medical & Hygiene Safety Badges (100% Organic Cotton, Dermatologically Tested, Chlorine-Free).
  - Quantity counter selector `[-] [1] [+]`.
  - Comprehensive ingredient & usage description.
  - Bottom action bar: Total Price + [Buy Now / Proceed to Cart].

---

### Screen 9: Order Summary & Checkout Dialog
- **Java Class:** `OrderSummaryDialog.java`
- **Layout File:** `dialog_order_summary.xml`
- **Visual Asset:** `assets/screen_order_dialog.png`
- **Key UI Elements:**
  - Itemized invoice breakdown: Subtotal, Delivery Fee (FREE for first 3 orders), Total Amount.
  - Delivery address input with "Use Saved Address" toggle.
  - Payment Method selection: Demo Pay (Instant Sim), UPI, Cards, Cash on Delivery.
  - Action button: [Place Order]. Triggers `POST /api/v1/orders`.

---

### Screen 10: Order Success Confirmation
- **Java Class:** `OrderSuccessActivity.java`
- **Layout File:** `activity_order_success.xml`
- **Visual Asset:** `assets/screen_order_success.png`
- **Key UI Elements:**
  - Panda Waving animation celebrating successful checkout.
  - Order Reference Number badge (e.g. `#CC-DEMO-1001`).
  - Estimated Delivery Time: "15–25 Minutes".
  - Dedicated Button: [Track Live Order].

---

### Screen 11: Real-Time Order Tracking & Courier Live Map
- **Java Class:** `OrderTrackingActivity.java`
- **Layout File:** `activity_order_tracking.xml`
- **Visual Asset:** `assets/screen_order_tracking.png`
- **Key UI Elements:**
  - Interactive Live Route Map View showing courier icon, route path, and delivery address pin.
  - Delivery OTP Card: Large prominent badge displaying secret 4-digit OTP: **4821** ("Share this OTP with courier at doorstep").
  - Order Timeline Stepper:
    1. Order Placed (Checked)
    2. Packed & Quality Checked (Checked)
    3. Out for Delivery (Active)
    4. Courier Arrived
    5. Handover Completed

---

### Screen 12: Delivery Agent Mode Dashboard
- **Java Class:** `DeliveryAgentActivity.java`
- **Layout File:** `activity_delivery_agent.xml`
- **Functionality:** Dedicated mode for courier riders.
- **Key UI Elements:**
  - Active Orders Counter: Today's Deliveries (1), In-Progress (1).
  - Assigned Delivery Card: Order ID `#CC-DEMO-1001`, Customer Name, Delivery Address.
  - Strict Privacy Guard: Zero menstrual phase or symptoms visible!
  - Step progression buttons: `[ Accept ]`, `[ Picked Up ]`, `[ Start Delivery ]`, `[ Simulate Movement ]`, `[ Arrive ]`, `[ Complete Delivery ]`.
  - Complete button triggers OTP input prompt requiring customer's `4821`.

---

### Screen 13: Partner Care Dashboard
- **Java Class:** `PartnerActivity.java`
- **Layout File:** `activity_partner.xml`
- **Visual Asset:** `assets/screen_partner_dashboard.png`
- **Key UI Elements:**
  - Connected Partner Profile Card: Name, Avatar, and Reciprocal Relationship Tag badge (e.g. "Husband" / "Wife").
  - Current Wellness Summary: Partner's cycle day, comfort advice, suggested support actions.
  - Button: [Invite Family / Partner via Code].
  - Button: [Relationship Settings] (opens reciprocal tag modal).
  - Quick Gifting action: [Send Care Hamper].

---

### Screen 14: Relationship Tagging Modal
- **Java Class:** `RelationshipTagDialogFragment.java`
- **Layout File:** `dialog_relationship_tag.xml`
- **Visual Asset:** `assets/screen_relationship_tag_modal.png`
- **Key UI Elements:**
  - Dropdown selector of primary relationship tags: [Husband], [Wife], [Boyfriend], [Girlfriend], [Father], [Mother], [Daughter], [Son], [Brother], [Sister].
  - Live Reciprocal Preview: Selecting "Husband" instantly previews: *"Partner will see you as: Wife"*.
  - Action button: [Save & Sync Relationship].

---

### Screen 15: Conversations Inbox & Chat Window
- **Java Classes:** `ConversationsActivity.java` & `ChatActivity.java`
- **Layout Files:** `activity_conversations.xml` & `activity_chat.xml`
- **Visual Assets:** `assets/screen_conversations_inbox.png` & `assets/screen_chat_messages.png`
- **Key UI Elements:**
  - Chat Bubble Stream with sender/receiver alignment, timestamps, and read receipts.
  - Care Items Gifting Sheet (`sheet_care_items.xml`): Bottom sheet with one-tap care packs (Chocolate box, Hot Water Bag, Herbal Tea).
  - In-Chat Interactive Card: When sent, renders a rich interactive card directly inside the chat thread with item picture, price, and instant [Accept & Order] button.

---

### Screen 16: Granular Sharing Permissions Sheet
- **Java Class:** `SharingPermissionsBottomSheet.java`
- **Layout File:** `sheet_sharing_permissions.xml`
- **Visual Asset:** `assets/screen_sharing_permissions.png`
- **Key UI Elements:**
  - Master Sharing Toggle [ON/OFF].
  - Individual Permission Toggles:
    - Share Current Cycle Phase [ON]
    - Share Daily Symptoms & Pain Levels [OFF]
    - Share Next Predicted Period Date [ON]
    - Share Intimate Daily Notes [OFF]
  - Synchronizes with `PUT /api/v1/partner/permissions`.

---

### Screen 17: User Profile, Settings & Social Sheet
- **Java Class:** `ProfileActivity.java`
- **Layout Files:** `activity_profile.xml` & `dialog_followers_sheet.xml`
- **Visual Assets:** `assets/screen_profile_view.png`, `assets/screen_profile_dark_mode.png`, `assets/screen_social_followers.png`
- **Key UI Elements:**
  - User Details Card: Name, Email, Age, Typical Cycle Length, Period Duration.
  - Social Community Stats: [Following] and [Followers] counters. Clicking opens the followers sheet.
  - Theme Selector Switch: [Dark Mode / Light Mode].
  - Action: [Edit Profile] and [Sign Out].

---

### Screen 18: Admin Control Panel (Web SPA)
- **File:** `backend/src/views/admin.html`
- **Visual Asset:** `assets/screen_admin_panel.png`
- **Key UI Elements:**
  - Top Navigation Bar: CycleCare Logo, Admin Session status, Real-time ping counter.
  - System Telemetry Cards: Total Users, Total Period Logs, Total Orders, Active Deliveries, Database Pool Health.
  - Interactive Action Panel: [Flush Cache], [Run Self-Test Diagnostics], [Simulate Demo Delivery], [Reset Demo Order].
  - Orders & Delivery Live Management Table.
  - Live Console Log stream displaying backend errors and database query timings.
