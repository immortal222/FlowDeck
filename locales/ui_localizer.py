from locales.localization import _


def localize_main_window(window):
    """Localizes main window titles, sidebar navigation, and sub-headings."""
    window.setWindowTitle(_("wiz_ui_window_title", "FlowDeck"))

    # Sidebar Navigation Titles
    if hasattr(window.ui, 'navTitle_Dashboard'):
        window.ui.navTitle_Dashboard.setText(_("nav_dashboard", "Dashboard"))
    if hasattr(window.ui, 'navTitle_Wizard'):
        window.ui.navTitle_Wizard.setText(_("nav_wizard", "Wizard"))
    if hasattr(window.ui, 'navTitle_Settings'):
        window.ui.navTitle_Settings.setText(_("nav_settings", "Settings"))
    if hasattr(window.ui, 'navTitle_MyApps'):
        window.ui.navTitle_MyApps.setText(_("nav_my_apps", "My Apps"))
    if hasattr(window.ui, 'navTitle_About'):
        window.ui.navTitle_About.setText(_("nav_about", "About"))

    # Sidebar Navigation Subtitles
    if hasattr(window.ui, 'navSub_Dashboard'):
        window.ui.navSub_Dashboard.setText(
            _("nav_sub_dashboard", "Overview & Stats"))
    if hasattr(window.ui, 'navSub_Wizard'):
        window.ui.navSub_Wizard.setText(
            _("nav_sub_wizard", "Add new applications"))
    if hasattr(window.ui, 'navSub_Settings'):
        window.ui.navSub_Settings.setText(
            _("nav_sub_settings", "Maintenance and tools"))
    if hasattr(window.ui, 'navSub_MyApps'):
        window.ui.navSub_MyApps.setText(
            _("nav_sub_my_apps", "Categories and organization"))
    if hasattr(window.ui, 'navSub_About'):
        window.ui.navSub_About.setText(
            _("nav_sub_about", "App info & credits"))


def localize_dashboard_page(window):
    """Localizes labels and section titles on the Dashboard page."""
    if hasattr(window.ui, 'lblDash_Welcome'):
        window.ui.lblDash_Welcome.setText(
            _("dash_welcome", "Welcome back, User!"))
    if hasattr(window.ui, 'lblDash_ActivityTitle'):
        window.ui.lblDash_ActivityTitle.setText(
            _("dash_activity_title", "Recent Activity"))
    if hasattr(window.ui, 'lblDash_TipTitle'):
        window.ui.lblDash_TipTitle.setText(
            _("dash_tips_title", "News & Tips"))
    if hasattr(window.ui, 'lblDash_StatAppsTitle'):
        window.ui.lblDash_StatAppsTitle.setText(
            _("dash_apps_title", "Apps Installed"))
    if hasattr(window.ui, 'lblDash_DiscSpaceTitle'):
        window.ui.lblDash_DiscSpaceTitle.setText(
            _("dash_disc_title", "Disk Space"))
    if hasattr(window.ui, 'lblDash_FavTitle'):
        window.ui.lblDash_FavTitle.setText(
            _("dash_quick_launch", "Quick Launch"))


def localize_myapps_page(window):
    """Localizes titles, search boxes, and buttons on the My Apps page."""
    if hasattr(window.ui, 'myApps_lblTitle'):
        window.ui.myApps_lblTitle.setText(
            _("apps_library_title", "My Apps Library"))
    if hasattr(window.ui, 'myApps_searchBox'):
        window.ui.myApps_searchBox.setPlaceholderText(
            _("apps_search_placeholder", "Search my library..."))
    if hasattr(window.ui, 'myApps_sortCombo'):
        sort_az_label = _("apps_ui_my_apps_sort_az", "Name (A-Z)")
        sort_recent_label = _(
            "apps_ui_my_apps_sort_recent", "Recently Installed")
        sort_update_label = _(
            "apps_ui_my_apps_sort_update", "Update Available")
        sort_favorite_label = _("apps_ui_my_apps_sort_favorite", "Favorite")
        if window.ui.myApps_sortCombo.count() >= 2:
            window.ui.myApps_sortCombo.setItemText(0, sort_az_label)
            window.ui.myApps_sortCombo.setItemText(1, sort_recent_label)
        if window.ui.myApps_sortCombo.findText(sort_update_label) == -1:
            window.ui.myApps_sortCombo.addItem(sort_update_label)
        if window.ui.myApps_sortCombo.findText(sort_favorite_label) == -1:
            window.ui.myApps_sortCombo.addItem(sort_favorite_label)
    if hasattr(window.ui, 'myApps_viewBtn'):
        window.ui.myApps_viewBtn.setText(_("apps_view_grid", "View: Grid"))
    if hasattr(window.ui, 'myApps_updateAllBtn'):
        window.ui.myApps_updateAllBtn.setText(
            _("apps_check_updates", "Check for Updates"))


def localize_settings_page(window):
    """Localizes all Settings page components including Tabs, Groups, and Buttons."""
    ui = window.ui

    # System Tab
    if hasattr(ui, 'group_installation'):
        ui.group_installation.setTitle(
            _("set_ui_group_install_path", "INSTALLATION FOLDER"))
    if hasattr(ui, 'btn_browsePath'):
        ui.btn_browsePath.setText(_("set_ui_btn_browse_path", "Browse..."))
    if hasattr(ui, 'btn_openPath'):
        ui.btn_openPath.setText(_("set_ui_btn_open_path", "Open Folder"))
    if hasattr(ui, 'group_systemOptions'):
        ui.group_systemOptions.setTitle(
            _("set_ui_group_system_options", "SYSTEM OPTIONS"))
    if hasattr(ui, 'chk_startOnBoot'):
        ui.chk_startOnBoot.setText(
            _("set_ui_chk_start_on_boot", "Start on Windows Boot"))
    if hasattr(ui, 'chk_minimizeToTray'):
        ui.chk_minimizeToTray.setText(
            _("set_ui_chk_minimize_to_tray", "Minimize to System Tray on close"))
    if hasattr(ui, 'chk_updateToStart'):
        ui.chk_updateToStart.setText(
            _("set_ui_chk_update_to_start", "Check for FlowDeck Updates on Start"))
    if hasattr(ui, 'group_language'):
        ui.group_language.setTitle(
            _("set_ui_group_language", "APPLICATION LANGUAGE"))
    if hasattr(ui, 'settingsTabWidget'):
        ui.settingsTabWidget.setTabText(0, _("set_ui_tab_system", "System"))

    # Appearance Tab
    if hasattr(ui, 'group_theme'):
        ui.group_theme.setTitle(_("set_ui_group_theme", "APPLICATION THEME"))
    if hasattr(ui, 'settingsTabWidget'):
        ui.settingsTabWidget.setTabText(
            1, _("set_ui_tab_appearance", "Appearance"))

    # Updates Tab
    if hasattr(ui, 'group_updateFreq'):
        ui.group_updateFreq.setTitle(
            _("set_ui_group_update_freq", "CHECK FREQUENCY"))
    if hasattr(ui, 'chk_enableSilentUpdater'):
        ui.chk_enableSilentUpdater.setText(
            _("set_ui_chk_silent_updater", "Silent background update checks (no notifications)"))
    if hasattr(ui, 'group_updateStatus'):
        ui.group_updateStatus.setTitle(
            _("set_ui_group_update_status", "UPDATE STATUS"))
    if hasattr(ui, 'lbl_lastCheckTime'):
        ui.lbl_lastCheckTime.setText(
            _("set_ui_lbl_last_check", "Last check: never"))
    if hasattr(ui, 'btn_checkUpdatesNow'):
        ui.btn_checkUpdatesNow.setText(
            _("set_ui_btn_check_now", "Check Now"))
    if hasattr(ui, 'settingsTabWidget'):
        ui.settingsTabWidget.setTabText(
            2, _("set_ui_tab_updates", "Updates"))

    # Maintenance Tab
    if hasattr(ui, 'group_dataMaintenance'):
        ui.group_dataMaintenance.setTitle(
            _("set_ui_group_maintenance", "DATA MAINTENANCE"))
    if hasattr(ui, 'btn_clearActivityLog'):
        ui.btn_clearActivityLog.setText(
            _("set_ui_btn_clear_log", "Clear Activity Log"))
    if hasattr(ui, 'btn_resetDefaults'):
        ui.btn_resetDefaults.setText(
            _("set_ui_btn_reset_defaults", "Reset to Factory Defaults"))
    if hasattr(ui, 'btn_backupApps'):
        ui.btn_backupApps.setText(
            _("set_ui_btn_backup_apps", "Create Backup of Applications"))
    if hasattr(ui, 'btn_scanAndRepair'):
        ui.btn_scanAndRepair.setText(
            _("set_ui_btn_scan_folder", "Auto-Maintain Applications (Scan)"))
    if hasattr(ui, 'settingsTabWidget'):
        ui.settingsTabWidget.setTabText(
            3, _("set_ui_tab_maintenance", "Maintenance"))

    if hasattr(ui, 'btn_saveSettings'):
        ui.btn_saveSettings.setText(
            _("set_ui_btn_save_settings", "Save Settings"))


def localize_backup_wizard(dialog):
    """Localizes the Backup & Restore Wizard dialog components."""
    ui = dialog.ui if hasattr(dialog, 'ui') else dialog

    if hasattr(ui, 'lbl_wizardTitle'):
        ui.lbl_wizardTitle.setText(
            _("wiz_backup_title", "Backup & Restore Wizard"))

    # TAB 1: EXPORT (BACKUP)
    if hasattr(ui, 'lbl_fdaSelect'):
        ui.lbl_fdaSelect.setText(
            _("wiz_Backup_exp_select", "Select Applications for export:"))
    if hasattr(ui, 'cbx_fdaAll'):
        ui.cbx_fdaAll.setText(
            _("wiz_Backup_btn_all", "Select All"))
    if hasattr(ui, 'lbl_fdaSave'):
        ui.lbl_fdaSave.setText(
            _("wiz_Backup_exp_dest", "Where should the Backup be saved?"))
    if hasattr(ui, 'txt_fdaPath'):
        ui.txt_fdaPath.setPlaceholderText(
            _("wiz_Backup_exp_dest_ph", "C:\\Backups\\FlowDeck.zip"))
    if hasattr(ui, 'btn_fdaBrowse'):
        ui.btn_fdaBrowse.setText(
            _("wiz_Backup_btn_browse", "Browse..."))

    if hasattr(ui, 'lbl_fdaCompress'):
        ui.lbl_fdaCompress.setText(
            _("wiz_Backup_exp_compress", "Compression Level:"))
    if hasattr(ui, 'rad_fast_zip'):
        ui.rad_fast_zip.setText(
            _("wiz_Backup_exp_fast_zip", "Fast Compression"))
    if hasattr(ui, 'rad_ultra_7z'):
        ui.rad_ultra_7z.setText(
            _("wiz_Backup_exp_ultra_7z", "Maximum Ultra Compression (will take several minutes)"))

    if hasattr(ui, 'btn_createFdaArchive'):
        ui.btn_createFdaArchive.setText(
            _("wiz_Backup_btn_start_export", "CREATE BACKUP 📤"))

    # TAB 2: IMPORT (RESTORE)
    if hasattr(ui, 'lbl_importSelect'):
        ui.lbl_importSelect.setText(
            _("wiz_Backup_imp_select", "Select Applications for import:"))
    if hasattr(ui, 'cbx_importAll'):
        ui.cbx_importAll.setText(
            _("wiz_Backup_btn_all", "Select All"))
    if hasattr(ui, 'lbl_importSource'):
        ui.lbl_importSource.setText(
            _("wiz_Backup_imp_source", "Select File:"))
    if hasattr(ui, 'btn_importSourceBrowse'):
        ui.btn_importSourceBrowse.setText(
            _("wiz_Backup_btn_browse", "Browse..."))
    if hasattr(ui, 'lbl_importDestination'):
        ui.lbl_importDestination.setText(
            _("wiz_Backup_imp_dest", "Where should the Portable apps be installed?"))
    if hasattr(ui, 'txt_importDestinationPath'):
        ui.txt_importDestinationPath.setPlaceholderText(
            _("wiz_Backup_imp_dest_ph", "C:\\FlowDeckApps"))
    if hasattr(ui, 'btn_importDestinationBrowse'):
        ui.btn_importDestinationBrowse.setText(
            _("wiz_Backup_btn_browse", "Browse..."))
    if hasattr(ui, 'cbx_importSetting'):
        ui.cbx_importSetting.setText(
            _("wiz_Backup_imp_settings", "Import Application Settings"))

    # Import Summary Information
    if hasattr(ui, 'lbl_importInfo'):
        ui.lbl_importInfo.setText(_("wiz_Backup_info", "Information"))
    if hasattr(ui, 'lblwIZ_SummarySize'):
        ui.lblwIZ_SummarySize.setText(
            _("wiz_Backup_size", "Required Disk Space:"))
    if hasattr(ui, 'lblWiz_FileName'):
        ui.lblWiz_FileName.setText(
            _("wiz_Backup_filename", "File Name:"))
    if hasattr(ui, 'lblWiz_SummaryApps'):
        ui.lblWiz_SummaryApps.setText(
            _("wiz_Backup_imp_apps", "Applications for import:"))
    if hasattr(ui, 'lblWiz_CurrentAction'):
        ui.lblWiz_CurrentAction.setText(
            _("wiz_Backup_status", "Status:"))
    if hasattr(ui, 'btn_startImport'):
        ui.btn_startImport.setText(
            _("wiz_Backup_btn_start_import", "RESTORE BACKUP 📥"))

    # Footer Buttons
    if hasattr(ui, 'btn_closeWizard'):
        ui.btn_closeWizard.setText(
            _("wiz_Backup_btn_close", "Cancel"))


def localize_wizard_page(controller):
    """Localizes static elements of the Installation Wizard page."""
    ui = controller.ui

    ui.wizard_lblTitle.setText(
        _("wiz_ui_wizard_title", "Install & Update Applications"))
    ui.wizard_lblSubTitle.setText(
        _("wiz_ui_wizard_subtitle", "The application installation wizard"))

    if hasattr(ui, 'dropLabel'):
        ui.dropLabel.setText(
            _("wiz_ui_drop_label", "Drag and drop .zip file here or click browse"))

    ui.lblPath_wizard.setText(_("wiz_ui_lbl_path", "File Path"))
    ui.filePathInput.setPlaceholderText(
        _("wiz_ui_path_placeholder", "Zip file path..."))
    ui.browseButton.setText(_("wiz_ui_btn_browse", "Browse File..."))

    ui.lblAppName_wizard.setText(_("wiz_ui_lbl_app_name", "Application Name"))
    ui.appNameInput.setPlaceholderText(
        _("wiz_ui_app_name_placeholder", "e.g., Firefox Portable"))

    ui.lblCategory_wizard.setText(_("wiz_ui_lbl_category", "Category"))
    ui.installButton.setText(_("wiz_ui_btn_install", "Install Application"))

    if hasattr(ui, 'sidebarTitle'):
        ui.sidebarTitle.setText(_("wiz_ui_sidebar_title", "Application"))
    if hasattr(ui, 'sidebarUrlBtn'):
        ui.sidebarUrlBtn.setText(
            _("wiz_ui_sidebar_url_btn", "🌐 Official Site"))
    if hasattr(ui, 'lblConsole_wizard'):
        ui.lblConsole_wizard.setText(
            _("wiz_ui_lbl_console", "Live Log / Console"))

    ui.sidebarTitle.setText(_("wiz_ui_sidebar_title", "Application"))

    # Tab Navigation Titles
    if hasattr(ui, 'tabs_Backup'):
        ui.tabs_Backup.setTabText(
            0, _("wiz_Backup_tab_export", "EXPORT (BACKUP)"))
        ui.tabs_Backup.setTabText(
            1, _("wiz_Backup_tab_import", "IMPORT (RESTORE)"))
