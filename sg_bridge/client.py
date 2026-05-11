"""
sg_bridge/client.py
ShotGrid (Flow Production Tracking) API client wrapper.
Wraps shotgun_api3 with sensible defaults for pipeline automation.
"""

from __future__ import annotations
from typing import Any

try:
    import shotgun_api3
except ImportError:
    raise ImportError("Install ShotGrid API: pip install shotgun_api3")


class ShotGridClient:
    """
    Thin wrapper around shotgun_api3.Shotgun.
    Handles connection, auth, and common pipeline operations.
    """

    def __init__(self, site_url: str, script_name: str, api_key: str):
        self._sg = shotgun_api3.Shotgun(
            site_url,
            script_name=script_name,
            api_key=api_key,
        )

    # ── Assets ────────────────────────────────────────────────────────────────

    def find_asset(self, project_id: int, asset_name: str) -> dict | None:
        return self._sg.find_one(
            "Asset",
            [["project", "is", {"type": "Project", "id": project_id}],
             ["code",    "is", asset_name]],
            ["id", "code", "sg_status_list", "tasks"],
        )

    def list_assets(self, project_id: int, status: str | None = None) -> list[dict]:
        filters = [["project", "is", {"type": "Project", "id": project_id}]]
        if status:
            filters.append(["sg_status_list", "is", status])
        return self._sg.find("Asset", filters, ["id", "code", "sg_status_list"])

    # ── Tasks ─────────────────────────────────────────────────────────────────

    def update_task_status(self, task_id: int, status: str) -> dict[str, Any]:
        """
        status options: wtg (waiting), ip (in progress), fin (final), na (not applicable)
        """
        return self._sg.update("Task", task_id, {"sg_status_list": status})

    def find_task(self, project_id: int, entity_name: str, task_name: str) -> dict | None:
        return self._sg.find_one(
            "Task",
            [["project",       "is",  {"type": "Project", "id": project_id}],
             ["entity.Asset.code", "is", entity_name],
             ["content",       "is",  task_name]],
            ["id", "content", "sg_status_list"],
        )

    # ── Versions ──────────────────────────────────────────────────────────────

    def create_version(self, project_id: int, asset_id: int, version_name: str,
                       description: str = "", file_path: str = "") -> dict[str, Any]:
        data = {
            "project"     : {"type": "Project", "id": project_id},
            "entity"      : {"type": "Asset",   "id": asset_id},
            "code"        : version_name,
            "description" : description,
        }
        version = self._sg.create("Version", data)
        if file_path:
            self._sg.upload("Version", version["id"], file_path, "sg_uploaded_movie")
        return version

    # ── Notes ────────────────────────────────────────────────────────────────

    def add_note(self, project_id: int, entity_type: str, entity_id: int,
                 subject: str, body: str) -> dict[str, Any]:
        return self._sg.create("Note", {
            "project"      : {"type": "Project",   "id": project_id},
            "note_links"   : [{"type": entity_type, "id": entity_id}],
            "subject"      : subject,
            "content"      : body,
        })
