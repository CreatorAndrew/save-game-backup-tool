pyinstaller --onefile --hide-console hide-early --icon=BackupTool.ico BackupTool.py
copy *.json dist
copy *.ico dist
copy LICENSE dist
robocopy Test dist\Test /e
rename dist "Save Game Backup Tool"
7z a save-game-backup-tool-win32-amd64.zip "Save Game Backup Tool"
rmdir /s /q "Save Game Backup Tool"
rmdir /s /q build
del *.spec
