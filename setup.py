"""
py2app setup for re.set.

py2app's default ad-hoc signing loops over every Mach-O with
``--preserve-metadata=identifier,entitlements,flags,runtime``, which often
fails on newer Python (e.g. 3.14) / macOS combos. We replace it with a single
``codesign --deep`` on the .app before setuptools loads the py2app command.
"""

from __future__ import annotations

import subprocess
import sys


def _patch_py2app_codesign() -> None:
    if sys.platform != "darwin":
        return
    import py2app.util as u
    from py2app.util import reset_blocking_status

    def codesign_adhoc_relaxed(bundle: str) -> None:
        bundle_s = str(bundle)
        # Use the absolute path to avoid Anaconda's stub codesign shadowing
        # the real Apple tool in PATH.
        with reset_blocking_status():
            subprocess.check_call(
                [
                    "/usr/bin/codesign",
                    "--sign",
                    "-",
                    "--force",
                    "--deep",
                    bundle_s,
                ]
            )

    u.codesign_adhoc = codesign_adhoc_relaxed


_patch_py2app_codesign()

from setuptools import setup

APP = ["break_reminder.py"]

# Read-only resources bundled into Contents/Resources
RESOURCES = [
    "break_reminder_ui.html",
    "records_ui.html",
    "away_form.html",
    "return_form.html",
    "preferences.html",
    "warning.html",
    "shared.js",
    "exercises.json",
    "activity_types.json",
    "re.set.app/Contents/Resources/AppIcon.icns",
]

OPTIONS = {
    "argv_emulation": False,
    "strip": False,
    "optimize": 0,
    "packages": [],
    "resources": RESOURCES,
    "plist": {
        "CFBundleName": "re.set",
        "CFBundleDisplayName": "re.set",
        "CFBundleIdentifier": "com.user.reset.breakreminder",
        "CFBundleShortVersionString": "1.0",
        "CFBundleVersion": "1.0",
        "LSUIElement": True,  # menu-bar only, no Dock icon
        "NSHighResolutionCapable": True,
        "NSSupportsAutomaticGraphicsSwitching": True,
        "CFBundleIconFile": "AppIcon",
        "NSAppleEventsUsageDescription":
            "re.set needs to detect user activity to time breaks accurately.",
    },
}

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
