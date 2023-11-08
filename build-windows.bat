pyinstaller --hide-console hide-early --icon=BackupTool.ico BackupTool.py
copy *.json dist\BackupTool
copy LICENSE dist\BackupTool
robocopy Test dist\BackupTool\Test /e
cd dist
rename BackupTool "Save Game Backup Tool"
7z a save-game-backup-tool-win32-amd64.zip "Save Game Backup Tool"
move save-game-backup-tool-win32-amd64.zip ..
cd ..
rmdir /s /q dist
rmdir /s /q build
del BackupTool.spec
