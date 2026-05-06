from __future__ import annotations

import frappe


WORKSPACE_NAME = "Google Ads KPI"
WORKSPACE_LABEL = "Google Ads KPI"
WORKSPACE_TITLE = "Google Ads KPI"
WORKSPACE_MODULE = "Google Ads KPI"
LEGACY_WORKSPACE_NAMES = ("Google Ads", "Google Ads Dashboard")

WORKSPACE_CONTENT = (
    '[{"id":"zWLLv","type":"header","data":{"text":"Google Ads KPI","col":12}},'
    '{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Campaign Performance","col":3}},'
    '{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Ad Performance","col":3}},'
    '{"id":"shortcuts3","type":"shortcut","data":{"shortcut_name":"Keyword Metrics","col":3}},'
    '{"id":"shortcuts4","type":"shortcut","data":{"shortcut_name":"Search Terms","col":3}},'
    '{"id":"ai_shortcuts_header","type":"header","data":{"text":"Google Ads AI","col":12}},'
    '{"id":"shortcuts5","type":"shortcut","data":{"shortcut_name":"AI Settings","col":4}},'
    '{"id":"shortcuts6","type":"shortcut","data":{"shortcut_name":"AI Recommendations","col":4}},'
    '{"id":"shortcuts7","type":"shortcut","data":{"shortcut_name":"AI Audit Log","col":4}}]'
)

WORKSPACE_SHORTCUTS = [
    {
        "color": "Blue",
        "label": "Campaign Performance",
        "link_to": "Google Ads Campaign KPI",
        "type": "DocType",
    },
    {
        "color": "Green",
        "label": "Ad Performance",
        "link_to": "Google Ads Ad KPI",
        "type": "DocType",
    },
    {
        "color": "Orange",
        "label": "Keyword Metrics",
        "link_to": "Google Ads Keyword KPI",
        "type": "DocType",
    },
    {
        "color": "Purple",
        "label": "Search Terms",
        "link_to": "Google Ads Search Term KPI",
        "type": "DocType",
    },
    {
        "color": "Gray",
        "label": "AI Settings",
        "link_to": "Google Ads AI Settings",
        "type": "DocType",
    },
    {
        "color": "Red",
        "label": "AI Recommendations",
        "link_to": "Google Ads AI Recommendation",
        "type": "DocType",
    },
    {
        "color": "Cyan",
        "label": "AI Audit Log",
        "link_to": "Google Ads AI Audit Log",
        "type": "DocType",
    },
]

DEFAULT_AI_SETTINGS = {
    "objective": "maximize_roas",
    "risk_tolerance": "medium",
    "filter_mode": "all",
    "max_budget_increase_percent": 20,
    "max_bid_change_percent": 15,
    "minimum_data_days": 14,
    "auto_execution_enabled": 0,
}


def before_install() -> None:
    if not frappe.db.exists("DocType", "Lead Source"):
        frappe.throw("Google Ads KPI requires ERPNext because KPI Source fields link to Lead Source.")


def after_install() -> None:
    ensure_ai_settings_defaults()
    ensure_workspace()
    clear_google_ads_cache()


def after_migrate() -> None:
    ensure_ai_settings_defaults()
    ensure_workspace()
    clear_google_ads_cache()


def clear_google_ads_cache() -> None:
    frappe.clear_cache(doctype="Google Ads AI Settings")
    frappe.clear_cache(doctype="Google Ads Campaign KPI")
    frappe.clear_cache(doctype="Workspace")


def ensure_ai_settings_defaults() -> None:
    if not frappe.db.exists("DocType", "Google Ads AI Settings"):
        return

    settings = frappe.get_single("Google Ads AI Settings")
    changed = False
    for fieldname, value in DEFAULT_AI_SETTINGS.items():
        if settings.get(fieldname) in (None, ""):
            settings.set(fieldname, value)
            changed = True

    if changed:
        settings.save(ignore_permissions=True)


def ensure_workspace() -> None:
    if not frappe.db.exists("DocType", "Workspace"):
        return

    migrate_legacy_workspace()
    release_duplicate_workspace_label()

    if not frappe.db.exists("Workspace", WORKSPACE_NAME):
        workspace = frappe.get_doc(
            {
                "doctype": "Workspace",
                "name": WORKSPACE_NAME,
                "label": WORKSPACE_LABEL,
                "title": WORKSPACE_TITLE,
                "module": WORKSPACE_MODULE,
                "public": 1,
                "is_hidden": 0,
                "icon": "chart",
                "content": WORKSPACE_CONTENT,
            }
        )
        for shortcut in WORKSPACE_SHORTCUTS:
            workspace.append("shortcuts", shortcut)
        workspace.insert(ignore_permissions=True)
        return

    frappe.db.set_value(
        "Workspace",
        WORKSPACE_NAME,
        {
            "label": WORKSPACE_LABEL,
            "title": WORKSPACE_TITLE,
            "module": WORKSPACE_MODULE,
            "public": 1,
            "is_hidden": 0,
            "icon": "chart",
            "content": WORKSPACE_CONTENT,
        },
        update_modified=False,
    )
    frappe.db.delete(
        "Workspace Shortcut",
        {
            "parent": WORKSPACE_NAME,
            "parenttype": "Workspace",
            "parentfield": "shortcuts",
        },
    )
    for idx, shortcut in enumerate(WORKSPACE_SHORTCUTS, start=1):
        row = frappe.get_doc(
            {
                "doctype": "Workspace Shortcut",
                "parent": WORKSPACE_NAME,
                "parenttype": "Workspace",
                "parentfield": "shortcuts",
                "idx": idx,
                "doc_view": "",
                **shortcut,
            }
        )
        row.db_insert()


def migrate_legacy_workspace() -> None:
    for workspace_name in LEGACY_WORKSPACE_NAMES:
        if workspace_name == WORKSPACE_NAME or not frappe.db.exists("Workspace", workspace_name):
            continue

        if not frappe.db.exists("Workspace", WORKSPACE_NAME):
            frappe.rename_doc(
                "Workspace",
                workspace_name,
                WORKSPACE_NAME,
                force=True,
            )
            return

        frappe.db.set_value(
            "Workspace",
            workspace_name,
            {
                "label": get_legacy_workspace_label(workspace_name),
                "is_hidden": 1,
                "public": 0,
            },
            update_modified=False,
        )


def release_duplicate_workspace_label() -> None:
    duplicate_workspaces = frappe.get_all(
        "Workspace",
        filters={"label": WORKSPACE_LABEL, "name": ["!=", WORKSPACE_NAME]},
        pluck="name",
    )

    for workspace_name in duplicate_workspaces:
        frappe.db.set_value(
            "Workspace",
            workspace_name,
            {
                "label": get_legacy_workspace_label(workspace_name),
                "is_hidden": 1,
                "public": 0,
            },
            update_modified=False,
        )


def get_legacy_workspace_label(workspace_name: str) -> str:
    base_label = f"{workspace_name} Legacy"
    label = base_label
    counter = 2

    while frappe.db.exists(
        "Workspace",
        {"label": label, "name": ["!=", workspace_name]},
    ):
        label = f"{base_label} {counter}"
        counter += 1

    return label
