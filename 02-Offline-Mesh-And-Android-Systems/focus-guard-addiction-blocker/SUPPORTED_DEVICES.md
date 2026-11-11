# Supported Devices & Technical Limitations
**P.RN Controller by projectX²**

### 1. Supported Android Versions
- **Minimum OS Version**: Android 10 (API Level 29)
- **Target OS Version**: Android 15 (API Level 35)
- Fully tested on standard AOSP, Google Pixel, Samsung One UI, Xiaomi HyperOS/MIUI, and OnePlus OxygenOS.

### 2. Supported Browsers & Applications
Keyword and repetition detection relies on standard Android Accessibility node hierarchies (`TYPE_VIEW_TEXT_CHANGED` and `TYPE_WINDOW_CONTENT_CHANGED`).

#### Fully Supported Browsers:
- Google Chrome
- Brave Browser
- Microsoft Edge
- Samsung Internet
- Mozilla Firefox
- Opera & Vivaldi

#### Supported Search Bars & Apps:
- Instagram (Search tab & explore queries)
- YouTube (Search query box)
- X (formerly Twitter) search input
- Reddit search

#### Documented Limitations:
1. **Custom Canvas / OpenGL Rendering**: Web browsers or specialized apps that render their entire UI inside a raw OpenGL/Vulkan canvas without exposing native Android Accessibility nodes cannot be inspected via AccessibilityService.
2. **Encrypted / Private Sandboxes**: Apps that actively prohibit accessibility service inspection via Android security policies will prevent node traversal.
3. **Aggressive OEM Task Killers**: Some manufacturers (e.g. Xiaomi, Huawei) aggressively terminate long-running accessibility services. Users should enable "Battery Optimization Exemption" in the app's Permission Center.
4. **Always-On VPN Conflicts**: Android permits only one active `VpnService` at a time. If the user connects to a corporate or third-party commercial VPN, P.RN Controller's local DNS sinkhole will be temporarily paused by the Android OS.
