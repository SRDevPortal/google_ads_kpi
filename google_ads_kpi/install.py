from __future__ import annotations

import frappe


WORKSPACE_NAME = "Google Ads KPI"

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
    frappe.clear_cache()


def after_migrate() -> None:
    ensure_ai_settings_defaults()
    ensure_workspace()
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

    if not frappe.db.exists("Workspace", WORKSPACE_NAME):
        workspace = frappe.get_doc(
            {
                "doctype": "Workspace",
                "name": WORKSPACE_NAME,
                "label": WORKSPACE_NAME,
                "title": WORKSPACE_NAME,
                "module": WORKSPACE_NAME,
                "public": 1,
                "icon": "chart",
            }
        )
        workspace.content = WORKSPACE_CONTENT
        for shortcut in WORKSPACE_SHORTCUTS:
            workspace.append("shortcuts", shortcut)
        workspace.insert(ignore_permissions=True)
        return

    frappe.db.set_value(
        "Workspace",
        WORKSPACE_NAME,
        {
            "label": WORKSPACE_NAME,
            "title": WORKSPACE_NAME,
            "module": WORKSPACE_NAME,
            "public": 1,
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
