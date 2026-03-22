from setuptools import setup

APP = ['run.py']
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'macrun/assets/MacRun.icns',
    'plist': {
        'CFBundleName': 'MacRun',
        'CFBundleDisplayName': 'MacRun',
        'CFBundleIdentifier': 'com.macrun.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # Hide dock icon
        'NSHighResolutionCapable': True,
    },
    'packages': ['macrun'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
