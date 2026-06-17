# ui/style_export.py

EXPORT_DARK_WIZARD_STYLE = """
#BackupWizardDialog {
    background-color: #050505;
    color: #ffffff;
}

/* 🎯 ΑΠΟΛΥΤΗ ΠΡΟΤΕΡΑΙΟΤΗΤΑ ΕΝΑΝΤΙ ΤΟΥ GLOBAL THEME ΓΙΑ ΤΑ LABELS */
#BackupWizardDialog QLabel {
    color: #A0AAB0;
    font-family: "Segoe UI";
    font-size: 13px;
    background: transparent;
}

#BackupWizardDialog QRadioButton {
    color: #A0AAB0;
    font-family: "Segoe UI";
    font-size: 13px;
    background: transparent;
}

#BackupWizardDialog QCheckBox {
    color: #A0AAB0;
    font-family: "Segoe UI";
    font-size: 13px;
    background: transparent;
}

#BackupWizardDialog QLabel#lbl_wizardTitle {
    color: #ffffff;
    font-family: "Segoe UI";
    font-size: 18px;
    font-weight: bold;
}

/* Στυλ για το κεντρικό Tab Widget */
#BackupWizardDialog QTabWidget::pane {
    border: 1px solid #252526;
    background-color: #1A1A1A;
    border-radius: 8px;
    top: -1px; /* Ενώνει οπτικά την μπάρα με το περιεχόμενο */
    padding: 15px;
    padding-top: 5px; /* Περισσότερο padding πάνω για να μην κολλάει το περιεχόμενο με την μπάρα */
}

#BackupWizardDialog QTabBar::tab {
    background-color: #252526;
    color: #8E8E93;
    border: 1px solid #2B2B2B;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    width: 170px;
    padding: 8px 0px;
    margin: 0px 2px 0px 0px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 500;
}

#BackupWizardDialog QTabBar::tab:selected {
    background-color: #1A1A1A;
    color: #2371C4; /* Το χαρακτηριστικό μπλε του FlowDeck */
    border: 1px solid #252526;
    border-bottom: 2px solid #2371C4; /* Μπλε γραμμή υπογράμμισης */
    font-weight: 600;
    width: 170px;
    margin: 0px 2px 0px 0px;
}

#BackupWizardDialog QTabBar::tab:hover {
    background-color: #2D2D30;
    color: #DBE5EB;
}

/* Λίστες με τις εφαρμογές */
#BackupWizardDialog QListWidget {
    background-color: #050505;
    border: 1px solid #3a3a42;
    border-radius: 6px;
    color: #ffffff;
    padding: 5px;
    font-family: "Segoe UI";
}

#BackupWizardDialog QListWidget::item {
    padding: 6px;
    border-bottom: 1px solid #23232a;
}

#BackupWizardDialog QListWidget::item:hover {
    background-color: #23232a;
    border-radius: 4px;
}

/* Πεδία κειμένου (Paths) */
#BackupWizardDialog QLineEdit {
    background-color: #050505;
    border: 1px solid #3a3a42;
    border-radius: 4px;
    color: #ffffff;
    padding: 6px;
    font-family: "Segoe UI";
}

/* Μπάρες Προόδου */
#BackupWizardDialog QProgressBar {
    border: 1px solid #3a3a42;
    border-radius: 4px;
    text-align: center;
    background-color: #16161a;
    color: #ffffff;
    font-weight: bold;
    font-family: "Segoe UI";
}

#BackupWizardDialog QProgressBar::chunk {
    background-color: #00b4d8;
    border-radius: 3px;
}

/* Γενικά Κουμπιά */
#BackupWizardDialog QPushButton {
    background-color: #2D2D30;
    color: #DBE5EB;
    border: 1px solid #3F3F46;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    min-height: 18px;
}

#BackupWizardDialog QPushButton:hover {
    background-color: #3a3a44;
}

#BackupWizardDialog QPushButton:pressed {
    background-color: #1e1e24;
}

/* 🎯 ΔΙΟΡΘΩΣΗ ΚΟΥΜΠΙΩΝ: Με το QPushButton μπροστά σε ΟΛΑ για να "πιάσουν" */
#BackupWizardDialog QPushButton#btn_startUsbTransfer, QPushButton#btn_createFdaArchive, QPushButton#btn_startImport {
    background-color: #2D2D30;
    color: #DBE5EB;
    border: 1px solid #3F3F46;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    min-height: 18px;
}
#BackupWizardDialog QPushButton#btn_startUsbTransfer:hover,QPushButton#btn_createFdaArchive:hover, QPushButton#btn_startImport:hover { 
    background-color: #3F3F46;
    border: 1px solid #0078D4; 
}

#BackupWizardDialog QPushButton#btn_startUsbTransfer:pressed, QPushButton#btn_createFdaArchive:pressed, QPushButton#btn_startImport:pressed {
    background-color: #1E1E1F;
}

#frm_usbApps, 
#frm_usbSpace, 
#frm_usbDest, 
#frm_fdaApps, 
#frm_fdaSavePath, 
#frm_importTools, 
#frm_importApps,
#frm_fdaCompress,
#frm_importInfo {
    border: 1px solid #2D2D30;
    border-radius: 6px;
    margin-top: 24px;
    padding: 20px 10px 10px 10px; /* Πάνω | Δεξιά | Κάτω | Αριστερά */
    background-color: #1E1E1E;
}

#BackupWizardDialog QProgressBar {
    background-color: #1A1A1A;     /* Σκούρο background για να ταιριάζει */
    border: 1px solid #333333;     /* Διακριτικό περίγραμμα */
    border-radius: 4px;            /* Στρογγυλεμένες άκρες */
    text-align: center;            /* Κεντράρισμα για το ποσοστό %, αν φαίνεται */
    color: #ffffff;
    font-weight: bold;
    max-height: 10px;               /* 🌟 Εδώ την κάνουμε λεπτή! */
}

/* --- Scrollbar handle --- */
/* Custom Σκοτεινό Στυλ για το Scrollbar της Βιβλιοθήκης */
QListWidget QScrollBar:vertical {
    border: none;
    background-color: #050505;
    width: 10px;
    margin: 0px;
}

QListWidget QScrollBar::handle:vertical {
    background-color: #333333;
    min-height: 20px;
    border-radius: 5px;
}

QListWidget QScrollBar::handle:vertical:hover {
    background-color: #2371C4; /* Ανάβει μπλε όταν το ακουμπάς */
}

QListWidget QScrollBar::add-line:vertical,
QListWidget QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Custom Σκοτεινό Στυλ για την Οριζόντια Μπάρα Κύλισης της Βιβλιοθήκης */
QListWidget QScrollBar:horizontal {
    border: none;
    background-color: #050505;
    height: 10px;
    margin: 0px;
}

QListWidget QScrollBar::handle:horizontal {
    background-color: #333333;
    min-width: 20px;
    border-radius: 5px;
}

QTextEdit QScrollBar::handle:horizontal:hover {
    background-color: #2371C4; /* Ανάβει μπλε στο hover */
}

QTextEdit QScrollBar::add-line:horizontal,
QTextEdit#dash_activityLog, QScrollArea#dash_favScrollContent QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

"""
EXPORT_LIGHT_WIZARD_STYLE = """
#BackupWizardDialog {
    background-color: #E8E8E8;
    color: #1A1A1A;
}

#BackupWizardDialog QLabel {
    color: #444444;
    font-family: "Segoe UI";
    font-size: 13px;
    background: transparent;
}

#BackupWizardDialog QRadioButton {
    color: #444444;
    font-family: "Segoe UI";
    font-size: 13px;
    background: transparent;
}

#BackupWizardDialog QCheckBox {
    color: #444444;
    font-family: "Segoe UI";
    font-size: 13px;
    background: transparent;
}

#BackupWizardDialog QLabel#lbl_wizardTitle {
    color: #1A1A1A;
    font-family: "Segoe UI";
    font-size: 18px;
    font-weight: bold;
}

#BackupWizardDialog QTabWidget::pane {
    border: 1px solid #DDDDDD;
    background-color: #FFFFFF;
    border-radius: 8px;
    top: -1px;
    padding: 15px;
    padding-top: 5px;
}

#BackupWizardDialog QTabBar::tab {
    background-color: #EEEEEE;
    color: #777777;
    border: 1px solid #DDDDDD;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    width: 170px;
    padding: 8px 0px;
    margin: 0px 2px 0px 0px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 500;
}

#BackupWizardDialog QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #2371C4;
    border: 1px solid #DDDDDD;
    border-bottom: 2px solid #2371C4;
    font-weight: 600;
    width: 170px;
    margin: 0px 2px 0px 0px;
}

#BackupWizardDialog QTabBar::tab:hover {
    background-color: #E4E4E4;
    color: #1A1A1A;
}

#BackupWizardDialog QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 6px;
    color: #1A1A1A;
    padding: 5px;
    font-family: "Segoe UI";
}

#BackupWizardDialog QListWidget::item {
    padding: 6px;
    border-bottom: 1px solid #EEEEEE;
}

#BackupWizardDialog QListWidget::item:hover {
    background-color: #F0F0F0;
    border-radius: 4px;
}

#BackupWizardDialog QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    color: #1A1A1A;
    padding: 6px;
    font-family: "Segoe UI";
}

#BackupWizardDialog QProgressBar {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    text-align: center;
    background-color: #EFEFEF;
    color: #1A1A1A;
    font-weight: bold;
    font-family: "Segoe UI";
    max-height: 10px;
}

#BackupWizardDialog QProgressBar::chunk {
    background-color: #2B9099;
    border-radius: 3px;
}

#BackupWizardDialog QPushButton {
    background-color: #EEEEEE;
    color: #1A1A1A;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    min-height: 18px;
}

#BackupWizardDialog QPushButton:hover {
    background-color: #E0E0E0;
}

#BackupWizardDialog QPushButton:pressed {
    background-color: #D5D5D5;
}

#BackupWizardDialog QPushButton#btn_startUsbTransfer, QPushButton#btn_createFdaArchive, QPushButton#btn_startImport {
    background-color: #EEEEEE;
    color: #1A1A1A;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    min-height: 18px;
}

#BackupWizardDialog QPushButton#btn_startUsbTransfer:hover, QPushButton#btn_createFdaArchive:hover, QPushButton#btn_startImport:hover {
    background-color: #E0E0E0;
    border: 1px solid #2371C4;
}

#BackupWizardDialog QPushButton#btn_startUsbTransfer:pressed, QPushButton#btn_createFdaArchive:pressed, QPushButton#btn_startImport:pressed {
    background-color: #D5D5D5;
}

#frm_usbApps,
#frm_usbSpace,
#frm_usbDest,
#frm_fdaApps,
#frm_fdaSavePath,
#frm_importTools,
#frm_importApps,
#frm_fdaCompress,
#frm_importInfo {
    border: 1px solid #DDDDDD;
    border-radius: 6px;
    margin-top: 24px;
    padding: 20px 10px 10px 10px;
    background-color: #F9F9F9;
}

/* --- Scrollbar handle --- */
QListWidget QScrollBar:vertical {
    border: none;
    background-color: #F0F0F0;
    width: 10px;
    margin: 0px;
}

QListWidget QScrollBar::handle:vertical {
    background-color: #BBBBBB;
    min-height: 20px;
    border-radius: 5px;
}

QListWidget QScrollBar::handle:vertical:hover {
    background-color: #2B9099;
}

QListWidget QScrollBar::add-line:vertical,
QListWidget QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QListWidget QScrollBar:horizontal {
    border: none;
    background-color: #F0F0F0;
    height: 10px;
    margin: 0px;
}

QListWidget QScrollBar::handle:horizontal {
    background-color: #BBBBBB;
    min-width: 20px;
    border-radius: 5px;
}

QTextEdit QScrollBar::handle:horizontal:hover {
    background-color: #2B9099;
}

QTextEdit QScrollBar::add-line:horizontal,
QTextEdit#dash_activityLog, QScrollArea#dash_favScrollContent QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

"""
