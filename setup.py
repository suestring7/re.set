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
    import os
    import py2app.util as u
    from py2app.util import reset_blocking_status

    # Mach-O magic bytes (both endians, 32/64-bit, fat binaries).
    _MACHO_MAGICS = frozenset([
        b'\xfe\xed\xfa\xce', b'\xfe\xed\xfa\xcf',
        b'\xce\xfa\xed\xfe', b'\xcf\xfa\xed\xfe',
        b'\xca\xfe\xba\xbe', b'\xbf\xba\xfe\xca',
    ])

    def _is_macho(path: str) -> bool:
        try:
            with open(path, 'rb') as f:
                return f.read(4) in _MACHO_MAGICS
        except OSError:
            return False

    def codesign_adhoc_relaxed(bundle: str) -> None:
        # `codesign --deep` only covers standard bundle dirs (Frameworks/,
        # MacOS/, PlugIns/).  Python extension modules land in
        # Contents/Resources/lib/…/lib-dynload/ and stay unsigned, causing
        # macOS 15+ CODESIGNING kills when dlopen loads them at runtime.
        #
        # We also strip every existing signature first.  Apple-signed
        # components (e.g. Python.framework) carry Apple's Team ID; mixing
        # those with ad-hoc re-signed binaries triggers a "different team
        # identifier" rejection on macOS 15+ / Tahoe.  A clean strip +
        # uniform ad-hoc re-sign avoids this.
        bundle_s = str(bundle)
        targets: list[str] = []
        for root, _, files in os.walk(bundle_s):
            for fname in files:
                fpath = os.path.join(root, fname)
                if _is_macho(fpath):
                    targets.append(fpath)
        # Deepest first so inner signatures are stable before outer ones
        targets.sort(key=lambda p: p.count(os.sep), reverse=True)

        with reset_blocking_status():
            # Strip existing signatures to eliminate team-ID conflicts
            for fpath in targets:
                subprocess.call(
                    ["/usr/bin/codesign", "--remove-signature", fpath],
                    stderr=subprocess.DEVNULL,
                )
            # Re-sign every Mach-O with a uniform ad-hoc identity
            for fpath in targets:
                subprocess.call(
                    ["/usr/bin/codesign", "--sign", "-", "--force", fpath],
                    stderr=subprocess.DEVNULL,
                )
            # Strip + re-sign the bundle itself last
            subprocess.call(
                ["/usr/bin/codesign", "--remove-signature", bundle_s],
                stderr=subprocess.DEVNULL,
            )
            subprocess.check_call(
                ["/usr/bin/codesign", "--sign", "-", "--force", bundle_s]
            )

    u.codesign_adhoc = codesign_adhoc_relaxed


_patch_py2app_codesign()

from setuptools import setup

APP = ["main_macos.py"]

# Read-only resources bundled into Contents/Resources
RESOURCES = [
    "ui/break_reminder_ui.html",
    "ui/records_ui.html",
    "ui/away_form.html",
    "ui/return_form.html",
    "ui/preferences.html",
    "ui/warning.html",
    "ui/shared.js",
    "ui/exercises.json",
    "ui/activity_types.json",
    "packaging/AppIcon.icns",
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
