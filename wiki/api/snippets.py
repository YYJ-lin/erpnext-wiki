"""Page starters now come from snippets, not a second doctype.

A snippet marked `is_template` is a page skeleton: the new-page dialog lists
them, and the content travels with the create call. One content-reuse concept
(the snippet picker) instead of a parallel "template" system.
"""

from __future__ import annotations

import frappe


@frappe.whitelist()
def list_page_templates() -> list[dict]:
	return frappe.get_all(
		"Wiki Snippet",
		filters={"is_template": 1},
		fields=["name", "title", "content"],
		order_by="title asc",
		limit=100,
	)
