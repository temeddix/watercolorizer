import os
import json
import pathlib

userpath = pathlib.Path.home()
pythonpath = userpath / "miniconda3/envs/watercolorize/python.exe"

vscode_settings = {
    "python.defaultInterpreterPath": str(pythonpath),
    "terminal.integrated.defaultProfile.windows": "Command Prompt",
    "editor.formatOnSave": True,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--experimental-string-processing"],
    "python.linting.enabled": True,
    "python.linting.lintOnSave": True,
    "python.linting.flake8Enabled": True,
    "python.linting.flake8Args": [
        "--max-line-length=88",
        "--ignore=E203,W503",
    ],
    "python.analysis.autoImportCompletions": False,
}

filepath = "./.vscode/settings.json"
os.makedirs(os.path.dirname(filepath), exist_ok=True)
with open(filepath, "w", encoding="utf8") as jsonfile:
    json.dump(vscode_settings, jsonfile, indent=4)
