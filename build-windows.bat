pyinstaller --hide-console hide-early BackupTool.py
copy MasterConfig.json dist\BackupTool
copy Test.json dist\BackupTool
copy Bully.json dist\BackupTool
copy LICENSE dist\BackupTool
robocopy Test dist\BackupTool\Test /e
cd dist
rename BackupTool "Save Game Backup Tool"
7z a save-game-backup-tool-win32-amd64.zip "Save Game Backup Tool"
move save-game-backup-tool-win32-amd64.zip ..
cd ..
rmdir /s dist
rmdir /s build
del BackupTool.spec
