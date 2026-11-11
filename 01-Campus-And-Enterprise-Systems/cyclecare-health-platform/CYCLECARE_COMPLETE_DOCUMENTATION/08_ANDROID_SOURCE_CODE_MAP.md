# CYCLECARE — ANDROID SOURCE CODE MAP
## Java Package Structure, MVVM Architecture, Layouts, Adapters & Native Components

---

## 1. ANDROID PROJECT ARCHITECTURE & BUILD CONFIGURATION

CycleCare Android application standard **Clean MVVM (Model-View-ViewModel)** layered pattern follow karti hai:

```
android/app/src/main/
├── AndroidManifest.xml
├── java/com/cyclecare/
│   ├── MainActivity.java
│   ├── SplashActivity.java
│   ├── api/                  <-- Retrofit Interfaces, Interceptors, POJOs
│   ├── auth/                 <-- Login, Register, Session Management
│   ├── cycle/                <-- Period Logging, Calendar, AI Engine
│   ├── partner/              <-- Partner Dashboard, Reciprocal Tags, Delivery
│   ├── chat/                 <-- Real-time Messages, Care Hamper BottomSheets
│   ├── store/                <-- E-Commerce Store, Cart, Product Details
│   ├── profile/              <-- Profile Settings, Dark Mode, Social Sheet
│   ├── monitoring/           <-- App Crash Diagnostics, Telemetry
│   ├── notifications/        <-- Push Notifications, Alarms, Reminders
│   └── utils/                <-- Date Formatters, Mascot Animation Helper
└── res/
    ├── drawable/             <-- Mascot WebP/PNGs, Neumorphic Cards, Gradients
    ├── layout/               <-- 40+ XML UI Layout Files
    ├── values/               <-- colors.xml, strings.xml, themes.xml
    └── values-night/         <-- Dark Mode Theme Overrides
```

---

## 2. JAVA SOURCE CODE COMPONENT MAP (पैकेज और क्लास विवरण)

### Package: `com.cyclecare.auth` (यूजर ऑथेंटिकेशन और सेशन)

| Java Class File | Architectural Role | Core Methods & Logic |
| :--- | :--- | :--- |
| `LoginActivity.java` | View (Activity) | Handles user email/password login. Sets up Panda mascot animations (`PandaAnimationHelper`), binds `btn_login`, and provides one-tap demo login via `btn_demo_delivery_login` for courier testing. |
| `RegisterActivity.java` | View (Activity) | Handles new user onboarding. Validates password strength, gender selection (Female, Male, Non-binary), and submits payload to `POST /api/v1/auth/register`. |
| `SessionManager.java` | Data Manager / Prefs | Encapsulates `SharedPreferences`. Stores JWT token, user ID, full name, role, and logged-in boolean. Provides `isLoggedIn()`, `getToken()`, and `logout()`. |

---

### Package: `com.cyclecare.cycle` (साइकल वेलनेस, कैलेंडर और प्रिडिक्शन)

| Java Class File | Architectural Role | Core Methods & Logic |
| :--- | :--- | :--- |
| `HomeFragment.java` | View (Fragment) | Displays animated cycle circular dial, days until next cycle, current phase pill, and today's wellness tips. Coordinates with `CycleViewModel`. |
| `CalendarFragment.java` | View (Fragment) | Monthly grid calendar rendering historical periods, future predicted windows, and fertile days. Tapping a date opens date details. |
| `PeriodLogDialogFragment.java` | View (DialogFragment) | Modal sheet for logging start/end dates, flow intensity chips (Light, Medium, Heavy), cramp pain slider (1-5), and mood tags. Calls `apiService.logPeriod()`. |
| `CyclePredictionEngine.java` | Business Logic / Math | Heuristic menstrual calculation engine. Uses 3-month weighted rolling average of cycle lengths to forecast next menstruation date, follicular phase, ovulation window (Day 14 +/- 2), and luteal phase. |
| `CycleViewModel.java` | ViewModel | Exposes `LiveData<CycleState>`, `LiveData<List<PeriodLog>>`. Manages data fetching asynchronously without blocking UI main thread. |

---

### Package: `com.cyclecare.partner` (पार्टनर केयर, टैगिंग और डिलीवरी एजेंट मोड)

| Java Class File | Architectural Role | Core Methods & Logic |
| :--- | :--- | :--- |
| `PartnerActivity.java` | View (Activity) | Partner care overview. Displays partner's wellness card, reciprocal relationship badge ("Husband" / "Wife"), and action buttons for gifts and permissions. |
| `RelationshipTagDialogFragment.java` | View (DialogFragment) | Interactive dialog allowing user to select a relationship tag (e.g. "Husband"). Displays live preview of reciprocal tag ("Wife") and submits to `POST /api/v1/partner/tags`. |
| `SharingPermissionsBottomSheet.java`| View (BottomSheet) | Toggles granular permissions (`share_phase`, `share_symptoms`, `share_predictions`). Synchronizes with `PUT /api/v1/partner/permissions`. |
| `DeliveryAgentActivity.java` | View (Activity) | Dedicated courier agent workflow. Displays active delivery card for `#CC-DEMO-1001` with zero health data shown. Provides step buttons `[Accept]`, `[Pickup]`, `[Start]`, `[Simulate]`, `[Arrive]`, `[Complete]`. Prompts for 4-digit OTP. |
| `OrderTrackingActivity.java` | View (Activity) | Customer live tracking view. Renders live route map progress, timeline stepper, and secret 4-digit Delivery OTP (`4821`). |

---

### Package: `com.cyclecare.chat` (ट्रस्टेड सर्कल चैट और केयर गिफ्टिंग)

| Java Class File | Architectural Role | Core Methods & Logic |
| :--- | :--- | :--- |
| `ConversationsActivity.java` | View (Activity) | Inbox listing trusted circle partners with last message preview and unread counters. |
| `ChatActivity.java` | View (Activity) | Real-time chat stream. Supports text bubbles and rich care item cards. Implements auto-polling every 3 seconds for new incoming messages. |
| `ChatAdapter.java` | UI Adapter | RecyclerView adapter with multi-viewtype support: `TYPE_TEXT_SENT`, `TYPE_TEXT_RECEIVED`, `TYPE_CARE_ITEM_CARD`. |
| `CareItemsBottomSheet.java` | View (BottomSheet) | Care hamper picker sheet (Chocolates, Hot Water Bag, Cramp Relief Tea). Sends interactive card into chat thread via `POST /api/v1/chat/care-item`. |

---

### Package: `com.cyclecare.store` (ई-कॉमर्स वेलनेस स्टोर)

| Java Class File | Architectural Role | Core Methods & Logic |
| :--- | :--- | :--- |
| `StoreFragment.java` | View (Fragment) | Wellness product catalog with category filter tabs and 2-column product grid. |
| `ProductDetailActivity.java` | View (Activity) | Full-screen product view with description, usage guides, quantity selector, and instant checkout action. |
| `ProductAdapter.java` | UI Adapter | RecyclerView adapter displaying product image, title, price (₹), and Add to Cart action. |
| `OrderSummaryDialog.java` | View (DialogFragment) | Checkout bottom modal with price breakdown, delivery address input, payment method selection, and Place Order confirmation. |
| `OrderSuccessActivity.java` | View (Activity) | Post-checkout celebration screen with waving Panda mascot, order reference `#CC-DEMO-1001`, and button to launch `OrderTrackingActivity`. |

---

### Package: `com.cyclecare.profile` (यूजर प्रोफाइल और सेटिंग्स)

| Java Class File | Architectural Role | Core Methods & Logic |
| :--- | :--- | :--- |
| `ProfileActivity.java` | View (Activity) | Shows user avatar, cycle parameters (length, duration), social stats (Followers/Following), theme toggle (Light/Dark), and Sign Out action. |
| `FollowersBottomSheet.java` | View (BottomSheet) | Dialog displaying community circle followers and following connections. |

---

### Package: `com.cyclecare.api` (नेटवर्किंग और रेट्रोफिट लेयर)

| Java Class File | Architectural Role | Core Methods & Logic |
| :--- | :--- | :--- |
| `ApiClient.java` | Network Factory | Singleton providing configured `Retrofit` instance. Sets base URL, Gson converter, and connects custom `OkHttpClient` with 15-second timeouts. |
| `AuthInterceptor.java` | OkHttp Interceptor | Intercepts all outgoing HTTP requests. Reads JWT token from `SessionManager` and attaches header `Authorization: Bearer <token>`. |
| `ApiService.java` | Retrofit Interface | Declares 50+ annotated REST methods (`@GET`, `@POST`, `@PUT`, `@DELETE`) with RxJava/Call wrappers. |

---

## 3. XML UI LAYOUT INVENTORY (एक्सएमएल लेआउट्स का विवरण)

| XML Layout File | Associated Class | Visual Screen / Component |
| :--- | :--- | :--- |
| `activity_main.xml` | `MainActivity` | Container layout with FragmentContainerView and BottomNavigationView |
| `activity_login.xml` | `LoginActivity` | Login screen with Panda mascot, inputs, and demo delivery button |
| `activity_register.xml`| `RegisterActivity`| User signup screen with gender selector |
| `fragment_home.xml` | `HomeFragment` | Home dashboard with cycle dial, phase pill, and tips card |
| `fragment_calendar.xml`| `CalendarFragment`| Monthly grid calendar view |
| `fragment_store.xml` | `StoreFragment` | Store catalog with category chips and product grid |
| `activity_partner.xml` | `PartnerActivity` | Partner dashboard card, comfort guide, and quick action buttons |
| `activity_profile.xml` | `ProfileActivity` | User profile card, cycle metrics, and theme switcher |
| `activity_chat.xml` | `ChatActivity` | Chat window layout with RecyclerView, input bar, and gift button |
| `activity_conversations.xml`| `ConversationsActivity`| Inbox list layout with partner cards |
| `activity_product_detail.xml`| `ProductDetailActivity`| Detailed product view with large banner and quantity selector |
| `activity_order_tracking.xml`| `OrderTrackingActivity`| Live map route, status timeline stepper, and OTP box |
| `activity_delivery_agent.xml`| `DeliveryAgentActivity`| Courier dashboard with active delivery card and workflow buttons |
| `activity_order_success.xml`| `OrderSuccessActivity`| Checkout celebration layout with waving panda |
| `dialog_period_log.xml` | `PeriodLogDialogFragment`| Period logging modal with flow chips, cramp slider, and mood chips |
| `dialog_relationship_tag.xml`| `RelationshipTagDialogFragment`| Tagging modal with tag selector and live reciprocal preview |
| `sheet_sharing_permissions.xml`| `SharingPermissionsBottomSheet`| Granular privacy switches bottom sheet |
| `sheet_care_items.xml` | `CareItemsBottomSheet`| Care hamper picker bottom sheet inside chat |
| `item_chat_message_sent.xml` | `ChatAdapter` | Sent message bubble layout |
| `item_chat_message_received.xml`| `ChatAdapter` | Received message bubble layout |
| `item_care_item_card.xml` | `ChatAdapter` | Rich in-chat care hamper product card |

---

## 4. GRADLE CONFIGURATION & DEPENDENCIES (`app/build.gradle`)

```groovy
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.lifecycle:lifecycle-viewmodel:2.6.2'
    implementation 'androidx.lifecycle:lifecycle-livedata:2.6.2'

    // Networking & Serialization
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:okhttp:3.14.9'
    implementation 'com.squareup.okhttp3:logging-interceptor:3.14.9'

    // Local Storage & Caching
    implementation 'androidx.room:room-runtime:2.6.1'
    annotationProcessor 'androidx.room:room-compiler:2.6.1'

    // Background Scheduling
    implementation 'androidx.work:work-runtime:2.9.0'
}
```
