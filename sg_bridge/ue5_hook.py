"""
sg_bridge/ue5_hook.py
UE5 Python hook — posts ShotGrid status updates when assets are validated or saved.
Run inside UE5 Python environment.
"""

from __future__ import annotations
import os

try:
    import unreal
except ImportError:
    raise RuntimeError("ue5_hook.py must run inside the UE5 editor Python environment")

from .client import ShotGridClient


def _get_client() -> ShotGridClient:
    site    = os.environ["SG_SITE_URL"]
    script  = os.environ["SG_SCRIPT_NAME"]
    api_key = os.environ["SG_API_KEY"]
    return ShotGridClient(site, script, api_key)


def on_asset_validated(project_id: int, asset_name: str, task_name: str = "Model") -> None:
    """
    Call this after a successful validate_for_ci() pass.
    Sets the ShotGrid task to 'fin' (final/approved).
    """
    sg = _get_client()
    task = sg.find_task(project_id, asset_name, task_name)
    if task:
        sg.update_task_status(task["id"], "fin")
        unreal.log(f"ShotGrid: '{asset_name}/{task_name}' → fin")
    else:
        unreal.warning(f"ShotGrid: task not found for {asset_name}/{task_name}")


def on_asset_saved(project_id: int, asset_name: str, asset_path: str,
                   task_name: str = "Model", description: str = "") -> None:
    """
    Call this on UE5 asset save to create a ShotGrid Version entry.
    """
    sg       = _get_client()
    asset    = sg.find_asset(project_id, asset_name)
    if not asset:
        unreal.warning(f"ShotGrid: asset '{asset_name}' not found in project {project_id}")
        return

    version_name = f"{asset_name}_v{unreal.SystemLibrary.get_engine_version()[:4]}"
    sg.create_version(project_id, asset["id"], version_name,
                      description=description or "Auto-version from UE5 save")
    unreal.log(f"ShotGrid: version '{version_name}' created for '{asset_name}'")
