pyinstaller -w BackupTool.py
copy *.json dist\BackupTool
copy BackupTool.bat
copy LICENSE dist\BackupTool
robocopy Test dist\BackupTool\Test /e
move dist\BackupTool .\"Save Game Backup Tool"
pyinstaller BackupTool.py
copy dist\BackupTool\BackupTool.exe "Save Game Backup Tool\BackupTool (Console).exe"
7z a save-game-backup-tool-win32-i386.zip "Save Game Backup Tool"
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q "Save Game Backup Tool"
del BackupTool.spec
