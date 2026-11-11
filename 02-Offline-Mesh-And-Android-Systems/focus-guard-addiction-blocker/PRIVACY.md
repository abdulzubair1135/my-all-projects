# Privacy & Security Architecture
**P.RN Controller by projectX²**

### 1. 100% Offline Architecture
P.RN Controller is fundamentally designed to never transmit data outside your physical device:
- **No Firebase**: Zero Google Firebase dependencies.
- **No Remote Backend**: No cloud servers, endpoints, or remote hosts.
- **No User Accounts**: No registration, email addresses, phone numbers, or passwords collected.
- **No Analytics / Telemetry**: No tracking SDKs, Mixpanel, Segment, or Sentry.
- **No Advertising SDKs**: Zero ad networks or tracking identifiers.

### 2. Local DNS VpnService Sandbox
The application's VPN capability operates strictly as a local loopback DNS sinkhole:
- No remote VPN tunnels are established.
- DNS packets directed to port 53 are inspected locally against your on-device blocklist.
- Unblocked traffic flows straight through your network without proxying or payload inspection.
- The app never performs HTTPS/TLS decryption or installs custom root certificates.

### 3. Accessibility Service Safeguards
When granted with explicit user consent, the Accessibility Service operates under strict boundaries:
- **Password Masking**: The service checks `AccessibilityNodeInfo.isPassword` and immediately terminates inspection for password fields.
- **No Text Logging**: Full text strings are not logged or stored. Only configured keyword matches trigger local repetition frequency counters.
- **No Message Scraping**: Private chat logs, contact books, cameras, and microphones are never accessed.

### 4. User-Controlled Data Erasure
Under **Settings -> Danger Zone**, users have one-tap complete wipe capability to erase all Room database tables, streaks, and settings permanently.
