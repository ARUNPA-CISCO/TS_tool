import os
import sys
from datetime import date
import time
import json
import platform
import re
from time import strptime
from datetime import datetime, timedelta
from pathlib import Path
from datetime import time

FTD_TROUBLESHOOT_PATH = ""
FMC_TROUBLESHOOT_PATH = ""

# dictionary which contains falied script to cdets component mapping
# Link - https://confluence-eng-rtp2.cisco.com/conf/pages/viewpage.action?spaceKey=DEV&title=Upgrade+scripts+and+components
component_map = {
    "000_start": {
        "000_start/000_00_run_cli_kick_start.sh": "ftd_upgrade",
        "000_start/000_00_run_troubleshoot.sh": "ftd_upgrade",
        "000_start/000_0_start_upgrade_status_api_stack.sh": "ftd_onbox", # update confluence
        "000_start/000_check_platform_support.sh": "ftd_upgrade",
        "000_start/000_check_update.sh": "ftd_upgrade",
        "000_start/000_db_schema_check.sh": "fmc_upgrade",
        "000_start/100_start_messages.sh": "ftd_upgrade",
        "000_start/101_run_pruning.pl": {
            "Could not connect to MariaDB.": "db_mariadb",
            "Failed when preparing statement": "db_mariadb",
            "Can't execute statement": "db_mariadb",
            "all": "ftd_upgrade"
        },
        "000_start/105_check_model_number.sh": "ftd_upgrade",
        "000_start/106_check_HA_state.pl": "Project: CSC.netbu, Product: pix-asa, Component: ha",
        "000_start/106_check_HA_updates.pl": "dc_ha",
        "000_start/107_version_check.sh": "ftd_upgrade",
        "000_start/108_clean_user_stale_entries.pl": "fmc-auth",
        "000_start/110_DB_integrity_check.sh": "db_framework",
        "000_start/113_EO_integrity_check.pl": "enterprise_obj_fw",
        "000_start/200_clean_csp_files.sh": "platform_support",
        "000_start/250_check_system_files.sh": "ftd_upgrade",
        "000_start/320_remove_backups.sh": "ftd_upgrade",
        "000_start/410_check_disk_space.sh": "ftd_upgrade"
    },
    "200_pre": {
        "200_pre/001_check_reg.pl": {
            "Process Manager is not up. Cannot continue.": "os_packages",
            "Device registration in progress.": "ftd_registration"
        },
        "200_pre/002_check_mounts.sh": "fmc_upgrade",
        "200_pre/004_check_deploy_package.pl": "policy_apply",
        "200_pre/005_check_manager.pl": "ftd_upgrade",
        "200_pre/006_check_snort.sh": "ftd_upgrade",
        "200_pre/007_check_sru_install.sh": "sru_install",
        "200_pre/009_check_snort_preproc.sh": "sru_install",
        "200_pre/011_check_self.sh": "ftd-upgrade",
        "200_pre/015_verify_rpm.sh": "ftd_upgrade",
        "200_pre/100_check_dashboards.pl": "dashboard-ui",
        "200_pre/100_get_snort_from_dc.pl": "ftd_upgrade",
        "200_pre/110_setup_upgrade_ui.sh": "fmc_upgrade",
        "200_pre/120_generate_auth_for_upgrade_ui.pl": "fmc_upgrade",
        "200_pre/152_save_etc_sf.sh": "ftd_upgrade",
        "200_pre/199_before_maintenance_mode.sh": "ftd_upgrade",
        "200_pre/200_enable_maintenance_mode.pl": "Project: CSC.netbu, Product: pix-asa, Component: ha",
        "200_pre/202_disable_syncd.sh": "ftd_upgrade",
        "200_pre/400_restrict_rpc.sh": "ftd_upgrade",
        "200_pre/500_stop_system.sh": "ftd_upgrade",
        "200_pre/501_recovery.sh": "fmc_upgrade",
        "200_pre/504_db_tempmerge_check.sh": "fmc_upgrade",
        "200_pre/505_revert_prep.sh": {
            "Could not restart mysqld.": "db_config",
            "Cannot backup database. MRG_MYISAM tables still exist!": "db_config",
            "Could not stop mysqld/ Mysql backup failed.": "db_config",
            "all": "ftd_upgrade"
        },
        "200_pre/600_ftd_onbox_data_export.sh": "upgrade (Product: ftd-onbox)",
        "200_pre/999_enable_sync.sh": "ftd_upgrade"
    },
    "300_os": {
        "300_os/001_verify_bundle.sh": "ftd_upgrade",
        "300_os/002_set_auto_neg.pl": "ftd_upgrade",
        "300_os/060_fix_fstab.sh": "os_kernel",
        "300_os/100_install_Fire_Linux_OS_aquila.sh": "ftd_upgrade",
        "300_os/100_install_Fire_Linux_OS_aquila_ssp.sh": "ftd_upgrade",
        "300_os/300_python2_pth.sh": "ftd_upgrade"
    },
    "475_schema_downgrade": {
        "475_schema_downgrade/100_revert_database.sh": "db_config",
    },
    "500_rpms": {
        "500_rpms/001_clean_up_ddd.sh": "fmc_upgrade",
        "500_rpms/100_install_rpms.sh": "ftd_upgrade",
        "500_rpms/100_restore_configs.sh": "fmc_upgrade",
        "500_rpms/101_install_fsic.sh": "fmc_upgrade",
        "500_rpms/105_restore_symlinks.sh": "ftd_upgrade",
        "500_rpms/106_restore_SFDC.sh": "ftd_upgrade",
        "500_rpms/107_restore_sftunnel.sh": "ftd_upgrade",
        "500_rpms/108_restore_iptables.sh": "ftd_upgrade",
        "500_rpms/110_generate_dbaccess.sh": "rep-services",
        "500_rpms/111_restore_connector_config.sh": "licensing (Product: ftd-onbox)",
        "500_rpms/112_restore_securex_properties.sh": "fmc_upgrade",
        "500_rpms/200_remove_dynpre.sh": "fmc_upgrade",
        "500_rpms/200_remove_snort.sh": "fmc_upgrade",
        "500_rpms/201_install_snort_dynamic_preprocessors.sh": "fmc_upgrade",
        "500_rpms/210_backup_gwt_files.sh": "fmc_upgrade",
        "500_rpms/215_update_mysql.sh": "fmc_upgrade",
        "500_rpms/216_update_monetdb.sh": "fmc_upgrade",
        "500_rpms/300_examine_vmware_tools.sh": "virtual_platform",
        "500_rpms/500_install_files.sh": "ftd_install",
        "500_rpms/550_configure_mysql.pl": "db_mariadb",
        "500_rpms/800_update_slackpackages_ftd.sh": {
            "Linux kernel packages for FTD is not expected.": "os_packages",
            "all": "ftd_upgrade"
        }
    },
    "600_schema": {
        "600_schema/100_update_database.sh": "db_framework",
        "600_schema/110_post_update_dbic.sh": "db_framework",
        "600_schema/099_pre_multischema.pl": "db_framework",
        "600_schema/109_multischema.pl": "db_framework",
        "600_schema/911_clean_sym_triggers.pl": "fmc_upgrade"
    },
    "800_post": {
        "800_post/100_ftd_onbox_data_import.sh": "upgrade (Product: ftd-onbox)",
        "800_post/901_reapply_sensor_policy.pl": "policy_apply",
        "800_post/005_extra_peer_info.pl": "dc_ha",
        "800_post/010_install_vmware_tools.sh": "virtual_platforms",
        "800_post/010_update_vmware_tools.sh": "virtual_platforms",
        "800_post/011_reconfigure_model_pack.sh": "fmc_modelpack",
        "800_post/015_configure_offbox.sh": "ftd_onbox",
        "800_post/021_reinstall_sru.sh": "sru_install",
        "800_post/110_update_perms_logrotate_conf.sh": "fmc_upgrade",
        "800_post/150_install_infodb.sh": "db_framework",
        "800_post/720_update_devices.pl": "fmc_upgrade",
        "800_post/780_remove_future_flagsconf.pl": "fmc_upgrade",
        "800_post/810_update_ld_conf.sh": "fmc_upgrade",
        "800_post/850_clear_eula.sh": "fmc_upgrade",
        "800_post/860_eo_convert.pl": "enterprise_obj_fw",
        "800_post/870_update_fireamp_cert.sh": "fmc_upgrade",
        "800_post/900_replace_snort.pl": "ftd_upgrade",
        "800_post/900_set_locale.pl": "dashboard-ui",
        "800_post/910_Edit_AC_Policy.pl": "system-csm-rpm",
        "800_post/950_feature_applied.sh": "fmc_upgrade",
        "800_post/980_health_modules.pl": "fmc_hm",
        "800_post/985_remediation_modules.sh": "remediation",
        "800_post/990schedule_tasks_register.pl": "fmc_upgrade",
        "800_post/998_expire_ac_policy.pl": "system-csm-rpm",
        "800_post/016_fix_sru_import_log.pl": "sru_install",
        "800_post/018_fix_ruleconfigs_in_layer.pl": "sru_install",
        "800_post/080_clear_temp_si_dir.pl": "rep-services",
        "800_post/150_install_infodb.sh": "db_framework",
        "800_post/240_saved_searches.pl": "reporting",
        "800_post/303_threat_beaker.pl": "rep-services",
        "800_post/810_clean_upgrade_workflow.sh": "os_kernel",
        "800_post/880_install_VDB.sh": "install_vdb",
        "800_post/890_install_version_masked_apps.pl": "app_detectors-ui",
        "800_post/900_720_create_event_handler_uec_config.pl": "reporting",
        "800_post/910_Edit_AC_Policy.pl": "system-csm-rpm",
        "800_post/910_compliance_mode_reapply_templates.pl": "os_packages",
        "800_post/961_clear_archives.pl": "policy_apply",
        "800_post/991_update_scheduled_tasks.pl": "vdb_upgrade",
        "800_post/998_update_vdb_package.sh": "install_vdb",
        "800_post/1027_ldap_external_auth_fix.pl": "fmc_auth",
        "800_post/1031_generate_default_ssl_cert.pl": "fmc_ui-syslog_cert",
        "800_post/1033_fmc_healthmon.pl": "fmc_hm",
        "800_post/1060_update_notification_table.pl": "policy_apply"
    },
    "999_finish": {
        "999_finish/200_post_upgrade_aquila.sh": "os_packages",
        "999_finish/200_post_upgrade_aquila_ssp.sh": "os_packages",
        "999_finish/500_clean_prev_version_var_partition.sh": "os_packages",
        "999_finish/800_update_version.sh": "ftd_upgrade",
        "999_finish/801_extra_peer_info.pl": "policy_apply",
        "999_finish/801_install_help.sh": "db_config",
        "999_finish/918_upgrade_mysql.sh": {
            "Old-root mysql never shutdown.": "db_maridb",
            "Other mysql proccess found.  Exiting.": "db_maridb",
            "new-root mysql never started.": "db_maridb",
            "Exiting: mariadb-upgrade failed with error code:": "db_maridb",
            "new-root mysql failed to stop": "db_maridb",
            "new-root mysql failed to start": "db_maridb",
            "all": "ftd_upgrade"
        },
        "999_finish/920_enable_all_rpc.sh": "comms",
        "999_finish/980_update_usb.sh": "os_packages",
        "999_finish/988_reconfigure_model.sh": "os_packages",
        "999_finish/989_update_bootos_aquila.sh": "ftd_upgrade",
        "999_finish/989_update_ngfw_conf_aquila.sh": "ftd_upgrade",
        "999_finish/989_update_ngfw_conf_aquila_ssp.sh": "platform_support",
        "999_finish/999_enable_syncd.sh": "ftd_upgrade",
        "999_finish/999_l_disable_recovery.sh": "ftd_upgrade",
        "999_finish/999_leave_maintenance_mode.pl": {
            "Failed to add ExitMaintenanceMode task": "db_config",
            "all": "ftd_upgrade"
        },
        "999_finish/999_rm_old_var.sh": "ftd_upgrade",
        "999_finish/999_y02_python2_pth_clean.sh": "db_framework",
        "999_finish/999_z_must_remain_last_finalize_boot.sh": "ftd_upgrade",
        "999_finish/999_zz_install_bundle.sh": "ftd_upgrade",
        "999_finish/999_zzz_complete_upgrade_message.sh": "ftd_upgrade",
        "999_finish/999_zzz_verify_fsic.sh": "ftd_upgrade"
    }
}


def parse_timestamp(line, prefix="TIMESTAMP:"):
    try:
        start_idx = line.find(prefix) + len(prefix)
        timestamp_str = line[start_idx:].split(" ")[0:5]
        timestamp_str = " ".join(timestamp_str)
        return datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Z %Y")
    except ValueError:
        return None


def get_timestamps(log_file, start_keyword="Running script 999_finish/999_zzz_verify_fsic.sh",
                   end_keyword="Fatal error:  Error running script 999_finish/999_zzz_verify_fsic.sh."):
    start_timestamp, end_timestamp = None, None

    with open(log_file, 'r') as file:
        lines = file.readlines()

    for line in reversed(lines):
        if end_keyword in line and "TIMESTAMP:" in line and end_timestamp is None:
            end_timestamp = parse_timestamp(line)
        elif start_keyword in line and "TIMESTAMP:" in line and start_timestamp is None:
            start_timestamp = parse_timestamp(line)
        if start_timestamp and end_timestamp:
            break

    return start_timestamp, end_timestamp


def find_lines_between_timestamps(log_file, start_timestamp, end_timestamp, keyword="verify_failed"):
    with open(log_file, 'r') as file:
        lines = file.readlines()
    result_lines = []
    for line in reversed(lines):
        if keyword in line:
            timestamp = parse_timestamp(line)
            if timestamp and start_timestamp <= timestamp <= end_timestamp:
                result_lines.append(line)

    return result_lines


# function to print logs from failed script
def printLogs(stage, reason, package_folder, path):
    # build the path to the failed script
    path += "/dir-archives/var-log/sf/"
    path += package_folder
    path += "/"
    path += stage
    path += ".log"

    print("Upgrade failed at stage: ", stage)
    lines = []
    component = ""

    failed_script = stage
    ind = failed_script.rfind("/")
    comp_map = component_map[failed_script[:ind]][failed_script]

    if "999_zzz_verify_fsic.sh" in failed_script:
        upgrade_log = path.replace("999_finish/999_zzz_verify_fsic.sh", "upgrade.log")
        verify_log = path.replace(package_folder + "/999_finish/999_zzz_verify_fsic.sh", "verify_file_integ.log")
        start_timestamp, end_timestamp = get_timestamps(upgrade_log)
        if start_timestamp and end_timestamp:
            verify_failed_lines = find_lines_between_timestamps(verify_log, start_timestamp, end_timestamp)
            for line in verify_failed_lines:
                if "verify failed" in line:
                    print(line)
                    if "lsp" in line:
                        print("Suggested Component: lsp")
                    elif "appid" in line or "navl" in line or "vdb" in line or "mercury" in line:
                        print("Suggested Component: vdb")
                    elif "snort" in line:
                        print("Suggested Component: snort")
                    else:
                        print("Suggested Component: ftd_upgrade")
                    break
        return
    elif "200_enable_maintenance_mode.pl" in failed_script:
        ngfwManagerlogpath = path.replace("sf/" + package_folder + "200_pre/200_enable_maintenance_mode.pl", "ngfwManager.log")
        with open(ngfwManagerlogpath, 'r') as file:
            ngfw_manager = file.read()

        if "line protocol is down >>>>>>>> Failover ifc's both admin and protocol are DOWN" in ngfw_manager:
            print("Reason for failure: Failover ifc's both admin and protocol are DOWN")
            print("Suggested Component: app_agent")
            return


    if isinstance(comp_map, dict):
        with open(path, 'r') as file:
            log_content = file.read()

        for error, value in comp_map.items():
            if error in log_content:
                component = value
                break
        else:
            component = comp_map["all"];
    else:
        component = comp_map

    # retrieve last 10 logs from failed script
    f = open(path, 'r')
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip('\n')
        lines.append(line)
    lines = lines[-10:]

    # print the logs retrieved
    print("Logs from " + failed_script + ".log: ")
    for line in lines:
        print(line)

    print("Reason for failure: ", reason)
    print("Suggested Component: ", component)


def checkIssues(date1, time1, date2, time2, path):
    print()
    path += "/dir-archives/var-log"
    os.chdir(path)

    messages_log = "messages"
    flag = 0
    error_strings = ["HMAC verification reached timeout", "Failed to connect to tunnel", "ShutDownPeer"]
    f = open(messages_log, 'r')
    while True:
        line = f.readline()
        if not line:
            break
        for error_string in error_strings:
            if error_string in line:
                timestamp = line[:15]
                try:
                    curr_date = date(date1.year, strptime(timestamp[0:3], '%b').tm_mon, int(timestamp[4:6]))
                    curr_time = time(int(timestamp[7:9]), int(timestamp[10:12]), int(timestamp[13:15]))
                    if (curr_date >= date1 and curr_time > time1) and (curr_date <= date2 and curr_time < time2):
                        flag = 1
                        print(line.strip('\n'))
                except:
                    pass

    if flag == 0:
        print("Error strings not found")
        return 0
    print("\nCould be an intermittent network issue")
    print("Could be some sftunnel/platform issue\n")
    print("Component: Please reach out to sftunnel/FMC team/management interface")
    print("Suggested Component: comms")


# function to compare current timestamp with timestamp from main_upgrade_script.log(FTD) or action_queue.log(FMC)
def isTimestampValid(timestamp, date1, time1):
    month = strptime(timestamp[0:3], '%b').tm_mon
    day = timestamp[4:6]
    hour = timestamp[7:9]
    minute = timestamp[10:12]
    seconds = timestamp[13:15]
    date2 = date(date1.year, month, int(day))
    time2 = time(int(hour), int(minute), int(seconds))

    if date2 >= date1 and time2 > time1:
        return True
    return False


# function to retrieve errors from messages log
def retrieveErrors(date1, time1):
    messages_log = "messages"
    unique_error_logs = {}
    error_logs = []  # stores unique error logs sorted a/c to timestamp
    reconnectTimestamp = datetime.combine(date1, time1) + timedelta(hours=1.5)

    f = open(messages_log, 'r')
    while True:
        line = f.readline()
        if not line:
            break
        timestamp = line[:15]
        try:
            currentTimestamp = datetime(date1.year, strptime(timestamp[0:3], '%b').tm_mon, int(timestamp[4:6]),
                                        int(timestamp[7:9]), int(timestamp[10:12]), int(timestamp[13:15]))
            if currentTimestamp > reconnectTimestamp:
                break
        except:
            continue
        if "[ERROR]" in line:
            if isTimestampValid(timestamp, date1,
                                time1):  # current timestamp must be greater than timestamp from main_upgrade_script.log
                time2 = time(int(timestamp[7:9]), int(timestamp[10:12]), int(timestamp[13:15]))
                ind = line.find("[ERROR]")
                error_log = line[ind:]
                error_log = error_log.strip('\n')
                if unique_error_logs.get(error_log, 0) == 0:
                    unique_error_logs[error_log] = 1
                    error_logs.append(str(time2) + " " + error_log)

    return error_logs


# fucntion to check for errors from messages log from both ftd and fmc side
def checkErrors(date1, time1, path):
    path += "/dir-archives/var-log"
    os.chdir(path)
    print("Checking for errors from ftd: " + path + "/messages")

    error_logs = retrieveErrors(date1, time1)
    print("Error logs from ftd: ")
    for error_log in error_logs:
        print(error_log)

    path = FMC_TROUBLESHOOT_PATH
    path += "/dir-archives/var-log"
    os.chdir(path)
    print("Checking for errors from fmc: " + path + "/messages")

    error_logs = retrieveErrors(date1, time1)
    print("Error logs from fmc: ")
    for error_log in error_logs:
        print(error_log)


# function to check status of ftd upgrade
def checkFMCStatus(date1, time1, device_name):
    path = FMC_TROUBLESHOOT_PATH
    path += "/command-outputs"
    os.chdir(path)
    # os.chdir(FMCLOG_DIREC)
    print("Checking ftd upgrade status from fmc: " + path + "/mysql.select_all_from_action_queue")
    mysql_file = "mysql.select_all_from_action_queue"

    flag1 = 0
    flag2 = 0
    timestamp = ""  # timestamp of upgrade status on fmc
    status = ""  # status of the upgrade
    f = open(mysql_file, 'rb')
    while True:
        line = f.readline()
        if not line:
            break
        # print(line)
        if b"row" in line:
            flag1 = 0
            flag2 = 0
        if b"description: Apply Cisco" in line and b"Upgrade" in line and device_name.encode('utf-8') in line:
            flag1 = 1
        elif flag1 == 1 and b"last_state_change" in line:  # check if current timestamp is valid
            line = str(line, 'UTF-8')
            line = line.strip('\n')
            ind = line.find(":")
            timestamp = line[ind + 2:]
            date2 = date(int(timestamp[0:4]), int(timestamp[5:7]), int(timestamp[8:10]))
            time2 = time(int(timestamp[11:13]), int(timestamp[14:16]), int(timestamp[17:19]))
            if date2 >= date1 and time2 > time1:
                flag1 = 0
                flag2 = 1
            else:
                flag1 = 0
                flag2 = 0
        elif flag2 == 1 and b"message" in line:  # retrieve upgrade status
            line = str(line, 'UTF-8')
            line = line.strip('\n')
            ind = line.find(":")
            status = line[ind + 2:]
            break

    print("Upgrade status timestamp on FMC: ", timestamp)
    return [timestamp, status]


# function to retrieve timestamp when device goes for reboot, after all scripts ran successfuly
def getRebootTimestamp(package_folder, path):
    path += "/dir-archives/var-log/sf/"
    path += package_folder
    os.chdir(path)
    print("Retrieving timestamp when device goes for reboot from: " + path + "/main_upgrade_script.log")
    f = open("main_upgrade_script.log", 'r')
    timestamp = []  # timestamp when all scripts ran successfully and device goes for reboot

    while True:
        line = f.readline()
        if not line:
            break
        if "MAIN_UPGRADE_SCRIPT_END" in line:  # check for the keyword in the line
            # date
            timestamp.append("20" + line[1:3])
            timestamp.append(line[3:5])
            timestamp.append(line[5:7])
            # time
            timestamp.append(line[8:10])
            timestamp.append(line[11:13])
            timestamp.append(line[14:16])
            break

    return timestamp


# function to check post update status
def postUpdateValidation(package_folder, path):
    path += "/dir-archives/var-log/sf/"
    path += package_folder
    os.chdir(path)
    print("Checking post upgrade status from: " + path + "/upgrade_status.json")
    json_file = "upgrade_status.json"
    flag = 0  # boolean value for checking post upgrade status

    f = open(json_file, 'r')
    data = json.load(f)

    sub_state = data["upgradeStatus"]["subState"]
    print(sub_state)
    if sub_state == "POST_UPGRADE_VALIDATION_COMPLETED":
        flag = 1

    return flag


# function to check upgrade status from ftd side
def checkDatabase(path):
    path += "/dir-archives/var-log/action_queue.log"
    print("Checking upgrade status from action_queue.log: " + path)

    exited_maintenance_mode = 0  # boolean value for checking exit status
    device_upgraded = 0  # boolean value for checking successful upgrade status

    with open(path, 'r') as file:
        lines = file.readlines()[::-1]

    for i, line in enumerate(lines):
        # Check if line contains "Exited Maintenance Mode"
        if exited_maintenance_mode == 0:
            if "Exited Maintenance Mode" in line:
                exited_maintenance_mode = 1

            # Check for "PM STATUS:  * - Down" pattern
            if "PM STATUS:" in line and " - Down" in line:
                # Check if the previous line (in reversed order) contains "Some critical processes are not running."
                if i + 1 < len(lines) and "Some critical processes are not running." in lines[i + 1]:
                    # Extract and print the * value from "PM STATUS:  * - Down"
                    status = line.split("PM STATUS:")[1].split("- Down")[0].strip()
                    match = re.search(r'\(([^)]+,)?(\w+)\)', status)
                    if match:
                        process_name = match.group(2)
                        print("Device failed to exit Maintenance mode since critical process not running: ",
                              process_name)
                        print("Suggested Component: ", process_name)
                    return 0

        if "Device successfully upgraded" in line or "Update Installed successfully" in line:
            device_upgraded = 1
            break

    return exited_maintenance_mode and device_upgraded


# function to check upgrade status from ftd side
def checkFTDStatus(package_folder, path, status):
    value = [0, 0]

    flag = checkDatabase(path)
    if flag == 1:
        value[0] = 1
        flag = postUpdateValidation(package_folder, path)
        if flag == 1:
            value[1] = 1
            print("Upgrade successful from " + status[3] + " to " + status[4] + " from FTD side.")
    else:
        print("uiMessage: ", status[6])

    return value


# function to retieve necessary info from upgrade_status.json
def getJson(package_folder, path):
    path += "/dir-archives/var-log/sf/"
    path += package_folder
    os.chdir(path)
    print("Retrieving upgrade info from: " + path + "/upgrade_status.json")
    json_file = "upgrade_status.json"
    value = []

    try:
        f = open(json_file, 'r')
        data = json.load(f)

        upgrade_status = data["upgradeStatus"]["status"]
        current_state = data["currentState"]
        task_uuid = data["taskUuid"]
        base_version = data["baseVersion"]
        target_version = data["targetVersion"]
        failed_script = data["upgradeStatus"]["failedScript"]
        ui_message = data["upgradeStatus"]["uiMessage"]
        device_name = data["deviceName"]
        device_ip = data["deviceIp"]
        value.append(upgrade_status)
        value.append(current_state)
        value.append(task_uuid)
        value.append(base_version)
        value.append(target_version)
        value.append(failed_script)
        value.append(ui_message)
        value.append(device_name)
        value.append(device_ip)
        value.append(data["upgradePackageFilename"])
    except:
        print("Error opening/parsing JSON file")

    print("Upgrade info: ")
    print(value)
    return value


def checkReadiness(package_folder, path):
    path += "/dir-archives/var-log/sf"
    path += package_folder
    os.chdir(path)
    print("Checking readiness from: " + path + "upgrade_readiness/upgrade_readiness_status.json")
    json_file = "upgrade_readiness/upgrade_readiness_status.json"
    if not os.path.exists(json_file):
        print("Upgrade Readiness not performed")
        return 1
    f = open(json_file, 'r')
    data = json.load(f)
    readiness_status = data["upgradeReadinessStatus"]
    detailed_failure = readiness_status["detailedFailure"]
    if len(detailed_failure) == 0:
        print("Upgrade Readiness Successful")
        return 1
    for entry in detailed_failure:
        name_path = entry["name"].split('/')[-2:]
        result = "/".join(name_path)
        directory = name_path[0]
        comp_map = component_map[directory][result]
        log_file = path + "/upgrade_readiness/" + result + ".log"
        print("Upgrade Readiness Failed: ", result)
        if isinstance(comp_map, dict):
            with open(log_file, 'r') as file:
                log_content = file.read()
            for error, value in comp_map.items():
                if error in log_content:
                    print("Suggested Component: ", value)
                    break
            else:
                print("Suggested Component: ", comp_map["all"])
        else:
            print("Suggested Component: ", comp_map)
    return 0


# function to retrieve timestamp when upgrade gets triggered on ftd
def getUpgradeTriggerTimestamp():
    path = FTD_TROUBLESHOOT_PATH
    path += "/dir-archives/var-log"
    os.chdir(path)
    print("Retrieving upgrade trigger timestamp for ftd from: " + path + "/action_queue.log")
    action_queue_log = "action_queue.log"

    f = open(action_queue_log, 'r')
    timestamp = ""  # timestamp when upgrade gets triggered on ftd
    status = ""
    while True:
        line = f.readline()
        if not line:
            break
        # check for the necessary conditions
        # Iterate back to actionq.1, .2 ... till we didn't receive "Apply Cisco"or check based on timestamp mysql_selectallfromaq
        # optimize - reverse loop through the file
        if "START TASK" in line and "Apply Cisco" in line and (
                "Upgrade" in line or "Patch" in line) and "Initializing" in line:
            timestamp = line[:15]
            status = line.strip('\n')

    print(status)
    return timestamp


def getAQIssue(path):
    path += "/dir-archives/var-log"
    os.chdir(path)
    print("Checking for disk space issues from: " + path + "/action_queue.log")
    disk_space_log = "action_queue.log"
    with open(disk_space_log, 'r') as file:
        lines = file.readlines()
    # check command output for disk space issues and get the component name.
    for line in reversed(lines):
        if "Not enough disk space available" in line:
            print("Disk space check failed")
            print("Suggested Component: ftd_upgrade")
            return 1
    print("Disk space check successful")
    return 0


def main():
    # retrieve upgrade trigger time for ftd
    # how to identify the upg failures timestamp
    trigger_time = getUpgradeTriggerTimestamp()
    if trigger_time == "":
        print("Upgrade isn't triggered on ftd")
        print("Suggested Component: fleet_upgrade")
        return
    print("Upgrade triggered on ftd at: ", trigger_time)

    # Check for disk space issues.
    path = FTD_TROUBLESHOOT_PATH
    if getAQIssue(path) == 1:
        return

    # for multiple upgrade scenario, pick most recent one
    upgrade_package = "Cisco_FTD"
    package_folder = ""
    path = FTD_TROUBLESHOOT_PATH
    path += "/dir-archives/var-log/sf"
    os.chdir(path)
    print("Retrieving most recent upgrade package from: " + path)
    dir_path = Path(os.getcwd())

    # Use glob to filter directories with the pattern Cisco_FTD*
    path = sorted(
        [p for p in dir_path.glob("Cisco_FTD*") if p.is_dir()],
        key=lambda p: os.path.getmtime(str(p))
    )
    print(path)
    for i in path:
        path_string = str(i)
        if platform.system() == "Windows":
            ind = path_string.rfind("\\")
        else:
            ind = path_string.rfind("/")
        if path_string[ind + 1:].startswith(upgrade_package) and ("Upgrade" in path_string or "Patch" in path_string):
            package_folder = path_string[ind + 1:]

    if package_folder == "":
        print("FTD Upgrade package not present")
        return

    print("FTD Upgrade package: ", package_folder)

    # Check for readiness
    path = FTD_TROUBLESHOOT_PATH
    if checkReadiness(package_folder, path) == 0:
        return

    path = FTD_TROUBLESHOOT_PATH

    # retrieve upgrade info from json file
    status = []
    status = getJson(package_folder, path)

    if len(status) == 0:
        return

    # Check for dev.crt
    if "DEV" in status[9]:
        if not os.path.exists(FTD_TROUBLESHOOT_PATH + "/dir-archives/etc/certs/dev.crt"):
            print("Dev certificate not present")
            print("Suggested Component: Junk")
            return
##s
    # Get the last string in the upgrade_status.log
    file_path_log = FTD_TROUBLESHOOT_PATH + "/dir-archives/var-log/sf/" + package_folder + "/upgrade_status.log"
    with open(file_path_log, 'r') as file:
        last_line = file.readlines()[-1].strip()
        if "The system will reboot after FXOS platform upgrade completes followed by a firmware upgrade." in last_line:
            print("FXOS upgrade is pending")
            print("Suggested Component: service-mgr")
            return

    # Check confreg value
    message_file_platform = FTD_TROUBLESHOOT_PATH + "/dir-archives/opt-cisco-platform-logs/messages"
    if os.path.exists(message_file_platform):
        with open(message_file_platform, 'r') as file:
            lines = file.readlines()
        for line in reversed(lines):
            if "Confreg value: confreg =" in line:
                confreg_value = line.split("confreg = ")[1].strip()
                if confreg_value != "0x10001":
                    print("Confreg value is not 0x10001, confreg_val= "+confreg_value)
                    print("Suggested Component: service-mgr")
                    return

    # when upgrade status isn't FAILED
    if status[0] != "FAILED":
        # Check status in FTD log
        path = FTD_TROUBLESHOOT_PATH
        value = checkFTDStatus(package_folder, path, status)
        if value[1] == 0:
            return

        # Check status in FMC log
        path = FTD_TROUBLESHOOT_PATH
        timestamp = getRebootTimestamp(package_folder, path)
        date1 = date(int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))
        time1 = time(int(timestamp[3]), int(timestamp[4]), int(timestamp[5]))
        print("Timestamp from main_upgrade_script.log: ", date1, time1)

        value = checkFMCStatus(date1, time1, status[7])
        timestamp = value[0]
        status = value[1]
        if status == "":
            print("Upgrade status not present on FMC for FTD")
        else:
            print("Status on FMC: ", status)
        print('\n', '\n')

        # when status is failed on fmc, check for errors on messages log
        if "Failed" in status or "failed" in status or status == "":
            print("Issue with upgrade status on FMC for ftd")
            path = FTD_TROUBLESHOOT_PATH
            checkErrors(date1, time1, path)

            # check for sftunnel/platform/network/management interface issues
            if status != "":
                date2 = date(date1.year, strptime(timestamp[0:3], '%b').tm_mon, int(timestamp[4:6]))
                time2 = time(int(timestamp[7:9]), int(timestamp[10:12]), int(timestamp[13:15]))
                if checkIssues(date1, time1, date2, time2, path) == 0:
                    print("No issues with sftunnel, check with FMC team.")
                    print("Suggested Component: fleet_upgrade")
            return

        return

    if "The upgrade was interrupted by a system restart." in status[6]:
        print("System restart interrupted the upgrade")
        if os.path.exists(FTD_TROUBLESHOOT_PATH+"/dir-archives/opt-cisco-platform-logs/prune_cores.log"):
            prune_core_log = FTD_TROUBLESHOOT_PATH+"/dir-archives/opt-cisco-platform-logs/prune_cores.log"
            with open(prune_core_log, 'r') as file:
                corelines = file.readlines()
            for line in reversed(corelines):
                if "core.sshd" in line:
                    print("SSHD Core dump found")
                    print("Suggested Component: asa, ssh")
                    return
                elif "core.lina" in line:
                    print("Lina Core dump found")
                    print("Suggested Component: asa")
                    return
            print("No core dumps found")
            print("Suggested Component: ftd_upgrade")
        print("Suggested Component: ftd_upgrade")
        return
    print("Suggested Component: ftd_upgrade")

    # when upgrade status is FAILED
    if len(status[5]) > 0:
        path = FTD_TROUBLESHOOT_PATH
        printLogs(status[5][0], status[6], package_folder, path)
    else:
        print("failedScript not present in upgrade_status.json")
        print("Suggested Component: ftd_upgrade")


if __name__ == "__main__":
    print("\n\nHow to use this script:")
    print("Provide the path of the troubleshoot files when prompted.")
    print("Note: Please ensure that the troubleshoot files are untarred before providing the path. Also this script "
          "and the troubleshoot files must be present on the same system.")
    print('\n', '\n')
    FTD_TROUBLESHOOT_PATH = str(input("Enter path of the ftd troubleshoot file: "))
    FMC_TROUBLESHOOT_PATH = str(input("Enter path of the fmc troubleshoot file: "))

    if FTD_TROUBLESHOOT_PATH.rfind('/') == -1:
        parts = FTD_TROUBLESHOOT_PATH.split('\\')
        FTD_TROUBLESHOOT_PATH = "/".join(parts)
        parts = FMC_TROUBLESHOOT_PATH.split('\\')
        FMC_TROUBLESHOOT_PATH = "/".join(parts)

    print('\n', '\n')
    main()
