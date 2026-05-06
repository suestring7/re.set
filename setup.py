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
        "LSUIElement": True,                   # menu-bar only, no Dock icon
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
