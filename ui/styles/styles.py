# ui/styles.py

# --- Light Mode Style ---
# Φόντα: #050505 / #1A1A1A / #111111 → #F5F5F5 / #FFFFFF / #F9F9F9
# Κείμενα: #DBE5EB / #ffffff → #1A1A1A / #333333
# Muted text: #888888 → #777777
# Scrollbars: #333333 handles → #BBBBBB
# Borders: #474747 / #2A2A2A → #CCCCCC / #DDDDDD / #E0E0E0
# Inputs / GroupBoxes: σκούρα φόντα → #FFFFFF / #F9F9F9
# Console/Terminal: #00FF66 neon πράσινο → #1A7A3A (σκούρο πράσινο, αναγνώσιμο σε λευκό φόντο)
# Reset button hover: κόκκινο φόντο → #FFECEC με σκούρο κόκκινο κείμενο
# Badges: ελαφρώς πιο σκούρα χρώματα κειμένου για αντίθεση σε λευκό φόντο
# Σταθερά χρώματα (αμετάβλητα): #2B9099 (teal accent), #75ABB0, #144477, #1c5b9e — παρέμειναν ίδια παντού.

# # --- Dark Mode Style ---
# - Φόντα (Backgrounds) -
# Κύριο φόντο, console, scrollbars, ListWidget: #050505
# Tab pane, frames, ProgressBar bg:#1A1A1A
# GroupBox frames (frm_usb*, frm_fda*): #1E1E1E
# ProgressBar (γενικός): #16161a
# ListWidget item hover: #23232a
# - Κείμενο (Text) -
# Τίτλος dialog, ListWidget, QLineEdit, ProgressBar text: #ffffff
# QLabel, QRadioButton, QCheckBox (γενικά): #A0AAB0
# QPushButton κείμενο: #DBE5EB
# Tab ανενεργό κείμενο:#8E8E93
# - Accent / Interactive -
# Tab selected, scrollbar hover, button action hover border: #2371C4
# ProgressBar chunk: #00b4d8
# btn_startUsbTransfer / btn_createFdaArchive / btn_startImport hover border: #0078D4
# - Borders / Dividers -
# Tab pane border, tab border: #252526
# Tab button border: #2B2B2B
# QPushButton bg, GroupBox border: #2D2D30
# ListWidget border, QLineEdit border, ProgressBar border: #3a3a42
# QPushButton border, hover bg: #3F3F46
# Scrollbar handle, ProgressBar border (2ος κανόνας): #333333
# - Hover / Pressed States -
# Tab hover bg: #2D2D30
# QPushButton hover bg: #3a3a44
# QPushButton pressed bg: #1e1e24
# btn_start* pressed bg: #1E1E1F


MODERN_STYLE = """

/*----------------------------------------*/
/* ΓΕΝΙΚΑ           */
/*----------------------------------------*/

/* --- scrollbar handle --- */
/* Custom Σκοτεινό Στυλ για το Scrollbar της Βιβλιοθήκης */
QTextEdit QScrollBar:vertical {
    border: none;
    background-color: #050505;
    width: 10px;
    margin: 0px;
}

QTextEdit QScrollBar::handle:vertical {
    background-color: #333333;
    min-height: 20px;
    border-radius: 5px;
}

QTextEdit QScrollBar::handle:vertical:hover {
    background-color: #2B9099; /* Ανάβει μπλε όταν το ακουμπάς */
}

QTextEdit QScrollBar::add-line:vertical,
QTextEdit QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Custom Σκοτεινό Στυλ για την Οριζόντια Μπάρα Κύλισης της Βιβλιοθήκης */
QTextEdit QScrollBar:horizontal {
    border: none;
    background-color: #050505;
    height: 10px;
    margin: 0px;
}

QTextEdit QScrollBar::handle:horizontal {
    background-color: #333333;
    min-width: 20px;
    border-radius: 5px;
}

QTextEdit QScrollBar::handle:horizontal:hover {
    background-color: #2B9099; /* Ανάβει μπλε στο hover */
}

QTextEdit QScrollBar::add-line:horizontal,
QTextEdit#dash_activityLog, QScrollArea#dash_favScrollContent QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

/*--- ScrollArea---*/
QScrollArea QScrollBar:vertical {
    border: none;
    background-color: #050505;
    width: 10px;
    margin: 0px;
}

QScrollArea QScrollBar::handle:vertical {
    background-color: #333333;
    min-height: 20px;
    border-radius: 5px;
}

QScrollArea QScrollBar::handle:vertical:hover {
    background-color: #2B9099; /* Ανάβει μπλε όταν το ακουμπάς */
}

QScrollArea QScrollBar::add-line:vertical,
QScrollArea QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Custom Σκοτεινό Στυλ για την Οριζόντια Μπάρα Κύλισης της Βιβλιοθήκης */
QScrollArea QScrollBar:horizontal {
    border: none;
    background-color: #050505;
    height: 10px;
    margin: 0px;
}

QScrollArea QScrollBar::handle:horizontal {
    background-color: #333333;
    min-width: 20px;
    border-radius: 5px;
}

QScrollArea QScrollBar::handle:horizontal:hover {
    background-color: #2B9099; /* Ανάβει μπλε στο hover */
}

QScrollArea QScrollBar::add-line:horizontal,
QScrollArea QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

/*----------------------------------------*/
/* MENU & NAVIGATION (ΠΛΑΪΝΟ)             */
/*----------------------------------------*/

/* Κεντρικό Παράθυρο */
QMainWindow {
    background-color: #050505;
}

/* Το κουτί των γραμμάτων (Μόνιμα σκούρο) */
QFrame[objectName^="navTitleFrame"] {
    background-color: #1A1A1A;
    border: none;
}

/* Τα ΝΕΑ FRAMES των εικονιδίων (Η "βάση" τους) */
QFrame[objectName^="navIconFrame"] {
    background-color: #DBE5EB;
    border-left: 5px solid transparent; 
}

/* HOVER EFFECT στα εικονίδια του μενού */
QFrame#navIconFrame_Dashboard:hover, 
QFrame#navIconFrame_MyApps:hover, 
QFrame#navIconFrame_Wizard:hover, 
QFrame#navIconFrame_Settings:hover,
QFrame#navIconFrame_About:hover {
    background-color: #CCD6DC;
}

/* ACTIVE EFFECT: Όταν ένα Frame πλοήγησης είναι επιλεγμένο (Μπλε Γραμμή) */
QFrame[objectName^="navIconFrame"][active="true"] {
    background-color: #BBC5CB;
    border-left: 5px solid #2B9099; /* Η ΜΠΛΕ ΓΡΑΜΜΗ */
}

/* Τα Labels των εικονιδίων πρέπει να είναι διαφανή για να φαίνεται το Frame από πίσω */
QLabel[objectName^="navIcon"] {
    background-color: transparent;
}

/* Τα Γράμματα (Καμία αλλαγή, σταθερά χρώματα) */
QLabel[objectName^="navTitle"] {
    color: #DBE5EB;
    font-weight: bold;
    /* font-size: 13px; */
    background: transparent;
}

QLabel[objectName^="navSub"] {
    color: #DBE5EB;
    /* font-size: 10px; */
    background: transparent;
}

/* Status Bar */
QStatusBar {
    background-color: #1A1A1A;
    border-top: 1px solid #474747;
}

/* Menu Bar */
QMenuBar {
    background-color: #1A1A1A;
    border-bottom: 1px solid #474747;
    color: #DBE5EB; /* Προσθήκη για να φαίνονται τα γράμματα του μενού */
}

/* navTitleFrame */
QFrame[objectName^="navTitleFrame"] {
    background-color: #1A1A1A;
    border: none;
    border-right: 1px solid #474747;
}

/*----------------------------------------*/
/* DASHBOARD PAGE                         */
/*----------------------------------------*/

/* Το κεντρικό Frame του Header (Καλωσόρισμα) */
QFrame#frameDash_Header {
    background-color: #1A1A1A;
    border-radius: 10px;
    padding: 13px;
    margin-bottom: 10px;
}

/* Ο μεγάλος τίτλος Welcome back */
QLabel#lblDash_Welcome {
    color: #ffffff;
    font-size: 22px;
    font-weight: bold;
    background: transparent;
}

/* Η ημερομηνία κάτω από το καλωσόρισμα και το tips*/
QLabel#lblDash_Date, QLabel#lblDash_Tip {
    color: #888888;
    font-size: 12px;
    background: transparent;
}

/* Τα πλακίδια/κάρτες των Στατιστικών */
QFrame[objectName^="dashStatCard_"] {
    background-color: #222222;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 10px 15px;
}

/* Τα κείμενα Τίτλος μέσα στις κάρτες στατιστικών */
QLabel#lblDash_StatAppsTitle, QLabel#lblDash_DiscSpaceTitle {
    color: #DBE5EB; 
    font-size: 12px;
    font-weight: bold;
    background: transparent;
}

/* Τα κείμενα πληροφοριών μέσα στις κάρτες στατιστικών */
QLabel#lblDash_StatAppsSize, QLabel#lblDash_DiscSpaceSize {
    color: #888888; 
    font-size: 12px;
    font-weight: bold;
    background: transparent;
}


/* Τα κεντρικά Frames των δύο στηλών (Αγαπημένα & Activity) */
QFrame#frameDash_Favorites, QFrame#frameDash_Activity {
    background-color: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
    padding: 5px;
}

QFrame#dash_tipsLog {
    height: 100px;
    background-color: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
    padding: 5px; 
}

/* Οι τίτλοι των ενοτήτων "Quick Launch" , "Recent Activity" , "News/Tips" και "Νουμερο Εφαρμογών" */
QLabel#lblDash_FavTitle, QLabel#lblDash_ActivityTitle, QLabel#lblDash_TipTitle {
    color: #DBE5EB;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
    padding-bottom: 5px;
}

/* Ο τίτλος του "Νουμερο Εφαρμογών" */
QLabel#lblDash_StatAppsCount {
    color: #DBE5EB;
    font-size: 16px;
    font-weight: bold;
    background: transparent;
}

/* Το activity log σε στυλ terminal/κονσόλας */
QTextEdit#dash_activityLog {
    /* ackground-color: #050505; */
    background-color: transparent;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    color: #00FF66; /* Neon Hacker πράσινο */
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 10px;
}

/* Το εξωτερικό περίβλημα της μπάρας (το "κανάλι") */
QProgressBar#diskProgressBar {
    background-color: #1A1A1A;     /* Σκούρο background για να ταιριάζει */
    border: 1px solid #333333;     /* Διακριτικό περίγραμμα */
    border-radius: 4px;            /* Στρογγυλεμένες άκρες */
    text-align: center;            /* Κεντράρισμα για το ποσοστό %, αν φαίνεται */
    color: #ffffff;
    font-weight: bold;
    max-height: 10px;               /* 🌟 Εδώ την κάνουμε λεπτή! */
}

/* Το εσωτερικό μέρος που γεμίζει (το "chunk") */
QProgressBar#diskProgressBar::chunk {
    background-color: #2B9099;     /* Το ίδιο Modern Μπλε των κουμπιών σου */
    border-radius: 3px;            /* Στρογγυλεμένες άκρες και στο γέμισμα */
}

/* Κάνουμε διάφανα τα ακριβή widgets του κώδικά σου */
QScrollArea#dash_favScrollContent {
    background-color: #1A1A1A;
    border: none;
}

/* Στοχεύουμε το εσωτερικό widget με το ακριβές όνομά του */
QWidget#scrollAreaWidgetContents {
    background-color: #1A1A1A;
    border: none;
}

/* Στοχεύουμε την κάρτα με βάση το Object Name της */
QFrame[objectName="appCard"] {
    background-color: #1A1A1A !important;
    border: 1px solid #333333 !important;
    border-radius: 8px !important;
}

/* Εφέ όταν περνάει το ποντίκι πάνω από την κάρτα */
QFrame[objectName="appCard"]:hover {
    border: 1px solid #2B9099 !important;
    background-color: #222222 !important;
}

/* Τίτλος εφαρμογής μέσα στην κάρτα */
QLabel#appCard_Title {
    color: #ffffff !important;
    font-size: 12px; 
    font-weight: bold !important;
    background: transparent !important;
    border: none !important;
}

/* Έκδοση εφαρμογής */
QLabel#appCard_Version {
    color: #888888 !important;
    font-size: 11px !important;
    background: transparent !important;
    border: none !important;
}

/* Το κουμπί Launch */
QPushButton#appCard_LaunchBtn {
    background-color: #2B9099 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 6px !important;
    font-weight: bold !important;
}

QPushButton#appCard_LaunchBtn:hover {
    background-color: #1c5b9e !important;
}






/*----------------------------------------*/
/* WIZARD                                 */
/*----------------------------------------*/

/* Κεφαλίδα (Header) */
QFrame#wizard_headerFrame {
    background-color: #1A1A1A;
    border-radius: 10px;
    padding: 13px;
    margin-bottom: 10px;
}

QLabel#wizard_lblTitle {
    color: #ffffff;
    font-size: 22px;
    font-weight: bold;
    background: transparent;
}

/* Το μικρότερο κείμενο κάτω από τον τίτλο */
QLabel#wizard_lblSubTitle {
    color: #888888;
    font-size: 12px;
    background: transparent;
}


/* Τα labels της σελίδας wizard */
QLabel#lblCategory_wizard, QLabel#lblAppName_wizard, QLabel#lblPath_wizard, QLabel#lblConsole_wizard {
    /*color: #DBE5EB;*/
    color: rgb(219,229,235);
    font-size: 13px;
    font-weight: bold;
}

/* Πλαίσιο Drag & Drop (Το μεγάλο τετράγωνο αρχείων) */
QFrame#DnDframe {
    background-color: #1A1A1A;
    border: 2px dashed #474747; /* Διακεκομμένη γραμμή */
    border-radius: 10px;
}

/* Όταν περνάς το ποντίκι ή σέρνεις αρχείο πάνω από το Drag & Drop */
QFrame#DnDframe:hover {
    border: 2px dashed #2B9099; /* Γίνεται μπλε */
    background-color: #1f1f1f;
}

/* Γράμματα/Μηνύματα μέσα στο πλαίσιο Drag & Drop */
QLabel#dropLabel {
    color: #DBE5EB; 
    font-size: 14px;
    font-weight: bold;
}

/* Πεδία κειμένου εισαγωγής (Inputs για Όνομα και Path) */
QLineEdit#appNameInput, QLineEdit#filePathInput {
    background-color: #1A1A1A;
    border: 1px solid #474747;
    border-radius: 5px;
    padding: 8px;
    color: #DBE5EB; /* Το ανοιχτόχρωμο των γραμμάτων σου */
    font-size: 13px;
}

/* Όταν κάνεις κλικ μέσα στα Inputs για να πληκτρολογήσεις */
QLineEdit#appNameInput:focus, QLineEdit#filePathInput:focus {
    border: 1px solid #2B9099; /* Μπλε περίγραμμα */
}

/* Dropdown Μενού επιλογής κατηγορίας (Category ComboBox) */
QComboBox#categoryCombo {
    background-color: #1A1A1A;
    border: 1px solid #474747;
    border-radius: 5px;
    padding: 8px;
    color: #DBE5EB;
    font-size: 13px;
}

/* Απόκρυψη του προεπιλεγμένου βέλους των Windows στο ComboBox */
QComboBox#categoryCombo::drop-down {
    border: none; 
}

/* Η αναδυόμενη λίστα επιλογών του ComboBox */
QComboBox#categoryCombo QAbstractItemView {
    background-color: #1A1A1A;
    color: #DBE5EB;
    selection-background-color: #2B9099; /* Μπλε όταν διαλέγεις κατηγορία */
}

/* Κουμπί Αναζήτησης Τοπικού Αρχείου (Browse) */
QPushButton#browseButton {
    background-color: #2A2A2A;
    border: 1px solid #474747;
    border-radius: 5px;
    padding: 8px 15px;
    color: #DBE5EB;
    font-weight: bold;
}

QPushButton#browseButton:hover {
    background-color: #3A3A3A;
}

/* Το μεγάλο κεντρικό Κουμπί Εγκατάστασης του Wizard */
QPushButton#installButton {
    background-color: #2B9099; /* Το μπλε σου */
    border: none;
    border-radius: 5px;
    padding: 12px;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#installButton:hover {
    background-color: #75ABB0; /* Πιο σκούρο μπλε στο hover */
}

QPushButton#installButton:pressed {
    background-color: #144477;
}

/* Το Label που εμφανίζει το Status των ενεργειών */
QLabel#statusLabel {
    color: #DBE5EB;
    font-size: 13px;
    padding: 5px;
    background: transparent;
}


/* Το Live Log / Console σε στυλ Terminal (Hacker προβολή) */
QTextEdit#consoleEdit {
    background-color: #050505;
    border: 1px solid #474747;
    border-radius: 10px;
    color: #00FF66; /* Το κλασικό neon πράσινο της κονσόλας */
    font-family: 'Consolas', 'Courier New', monospace; /* Μονοκόμματα γράμματα κώδικα */
    font-size: 12px;
    padding: 12px;
}

/* Δεξί Panel Πληροφοριών της Εφαρμογής (Sidebar) */
QFrame#frameWiz_Info, QFrame#frameWiz_InsertApp, QFrame#frameWiz_Console, QFrame#frameWiz_AutoInstall  {
    background-color: #1A1A1A;
    border: 1px solid #474747;
    border-radius: 10px;
}

/* Το Label του τίτλου "Πληροφορίες Εφαρμογής..." μέσα στο Sidebar */
QFrame#frameWiz_Info QLabel#sidebarTitle {
    color: #DBE5EB;
    font-size: 14px;
    font-weight: bold;
    border: none;
    background: transparent;
    padding-left: 10px;
    padding-top: 5px;
}

/* Το Label που φιλοξενεί το Εικονίδιο μέσα στο Sidebar */
QFrame#frameWiz_Info QLabel#sidebarIcon{
    border: none;
    background: transparent;
    margin: 10px 0px;
}

QLabel#sidebarIcon {
    font-size: 50px;
}

/* Το πλαίσιο κειμένου (Rich Text HTML) της περιγραφής μέσα στο Sidebar */
QFrame#frameWiz_Info QTextEdit#sidebarDesc {
    background-color: #050505; /* Σκούρο μαύρο όπως η κονσόλα */
    border: 1px solid #333333; /* Διακριτικό περίγραμμα */
    border-radius: 5px;
    color: #DBE5EB;
    font-size: 13px;
    padding: 10px;
}

/* Το Κουμπί επίσκεψης της Ιστοσελίδας μέσα στο Sidebar */
QPushButton#sidebarUrlBtn {
    background-color: #2B9099; /* Το μπλε σου */
    border: none;
    border-radius: 5px;
    padding: 5px;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#sidebarUrlBtn:hover {
    background-color: #75ABB0; /* Πιο σκούρο μπλε στο hover */
}

QPushButton#sidebarUrlBtn:pressed {
    background-color: #144477;
}

/* 3. Το Κάτω Δεξιά Panel των Δημοφιλών Εφαρμογών (Store) */
QFrame#popularAppsFrame {
    background-color: #1A1A1A;
    border: 1px solid #474747;
    border-radius: 10px;
}

/* Τα κουμπιά/πλακίδια των εφαρμογών μέσα στο Grid (π.χ. KeePass, VLC)
QFrame#popularAppsFrame QPushButton, QFrame#popularAppsFrame QToolButton {
    background-color: #222222;
    border: 1px solid #474747;
    border-radius: 8px;
    color: #DBE5EB;
    padding: 10px;
    font-size: 12px;
    font-weight: bold;
}

/* Hover εφέ: Όταν περνάει το ποντίκι πάνω από μια δημοφιλή εφαρμογή */
QFrame#popularAppsFrame QPushButton:hover, QFrame#popularAppsFrame QToolButton:hover {
    background-color: #2B9099; /* Ανάβει με το μπλε σου */
    border: 1px solid #2B9099;
    color: #ffffff;
}


/*----------------------------------------*/
/* MY APPS LIBRARY (ΒΙΒΛΙΟΘΗΚΗ)           */
/*----------------------------------------*/

/* Κεφαλίδα (Header) */
QFrame#myApps_headerFrame {
    background-color: #1A1A1A;
    border-radius: 10px;
    padding: 13px;
    margin-bottom: 10px;
}

QLabel#myApps_lblTitle {
    color: #ffffff;
    font-size: 22px;
    font-weight: bold;
    background: transparent;
}

/* Το μικρότερο κείμενο κάτω από τον τίτλο */
QLabel#myApps_lblStats {
    color: #888888;
    font-size: 12px;
    background: transparent;
}

/* Μπάρα Εργαλείων (Toolbar) */
QFrame#myApps_toolbarFrame {
    background: transparent;
    padding: 10px 0px;
}

/* Το κουτί της Αναζήτησης */
QLineEdit#myApps_searchBox {
    background-color: #1A1A1A;
    border: 1px solid #474747;
    border-radius: 6px;
    padding: 8px 12px;
    color: #DBE5EB;
    font-size: 13px;
    min-width: 300px;
}

QLineEdit#myApps_searchBox:focus {
    border: 1px solid #2B9099;
}

/* Τα dropdowns και τα κουμπιά της Μπάρας Εργαλείων */
QComboBox#myApps_sortCombo, 
QPushButton#myApps_viewBtn, 
QPushButton#myApps_updateAllBtn {
    background-color: #1A1A1A;
    border: 1px solid #474747;
    border-radius: 6px;
    padding: 8px 15px;
    color: #DBE5EB;
    font-size: 13px;
    font-weight: bold;
}

QComboBox#myApps_sortCombo::drop-down {
    border: none;
}

QComboBox#myApps_sortCombo QAbstractItemView {
    background-color: #1A1A1A;
    color: #DBE5EB;
    selection-background-color: #2B9099;
}

QPushButton#myApps_viewBtn:hover, 
QPushButton#myApps_updateAllBtn:hover,
QComboBox#myApps_sortCombo:hover {
    background-color: #222222;
    border: 1px solid #555555;
}

/* Ο μεγάλος Καμβάς (Scroll Area) */
QScrollArea#myApps_scrollArea {
    background-color: transparent;
    border: none;
}

/* Το εσωτερικό περιεχόμενο του Scroll Area που κρατάει τις κάρτες */
QWidget#myApps_scrollContent {
    background-color: transparent;
    border: 1px solid #C1C1C1;
    border-radius: 12px;
}

/* ---------------------------------------------------------------- */
/* ΤΑ ΠΛΑΚΙΔΙΑ ΤΩΝ ΕΦΑΡΜΟΓΩΝ (Δημιουργούνται δυναμικά από τον κώδικα) */
/* ---------------------------------------------------------------- */

/* Το φόντο της κάθε Κάρτας/App */
QFrame.AppCard {
    background-color: #111111;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
    /*padding: 5px 15px 15px 15px;  Μειώνουμε μόνο το πάνω padding (top) σε 5px */
}

QFrame.AppCard:hover {
    border: 1px solid #3A3A3A;
    background-color: #141414;
}

/* Το Label που θα δείχνει το μεγάλο Εικονίδιο */
QLabel.AppIconLabel {
    border: none;
    background: transparent;
}

/* Το Όνομα της Εφαρμογής μέσα στην κάρτα */
QLabel.AppNameLabel {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
    background: transparent;
}

/* Η Έκδοση (Version) */
QLabel.AppVersionLabel {
    color: #888888;
    font-size: 12px;
    background: transparent;
}

/* Το μεγάλο Μπλε Κουμπί Launch */
QPushButton.AppLaunchButton {
    background-color: #2B9099;
    border: none;
    border-radius: 6px;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    padding: 8px;
}

QPushButton.AppLaunchButton:hover {
    background-color: #75ABB0;
}

/* Το μικρό τετράγωνο κουμπί των επιλογών (...) */
QPushButton.AppOptionsButton {
    background-color: #222222;
    border: 1px solid #474747;
    border-radius: 6px;
    color: #DBE5EB;
    font-weight: bold;
    font-size: 14px;
    padding: 6px;
}

QPushButton.AppOptionsButton:hover {
    background-color: #333333;
}

/* Τα Badges Κατάστασης (Latest Version / Update Available) */
QLabel.BadgeLatest {
    background-color: rgba(76, 175, 80, 0.15); /* Απαλό διάφανο πράσινο */
    color: #4CAF50;
    border: 1px solid rgba(76, 175, 80, 0.3);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
}

QLabel.BadgeUpdate {
    background-color: rgba(255, 152, 0, 0.15); /* Απαλό διάφανο πορτοκαλί/κίτρινο */
    color: #FF9800;
    border: 1px solid rgba(255, 152, 0, 0.3);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
}

QLabel.BadgeManual {
    /* background-color: #555555; */
    background-color: rgba(224, 224, 224, 0.15);
    color: #FFFFFF;
    border: 1px solid rgba(224, 224, 224, 0.3);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: bold;
}

/* ============================================================================
   🎨 MODERN DARK STYLE FOR FLOWDECK SETTINGS
   ============================================================================ */

/* Το κεντρικό Tab Widget */
QTabWidget#settingsTabWidget {
    background-color: #121212;
    border: none;
}

/* Η πίσω μπάρα που κρατάει τα Tab Buttons */
QTabWidget#settingsTabWidget::pane {
    border: 1px solid #252526;
    background-color: #1A1A1A;
    border-radius: 8px;
    top: -1px; /* Ενώνει οπτικά την μπάρα με το περιεχόμενο */
    padding: 15px;
}

QTabWidget#settingsTabWidget::tab-bar {
    alignment: left;
}

/* Τα κουμπιά των Tabs (Ανενεργά) */
QTabBar::tab {
    background-color: #252526;
    color: #8E8E93;
    border: 1px solid #2B2B2B;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
    font-weight: 500;
}

/* Tabs όταν τα ακουμπάει ο κέρσορας (Hover) */
QTabBar::tab:hover {
    background-color: #2D2D30;
    color: #DBE5EB;
}

/* Το ενεργό Tab (Επιλεγμένο) */
QTabBar::tab:selected {
    background-color: #1A1A1A;
    color: #2B9099; /* Το χαρακτηριστικό μπλε του FlowDeck */
    border: 1px solid #252526;
    border-bottom: 2px solid #2B9099; /* Μπλε γραμμή υπογράμμισης */
    font-weight: 600;
    min-width: 105px;
}

/* ============================================================================
   📦 GROUP BOXES (Κατηγορίες ρυθμίσεων μέσα στα Tabs)
   ============================================================================ */
QGroupBox#group_installation, 
QGroupBox#group_systemOptions, 
QGroupBox#group_theme, 
QGroupBox#group_updateFreq, 
QGroupBox#group_updateStatus, 
QGroupBox#group_language, 
QGroupBox#group_dataMaintenance,
QGroupBox#group_systemStatistics,
QGroupBox#group_systemInfo,
QGroupBox#group_systemMostused,
QGroupBox#group_systemBigapps {
    border: 1px solid #2D2D30;
    border-radius: 6px;
    margin-top: 24px;
    padding-top: 20px;
    padding-left: 10px;
    padding-right: 10px;
    padding-bottom: 10px;
    background-color: #1E1E1E;
}

/* Ο τίτλος του κάθε GroupBox */
QGroupBox#group_installation::title, 
QGroupBox#group_systemOptions::title, 
QGroupBox#group_theme::title, 
QGroupBox#group_updateFreq::title, 
QGroupBox#group_updateStatus::title, 
QGroupBox#group_language::title, 
QGroupBox#group_dataMaintenance::title, 
QGroupBox#group_systemStatistics::title, 
QGroupBox#group_systemInfo::title, 
QGroupBox#group_systemMostused::title, 
QGroupBox#group_systemBigapps::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    top: 5px;
    padding: 0 5px;
    color: #2B9099; 
    font-family: "Segoe UI", sans-serif;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ============================================================================
   🔘 BUTTONS (Κουμπιά μέσα στα Settings)
   ============================================================================ */

/* Τα απλά κουμπιά (Browse, Backup, Logs κλπ) */
QPushButton#btn_browsePath,
QPushButton#btn_openPath,
QPushButton#btn_clearActivityLog,
QPushButton#btn_backupApps,
QPushButton#btn_scanAndRepair,
QPushButton#btn_resetDefaults,
QPushButton#btn_checkUpdatesNow {
    background-color: #2D2D30;
    color: #DBE5EB;
    border: 1px solid #3F3F46;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    min-height: 18px;
}

QPushButton#btn_browsePath:hover,
QPushButton#btn_openPath:hover,
QPushButton#btn_clearActivityLog:hover,
QPushButton#btn_backupApps:hover,
QPushButton#btn_scanAndRepair:hover,
QPushButton#btn_resetDefaults:hover,
QPushButton#btn_checkUpdatesNow:hover {
    background-color: #3F3F46;
    border: 1px solid #2B9099;
}

QPushButton#btn_browsePath:pressed,
QPushButton#btn_openPath:pressed,
QPushButton#btn_clearActivityLog:pressed,
QPushButton#btn_backupApps:pressed,
QPushButton#btn_scanAndRepair:pressed,
QPushButton#btn_resetDefaults:pressed,
QPushButton#btn_checkUpdatesNow:pressed {
    background-color: #1E1E1F;
}

/* ⚠️ Ειδικό στυλ για το κουμπί ολικής επαναφοράς (Κόκκινο Hover) */
QPushButton#btn_resetDefaults:hover {
    background-color: #A80000;
    border: 1px solid #E81123;
    color: #FFFFFF;
}

/* ============================================================================
   💾 ΤΟ ΜΕΓΑΛΟ ΚΟΥΜΠΙ: ΑΠΟΘΗΚΕΥΣΗ ΡΥΘΜΙΣΕΩΝ
   ============================================================================ */
QPushButton#btn_saveSettings {
    background-color: #2B9099;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 12px 24px;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
    font-weight: 600;
    min-height: 25px;
}

QPushButton#btn_saveSettings:hover {
    background-color: #75ABB0;
}

QPushButton#btn_saveSettings:pressed {
    background-color: #2B9099;
}

/* ============================================================================
   Inputs (LineEdits, ComboBoxes, CheckBoxes)
   ============================================================================ */
QLineEdit#txt_installPath {
    background-color: #121212;
    color: #DBE5EB;
    border: 1px solid #3F3F46;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
}

QLineEdit#txt_installPath:focus {
    border: 1px solid #2B9099;
}

QComboBox#combo_themeSelect,
QComboBox#combo_updateFrequency,
QComboBox#combo_languageSelect {
    background-color: #2D2D30;
    color: #DBE5EB;
    border: 1px solid #3F3F46;
    border-radius: 4px;
    padding: 6px 30px 6px 10px;
    min-width: 150px;
}

QComboBox#combo_themeSelect:hover,
QComboBox#combo_updateFrequency:hover,
QComboBox#combo_languageSelect:hover {
    border: 1px solid #2B9099;
}

QCheckBox#chk_startOnBoot,
QCheckBox#chk_minimizeToTray,
QCheckBox#chk_updateToStart,
QCheckBox#chk_enableSilentUpdater {
    color: #A0AAB0;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
}

/* ============================================================================
   Labels
   ============================================================================ */

/* Labels για την κατάσταση */
QLabel#lbl_lastCheckTime,
QLabel#system_lbl_1,
QLabel#system_lbl_2,
QLabel#system_lbl_3,
QLabel#system_lbl_4,
QLabel#system_lbl_5,
QLabel#system_lbl_6,
QLabel#system_lbl_7,
QLabel#system_lbl_8,
QLabel#system_lbl_9,
QLabel#system_lbl_10,
QLabel#system_lbl_11,
QLabel#system_lbl_12,
QLabel#system_lbl_13,
QLabel#system_lbl_14,
QLabel#system_lbl_15,
QLabel#system_lbl_16,
QLabel#system_lbl_17,
QLabel#system_lbl_inst_app,
QLabel#system_lbl_update,
QLabel#system_lbl_favorites,
QLabel#system_lbl_size,
QLabel#system_lbl_dbcheck,
QLabel#system_lbl_scoopver,
QLabel#system_ldl_version,
QLabel#system_lbl_most1,
QLabel#system_lbl_most2,
QLabel#system_lbl_most3,
QLabel#system_lbl_most4,
QLabel#system_lbl_most5,
QLabel#system_lbl_space1,
QLabel#system_lbl_space2,
QLabel#system_lbl_space3,
QLabel#system_lbl_space4,
QLabel#system_lbl_space5 {
    color: #A0AAB0;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
}





"""

LIGHT_STYLE = """
/*----------------------------------------*/
/* ΓΕΝΙΚΑ                                 */
/*----------------------------------------*/

/* --- scrollbar handle --- */
QTextEdit QScrollBar:vertical {
    border: none;
    background-color: #F0F0F0;
    width: 10px;
    margin: 0px;
}

QTextEdit QScrollBar::handle:vertical {
    background-color: #BBBBBB;
    min-height: 20px;
    border-radius: 5px;
}

QTextEdit QScrollBar::handle:vertical:hover {
    background-color: #2B9099;
}

QTextEdit QScrollBar::add-line:vertical,
QTextEdit QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QTextEdit QScrollBar:horizontal {
    border: none;
    background-color: #F0F0F0;
    height: 10px;
    margin: 0px;
}

QTextEdit QScrollBar::handle:horizontal {
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

/*--- ScrollArea---*/
QScrollArea QScrollBar:vertical {
    border: none;
    background-color: #F0F0F0;
    width: 10px;
    margin: 0px;
}

QScrollArea QScrollBar::handle:vertical {
    background-color: #BBBBBB;
    min-height: 20px;
    border-radius: 5px;
}

QScrollArea QScrollBar::handle:vertical:hover {
    background-color: #2B9099;
}

QScrollArea QScrollBar::add-line:vertical,
QScrollArea QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollArea QScrollBar:horizontal {
    border: none;
    background-color: #F0F0F0;
    height: 10px;
    margin: 0px;
}

QScrollArea QScrollBar::handle:horizontal {
    background-color: #BBBBBB;
    min-width: 20px;
    border-radius: 5px;
}

QScrollArea QScrollBar::handle:horizontal:hover {
    background-color: #2B9099;
}

QScrollArea QScrollBar::add-line:horizontal,
QScrollArea QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

/*----------------------------------------*/
/* MENU & NAVIGATION (ΠΛΑΪΝΟ)             */
/*----------------------------------------*/

QMainWindow {
    background-color: #E8E8E8;
}

QFrame[objectName^="navTitleFrame"] {
    background-color: #2B9099;
    border: none;
}

QFrame[objectName^="navIconFrame"] {
    background-color: #FFFFFF;
    border-left: 5px solid transparent;
}

QFrame#navIconFrame_Dashboard:hover,
QFrame#navIconFrame_MyApps:hover,
QFrame#navIconFrame_Wizard:hover,
QFrame#navIconFrame_Settings:hover,
QFrame#navIconFrame_About:hover {
    background-color: #E8F6F7;
}

QFrame[objectName^="navIconFrame"][active="true"] {
    background-color: #D0ECEE;
    border-left: 5px solid #2B9099;
}

QLabel[objectName^="navIcon"] {
    background-color: transparent;
}

QLabel[objectName^="navTitle"] {
    color: #FFFFFF;
    font-weight: bold;
    background: transparent;
}

QLabel[objectName^="navSub"] {
    color: #FFFFFF;
    background: transparent;
}

QStatusBar {
    background-color: #E8E8E8;
    border-top: 1px solid #CCCCCC;
}

QMenuBar {
    background-color: #E8E8E8;
    border-bottom: 1px solid #CCCCCC;
    color: #1A1A1A;
}

QFrame[objectName^="navTitleFrame"] {
    background-color: #2B9099;
    border: none;
    border-right: 1px solid #1F7077;
}

/*----------------------------------------*/
/* DASHBOARD PAGE                         */
/*----------------------------------------*/

QFrame#frameDash_Header {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 13px;
    margin-bottom: 10px;
}

QLabel#lblDash_Welcome {
    color: #1A1A1A;
    font-size: 22px;
    font-weight: bold;
    background: transparent;
}

QLabel#lblDash_Date, QLabel#lblDash_Tip {
    color: #777777;
    font-size: 12px;
    background: transparent;
}

QFrame[objectName^="dashStatCard_"] {
    background-color: #FFFFFF;
    border: 1px solid #DDDDDD;
    border-radius: 8px;
    padding: 10px 15px;
}

QLabel#lblDash_StatAppsTitle, QLabel#lblDash_DiscSpaceTitle {
    color: #1A1A1A;
    font-size: 12px;
    font-weight: bold;
    background: transparent;
}

QLabel#lblDash_StatAppsSize, QLabel#lblDash_DiscSpaceSize {
    color: #777777;
    font-size: 12px;
    font-weight: bold;
    background: transparent;
}

QFrame#frameDash_Favorites, QFrame#frameDash_Activity {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 5px;
}

QFrame#dash_tipsLog {
    height: 100px;
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 5px;
}

QLabel#lblDash_FavTitle, QLabel#lblDash_ActivityTitle, QLabel#lblDash_TipTitle {
    color: #1A1A1A;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
    padding-bottom: 5px;
}

QLabel#lblDash_StatAppsCount {
    color: #1A1A1A;
    font-size: 16px;
    font-weight: bold;
    background: transparent;
}

QTextEdit#dash_activityLog {
    background-color: transparent;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    color: #1A7A3A;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 10px;
}

QProgressBar#diskProgressBar {
    background-color: #EFEFEF;
    border: 1px solid #DDDDDD;
    border-radius: 4px;
    text-align: center;
    color: #1A1A1A;
    font-weight: bold;
    max-height: 10px;
}

QProgressBar#diskProgressBar::chunk {
    background-color: #2B9099;
    border-radius: 3px;
}

QScrollArea#dash_favScrollContent {
    background-color: #FFFFFF;
    border: none;
}

QWidget#scrollAreaWidgetContents {
    background-color: #FFFFFF;
    border: none;
}

QFrame[objectName="appCard"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DDDDDD !important;
    border-radius: 8px !important;
}

QFrame[objectName="appCard"]:hover {
    border: 1px solid #2B9099 !important;
    background-color: #F0FAFA !important;
}

QLabel#appCard_Title {
    color: #1A1A1A !important;
    font-size: 12px;
    font-weight: bold !important;
    background: transparent !important;
    border: none !important;
}

QLabel#appCard_Version {
    color: #777777 !important;
    font-size: 11px !important;
    background: transparent !important;
    border: none !important;
}

QPushButton#appCard_LaunchBtn {
    background-color: #2B9099 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 6px !important;
    font-weight: bold !important;
}

QPushButton#appCard_LaunchBtn:hover {
    background-color: #1c5b9e !important;
}


/*----------------------------------------*/
/* WIZARD                                 */
/*----------------------------------------*/

QFrame#wizard_headerFrame {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 13px;
    margin-bottom: 10px;
}

QLabel#wizard_lblTitle {
    color: #1A1A1A;
    font-size: 22px;
    font-weight: bold;
    background: transparent;
}

QLabel#wizard_lblSubTitle {
    color: #777777;
    font-size: 12px;
    background: transparent;
}

QLabel#lblCategory_wizard, QLabel#lblAppName_wizard, QLabel#lblPath_wizard, QLabel#lblConsole_wizard {
    color: rgb(30, 40, 50);
    font-size: 13px;
    font-weight: bold;
}

QFrame#DnDframe {
    background-color: #FFFFFF;
    border: 2px dashed #AAAAAA;
    border-radius: 10px;
}

QFrame#DnDframe:hover {
    border: 2px dashed #2B9099;
    background-color: #F0FAFA;
}

QLabel#dropLabel {
    color: #333333;
    font-size: 14px;
    font-weight: bold;
}

QLineEdit#appNameInput, QLineEdit#filePathInput {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    padding: 8px;
    color: #1A1A1A;
    font-size: 13px;
}

QLineEdit#appNameInput:focus, QLineEdit#filePathInput:focus {
    border: 1px solid #2B9099;
}

QComboBox#categoryCombo {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    padding: 8px;
    color: #1A1A1A;
    font-size: 13px;
}

QComboBox#categoryCombo::drop-down {
    border: none;
}

QComboBox#categoryCombo QAbstractItemView {
    background-color: #FFFFFF;
    color: #1A1A1A;
    selection-background-color: #2B9099;
}

QPushButton#browseButton {
    background-color: #EEEEEE;
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    padding: 8px 15px;
    color: #1A1A1A;
    font-weight: bold;
}

QPushButton#browseButton:hover {
    background-color: #E0E0E0;
}

QPushButton#installButton {
    background-color: #2B9099;
    border: none;
    border-radius: 5px;
    padding: 12px;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#installButton:hover {
    background-color: #75ABB0;
}

QPushButton#installButton:pressed {
    background-color: #144477;
}

QLabel#statusLabel {
    color: #333333;
    font-size: 13px;
    padding: 5px;
    background: transparent;
}

QTextEdit#consoleEdit {
    background-color: #F7F7F7;
    border: 1px solid #CCCCCC;
    border-radius: 10px;
    color: #1A7A3A;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 12px;
}

QFrame#frameWiz_Info, QFrame#frameWiz_InsertApp, QFrame#frameWiz_Console, QFrame#frameWiz_AutoInstall {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 10px;
}

QFrame#frameWiz_Info QLabel#sidebarTitle {
    color: #1A1A1A;
    font-size: 14px;
    font-weight: bold;
    border: none;
    background: transparent;
    padding-left: 10px;
    padding-top: 5px;
}

QFrame#frameWiz_Info QLabel#sidebarIcon {
    border: none;
    background: transparent;
    margin: 10px 0px;
}

QLabel#sidebarIcon {
    font-size: 50px;
}

QFrame#frameWiz_Info QTextEdit#sidebarDesc {
    background-color: #F7F7F7;
    border: 1px solid #DDDDDD;
    border-radius: 5px;
    color: #1A1A1A;
    font-size: 13px;
    padding: 10px;
}

QPushButton#sidebarUrlBtn {
    background-color: #2B9099;
    border: none;
    border-radius: 5px;
    padding: 5px;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#sidebarUrlBtn:hover {
    background-color: #75ABB0;
}

QPushButton#sidebarUrlBtn:pressed {
    background-color: #144477;
}

QFrame#popularAppsFrame {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 10px;
}

/*----------------------------------------*/
/* MY APPS LIBRARY (ΒΙΒΛΙΟΘΗΚΗ)           */
/*----------------------------------------*/

QFrame#myApps_headerFrame {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 13px;
    margin-bottom: 10px;
}

QLabel#myApps_lblTitle {
    color: #1A1A1A;
    font-size: 22px;
    font-weight: bold;
    background: transparent;
}

QLabel#myApps_lblStats {
    color: #777777;
    font-size: 12px;
    background: transparent;
}

QFrame#myApps_toolbarFrame {
    background: transparent;
    padding: 10px 0px;
}

QLineEdit#myApps_searchBox {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 6px;
    padding: 8px 12px;
    color: #1A1A1A;
    font-size: 13px;
    min-width: 300px;
}

QLineEdit#myApps_searchBox:focus {
    border: 1px solid #2B9099;
}

QComboBox#myApps_sortCombo,
QPushButton#myApps_viewBtn,
QPushButton#myApps_updateAllBtn {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 6px;
    padding: 8px 15px;
    color: #1A1A1A;
    font-size: 13px;
    font-weight: bold;
}

QComboBox#myApps_sortCombo::drop-down {
    border: none;
}

QComboBox#myApps_sortCombo QAbstractItemView {
    background-color: #FFFFFF;
    color: #1A1A1A;
    selection-background-color: #2B9099;
}

QPushButton#myApps_viewBtn:hover,
QPushButton#myApps_updateAllBtn:hover,
QComboBox#myApps_sortCombo:hover {
    background-color: #F0F0F0;
    border: 1px solid #AAAAAA;
}

QScrollArea#myApps_scrollArea {
    background-color: transparent;
    border: none;
}

QWidget#myApps_scrollContent {
    background-color: transparent;
    border: 1px solid #C1C1C1;
    border-radius: 12px;
}

QFrame.AppCard {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
}

QFrame.AppCard:hover {
    border: 1px solid #AAAAAA;
    background-color: #F9F9F9;
}

QLabel.AppIconLabel {
    border: none;
    background: transparent;
}

QLabel.AppNameLabel {
    color: #1A1A1A;
    font-size: 15px;
    font-weight: bold;
    background: transparent;
}

QLabel.AppVersionLabel {
    color: #777777;
    font-size: 12px;
    background: transparent;
}

QPushButton.AppLaunchButton {
    background-color: #2B9099;
    border: none;
    border-radius: 6px;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    padding: 8px;
}

QPushButton.AppLaunchButton:hover {
    background-color: #75ABB0;
}

QPushButton.AppOptionsButton {
    background-color: #EEEEEE;
    border: 1px solid #CCCCCC;
    border-radius: 6px;
    color: #333333;
    font-weight: bold;
    font-size: 14px;
    padding: 6px;
}

QPushButton.AppOptionsButton:hover {
    background-color: #E0E0E0;
}

QLabel.BadgeLatest {
    background-color: rgba(76, 175, 80, 0.12);
    color: #2E7D32;
    border: 1px solid rgba(76, 175, 80, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
}

QLabel.BadgeUpdate {
    background-color: rgba(255, 152, 0, 0.12);
    color: #E65100;
    border: 1px solid rgba(255, 152, 0, 0.35);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
}

QLabel.BadgeManual {
    background-color: rgba(100, 100, 100, 0.1);
    color: #444444;
    border: 1px solid rgba(100, 100, 100, 0.25);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: bold;
}

/* ============================================================================
   SETTINGS
   ============================================================================ */

QTabWidget#settingsTabWidget {
    background-color: #F5F5F5;
    border: none;
}

QTabWidget#settingsTabWidget::pane {
    border: 1px solid #DDDDDD;
    background-color: #FFFFFF;
    border-radius: 8px;
    top: -1px;
    padding: 15px;
}

QTabWidget#settingsTabWidget::tab-bar {
    alignment: left;
}

QTabBar::tab {
    background-color: #EEEEEE;
    color: #777777;
    border: 1px solid #DDDDDD;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
    font-weight: 500;
}

QTabBar::tab:hover {
    background-color: #E4E4E4;
    color: #1A1A1A;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #2B9099;
    border: 1px solid #DDDDDD;
    border-bottom: 2px solid #2B9099;
    font-weight: 600;
    min-width: 105px;
}

/* ============================================================================
   GROUP BOXES
   ============================================================================ */
QGroupBox#group_installation,
QGroupBox#group_systemOptions,
QGroupBox#group_theme,
QGroupBox#group_updateFreq,
QGroupBox#group_updateStatus,
QGroupBox#group_language,
QGroupBox#group_dataMaintenance,
QGroupBox#group_systemStatistics,
QGroupBox#group_systemInfo,
QGroupBox#group_systemMostused,
QGroupBox#group_systemBigapps {
    border: 1px solid #DDDDDD;
    border-radius: 6px;
    margin-top: 24px;
    padding-top: 20px;
    padding-left: 10px;
    padding-right: 10px;
    padding-bottom: 10px;
    background-color: #F9F9F9;
}

QGroupBox#group_installation::title,
QGroupBox#group_systemOptions::title,
QGroupBox#group_theme::title,
QGroupBox#group_updateFreq::title,
QGroupBox#group_updateStatus::title,
QGroupBox#group_language::title,
QGroupBox#group_dataMaintenance::title,
QGroupBox#group_systemStatistics::title,
QGroupBox#group_systemInfo::title,
QGroupBox#group_systemMostused::title,
QGroupBox#group_systemBigapps::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    top: 5px;
    padding: 0 5px;
    color: #2B9099;
    font-family: "Segoe UI", sans-serif;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ============================================================================
   BUTTONS (Settings)
   ============================================================================ */

QPushButton#btn_browsePath,
QPushButton#btn_openPath,
QPushButton#btn_clearActivityLog,
QPushButton#btn_backupApps,
QPushButton#btn_scanAndRepair,
QPushButton#btn_resetDefaults,
QPushButton#btn_checkUpdatesNow {
    background-color: #EEEEEE;
    color: #1A1A1A;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    min-height: 18px;
}

QPushButton#btn_browsePath:hover,
QPushButton#btn_openPath:hover,
QPushButton#btn_clearActivityLog:hover,
QPushButton#btn_backupApps:hover,
QPushButton#btn_scanAndRepair:hover,
QPushButton#btn_resetDefaults:hover,
QPushButton#btn_checkUpdatesNow:hover {
    background-color: #E0E0E0;
    border: 1px solid #2B9099;
}

QPushButton#btn_browsePath:pressed,
QPushButton#btn_openPath:pressed,
QPushButton#btn_clearActivityLog:pressed,
QPushButton#btn_backupApps:pressed,
QPushButton#btn_scanAndRepair:pressed,
QPushButton#btn_resetDefaults:pressed,
QPushButton#btn_checkUpdatesNow:pressed {
    background-color: #D5D5D5;
}

QPushButton#btn_resetDefaults:hover {
    background-color: #FFECEC;
    border: 1px solid #E81123;
    color: #A80000;
}

/* ============================================================================
   SAVE BUTTON
   ============================================================================ */
QPushButton#btn_saveSettings {
    background-color: #2B9099;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 12px 24px;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
    font-weight: 600;
    min-height: 25px;
}

QPushButton#btn_saveSettings:hover {
    background-color: #75ABB0;
}

QPushButton#btn_saveSettings:pressed {
    background-color: #2B9099;
}

/* ============================================================================
   Inputs (LineEdits, ComboBoxes, CheckBoxes)
   ============================================================================ */
QLineEdit#txt_installPath {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
}

QLineEdit#txt_installPath:focus {
    border: 1px solid #2B9099;
}

QComboBox#combo_themeSelect,
QComboBox#combo_updateFrequency,
QComboBox#combo_languageSelect {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 6px 30px 6px 10px;
    min-width: 150px;
}

QComboBox#combo_themeSelect:hover,
QComboBox#combo_updateFrequency:hover,
QComboBox#combo_languageSelect:hover {
    border: 1px solid #2B9099;
}

QCheckBox#chk_startOnBoot,
QCheckBox#chk_minimizeToTray,
QCheckBox#chk_updateToStart,
QCheckBox#chk_enableSilentUpdater {
    color: #444444;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
}

/* ============================================================================
   Labels
   ============================================================================ */

QLabel#lbl_lastCheckTime,
QLabel#system_lbl_1,
QLabel#system_lbl_2,
QLabel#system_lbl_3,
QLabel#system_lbl_4,
QLabel#system_lbl_5,
QLabel#system_lbl_6,
QLabel#system_lbl_7,
QLabel#system_lbl_8,
QLabel#system_lbl_9,
QLabel#system_lbl_10,
QLabel#system_lbl_11,
QLabel#system_lbl_12,
QLabel#system_lbl_13,
QLabel#system_lbl_14,
QLabel#system_lbl_15,
QLabel#system_lbl_16,
QLabel#system_lbl_17,
QLabel#system_lbl_inst_app,
QLabel#system_lbl_update,
QLabel#system_lbl_favorites,
QLabel#system_lbl_size,
QLabel#system_lbl_dbcheck,
QLabel#system_lbl_scoopver,
QLabel#system_ldl_version,
QLabel#system_lbl_most1,
QLabel#system_lbl_most2,
QLabel#system_lbl_most3,
QLabel#system_lbl_most4,
QLabel#system_lbl_most5,
QLabel#system_lbl_space1,
QLabel#system_lbl_space2,
QLabel#system_lbl_space3,
QLabel#system_lbl_space4,
QLabel#system_lbl_space5 {
    color: #666666;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
}



"""

DIALOG_STYLE = """
QDialog, QMessageBox, QInputDialog, QMessageBox QLabel, QDialog QLabel {
    background-color: #1A1A1A !important;
    color: #ffffff !important;
}
QDialog QLabel, QMessageBox QLabel, QInputDialog QLabel {
    color: #DBE5EB !important;
    font-size: 13px;
    background-color: transparent !important;
}
QLineEdit, QComboBox, QListView, QAbstractItemView {
    background-color: #050505;
    border: 1px solid #474747;
    border-radius: 4px;
    color: #DBE5EB;
    padding: 6px;
}
QPushButton {
    background-color: #2A2A2A;
    border: 1px solid #474747;
    border-radius: 4px;
    padding: 8px 15px;
    color: #DBE5EB;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3A3A3A;
}
/* Το μπλε κουμπί "Επόμενο" */
QPushButton#primaryButton {
    background-color: #2B9099;
    border: none;
    color: white;
}
QPushButton#primaryButton:hover {
    background-color: #75ABB0;
}

/* QProgressBar styling for Dark Mode Dialogs */
QProgressBar {
    background-color: #050505;
    border: 1px solid #474747;
    border-radius: 4px;
    text-align: center;
    color: #ffffff !important;
    font-weight: bold;
    min-height: 18px;
}
QProgressBar::chunk {
    background-color: #2B9099;
    border-radius: 3px;
}

"""
DIALOG_LIGHT_STYLE = """
QDialog, QMessageBox, QInputDialog, QMessageBox QLabel, QDialog QLabel {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
}
QDialog QLabel, QMessageBox QLabel, QInputDialog QLabel {
    color: #333333 !important;
    font-size: 13px;
    background-color: transparent !important;
}
QLineEdit, QComboBox, QListView, QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    color: #1A1A1A;
    padding: 6px;
}
QPushButton {
    background-color: #EEEEEE;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px 15px;
    color: #1A1A1A;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #E0E0E0;
}
/* Το μπλε κουμπί "Επόμενο" */
QPushButton#primaryButton {
    background-color: #2B9099;
    border: none;
    color: white;
}
QPushButton#primaryButton:hover {
    background-color: #75ABB0;
}

/* QProgressBar styling for Light Mode Dialogs */
QProgressBar {
    background-color: #F0F0F0;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    text-align: center;
    color: #1A1A1A !important;
    font-weight: bold;
    min-height: 18px;
}
QProgressBar::chunk {
    background-color: #2B9099;
    border-radius: 3px;
}

"""

ACTIVITY_THEMES = {
    "Modern Dark": {
        "style": MODERN_STYLE,
        "arrow": "icons/arrow_down_white.png",
        "timeline_text": "#DBE5EB",
        "timeline_time": "#888888"
    },
    "Modern Light": {
        "style": LIGHT_STYLE,
        "arrow": "icons/arrow_down_black.png",
        "timeline_text": "#1D1D1D",
        "timeline_time": "#626262"
    }
}

TIPS_THEMES = {
    "Modern Dark": "#DBE5EB",
    "Modern Light": "#626262"
}
