# FollowTrack

> **"Know Who Follows You. Track Every Change."**

A premium, privacy-first Instagram follower and following analytics web application built with **React**, **Vite**, **TypeScript**, **Tailwind CSS**, and **IndexedDB**. 

FollowTrack analyzes official Instagram data exports directly in the user's browser with **zero password access, zero cookie collection, and zero external server transmission**.

---

## 🚀 Key Highlights & Architectural Guarantees

* **100% Client-Side In-Memory Engine**: Instagram exports (`.zip` archives or individual `.json`/`.html` files) are parsed directly in the browser via `JSZip` and native JavaScript JSON streaming.
* **Zero Credential Requirement**: Users never enter their Instagram passwords, 2FA codes, or session cookies.
* **True Unfollower Detection**: Uses high-performance `Set`-based differencing between chronological snapshots (`Previous Followers - Current Followers`). Never fabricates unfollow dates.
* **Smart Unfollow Manager**: A safe, manual curation workflow with direct profile links, batch selection, whitelisting, rate-limit safety guidance, and local audit logging.
* **Custom Snapshot History & Differencing**: Compare any two arbitrary snapshots across time to calculate new followers, lost followers, and net growth velocity.
* **Comprehensive Export Suite**: Download CSV lists for followers, following, unfollowers, mutuals, fans, and non-reciprocal follows, or generate a print-ready executive PDF report.
* **Pre-bundled Realistic Sample Data**: Test all comparison views, charts, and management tools immediately with one click.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend Framework** | React 19 + TypeScript (Strict Mode) |
| **Build Tool** | Vite 8 + `@tailwindcss/vite` |
| **Design System** | Tailwind CSS v4 (Custom SaaS Dark Palette) |
| **Icons** | Lucide React |
| **Visualizations** | Recharts (AreaChart, BarChart, PieChart) |
| **Data Processing** | JSZip, Native JSON, Set algorithms |
| **Local Storage** | Browser IndexedDB (`idb` wrapper) + LocalStorage |
| **Testing** | Vitest + React Testing Library + JSDOM |
| **Deployment Target** | Cloudflare Pages / Static Hosting |

---

## 🎨 Design System & Color Palette

* **Background**: `#0B0D12`
* **Sidebar**: `#10141D`
* **Cards**: `#151B27`
* **Card Hover**: `#1C2433`
* **Primary / Accent**: `#8B5CF6`
* **Secondary**: `#6366F1`
* **Success**: `#22C55E`
* **Danger**: `#EF4444`
* **Warning**: `#F59E0B`
* **Text**: `#F8FAFC`
* **Muted**: `#94A3B8`
* **Border**: `#252B38`

---

## 📂 Navigation & Feature Structure

1. **Landing Page**: Value proposition, architecture overview, how-it-works visual guide, and 1-click sample data loader.
2. **Dashboard**: 6 core metric cards, relationship distribution pie chart, snapshots growth trend bar chart, recent unfollowers preview, and not-following-back preview.
3. **Import Instagram Data**: Drag-and-drop zone for `.zip` or multi-file `.json`/`.html` uploads with a real-time 6-step progress pipeline.
4. **Followers**: Searchable, sortable table of all accounts following you.
5. **Following**: Searchable, sortable table of all accounts you follow.
6. **Unfollowers**: Accounts present in an earlier snapshot but absent from the current snapshot.
7. **Not Following Back**: Accounts you follow that do not follow you back.
8. **Your Fans**: Followers whom you do not follow back.
9. **Mutual Followers**: Accounts where both users follow each other.
10. **Follower Growth (Analytics)**: Area charts, reciprocity rates, fan audience share, and retention metrics.
11. **History & Snapshots**: Timeline of all exports, snapshot differencing tool (Snapshot A vs. Snapshot B), and snapshot deletion.
12. **Smart Unfollow Manager**: Guided manual unfollow interface with direct Instagram links, confirmation modals, rate-limiting advice, and local audit tags.
13. **Export Reports**: Instant CSV exports for all lists and print-ready executive PDF report generator.
14. **Application Settings**: Preferences, full database JSON backup export & restore, and complete data purge.
15. **Privacy & Security**: Deep-dive audit comparing FollowTrack against insecure bot extensions.

---

## 📖 How to Download Your Instagram Data Export

FollowTrack processes official Meta exports compliant with Instagram’s data portability guidelines:

1. Open **Instagram** (App or [instagram.com](https://www.instagram.com)).
2. Go to **Settings** &rarr; **Accounts Center** &rarr; **Your information and permissions**.
3. Select **Download your information** &rarr; **Download or transfer information**.
4. Choose **Some of your information** &rarr; Check **Followers and following**.
5. Choose **Download to device**.
6. Set **Format** to **JSON** (recommended) or HTML, and **Date range** to **All time**.
7. Once Meta prepares your file, download the `.zip` archive and drop it directly into FollowTrack!

---

## 🧪 Testing Suite

The application includes automated unit tests covering the parsing engine, set calculations, duplicate detection, and file exports:

```bash
# Run Vitest test suite
npm run test
```

### Verified Test Suites:
* `InstagramImportService.test.ts`:
  * Normalization of casing, whitespace, and `@` prefixes.
  * Username extraction from URLs.
  * Modern `followers_*.json` parsing (`string_list_data` arrays).
  * Wrapped object format parsing (`relationships_following`).
  * Deduplication of multiple records.
  * HTML export fallback parsing.
  * Full ZIP archive decompression and file resolution.
* `FollowerComparisonService.test.ts`:
  * Calculation of Not Following Back, Fans, and Mutuals.
  * Detection of true Unfollowers (`Prev - Curr`).
  * Detection of New Followers (`Curr - Prev`).
  * Dynamic comparison between any two arbitrary snapshots.
* `ExportService.test.ts`:
  * CSV generation and automatic download triggering.

---

## 💻 Local Development & Build

### Prerequisites
* Node.js v18+ (tested on Node v25)
* npm v9+

### Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run unit tests
npm run test

# Build production bundle
npm run build

# Preview production build locally
npm run preview
```

---

## 🔒 Security & Privacy Statement

* **No Server Storage**: FollowTrack has no backend database. Files are loaded via `FileReader` and `JSZip` into client RAM.
* **Zip Slip Prevention**: Relative paths inside uploaded archives are stripped to base filenames to prevent directory traversal attacks.
* **Sandboxed Storage**: Historical snapshots are stored strictly in the user's browser IndexedDB under the origin's domain boundary.
* **Safe Rate Limiting**: Discourages rapid clicking and provides guidance on Instagram's manual action thresholds.
