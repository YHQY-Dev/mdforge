APP_STYLESHEET = """
QMainWindow {
    background-color: #eef2f8;
}
QWidget#centralRoot, QStackedWidget, QScrollArea#settingsScroll > QWidget > QWidget {
    background-color: transparent;
}
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0f2744, stop:1 #0a1628);
    border: none;
    border-right: 1px solid rgba(255,255,255,0.06);
}
QLabel#brandTitle {
    color: #f8fafc;
    font-size: 18pt;
    font-weight: 800;
    letter-spacing: 0.5px;
}
QLabel#brandSubtitle {
    color: #94a3b8;
    font-size: 9pt;
    padding-bottom: 16px;
}
QPushButton#navBtn {
    background: transparent;
    color: #cbd5e1;
    border: none;
    border-radius: 12px;
    padding: 12px 14px;
    text-align: left;
    font-size: 11pt;
    margin: 2px 0;
    min-height: 40px;
}
QPushButton#navBtn:hover {
    background-color: rgba(255, 255, 255, 0.07);
    color: #ffffff;
}
QPushButton#navBtn:checked {
    background-color: rgba(59, 130, 246, 0.95);
    color: white;
    font-weight: 600;
}
QFrame#contentCard {
    background-color: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
}
QStackedWidget#pageStack {
    background: transparent;
}
QLabel#cardTitle {
    font-size: 22pt;
    font-weight: 800;
    color: #0f172a;
}
QLabel#cardSubtitle {
    color: #64748b;
    font-size: 10pt;
    line-height: 1.4;
}
QLabel#activeParserBadge {
    color: #1d4ed8;
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 20px;
    padding: 8px 14px;
    font-size: 9pt;
    font-weight: 600;
    min-height: 20px;
}
QFrame#sectionFrame {
    background-color: #f8fafc;
    border: 1px solid #e8edf4;
    border-radius: 14px;
}
QLabel#sectionTitle {
    font-size: 11pt;
    font-weight: 700;
    color: #334155;
}
QLabel#hintLabel {
    color: #64748b;
    font-size: 9pt;
}
QScrollArea#pageScroll {
    background: transparent;
    border: none;
}
QLineEdit, QComboBox, QListWidget {
    background-color: #ffffff;
    border: 1px solid #d1d9e6;
    border-radius: 10px;
    padding: 8px 12px;
    min-height: 36px;
    font-size: 10pt;
    selection-background-color: #3b82f6;
}
QComboBox {
    padding-right: 28px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid #d1d9e6;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}
QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}
QComboBox QAbstractItemView {
    min-width: 160px;
    padding: 4px;
    border: 1px solid #d1d9e6;
    selection-background-color: #dbeafe;
}
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #d1d9e6;
    border-radius: 10px;
    padding: 10px 14px;
    selection-background-color: #3b82f6;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QListWidget:focus {
    border: 2px solid #3b82f6;
    background-color: #ffffff;
}
QListWidget#fileList {
    background-color: #ffffff;
}
QPushButton#cancelBtn {
    background-color: #ffffff;
    color: #b91c1c;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 600;
    font-size: 10pt;
    min-height: 44px;
    min-width: 72px;
}
QPushButton#cancelBtn:hover {
    background-color: #fef2f2;
    border-color: #f87171;
}
QPushButton#cancelBtn:disabled {
    color: #94a3b8;
    border-color: #e2e8f0;
    background-color: #f8fafc;
}
QPushButton#primaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2563eb, stop:1 #0891b2);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 700;
    font-size: 11pt;
    min-height: 44px;
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1d4ed8, stop:1 #0e7490);
}
QPushButton#primaryBtn:disabled {
    background: #94a3b8;
}
QPushButton#secondaryBtn {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 600;
    font-size: 10pt;
    min-height: 36px;
    min-width: 72px;
}
QPushButton#secondaryBtn:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}
QPushButton#ghostBtn {
    background: transparent;
    color: #64748b;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 10pt;
    min-height: 36px;
    min-width: 64px;
}
QPushButton#ghostBtn:hover {
    background-color: #f1f5f9;
    color: #334155;
}
QProgressBar#mainProgress {
    border: none;
    border-radius: 8px;
    background-color: #e2e8f0;
    text-align: center;
    min-height: 14px;
    max-height: 14px;
    color: #475569;
    font-size: 9pt;
}
QProgressBar#mainProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3b82f6, stop:1 #06b6d4);
    border-radius: 8px;
}
QTextEdit#logPanel {
    background-color: #0f172a;
    color: #e2e8f0;
    border: 1px solid #1e293b;
    border-radius: 12px;
    font-family: "Cascadia Code", "Consolas", "Microsoft YaHei UI", monospace;
    font-size: 9pt;
    padding: 10px;
}
QFrame#parserCard, QFrame#modeCard {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 14px;
    min-height: 100px;
}
QFrame#modeCard {
    min-width: 140px;
}
QFrame#parserCard:hover, QFrame#modeCard:hover {
    border-color: #93c5fd;
}
QFrame#parserCard[selected="true"], QFrame#modeCard[selected="true"] {
    border-color: #2563eb;
    background-color: #eff6ff;
}
QLabel#modeCardTitle {
    font-size: 12pt;
    font-weight: 700;
    color: #0f172a;
}
QLabel#modeCardBadge {
    font-size: 8pt;
    color: #0369a1;
    background-color: #e0f2fe;
    border-radius: 6px;
    padding: 3px 8px;
}
QLabel#modeCardDesc {
    font-size: 9pt;
    color: #64748b;
}
QLabel#modeHint {
    color: #475569;
    font-size: 9pt;
    padding: 4px 2px 0 2px;
}
QLabel#parserCardTitle {
    font-size: 12pt;
    font-weight: 700;
    color: #0f172a;
}
QLabel#parserCardBadge {
    font-size: 8pt;
    color: #1d4ed8;
    background-color: #dbeafe;
    border-radius: 6px;
    padding: 3px 8px;
}
QLabel#parserCardDesc {
    font-size: 9pt;
    color: #64748b;
}
QLabel#parserStatus {
    background-color: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 12px;
    padding: 14px 16px;
    color: #0c4a6e;
    font-size: 10pt;
}
QFrame#settingsPanel {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
}
QLabel#panelHint {
    color: #0369a1;
    font-size: 9pt;
}
QLabel#savePolicyHint {
    color: #64748b;
    font-size: 9pt;
    padding: 4px 2px;
}
QScrollBar:vertical {
    width: 10px;
    background: transparent;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 5px;
    min-height: 24px;
}
"""
