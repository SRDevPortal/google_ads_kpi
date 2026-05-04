from __future__ import annotations

import frappe


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
    frappe.clear_cache()


def after_migrate() -> None:
    ensure_ai_settings_defaults()
    frappe.clear_cache(doctype="Google Ads AI Settings")
    frappe.clear_cache(doctype="Google Ads Campaign KPI")


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
