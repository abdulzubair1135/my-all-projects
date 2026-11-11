# ProjectFlow Intelligence — Natural मिट्टी (Earth-Tone) Design System

## 1. Design Philosophy
The ProjectFlow Intelligence design system is grounded in the organic aesthetics of **natural मिट्टी (raw earth, terracotta, alluvial clay, and limestone mineral sands)**. It avoids harsh artificial blacks, aggressive saturated neons, and overly glossy gradients in favor of tactile warmth, calm focus, and high typographic contrast.

---

## 2. Color Tokens Specification

### 2.1 Light Theme Palette

| Token Name | Hex Code | Android Resource | Role & Usage |
|---|---|---|---|
| **App Background** | `#F3EDE2` | `@color/earth_bg` | Master screen backdrop across all fragments |
| **Main Surface** | `#FBF8F1` | `@color/earth_surface` | Card containers, list items, dialog sheets |
| **Raised Surface** | `#FFFDF8` | `@color/earth_raised` | Elevated modals, dropdown menus, focused cards |
| **Primary Earth** | `#795B43` | `@color/primary_earth` | Primary action buttons, active tab indicators |
| **Deep Earth** | `#493628` | `@color/deep_earth` | App brand accents, dark headers, pressed states |
| **Muted Clay** | `#B69A78` | `@color/muted_clay` | Secondary buttons, avatars, unread markers |
| **Secondary Sand** | `#D9C9B2` | `@color/secondary_sand` | Inactive tracks, dividers, subtle fills |
| **Border / Stroke** | `#E1D6C6` | `@color/earth_border` | 1dp card borders, outline chips, table dividers |
| **Main Text** | `#30271F` | `@color/text_main` | Primary screen titles, card headings, body copy |
| **Secondary Text** | `#74695C` | `@color/text_secondary` | Subtitles, metadata, timestamps, input labels |
| **Muted Text** | `#92877A` | `@color/text_muted` | Placeholder hints, disabled states, captions |
| **Success** | `#47745A` | `@color/earth_success` | Completed tasks, positive health, verified status |
| **Warning** | `#A56A2B` | `@color/earth_warning` | Approaching deadlines, at-risk tasks, cautions |
| **Error** | `#B7473C` | `@color/earth_error` | Critical overdue tasks, failed sync, network errors |
| **Information** | `#4D718C` | `@color/earth_info` | System announcements, audit events, notes |

### 2.2 Dark Theme Palette

| Token Name | Hex Code | Android Resource | Role & Usage |
|---|---|---|---|
| **Dark Background** | `#211C17` | `@color/earth_bg` | Deep night earth backdrop |
| **Dark Main Surface** | `#2B241E` | `@color/earth_surface` | Darkened cards and navigation surfaces |
| **Dark Raised Surface**| `#342A22` | `@color/earth_raised` | High-contrast modal layers and sheets |
| **Dark Primary** | `#C3A17D` | `@color/primary_earth` | Warm golden clay for primary buttons & highlights |
| **Dark Main Text** | `#F5EEE4` | `@color/text_main` | Soft high-contrast text |
| **Dark Secondary Text**| `#C1B3A2` | `@color/text_secondary`| Secondary labels and timestamps |
| **Dark Border** | `#493A2D` | `@color/earth_border` | Subtle charcoal-clay component outlines |

---

## 3. Typography Scale & Spacing Grid

### 3.1 Type Scale
- **Screen Title:** 24–28sp, Bold, `@color/text_main`
- **Section Heading:** 18–20sp, Bold, `@color/text_main`
- **Card Title / Primary Label:** 15–16sp, SemiBold, `@color/text_main`
- **Body Text:** 14sp, Regular, `@color/text_secondary`
- **Caption / Metadata / Badges:** 11–12sp, Medium/Bold, `@color/text_muted`

### 3.2 4dp Spacing Grid
- **XS (4dp):** Badge padding, icon-text gap.
- **SM (8dp):** Inter-item spacing, chip margins.
- **MD (16dp):** Standard screen padding, card internal padding.
- **LG (24dp):** Inter-section vertical separation.
- **XL (32dp):** Screen top spacing, header separation.

---

## 4. Component Standards
1. **Cards:** Corner radius `16dp`, background `@color/earth_surface`, border `1dp` `@color/earth_border`, elevation `2dp`.
2. **Buttons:** Corner radius `12dp`, background `@color/primary_earth` with `#33FFFFFF` ripple.
3. **Filter Chips:** Pill shape with `20dp` corner radius, toggleable between `@color/primary_earth` and `@color/earth_surface`.
4. **Input Fields:** Corner radius `12dp`, internal padding `12dp 16dp`, border `1dp` `@color/earth_border`.
