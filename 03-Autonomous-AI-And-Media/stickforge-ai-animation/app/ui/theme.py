"""
UI Theme and Stylesheet definition for StickForge AI.
Modern dark studio design system with high contrast and readable typography.
"""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #121316;
    color: #E2E8F0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QWidget {
    color: #E2E8F0;
    font-size: 13px;
}

/* Sidebar navigation */
#SidebarFrame {
    background-color: #18191E;
    border-right: 1px solid #27272A;
    min-width: 220px;
    max-width: 220px;
}

#SidebarHeader {
    font-size: 16px;
    font-weight: 700;
    color: #38BDF8;
    padding: 18px 16px 12px 16px;
}

QPushButton.nav-btn {
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    margin: 2px 8px;
    background-color: transparent;
    color: #94A3B8;
    font-weight: 500;
}

QPushButton.nav-btn:hover {
    background-color: #26272F;
    color: #F8FAFC;
}

QPushButton.nav-btn:checked {
    background-color: #0284C7;
    color: #FFFFFF;
    font-weight: 600;
}

/* Content Area */
#ContentArea {
    background-color: #121316;
    padding: 20px;
}

/* Cards & Panels */
QFrame.card {
    background-color: #1C1D24;
    border: 1px solid #2D3039;
    border-radius: 8px;
    padding: 16px;
}

QLabel.card-title {
    font-size: 15px;
    font-weight: 600;
    color: #F1F5F9;
    margin-bottom: 8px;
}

QLabel.card-subtitle {
    font-size: 12px;
    color: #94A3B8;
}

/* Action Buttons */
QPushButton.btn-primary {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.btn-primary:hover {
    background-color: #0369A1;
}

QPushButton.btn-primary:disabled {
    background-color: #334155;
    color: #64748B;
}

QPushButton.btn-secondary {
    background-color: #27272A;
    color: #E2E8F0;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 8px 14px;
}

QPushButton.btn-secondary:hover {
    background-color: #3F3F46;
}

QPushButton.btn-danger {
    background-color: #DC2626;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
}

QPushButton.btn-danger:hover {
    background-color: #B91C1C;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #18191F;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 8px 10px;
    color: #F8FAFC;
    selection-background-color: #0284C7;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #38BDF8;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

/* Status Bar */
QStatusBar {
    background-color: #18191E;
    border-top: 1px solid #27272A;
    color: #94A3B8;
    font-size: 12px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #121316;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #2D3039;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #3E424E;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Progress bar */
QProgressBar {
    border: 1px solid #2D3039;
    border-radius: 5px;
    background-color: #18191F;
    text-align: center;
    color: #F8FAFC;
    height: 16px;
}

QProgressBar::chunk {
    background-color: #0284C7;
    border-radius: 4px;
}
"""
