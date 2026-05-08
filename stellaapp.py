__artifacts_v2__ = {
    "stella_case_settings": {
        "name": "Meta Glasses Case Settings",
        "description": "Extracts Meta Glasses case identifiers and settings from Stella app plist data",
        "author": "@OpenAI",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Wearables",
        "notes": "Targets com.facebook.stellaapp namespace plist data for Meta Glasses case details",
        "paths": (
            "*com.meta.mwa.glasses.userSettingsStore*.plist",
            "*com.meta.mwa.glasses.userSettingStore*.plist",
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu"
    },
    "stella_device_sync_log": {
        "name": "Meta Glasses Device Sync Log",
        "description": "Extracts Meta Glasses sync and firmware information from Stella app plist data",
        "author": "@OpenAI",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Wearables",
        "notes": "Targets com.facebook.stellaapp namespace plist data for Meta Glasses software details",
        "paths": (
            "*com.meta.mwa.dmcsynclog*.plist",
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu"
    },
    "stella_derived_sku_info": {
        "name": "Meta Glasses Derived SKU Info",
        "description": "Extracts Meta Glasses model, frame, and lens information from Stella app plist data",
        "author": "@OpenAI",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Wearables",
        "notes": "Targets com.facebook.stellaapp namespace plist data for Meta Glasses hardware and style details",
        "paths": (
            "*com.meta.mwa.derivedskuinfo*.plist",
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu"
    },
    "stella_linked_accounts": {
        "name": "Meta Glasses Linked Accounts",
        "description": "Extracts accounts linked to the Stella app",
        "author": "@OpenAI",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Accounts",
        "notes": "Targets com.stellaapp.fxlinkedaccountsstore.plist",
        "paths": (
            "*com.stellaapp.fxlinkedaccountsstore.plist",
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "stella_metaai_logs": {
        "name": "Meta Glasses Meta AI Prompts",
        "description": "Extracts wearer prompts and agent-response markers from MetaAI logs",
        "author": "@OpenAI",
        "creation_date": "2026-03-04",
        "last_update_date": "2026-03-04",
        "requirements": "none",
        "category": "Chats",
        "notes": "Parses SilverstoneModels.SLVPostTitle prompts and Last Response agent option lines",
        "paths": (
            "*MetaAI-log-*.txt",
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-circle"
    }
}

import os
import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    get_plist_content,
    get_plist_file_content,
)


def _basename(path):
    return os.path.basename(path)


def _device_id_from_path(path):
    name = _basename(path)
    marker = "-Namespace("
    if marker in name:
        return name.split(marker, 1)[0]
    return name


def _suffix_key(full_key):
    return full_key.rsplit(")-", 1)[-1]


def _normalize_timestamp(value):
    if isinstance(value, (int, float)) and value:
        return convert_unix_ts_to_utc(value)
    return value if value is not None else ""

def _extract_log_timestamp(line):
    if len(line) >= 23:
        # Example: 2026-02-20 11:16:41.943
        return line[:23]
    return ""


def _clean_log_string(value):
    return (
        value
        .replace('\\"', '"')
        .replace("\\'", "'")
        .replace("\\n", "\n")
        .replace("\\t", "\t")
    )


@artifact_processor
def stella_case_settings(context):
    data_list = []

    for source_path in context.get_files_found():
        pl = get_plist_file_content(source_path)
        if not isinstance(pl, dict):
            continue

        normalized = {_suffix_key(key): value for key, value in pl.items()}
        data_list.append((
            _device_id_from_path(source_path),
            normalized.get("caseSerial", ""),
            normalized.get("caseVersion", ""),
            _normalize_timestamp(normalized.get("lastSettingsSnapshotTime", "")),
            normalized.get("hasCompletedVoiceOOBE", ""),
            normalized.get("metaAIOptInCompleted", ""),
            normalized.get("metaAIGeoOptInCompleted", ""),
            normalized.get("liveAIEAPOptInStatus", ""),
            normalized.get("hasDefaultProviderBackwardCompatibilityScriptRun", ""),
            normalized.get("hasDefaultProviderBackwardCompatibilityScriptRunV2", ""),
            normalized.get("shouldShowLanguageRevertedNotification", ""),
            normalized.get("shouldShowLanguageRevertedPushNotification", ""),
            source_path,
        ))

    data_headers = (
        "Glasses Device ID",
        "Case Serial Number",
        "Case Software Version",
        ("Last Settings Snapshot Time", "datetime"),
        "Has Completed Voice OOBE",
        "Meta AI Opt-In Completed",
        "Meta AI Geo Opt-In Completed",
        "Live AI EAP Opt-In Status",
        "Default Provider Backward Compatibility Script Run",
        "Default Provider Backward Compatibility Script Run V2",
        "Show Language Reverted Notification",
        "Show Language Reverted Push Notification",
        "Source",
    )
    return data_headers, data_list, "Source column in the report"


@artifact_processor
def stella_device_sync_log(context):
    data_list = []

    for source_path in context.get_files_found():
        pl = get_plist_file_content(source_path)
        if not isinstance(pl, dict):
            continue

        normalized = {_suffix_key(key): value for key, value in pl.items()}
        data_list.append((
            _device_id_from_path(source_path),
            normalized.get("lastSyncFirmware", ""),
            normalized.get("lastSyncAppVersion", ""),
            _normalize_timestamp(normalized.get("lastSyncTime", "")),
            source_path,
        ))

    data_headers = (
        "Glasses Device ID",
        "Glasses Firmware Version",
        "App Version at Last Sync",
        ("Last Sync Time", "datetime"),
        "Source",
    )
    return data_headers, data_list, "Source column in the report"


@artifact_processor
def stella_derived_sku_info(context):
    data_list = []

    for source_path in context.get_files_found():
        pl = get_plist_file_content(source_path)
        if not isinstance(pl, dict):
            continue

        normalized = {_suffix_key(key): value for key, value in pl.items()}
        data_list.append((
            _device_id_from_path(source_path),
            normalized.get("frameTypeDisplayName", ""),
            normalized.get("frameTypeShortDisplayName", ""),
            normalized.get("frameStyle", ""),
            normalized.get("frameColorDisplayName", ""),
            normalized.get("frameColor", ""),
            normalized.get("lensColorDisplayName", ""),
            normalized.get("lensColor", ""),
            source_path,
        ))

    data_headers = (
        "Glasses Serial Number",
        "Model",
        "Model Short Name",
        "Frame Style",
        "Frame Color Display Name",
        "Frame Color",
        "Lens Color Display Name",
        "Lens Color",
        "Source",
    )
    return data_headers, data_list, "Source column in the report"


@artifact_processor
def stella_linked_accounts(context):
    data_list = []

    for source_path in context.get_files_found():
        pl = get_plist_file_content(source_path)
        if not isinstance(pl, dict):
            continue

        accounts_blob = pl.get("com.stellaapp.fxlinkedaccountsstore-linkedAccounts", b"")
        accounts = get_plist_content(accounts_blob) if accounts_blob else []
        store_timestamp = pl.get("com.stellaapp.fxlinkedaccountsstore-timestamp", "")

        if not isinstance(accounts, list):
            continue

        for account_entry in accounts:
            account = account_entry.get("ACCOUNT", {})
            data_list.append((
                store_timestamp,
                account_entry.get("ACCOUNT_ID", ""),
                account_entry.get("INSTAGRAM_ACCOUNT_ID", ""),
                account.get("ACCOUNT_TYPE", ""),
                account.get("USERNAME", ""),
                account.get("NAME", ""),
                account.get("LINK_STATUS", ""),
                account.get("VERSION_ID", ""),
                account.get("OBFUSCATED_ACCOUNT_ID", ""),
                account.get("PROFILE_PICTURE_URL", ""),
                source_path,
            ))

    data_headers = (
        ("Store Timestamp", "datetime"),
        "Account ID",
        "Instagram Account ID",
        "Account Type",
        "Username",
        "Name",
        "Link Status",
        "Version ID",
        "Obfuscated Account ID",
        "Profile Picture URL",
        "Source",
    )
    return data_headers, data_list, "Source column in the report"


@artifact_processor
def stella_metaai_logs(context):
    data_list = []

    prompt_re = re.compile(
        r'SilverstoneModels\.SLVPostTitle\(text:\s*Optional\("(?P<prompt>.*?)"\),\s*mediaItems:'
    )
    response_re = re.compile(r'Last Response agent option:\s*(?P<response>.*)$')

    for source_path in context.get_files_found():
        pending_prompts = []
        with open(source_path, "r", encoding="utf-8", errors="replace") as f:
            for line_number, line in enumerate(f, start=1):
                prompt_match = prompt_re.search(line)
                if prompt_match:
                    pending_prompts.append({
                        "timestamp": _extract_log_timestamp(line),
                        "line_number": line_number,
                        "prompt": _clean_log_string(prompt_match.group("prompt")),
                    })
                    continue

                response_match = response_re.search(line)
                if response_match:
                    response_timestamp = _extract_log_timestamp(line)
                    response_value = _clean_log_string(response_match.group("response").strip())
                    if pending_prompts:
                        prompt_item = pending_prompts.pop(0)
                        data_list.append((
                            prompt_item["timestamp"],
                            response_timestamp,
                            prompt_item["prompt"],
                            response_value,
                            prompt_item["line_number"],
                            line_number,
                            source_path,
                        ))
                    else:
                        data_list.append((
                            "",
                            response_timestamp,
                            "",
                            response_value,
                            "",
                            line_number,
                            source_path,
                        ))

        for prompt_item in pending_prompts:
            data_list.append((
                prompt_item["timestamp"],
                "",
                prompt_item["prompt"],
                "",
                prompt_item["line_number"],
                "",
                source_path,
            ))

    data_headers = (
        ("Prompt Timestamp", "datetime"),
        ("Response Marker Timestamp", "datetime"),
        "Prompt Text",
        "Last Response Agent Option",
        "Prompt Line Number",
        "Response Line Number",
        "Source",
    )
    return data_headers, data_list, "Source column in the report"
