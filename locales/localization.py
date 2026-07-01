# GR: Αυτό το αρχείο διαχειρίζεται το λεξικό μεταφράσεων και την εναλλαγή γλώσσας σε όλη την εφαρμογή.
# EN: This file manages the translation dictionary and language switching across the entire application.

# locales/localization.py

# Εδώ ορίζουμε το λεξικό με όλες τις μεταφράσεις για το FlowDeck
TRANSLATIONS = {
    "el": {

        # ------------------------------------------------------------------------#
        # --------------------------- Main Page ----------------------------------#
        # ------------------------------------------------------------------------#

        "tray_title": "FlowDeck",
        "tray_message": "Η εφαρμογή συνεχίζει να εκτελείται στο παρασκήνιο.",
        "tray_menu_show": "Εμφάνιση",
        "tray_menu_exit": "Έξοδος",
        "nav_dashboard": "Αρχική",
        "nav_wizard": "Οδηγός",
        "nav_settings": "Ρυθμίσεις",
        "tray_menu_exit": "Έξοδος",
        "nav_my_apps": "Εφαρμογές μου",
        "nav_sub_dashboard": "Κεντρική προβολή",
        "nav_sub_wizard": "Προσθήκη νέων εφαρμογών",
        "nav_sub_settings": "Συντήρηση και εργαλεία",
        "nav_sub_my_apps": "Κατηγορίες και οργάνωση",
        "nav_about": "Σχετικά",
        "nav_sub_about": "Πληροφορίες & μνεία",
        "about_window_title": "Σχετικά με το FlowDeck",
        "about_description": "Διαχειριστής φορητών (portable) εφαρμογών για Windows.",
        "about_7zip_mention": "Περιλαμβάνει το 7-Zip (7za.exe) για τη διαχείριση αρχείων.",
        "about_scoop_mention": "Βασίζεται στο οικοσύστημα του Scoop για portable εφαρμογές.",
        "about_chocolatey_mention": "Υποστηρίζει το Chocolatey για εγκατάσταση συστημικών εφαρμογών.",
        "about_version_label": "Έκδοση",
        "about_license_label": "Άδεια χρήσης",
        "about_license_value": "GNU GPLv3",
        "about_github": "GitHub",
        "no_updates_title": "Ενημέρωση",
        "no_updates_text": "Έχετε ήδη την τελευταία έκδοση της εφαρμογής!",

        # ------------------------------------------------------------------------#
        # --------------------------- Dashboard Page -----------------------------#
        # ------------------------------------------------------------------------#

        "dash_welcome": "Καλώς ήρθες, Χρήστη!",
        "dash_activity_title": "Πρόσφατη Δραστηριότητα",
        "dash_tips_title": "Νέα & Συμβουλές",
        "dash_apps_title": "Εφαρμογές",
        "dash_disc_title": "Χώρος Δίσκου",
        "dash_quick_launch": "Γρήγορη Εκκίνηση",
        "dash_updates": "Ενημερώσεις",
        "dash_up_to_date": "Ενημερωμένο",
        "dash_btn_launch": "Εκκίνηση",
        "dash_status_online": "Συνδεδεμένος",
        "dash_status_offline": "Χωρίς Σύνδεση",

        # ------------------------------------------------------------------------#
        # --------------------------- My Apps Page -------------------------------#
        # ------------------------------------------------------------------------#

        "apps_library_title": "Βιβλιοθήκη Εφαρμογών",
        "apps_search_placeholder": "Αναζήτηση στη βιβλιοθήκη...",
        "apps_view_grid": "Προβολή: Πλέγμα",
        "apps_check_updates": "Έλεγχος Ενημερώσεων",
        "apps_btn_launch": "Εκκίνηση",
        "apps_latest": "Τελευταία Έκδοση",
        "apps_update_to": "Ενημέρωση σε v{ver}",
        "apps_installed": "Εγκατεστημένες Εφαρμογές",
        "apps_manual": "Manual",
        "apps_updates_avail": "Διαθέσιμες Ενημερώσεις",
        "apps_open": "Άνοιγμα Εφαρμογής",
        "apps_open_folder": "Άνοιγμα Φακέλου",
        "apps_go_to_site": "Μετάβαση στη Σελίδα",
        "apps_check_update": "Έλεγχος για Ενημέρωση",
        "apps_favorite": "Προσθήκη στα Αγαπημένα",
        "apps_favorite_remove": "Αφαίρεση από τα Αγαπημένα",
        "apps_edit_repair": "Επεξεργασία & Επισκευή",
        "edit_msg_title_confirm": "Επιβεβαίωση",
        "edit_msg_found_version": "Βρέθηκε η έκδοση {version} στο Scoop. Θέλετε να ενημερώσετε το πεδίο;",
        "apps_uninstall": "Απεγκατάσταση",
        # My Apps Library Page
        "apps_ui_my_apps_title": "My Apps Library",
        "apps_ui_my_apps_search_placeholder": "Search my library...",
        "apps_ui_my_apps_sort_az": "Όνομα (A-Z)",
        "apps_ui_my_apps_sort_recent": "Πρόσφατα Εγκατεστημένες",
        "apps_ui_my_apps_sort_update": "Διαθέσιμη Ενημέρωση",
        "apps_ui_my_apps_sort_favorite": "Αγαπημένα",
        "apps_ui_my_apps_view_grid": "View: Grid",
        "apps_ui_my_apps_btn_update_all": "Check for Updates",


        # ------------------------------------------------------------------------#
        # --------------------------- Wizard Page -------------------------------#
        # ------------------------------------------------------------------------#

        "wiz_step2_title": "Βήμα 2: Όνομα Εφαρμογής",
        "wiz_step2_msg": "Βρέθηκε το παρακάτω όνομα. Είναι σωστό;",
        "wiz_next": "Επόμενο",
        "wiz_cancel": "Άκυρο",
        "wiz_step5_title": "Βήμα 5: Επιβεβαίωση Έκδοσης",
        "wiz_set_scoop": "← Βάλε Scoop",
        "wiz_log_sys_ready": "Σύστημα έτοιμο. Αναμονή για αρχείο .zip ή .7z...",
        "wiz_log_scoop_exe_warn": "⚠️ Το Scoop επέστρεψε Installer (.exe). Αναζήτηση Portable έκδοσης στο Chocolatey...",
        "wiz_log_scoop_not_found": "🔍 Δεν βρέθηκε στο Scoop. Αναζήτηση στο Chocolatey...",
        "wiz_app_info": "Πληροφορίες Εφαρμογής",
        "wiz_no_desc": "Δεν υπάρχει διαθέσιμη περιγραφή.",
        "wiz_local": "Τοπικό",
        "wiz_waiting": "Αναμονή...",
        "wiz_searching_api": "Αναζήτηση στο API...",
        "wiz_analyzing_file": "Γίνεται ανάλυση του αρχείου και αναζήτηση πληροφοριών στο διαδίκτυο...",
        "wiz_unknown": "Άγνωστη",
        "wiz_no_desc": "Δεν υπάρχει διαθέσιμη περιγραφή.",
        "wiz_first_install": "Πρώτη εγκατάσταση",
        "wiz_new_installation": "Νέα Εγκατάσταση",
        "wiz_latest_version": "Τελευταία Έκδοση",
        "wiz_update_avail": "Νέα Έκδοση Διαθέσιμη",
        "wiz_out_of_api": "Εκτός API",
        "wiz_no_online_info": "Δεν βρέθηκαν πληροφορίες online. Η εγκατάσταση θα γίνει με τοπικά στοιχεία.",
        "wiz_side_app_name": "Όνομα Εφαρμογής",
        "wiz_side_version": "Έκδοση",
        "wiz_side_status": "Κατάσταση",
        "wiz_browse_title": "Επιλογή Αρχείου ZIP/7Z",
        "wiz_err_title": "Σφάλμα",
        "wiz_err_select_file": "Παρακαλώ επιλέξτε ένα έγκυρο αρχείο ZIP ή 7Z πρώτα!",
        "wiz_waiting": "Αναμονή...",
        "wiz_log_no_exe_err": "ΣΦΑΛΜΑ: Το αρχείο δεν περιέχει εκτελέσιμο (.exe)!",
        "wiz_invalid_file_title": "Άκυρο Αρχείο",
        "wiz_invalid_file_msg": "Το αρχείο δεν φαίνεται να είναι Portable App.",
        "wiz_log_detected_name_wait": "Ανιχνεύθηκε όνομα: {detected_name}. Αναμονή επιβεβαίωσης...",
        "wiz_log_name_confirmed": "Όνομα επιβεβαιώθηκε",
        "wiz_log_install_cancelled": "Η εγκατάσταση ακυρώθηκε από τον χρήστη.",
        "wiz_log_searching_scoop": "Αναζήτηση πληροφοριών για το '{app_name}' στο Scoop...",
        "wiz_log_scoop_match": "Βρέθηκε match στο Scoop (Έκδοση: {scoop_ver})",
        "wiz_msg_newer_ver_regex": "Νεότερη έκδοση: {scoop_ver}. Βρέθηκε στο αρχείο: {detected_ver}. Είναι σωστή;",
        "wiz_msg_newer_ver_no_regex": "Νεότερη έκδοση: {scoop_ver}. Δεν βρέθηκε έκδοση στο όνομα. Είναι σωστή;",
        "wiz_log_scoop_not_found": "Δεν βρέθηκε η εφαρμογή στο Scoop API.",
        "wiz_msg_scoop_not_found": "Δεν βρέθηκε έκδοση στη βάση εφαρμογών.",
        "wiz_log_version_set": "Έκδοση ορίστηκε: {final_version}",
        "wiz_log_install_cancelled_version": "Η εγκατάσταση ακυρώθηκε στο βήμα έκδοσης.",
        "wiz_log_extracting_to": "Έναρξη αποσυμπίεσης στο φάκελο: {target_dir}...",
        "wiz_log_choc_sfx": "📦 Chocolatey SFX file detected. Internal extraction using 7za...",
        "wiz_err_no_7za": "Το 7za.exe δεν βρέθηκε στο project!",
        "wiz_log_internal_extract_ok": "✨ Η εσωτερική αποσυμπίεση ολοκληρώθηκε με επιτυχία!",
        "wiz_log_internal_extract_err": "❌ Σφάλμα κατά την εσωτερική αποσυμπίεση: {error}",
        "wiz_log_searching_exes": "Αποσυμπίεση ολοκληρώθηκε. Αναζήτηση εκτελέσιμων (.exe)...",
        "wiz_title_select_exe": "Βήμα 6: Επιλογή EXE",
        "wiz_log_exe_selected": "Επιλέχθηκε το: {exe_rel}. Εγγραφή στη βάση...",
        "wiz_act_install_success": "Επιτυχής εγκατάσταση του {app_name} v{version}",
        "wiz_log_install_success": "✅ Η εγκατάσταση του {app_name} ολοκληρώθηκε με επιτυχία!",
        "wiz_msg_success_title": "Επιτυχία!",
        "wiz_msg_success_text": "Επιτυχία!\nΗ εφαρμογή {app_name} είναι έτοιμη.",
        "wiz_err_no_exe_found": "ΣΦΑΛΜΑ: Δεν βρέθηκε κανένα .exe στον φάκελο!",
        "wiz_err_extract_failed": "ΣΦΑΛΜΑ: Η αποσυμπίεση απέτυχε.",
        "wiz_log_warn_shortcut_failed": "⚠️ Προειδοποίηση: Η συντόμευση δεν δημιουργήθηκε ({error})",
        "wiz_log_already_running": "⏳ Μια εγκατάσταση είναι ήδη σε εξέλιξη. Παρακαλώ περιμένετε.",
        "wiz_log_quick_start": "--- ΕΝΑΡΞΗ QUICK INSTALL: {app_name} ---",
        "wiz_log_quick_err_no_data": "ΣΦΑΛΜΑ: Δεν βρέθηκαν δεδομένα για το '{app_name}'.",
        "wiz_status_downloading": "Λήψη...",
        "wiz_err_no_download_link": "ΣΦΑΛΜΑ: Δεν βρέθηκε ενεργό Link λήψης.",
        "wiz_log_choc_downloading": "📦 Λήψη και ανάλυση πακέτου Chocolatey...",
        "wiz_log_official_url_found": "✅ Βρέθηκε το επίσημο Portable URL: {url}",
        "wiz_log_checking_embedded": "📦 Έλεγχος για ενσωματωμένα (embedded) αρχεία στο nupkg...",
        "wiz_log_embedded_zip_found": "✅ Βρέθηκε ενσωματωμένο ZIP: {zip_name}",
        "wiz_log_direct_extract": "✅ Τα αρχεία είναι μέσα στο nupkg. Απευθείας αποσυμπίεση.",
        "wiz_log_choc_err": "❌ Σφάλμα Chocolatey: {error}",
        "wiz_err_security_installer_instead_of_zip": "❌ ΣΦΑΛΜΑ ΑΣΦΑΛΕΙΑΣ: Το τελικό αρχείο είναι Installer (.exe/.msi) αντί για .zip.",
        "wiz_status_error": "Σφάλμα",
        "wiz_log_download_final_start": "Έναρξη λήψης του τελικού αρχείου...",
        "wiz_log_download_complete": "Η λήψη ολοκληρώθηκε!",
        "wiz_log_download_err": "ΣΦΑΛΜΑ Λήψης: {error}",
        "wiz_log_local_file": "Το αρχείο είναι ήδη τοπικό, παράκαμψη λήψης...",
        "wiz_official_site": "🌐 Επίσημο Site",
        "wiz_no_site": "Μη διαθέσιμο",
        "wiz_log_security_check": "🔒 Έλεγχος Ασφαλείας (Αλγόριθμος: {algo})...",
        "wiz_log_expected_hash": "📋 Αναμενόμενο Hash (Online API): {hash_val}",
        "wiz_log_calculated_hash": "🧮 Υπολογισμένο Hash (Τοπικό Αρχείο): {hash_val}",
        "wiz_err_checksum_mismatch": "❌ ΚΡΙΣΙΜΟ ΣΦΑΛΜΑ ΑΣΦΑΛΕΙΑΣ: Τα Checksums ΔΕΝ ταιριάζουν! Η εγκατάσταση ακυρώθηκε.",
        "wiz_status_hash_error": "Σφάλμα Hash",
        "wiz_log_hash_success": "✅ Η επαλήθευση πέτυχε! Το αρχείο είναι 100% αυθεντικό και ασφαλές.",
        "wiz_log_warn_no_checksum": "⚠️ Προειδοποίηση: Δεν βρέθηκε Checksum στο API. Παράκαμψη ελέγχου.",
        "wiz_log_extracting_7zip": "Αποσυμπίεση με το 7-Zip...",
        "wiz_log_choc_container_found": "📦 Εντοπίστηκε Chocolatey Container. Καθαρή αποσυμπίεση SFX...",
        "wiz_console_7za_extract": "\n🚀 [FLOWDECK] Extraction του 7-Zip με 7za!",
        "wiz_err_7za_not_found": "Το 7za.exe δεν βρέθηκε στο project!",
        "wiz_console_7za_found": "🎯 Το 7za.exe βρέθηκε στο: {path}",
        "wiz_log_sfx_unzipping": "📦 Unzipping του {file_name} στον κεντρικό φάκελο: {dest_dir}",
        "wiz_console_sfx_success": "✅ Η αποσυμπίεση του SFX ολοκληρώθηκε επιτυχώς!",
        "wiz_log_internal_extract_success": "✨ Η εσωτερική αποσυμπίεση ολοκληρώθηκε και ο φάκελος tools καθαρίστηκε!",
        "wiz_log_extract_err": "❌ Σφάλμα κατά το extraction: {error}",
        "wiz_console_extract_fail": "❌ ΑΠΟΤΥΧΙΑ EXTRACTION ΜΕ 7ZA: {error}",
        "act_log_install_success": "Η εφαρμογή {name} v{ver} εγκαταστάθηκε επιτυχώς!",
        "wiz_msg_install_success": "Η εφαρμογή {name} εγκαταστάθηκε επιτυχώς!",
        "wiz_err_no_exe_found_after_extract": "ΣΦΑΛΜΑ: Δεν βρέθηκε κανένα εκτελέσιμο (.exe) μετά την αποσυμπίεση.",
        "wiz_console_cleanup_err": "Σφάλμα καθαρισμού: {error}",
        "wiz_log_success_simple": "✅ Επιτυχία! Το {app_name} εγκαταστάθηκε.",
        "wiz_log_cleanup_success": "🧹 Καθαρισμός: Διαγράφηκε το αρχείο λήψης {filename}.",
        "wiz_ui_wizard_title": "Εγκατάσταση & Ενημέρωση Εφαρμογών",
        "wiz_ui_wizard_subtitle": "Ο Wizard εγκατάστασης εφαρμογών",
        "wiz_ui_drop_label": "Σύρετε εδώ το .zip αρχείο ή πατήστε αναζήτηση",
        "wiz_ui_lbl_path": "Διαδρομή Αρχείου",
        "wiz_ui_path_placeholder": "Διαδρομή αρχείου .zip...",
        "wiz_ui_btn_browse": "Επιλογή Αρχείου...",
        "wiz_ui_lbl_app_name": "Όνομα Εφαρμογής",
        "wiz_ui_app_name_placeholder": "π.χ. Firefox Portable",
        "wiz_ui_lbl_category": "Κατηγορία",
        "wiz_ui_btn_install": "Εγκατάσταση Εφαρμογής",
        "wiz_ui_sidebar_title": "Εφαρμογή",
        "wiz_ui_sidebar_url_btn": "🌐 Επίσημο Site",
        "wiz_ui_lbl_console": "Live Log / Console",

        # ------------------------------------------------------------------------#
        # --------------------------- Settings Page ------------------------------#
        # ------------------------------------------------------------------------#
        # General System Settings
        "set_msg_title_success": "Επιτυχία",
        "set_msg_success_text": "Οι ρυθμίσεις αποθηκεύτηκαν επιτυχώς!",
        "set_msg_title_error": "Σφάλμα",
        "set_msg_error_text": "Αποτυχία αποθήκευσης ρυθμίσεων:\n{error}",

        # System Tab
        "set_ui_group_install_path": "ΦΑΚΕΛΟΣ ΕΓΚΑΤΑΣΤΑΣΗΣ",
        "set_ui_btn_browse_path": "Αναζήτηση...",
        "set_ui_btn_open_path": "Άνοιγμα Φακέλου",
        "set_ui_group_system_options": "ΕΠΙΛΟΓΕΣ ΣΥΣΤΗΜΑΤΟΣ",
        "set_ui_chk_start_on_boot": "Εκκίνηση με τα Windows",
        "set_ui_chk_minimize_to_tray": "Ελαχιστοποίηση στο System Tray κατά το κλείσιμο",
        "set_ui_chk_update_to_start": "Έλεγχος για ενημερώσεις του FlowDeck κατά την εκκίνηση",
        "set_ui_group_language": "ΓΛΩΣΣΑ ΕΦΑΡΜΟΓΗΣ",
        "set_ui_tab_system": "Σύστημα",
        "set_lang_el": "Ελληνικά",
        "set_lang_en": "English",

        # Appearance & Updates
        "set_ui_group_theme": "ΘΕΜΑ ΕΦΑΡΜΟΓΗΣ",
        "set_ui_tab_appearance": "Εμφάνιση",
        "set_ui_group_update_freq": "ΣΥΧΝΟΤΗΤΑ ΕΛΕΓΧΟΥ",
        "set_ui_update_freq_boot": "Κάθε εκκίνηση",
        "set_ui_update_freq_24h": "Κάθε 24 ώρες",
        "set_ui_update_freq_manual": "Μόνο χειροκίνητα",
        "set_ui_chk_silent_updater": "Αθόρυβος έλεγχος ενημερώσεων στο παρασκήνιο (χωρίς ειδοποιήσεις)",
        "set_ui_group_update_status": "ΚΑΤΑΣΤΑΣΗ ΕΝΗΜΕΡΩΣΕΩΝ",
        "set_ui_lbl_last_check": "Τελευταίος έλεγχος: ποτέ",
        "set_ui_btn_check_now": "Έλεγχος Τώρα",
        "set_ui_tab_updates": "Ενημερώσεις",
        "set_freq_startup": "Κάθε εκκίνηση",
        "set_freq_daily": "Κάθε 24 ώρες",
        "set_freq_manual": "Χειροκίνητα",

        # Maintenance
        "set_ui_group_maintenance": "ΔΙΑΧΕΙΡΙΣΗ ΔΕΔΟΜΕΝΩΝ",
        "set_ui_btn_clear_log": "Καθαρισμός Activity Log",
        "set_ui_btn_reset_defaults": "Επαναφορά Εργοστασιακών Ρυθμίσεων",
        "set_ui_btn_backup_apps": "Δημιουργία Αντιγράφου Ασφαλείας Εφαρμογών",
        "set_ui_btn_scan_folder": "Αυτόματη Συντήρηση Εφαρμογών (Scan)",
        "set_ui_tab_maintenance": "Συντήρηση",
        "set_ui_btn_save_settings": "Αποθήκευση Ρυθμίσεων",
        "set_log_clear_success": "🧹 Το ιστορικό δραστηριότητας καθαρίστηκε με επιτυχία!",
        "set_scan_detected_msg": "<b>🧹 Νέα φορητή εφαρμογή βρέθηκε!</b>",
        "set_scan_folder_label": "Ονομα φακέλου στο δίσκο:",
        "set_scan_name_field": "Ονομα Εφαρμογής:",
        "set_scan_version_field": "Εκδοση:",
        "set_scan_btn_register": "Εγγραφή",
        "set_scan_btn_skip": "Παράλειψη",
        "set_maintenance_finished": "Η συντήρηση ολοκληρώθηκε",
        "set_maintenance_details": (
                        "🧹 Η συντήρηση ολοκληρώθηκε με επιτυχία!\n"
                        "\n"
                        "• ΑΝΤΙΓΡΑΦΟ ΑΣΦΑΛΕΙΑΣ ΒΑΣΗΣ: Δημιουργήθηκε επιτυχώς\n"
                        "• Ορφανές εγραφές εφαρμογών: {removed}\n"
                        "• Νέες εφαρμογές: {added}"),

        # ------------------------------------------------------------------------#
        # --------------------------- Activity Manager page ----------------------#
        # ------------------------------------------------------------------------#

        "act_time_just_now": "Μόλις τώρα",
        "act_time_yesterday": "Χθες",
        "act_time_some_time_ago": "Πριν από λίγο",
        "act_time_minutes_ago": "Πριν από {minutes} λεπτά",
        "act_time_minute_ago": "Πριν από 1 λεπτό",
        "act_time_hours_ago": "Πριν από {hours} ώρες",
        "act_time_hour_ago": "Πριν από 1 ώρα",
        "act_time_days_ago": "Πριν από {days} ημέρες",
        "act_unknown_event": "Άγνωστη Δραστηριότητα",
        "act_err_load_log": "❌ Αποτυχία φόρτωσης του ιστορικού δραστηριότητας: {error}",
        "act_err_save_log": "❌ Αποτυχία αποθήκευσης του ιστορικού δραστηριότητας: {error}",

        # ------------------------------------------------------------------------#
        # --------------------------- Update Manager -----------------------------#
        # ------------------------------------------------------------------------#
        "upd_title_warning": "Προειδοποίηση",
        "upd_no_apps": "Δεν υπάρχουν εγκατεστημένες εφαρμογές στη βάση.",
        "upd_title_success": "Έλεγχος Ενημερώσεων",
        "upd_success_text": "Ο έλεγχος ενημερώσεων ολοκληρώθηκε!",
        "upd_found_text": "Ο έλεγχος ολοκληρώθηκε! Βρέθηκαν {count} ενημερώσεις.",
        "upd_not_found_text": "Ο έλεγχος ολοκληρώθηκε! Όλες οι εφαρμογές είναι ενημερωμένες.",
        "upd_title_error": "Σφάλμα Δικτύου",
        "upd_no_internet_text": "Αδυναμία σύνδεσης στο διαδίκτυο.\nΠαρακαλώ ελέγξτε τη σύνδεσή σας και δοκιμάστε ξανά.",

        # ------------------------------------------------------------------------#
        # --------------------------- Activity Manager ---------------------------#
        # ------------------------------------------------------------------------#
        "log_update_check": "Έλεγχος για ενημερώσεις",
        "act_uninstalled_app": "Η εφαρμογή {app_name} απεγκαταστάθηκε",
        "act_launch_success": "Εκκίνηση της εφαρμογής {app_name}",
        "act_launch_failed": "Αποτυχία εκκίνησης της εφαρμογής {app_name}",
        "act_launch_not_found": "Δεν βρέθηκε το εκτελέσιμο για την εφαρμογή {app_name}",
        "act_fav_added": "Η εφαρμογή {app_name} προστέθηκε στα Αγαπημένα",
        "act_fav_removed": "Η εφαρμογή {app_name} αφαιρέθηκε από τα Αγαπημένα",
        "act_scan_repair_success": "Η συντήρηση ολοκληρώθηκε: {added_count} προστέθηκαν, {removed_count} αφαιρέθηκαν",

        # ------------------------------------------------------------------------#
        # ---------------------- Οδηγός Backup & Restore -------------------------#
        # ------------------------------------------------------------------------#
        "wiz_backup_title": "Οδηγός Αντιγράφων Ασφαλείας & Επαναφοράς",
        "wiz_Backup_tab_export": "ΕΞΑΓΩΓΗ (BACKUP)",
        "wiz_Backup_tab_import": "ΕΙΣΑΓΩΓΗ (RESTORE)",

        # Καρτέλα Εξαγωγής (Backup)
        "wiz_Backup_exp_select": "Επιλέξτε Εφαρμογές για εξαγωγή:",
        "wiz_Backup_btn_all": "Επιλογή όλων",
        "wiz_Backup_exp_dest": "Πού θα αποθηκευτεί το Αντίγραφο Ασφαλείας;",
        "wiz_Backup_exp_dest_ph": "C:\\Backups\\FlowDeck.zip",
        "wiz_Backup_btn_browse": "Αναζήτηση...",
        "wiz_Backup_exp_settings": "Εξαγωγή Ρυθμίσεων Εφαρμογής",
        "wiz_Backup_info": "Πληροφορίες",
        "wiz_Backup_size": "Απαιτούμενος Χώρος Στον Δίσκο:",
        "wiz_Backup_filename": "Όνομα Αρχείου:",
        "wiz_Backup_exp_apps": "Εφαρμογές για εξαγωγή:",
        "wiz_Backup_status": "Κατάσταση:",
        "wiz_Backup_btn_start_export": "ΔΗΜΙΟΥΡΓΙΑ BACKUP 📤",

        # Καρτέλα Εισαγωγής (Restore)
        "wiz_Backup_imp_select": "Επιλέξτε Εφαρμογές για εισαγωγή:",
        "wiz_Backup_imp_source": "Επιλέξτε Αρχείο Αντιγράφου (.zip):",
        "wiz_Backup_imp_dest": "Πού θα εγκατασταθούν οι Portable εφαρμογές;",
        "wiz_Backup_imp_dest_ph": "C:\\FlowDeckApps",
        "wiz_Backup_imp_settings": "Εισαγωγή Ρυθμίσεων Εφαρμογής",
        "wiz_Backup_imp_apps": "Εφαρμογές για εισαγωγή:",
        "wiz_Backup_btn_start_import": "ΕΠΑΝΑΦΟΡΑ BACKUP 📥",
        "wiz_Backup_exp_compress": "Επίπεδο Συμπίεσης:",
        "wiz_Backup_exp_fast_zip": "Γρήγορη Συμπίεση",
        "wiz_Backup_exp_ultra_7z": "Μέγιστη Συμπίεση Ultra (θα διαρκέσει αρκετά λεπτά)",
        "wiz_Backup_btn_close": "Άκυρο",

        # ------------------------------------------------------------------------#
        # --------------------------- Backup Manager -----------------------------#
        # ------------------------------------------------------------------------#
        "bak_err_no_apps_export": "Δεν επιλέχθηκε καμία εφαρμογή για εξαγωγή.",
        "bak_err_7za_not_found": "Το 7za.exe δεν βρέθηκε στη διαδρομή: {path}",
        "bak_status_preparing": "Προετοιμασία: {app_name}...",
        "bak_status_copying": "Αντιγραφή αρχείων: {app_name}...",
        "bak_status_manifest": "Δημιουργία manifest.json...",
        "bak_err_manifest_fail": "Αποτυχία δημιουργίας manifest.json: {error}",
        "bak_status_compressing": "Έναρξη συμπίεσης (Παρακαλώ περιμένετε)...",
        "bak_status_compressing_7z": "Έναρξη συμπίεσης Ultra 7-Zip (Παρακαλώ περιμένετε)...",
        "bak_status_compressing_zip": "Έναρξη Γρήγορης συμπίεσης ZIP...",
        "bak_msg_export_success": "Η εξαγωγή ολοκληρώθηκε επιτυχώς μέσω 7-Zip!\nΑρχείο: {filename}",
        "bak_err_7z_error": "Σφάλμα 7-Zip: {error}",
        "bak_err_7z_call_fail": "Αποτυχία κλήσης 7-Zip: {error}",
        "bak_err_no_apps_import": "Δεν επιλέχθηκε καμία εφαρμογή για εισαγωγή.",
        "bak_status_prep_extract": "Προετοιμασία αποσυμπίεσης...",
        "bak_status_extracting": "Αποσυμπίεση αρχείου (Παρακαλώ περιμένετε)...",
        "bak_status_reading_manifest": "Ανάγνωση ρυθμίσεων (manifest.json)...",
        "bak_err_invalid_backup": "Το αρχείο δεν περιέχει manifest.json. Μη έγκυρο backup.",
        "bak_status_installing": "Εγκατάσταση: {app_name}...",
        "bak_msg_import_success": "Η εισαγωγή ολοκληρώθηκε με επιτυχία!",

        # ------------------------------------------------------------------------#
        # ------------------- Backup Wizard Controller ---------------------------#
        # ------------------------------------------------------------------------#
        "bak_ctrl_export_apps_count": "Εφαρμογές για εξαγωγή: {checked} από {total}",
        "bak_ctrl_total_size": "Συνολικό Μέγεθος (Ασυμπίεστο): {size} MB",
        "bak_ctrl_overwrite_term": "Αντικατάσταση",
        "bak_ctrl_import_selected": "Επιλεγμένες Εφαρμογές: {checked} από {total}",
        "bak_ctrl_space_req": "Απαιτούμενος Χώρος: {req} MB / Διαθέσιμος Χώρος: {free} GB",
        "bak_ctrl_status_no_apps": "Κατάσταση: Καμία επιλεγμένη εφαρμογή",
        "bak_ctrl_status_overwrite_warn": "Κατάσταση: ⚠️ {count} εφαρμογές θα αντικατασταθούν!",
        "bak_ctrl_status_new_apps": "Κατάσταση: Όλες οι επιλεγμένες εφαρμογές είναι νέες",
        "bak_ctrl_filename": "Όνομα Αρχείου: {name}",
        "bak_ctrl_status_ready_export": "Κατάσταση: Έτοιμο για εξαγωγή",
        "bak_ctrl_app_item_format": " {name} (v{version})  —  [{size}]",
        "bak_ctrl_dest_title": "Επιλέξτε Φάκελο Εγκατάστασης Εφαρμογών",
        "bak_ctrl_filter_7z": "7-Zip Archive (*.7z)",
        "bak_ctrl_filter_zip": "Zip Archive (*.zip)",
        "bak_ctrl_save_title": "Αποθήκευση Αρχείου Μεταφοράς",
        "bak_ctrl_err_dest": "Παρακαλώ επιλέξτε διαδρομή αποθήκευσης!",
        "bak_ctrl_err_no_select": "Δεν έχετε επιλέξει καμία εφαρμογή!",
        "bak_ctrl_import_title": "Επιλέξτε Αρχείο Μεταφοράς",
        "bak_ctrl_import_filter": "Archives (*.7z *.zip)",
        "bak_ctrl_invalid_backup": "Το αρχείο δεν είναι έγκυρο backup (λείπει το manifest.json).",
        "bak_ctrl_ver_prev": "προηγούμενη",
        "bak_ctrl_ver_next": "νεότερη",
        "bak_ctrl_ver_same": "ίδια",
        "bak_ctrl_app_exists": "{name} (Υπάρχει ήδη σε {ver} έκδοση - Αντικατάσταση;)",
        "bak_ctrl_folder_exists": "{name} (Ο φάκελος υπάρχει ήδη - Αντικατάσταση;)",
        "bak_ctrl_app_new": "{name} (Νέα - v{ver})",
        "bak_ctrl_dest_title": "Επιλέξτε Φάκελο Εγκατάστασης Εφαρμογών",
        "bak_ctrl_err_source": "Παρακαλώ επιλέξτε το αρχείο εισαγωγής (.7z ή .zip)!",

        # Database Management
        "db_restore_title": "Επαναφορά Βάσης Δεδομένων",
        "db_restore_prompt": "Η βάση δεδομένων δεν βρέθηκε, αλλά εντοπίστηκε αντίγραφο ασφαλείας.\n\nΘέλετε να γίνει επαναφορά από το πιο πρόσφατο backup;",
        "db_restore_success": "Η βάση αποκαταστάθηκε επιτυχώς!",
        "db_restore_error": "Αποτυχία επαναφοράς της βάσης.",
        "act_db_restored": "Η βάση δεδομένων αποκαταστάθηκε από αντίγραφο ασφαλείας",

        # Factory Reset
        "set_factory_reset_title": "Επαναφορά στις Εργοστασιακές Ρυθμίσεις",
        "set_factory_reset_confirm": "Είστε σίγουροι ότι θέλετε να κάνετε επαναφορά στις εργοστασιακές ρυθμίσεις;\n\nΑυτή η ενέργεια θα διαγράψει όλες τις ρυθμίσεις, τη βάση δεδομένων και το ιστορικό δραστηριοτήτων. Δεν μπορεί να αναιρεθεί!",
        "set_factory_reset_apps_confirm": "Θέλετε επίσης να διαγράψετε τον φάκελο με τις φορητές εφαρμογές (apps);\n\nΠροειδοποίηση: Αυτό θα διαγράψει οριστικά όλες τις εγκατεστημένες εφαρμογές σας!",
        "set_factory_reset_success_title": "Η επαναφορά ολοκληρώθηκε",
        "set_factory_reset_success_msg": "Η επαναφορά στις εργοστασιακές ρυθμίσεις ολοκληρώθηκε με επιτυχία!\n\nΌλες οι ρυθμίσεις, η βάση δεδομένων και το ιστορικό δραστηριοτήτων έχουν διαγραφεί.",

        # Update Notifications
        "update_title": "Διαθέσιμη Ενημέρωση",
        "update_available": "Νέα Έκδοση Διαθέσιμη",
        "new_version": "Νέα Έκδοση",
        "release_title": "Κυκλοφορία",
        "changelog": "Αλλαγές",
        "click_below": "Κάντε κλικ στο κουμπί παρακάτω για λήψη της νέας έκδοσης από το GitHub.",
        "download_button": "Λήψη",


    },
    "en": {

        # ------------------------------------------------------------------------#
        # --------------------------- Main Page ----------------------------------#
        # ------------------------------------------------------------------------#
        "tray_title": "FlowDeck",
        "tray_message": "The application continues to run in the background.",
        "tray_menu_show": "Show",
        "tray_menu_exit": "Exit",
        "nav_dashboard": "Dashboard",
        "nav_wizard": "Wizard",
        "nav_settings": "Settings",
        "nav_my_apps": "My Apps",
        "tray_menu_exit": "Exit",
        "nav_sub_dashboard": "Overview & Stats",
        "nav_sub_wizard": "Add new applications",
        "nav_sub_settings": "Purge and other logic",
        "nav_sub_my_apps": "Categories/Buckets",
        "nav_about": "About",
        "nav_sub_about": "App info & credits",
        "about_window_title": "About FlowDeck",
        "about_description": "Portable application manager for Windows.",
        "about_7zip_mention": "Includes 7-Zip (7za.exe) for archive management.",
        "about_scoop_mention": "Powered by the Scoop ecosystem for portable apps.",
        "about_chocolatey_mention": "Supports Chocolatey for system package installations.",
        "about_version_label": "Version",
        "about_license_label": "License",
        "about_license_value": "GNU GPLv3",
        "about_github": "GitHub",
        "no_updates_title": "No Updates Available",
        "no_updates_text": "Your system is up to date. No updates are available at this time.",

        # ------------------------------------------------------------------------#
        # --------------------------- Dashboard Page -----------------------------#
        # ------------------------------------------------------------------------#
        "dash_welcome": "Welcome back, User!",
        "dash_activity_title": "Recent Activity",
        "dash_tips_title": "FlowDeck News/Tips",
        "dash_apps_title": "Apps Installed",
        "dash_disc_title": "Disc Space",
        "dash_quick_launch": "Quick Launch",
        "dash_updates": "Updates",
        "dash_up_to_date": "System Up To Date",
        "dash_btn_launch": "Launch",
        "dash_status_online": "Online",
        "dash_status_offline": "No Connection",

        # ------------------------------------------------------------------------#
        # --------------------------- My Apps Page -------------------------------#
        # ------------------------------------------------------------------------#
        "apps_library_title": "My Apps Library",
        "apps_search_placeholder": "Search my library...",
        "apps_view_grid": "View: Grid",
        "apps_check_updates": "Check for Updates",
        "apps_btn_launch": "Launch",
        "apps_latest": "Latest Version",
        "apps_update_to": "Update to v{ver}",
        "apps_installed": "Applications Installed",
        "apps_manual": "Manual",
        "apps_updates_avail": "Updates Available",
        "apps_open": "Open Application",
        "apps_open_folder": "Open Folder",
        "apps_go_to_site": "Go to Site",
        "apps_check_update": "Check for Update",
        "apps_favorite": "Add to Favorites",
        "apps_favorite_remove": "Remove from Favorites",
        "apps_edit_repair": "Edit & Repair",
        "edit_msg_title_confirm": "Confirmation",
        "edit_msg_found_version": "Version {version} found on Scoop. Do you want to update the field?",
        "apps_uninstall": "Uninstall",
        # My Apps Library Page
        "apps_ui_my_apps_title": "My Apps Library",
        "apps_ui_my_apps_search_placeholder": "Search my library...",
        "apps_ui_my_apps_sort_az": "Name (A-Z)",
        "apps_ui_my_apps_sort_recent": "Recently Installed",
        "apps_ui_my_apps_sort_update": "Update Available",
        "apps_ui_my_apps_sort_favorite": "Favorite",
        "apps_ui_my_apps_view_grid": "View: Grid",
        "apps_ui_my_apps_btn_update_all": "Check for Updates",

        # ------------------------------------------------------------------------#
        # --------------------------- Wizard Page -------------------------------#
        # ------------------------------------------------------------------------#
        "wiz_step2_title": "Step 2: App Name",
        "wiz_step2_msg": "The following name was detected. Is it correct?",
        "wiz_next": "Next",
        "wiz_cancel": "Cancel",
        "wiz_step5_title": "Step 5: Confirm Version",
        "wiz_set_scoop": "← Use Scoop",
        "wiz_log_sys_ready": "System ready. Waiting for .zip or .7z file...",
        "wiz_log_scoop_exe_warn": "⚠️ The Scoop returned an Installer (.exe). Searching for Portable version in Chocolatey...",
        "wiz_log_scoop_not_found": "🔍 Not found in Scoop. Searching in Chocolatey...",
        "wiz_app_info": "App Information",
        "wiz_no_desc": "No description available.",
        "wiz_local": "Local",
        "wiz_waiting": "Waiting...",
        "wiz_searching_api": "Searching API...",
        "wiz_analyzing_file": "Analyzing file and searching for information online...",
        "wiz_unknown": "Unknown",
        "wiz_no_desc": "No description available.",
        "wiz_first_install": "First install",
        "wiz_new_installation": "New Installation",
        "wiz_latest_version": "Latest Version",
        "wiz_update_avail": "New Version Available",
        "wiz_out_of_api": "Out of API",
        "wiz_no_online_info": "No online information found. Installation will proceed with local details.",
        "wiz_side_app_name": "App Name",
        "wiz_side_version": "Version",
        "wiz_side_status": "Status",
        "wiz_browse_title": "Select ZIP/7Z File",
        "wiz_err_title": "Error",
        "wiz_err_select_file": "Please select a valid ZIP or 7Z file first!",
        "wiz_waiting": "Waiting...",
        "wiz_log_no_exe_err": "ERROR: The file does not contain an executable (.exe)!",
        "wiz_invalid_file_title": "Invalid File",
        "wiz_invalid_file_msg": "The file does not appear to be a Portable App.",
        "wiz_log_detected_name_wait": "Detected name: {detected_name}. Awaiting confirmation...",
        "wiz_log_name_confirmed": "Name confirmed",
        "wiz_log_install_cancelled": "Installation cancelled by user.",
        "wiz_log_searching_scoop": "Searching information for '{app_name}' in Scoop...",
        "wiz_log_scoop_match": "Match found in Scoop (Version: {scoop_ver})",
        "wiz_msg_newer_ver_regex": "Newer version: {scoop_ver}. Found in file: {detected_ver}. Is this correct?",
        "wiz_msg_newer_ver_no_regex": "Newer version: {scoop_ver}. No version found in the name. Is this correct?",
        "wiz_log_scoop_not_found": "Application not found in Scoop API.",
        "wiz_msg_scoop_not_found": "No version found in the app database.",
        "wiz_log_version_set": "Version set: {final_version}",
        "wiz_log_install_cancelled_version": "Installation cancelled at the version step.",
        "wiz_log_extracting_to": "Starting extraction to folder: {target_dir}...",
        "wiz_log_choc_sfx": "📦 Chocolatey SFX file detected. Internal extraction using 7za...",
        "wiz_err_no_7za": "7za.exe not found in the project!",
        "wiz_log_internal_extract_ok": "✨ Internal extraction completed successfully!",
        "wiz_log_internal_extract_err": "❌ Error during internal extraction: {error}",
        "wiz_log_searching_exes": "Extraction completed. Searching for executables (.exe)...",
        "wiz_title_select_exe": "Step 6: Select EXE",
        "wiz_log_exe_selected": "Selected: {exe_rel}. Writing to database...",
        "wiz_act_install_success": "Successfully installed {app_name} v{version}",
        "wiz_log_install_success": "✅ Installation of {app_name} completed successfully!",
        "act_log_install_success": "Successfully installed {name} v{ver}",
        "wiz_msg_success_title": "Success!",
        "wiz_msg_success_text": "Success!\nThe application {app_name} is ready.",
        "wiz_err_no_exe_found": "ERROR: No .exe found in the folder!",
        "wiz_err_extract_failed": "ERROR: Extraction failed.",
        "wiz_log_warn_shortcut_failed": "⚠️ Warning: Shortcut could not be created ({error})",
        "wiz_log_already_running": "⏳ An installation is already in progress. Please wait.",
        "wiz_log_quick_start": "--- STARTING QUICK INSTALL: {app_name} ---",
        "wiz_log_quick_err_no_data": "ERROR: No data found for '{app_name}'.",
        "wiz_status_downloading": "Downloading...",
        "wiz_err_no_download_link": "ERROR: No active download link found.",
        "wiz_log_choc_downloading": "📦 Downloading and analyzing Chocolatey package...",
        "wiz_log_official_url_found": "✅ Official Portable URL found: {url}",
        "wiz_log_checking_embedded": "📦 Checking for embedded files in nupkg...",
        "wiz_log_embedded_zip_found": "✅ Embedded ZIP found: {zip_name}",
        "wiz_log_direct_extract": "✅ Files are inside the nupkg. Direct extraction.",
        "wiz_log_choc_err": "❌ Chocolatey error: {error}",
        "wiz_err_security_installer_instead_of_zip": "❌ SECURITY ERROR: The final file is an Installer (.exe/.msi) instead of a .zip.",
        "wiz_status_error": "Error",
        "wiz_log_download_final_start": "Starting download of the final file...",
        "wiz_log_download_complete": "Download completed!",
        "wiz_log_download_err": "Download ERROR: {error}",
        "wiz_log_local_file": "The file is already local, skipping download...",
        "wiz_official_site": "🌐 Official Site",
        "wiz_no_site": "Not available",
        "wiz_log_security_check": "🔒 Security Check (Algorithm: {algo})...",
        "wiz_log_expected_hash": "📋 Expected Hash (Online API): {hash_val}",
        "wiz_log_calculated_hash": "🧮 Calculated Hash (Local File): {hash_val}",
        "wiz_err_checksum_mismatch": "❌ CRITICAL SECURITY ERROR: Checksums DO NOT match! Installation aborted.",
        "wiz_status_hash_error": "Hash Error",
        "wiz_log_hash_success": "✅ Verification successful! The file is 100% authentic and safe.",
        "wiz_log_warn_no_checksum": "⚠️ Warning: No Checksum found in the API. Skipping verification.",
        "wiz_log_extracting_7zip": "Extracting with 7-Zip...",
        "wiz_log_choc_container_found": "📦 Chocolatey Container detected. Clean SFX extraction...",
        "wiz_console_7za_extract": "\n🚀 [FLOWDECK] Extracting 7-Zip with 7za!",
        "wiz_err_7za_not_found": "7za.exe was not found in the project!",
        "wiz_console_7za_found": "🎯 7za.exe found at: {path}",
        "wiz_log_sfx_unzipping": "📦 Unzipping {file_name} to the main folder: {dest_dir}",
        "wiz_console_sfx_success": "✅ SFX extraction completed successfully!",
        "wiz_log_internal_extract_success": "✨ Internal extraction completed and tools folder was cleaned up!",
        "wiz_log_extract_err": "❌ Error during extraction: {error}",
        "wiz_console_extract_fail": "❌ EXTRACTION FAILED WITH 7ZA: {error}",
        "wix_log_install_success": "Successfully installed {name} v{ver}",
        "wiz_msg_install_success": "{name} installed successfully!",
        "wiz_err_no_exe_found_after_extract": "ERROR: No executable (.exe) found after extraction.",
        "wiz_console_cleanup_err": "Cleanup error: {error}",
        "wiz_log_success_simple": "✅ Success! {app_name} has been installed.",
        "wiz_log_cleanup_success": "🧹 Cleanup: Downloaded file {filename} was deleted.",
        "wiz_ui_wizard_title": "Install & Update Applications",
        "wiz_ui_wizard_subtitle": "The application installation wizard",
        "wiz_ui_drop_label": "Drag and drop .zip file here or click browse",
        "wiz_ui_lbl_path": "File Path",
        "wiz_ui_path_placeholder": "Zip file path...",
        "wiz_ui_btn_browse": "Browse File...",
        "wiz_ui_lbl_app_name": "Application Name",
        "wiz_ui_app_name_placeholder": "e.g., Firefox Portable",
        "wiz_ui_lbl_category": "Category",
        "wiz_ui_btn_install": "Install Application",
        "wiz_ui_sidebar_title": "Application",
        "wiz_ui_sidebar_url_btn": "🌐 Official Site",
        "wiz_ui_lbl_console": "Live Log / Console",

        # ------------------------------------------------------------------------#
        # --------------------------- Settings Page ------------------------------#
        # ------------------------------------------------------------------------#
        # General System Settings
        "set_msg_title_success": "Success",
        "set_msg_success_text": "Settings saved successfully!",
        "set_msg_title_error": "Error",
        "set_msg_error_text": "Failed to save settings:\n{error}",

        # System Tab
        "set_ui_group_install_path": "INSTALLATION FOLDER",
        "set_ui_btn_browse_path": "Browse...",
        "set_ui_btn_open_path": "Open Folder",
        "set_ui_group_system_options": "SYSTEM OPTIONS",
        "set_ui_chk_start_on_boot": "Start on Windows Boot",
        "set_ui_chk_minimize_to_tray": "Minimize to System Tray on close",
        "set_ui_chk_update_to_start": "Check for FlowDeck Updates on Start",
        "set_ui_group_language": "APPLICATION LANGUAGE",
        "set_ui_tab_system": "System",
        "set_lang_el": "Greek",
        "set_lang_en": "English",

        # Appearance & Updates
        "set_ui_group_theme": "APPLICATION THEME",
        "set_ui_tab_appearance": "Appearance",
        "set_ui_group_update_freq": "CHECK FREQUENCY",
        "set_ui_update_freq_boot": "On every boot",
        "set_ui_update_freq_24h": "Every 24 hours",
        "set_ui_update_freq_manual": "Manually only",
        "set_ui_chk_silent_updater": "Silent background update checks (no notifications)",
        "set_ui_group_update_status": "UPDATE STATUS",
        "set_ui_lbl_last_check": "Last check: never",
        "set_ui_btn_check_now": "Check Now",
        "set_ui_tab_updates": "Updates",
        "set_freq_startup": "On Startup",
        "set_freq_daily": "Every 24 Hours",
        "set_freq_manual": "Manual Only",

        # Maintenance
        "set_ui_group_maintenance": "DATA MAINTENANCE",
        "set_ui_btn_clear_log": "Clear Activity Log",
        "set_ui_btn_reset_defaults": "Reset to Factory Defaults",
        "set_ui_btn_backup_apps": "Create Backup of Applications",
        "set_ui_btn_scan_folder": "Auto-Maintain Applications (Scan)",
        "set_ui_tab_maintenance": "Maintenance",
        "set_ui_btn_save_settings": "Save Settings",
        "set_log_clear_success": "🧹 Activity history has been cleared successfully!",
        "set_scan_detected_msg": "<b>🧹 New portable application found!</b>",
        "set_scan_folder_label": "Folder name on disk:",
        "set_scan_name_field": "Application Name:",
        "set_scan_version_field": "Version:",
        "set_scan_btn_register": "Register",
        "set_scan_btn_skip": "Skip",
        "set_maintenance_finished": "Maintenance Complete",
        "set_maintenance_details": (
                        "🧹 Maintenance completed safely!\n\n"
                        "• Database backup: Created successfully.\n"
                        "• Orphaned records removed: {removed}\n"
                        "• New portable applications detected: {added}"),
        # ------------------------------------------------------------------------#
        # --------------------------- Activity Manager page ----------------------#
        # ------------------------------------------------------------------------#
        "act_time_just_now": "Just now",
        "act_time_minute_ago": "1 minute ago",
        "act_time_minutes_ago": "{minutes} minutes ago",
        "act_time_hour_ago": "1 hour ago",
        "act_time_hours_ago": "{hours} hours ago",
        "act_time_yesterday": "Yesterday",
        "act_time_days_ago": "{days} days ago",
        "act_time_some_time_ago": "Some time ago",
        "act_unknown_event": "Unknown Event",
        "act_err_load_log": "❌ Failed to load activity log: {error}",
        "act_err_save_log": "❌ Failed to save activity log: {error}",

        # ------------------------------------------------------------------------#
        # --------------------------- Update Manager -----------------------------#
        # ------------------------------------------------------------------------#
        "upd_title_warning": "Warning",
        "upd_no_apps": "There are no installed applications in the database.",
        "upd_title_success": "Update Check",
        "upd_success_text": "Update check completed successfully!",
        "upd_found_text": "Check completed! Found {count} available updates.",
        "upd_not_found_text": "Check completed! All applications are up to date.",
        "upd_title_error": "Network Error",
        "upd_no_internet_text": "No internet connection detected.\nPlease check your connection and try again.",

        # ------------------------------------------------------------------------#
        # --------------------------- Activity Manager ---------------------------#
        # ------------------------------------------------------------------------#
        "log_update_check": "Checked for updates",
        "act_uninstalled_app": "Uninstalled {app_name}",
        "act_launch_success": "Launched {app_name}",
        "act_launch_failed": "Failed to launch {app_name}",
        "act_launch_not_found": "{app_name}: Executable not found",
        "act_fav_added": "{app_name} added to Favorites",
        "act_fav_removed": "{app_name} removed from Favorites",
        "act_scan_repair_success": "Maintenance completed: {added_count} added, {removed_count} removed",

        # ------------------------------------------------------------------------#
        # ---------------------- Backup & Restore Wizard -------------------------#
        # ------------------------------------------------------------------------#
        "wiz_backup_title": "Backup & Restore Wizard",
        "wiz_Backup_tab_export": "EXPORT (BACKUP)",
        "wiz_Backup_tab_import": "IMPORT (RESTORE)",

        # Export Tab (Backup)
        "wiz_Backup_exp_select": "Select Applications to export:",
        "wiz_Backup_btn_all": "Select All",
        "wiz_Backup_exp_dest": "Where should the Backup file be saved?",
        "wiz_Backup_exp_dest_ph": "C:\\Backups\\FlowDeck.zip",
        "wiz_Backup_btn_browse": "Browse...",
        "wiz_Backup_exp_settings": "Export Application Settings",
        "wiz_Backup_info": "Information",
        "wiz_Backup_size": "Required Disk Space:",
        "wiz_Backup_filename": "File Name:",
        "wiz_Backup_exp_apps": "Applications to export:",
        "wiz_Backup_status": "Status:",
        "wiz_Backup_btn_start_export": "CREATE BACKUP 📤",

        # Import Tab (Restore)
        "wiz_Backup_imp_select": "Select Applications to import:",
        "wiz_Backup_imp_source": "Select Backup File (.zip):",
        "wiz_Backup_imp_dest": "Where should the Portable apps be installed?",
        "wiz_Backup_imp_dest_ph": "C:\\FlowDeckApps",
        "wiz_Backup_imp_settings": "Import Application Settings",
        "wiz_Backup_imp_apps": "Applications to import:",
        "wiz_Backup_btn_start_import": "RESTORE BACKUP 📥",
        "wiz_Backup_exp_compress": "Compression Level:",
        "wiz_Backup_exp_fast_zip": "Fast Compression",
        "wiz_Backup_exp_ultra_7z": "Maximum Ultra Compression (will take several minutes)",
        "wiz_Backup_btn_close": "Cancel",

        # ------------------------------------------------------------------------#
        # --------------------------- Backup Manager -----------------------------#
        # ------------------------------------------------------------------------#
        "bak_err_no_apps_export": "No applications selected for export.",
        "bak_err_7za_not_found": "7za.exe not found at path: {path}",
        "bak_status_preparing": "Preparing: {app_name}...",
        "bak_status_copying": "Copying files: {app_name}...",
        "bak_status_manifest": "Creating manifest.json...",
        "bak_err_manifest_fail": "Failed to create manifest.json: {error}",
        "bak_status_compressing": "Starting compression (Please wait)...",
        "bak_status_compressing_7z": "Starting Ultra 7-Zip compression (Please wait)...",
        "bak_status_compressing_zip": "Starting Fast ZIP compression...",
        "bak_msg_export_success": "Export completed successfully via 7-Zip!\nFile: {filename}",
        "bak_err_7z_error": "7-Zip error: {error}",
        "bak_err_7z_call_fail": "7-Zip call failed: {error}",
        "bak_err_no_apps_import": "No applications selected for import.",
        "bak_status_prep_extract": "Preparing extraction...",
        "bak_status_extracting": "Extracting file (Please wait)...",
        "bak_status_reading_manifest": "Reading settings (manifest.json)...",
        "bak_err_invalid_backup": "File does not contain manifest.json. Invalid backup.",
        "bak_status_installing": "Installing: {app_name}...",
        "bak_msg_import_success": "Import completed successfully!",

        # ------------------------------------------------------------------------#
        # ------------------- Backup Wizard Controller ---------------------------#
        # ------------------------------------------------------------------------#
        "bak_ctrl_export_apps_count": "Applications to export: {checked} of {total}",
        "bak_ctrl_total_size": "Total Size (Uncompressed): {size} MB",
        "bak_ctrl_overwrite_term": "Overwrite",
        "bak_ctrl_import_selected": "Selected Applications: {checked} of {total}",
        "bak_ctrl_space_req": "Required Space: {req} MB / Available Space: {free} GB",
        "bak_ctrl_status_no_apps": "Status: No applications selected",
        "bak_ctrl_status_overwrite_warn": "Status: ⚠️ {count} applications will be overwritten!",
        "bak_ctrl_status_new_apps": "Status: All selected applications are new",
        "bak_ctrl_filename": "File Name: {name}",
        "bak_ctrl_status_ready_export": "Status: Ready for export",
        "bak_ctrl_app_item_format": " {name} (v{version})  —  [{size}]",
        "bak_ctrl_filter_7z": "7-Zip Archive (*.7z)",
        "bak_ctrl_filter_zip": "Zip Archive (*.zip)",
        "bak_ctrl_save_title": "Save Transfer File",
        "bak_ctrl_err_dest": "Please select a save path!",
        "bak_ctrl_err_no_select": "No applications selected!",
        "bak_ctrl_import_title": "Select Transfer File",
        "bak_ctrl_import_filter": "Archives (*.7z *.zip)",
        "bak_ctrl_invalid_backup": "The file is not a valid backup (manifest.json missing).",
        "bak_ctrl_ver_prev": "previous",
        "bak_ctrl_ver_next": "newer",
        "bak_ctrl_ver_same": "same",
        "bak_ctrl_app_exists": "{name} (Already exists in {ver} version - Overwrite?)",
        "bak_ctrl_folder_exists": "{name} (Folder already exists - Overwrite?)",
        "bak_ctrl_app_new": "{name} (New - v{ver})",
        "bak_ctrl_dest_title": "Select Application Installation Folder",
        "bak_ctrl_err_source": "Please select the import file (.7z or .zip)!",

        # Database Management
        "db_restore_title": "Database Restoration",
        "db_restore_prompt": "The database was not found, but a backup was detected.\n\nWould you like to restore from the most recent backup?",
        "db_restore_success": "Database restored successfully!",
        "db_restore_error": "Failed to restore database.",
        "act_db_restored": "Database restored from backup",

        # Factory Reset
        "set_factory_reset_title": "Factory Reset",
        "set_factory_reset_confirm": "Are you sure you want to perform a factory reset?\n\nThis will delete all settings, the database, and the activity log. This action cannot be undone!",
        "set_factory_reset_apps_confirm": "Would you also like to delete the folder containing your portable applications?\n\nWarning: This will permanently delete all your installed applications!",
        "set_factory_reset_success_title": "Reset Complete",
        "set_factory_reset_success_msg": "Factory reset completed successfully! All settings and data have been restored to default values.",

        # Update Notifications
        "update_title": "Update Available",
        "update_available": "New Version Available",
        "new_version": "New Version",
        "release_title": "Release",
        "changelog": "Changes",
        "click_below": "Click the button below to download the new version from GitHub.",
        "download_button": "Download",

    }
}


class LanguageManager:
    def __init__(self):
        # Ορίζουμε τα Ελληνικά ως προεπιλογή
        self.current_lang = "el"

    def set_language(self, language_name):
        """ Αλλάζει την ενεργή γλώσσα με βάση το όνομα από τις ρυθμίσεις """
        if language_name in ["English", "en", "Αγγλικά"]:
            self.current_lang = "en"
        else:
            self.current_lang = "el"

    def get_string(self, key, default=""):
        """ Επιστρέφει το μεταφρασμένο κείμενο με βάση το κλειδί """
        return TRANSLATIONS[self.current_lang].get(key, default if default else key)


# Δημιουργούμε ένα κεντρικό αντικείμενο για να το χρησιμοποιούμε παντού
_manager = LanguageManager()

# Η συνάρτηση-συντόμευση που θα καλούμε στα άλλα αρχεία


def _(key, default=""):
    return _manager.get_string(key, default)


def get_current_lang():
    return _manager.current_lang
