python -m PyInstaller --windowed --icon=BackupTool.ico backup_tool.py -n BackupTool
copy BackupTool.bat dist\BackupTool
copy *.json dist\BackupTool
copy *.ico dist\BackupTool
copy LICENSE.md dist\BackupTool
mkdir dist\BackupTool\Test
copy Test\Test.txt dist\BackupTool\Test
move dist\BackupTool .\"Save Game Backup Tool"
pyinstaller --icon=BackupTool.ico backup_tool.py
copy dist\BackupTool\backup_tool.exe "Save Game Backup Tool\BackupTool (Console).exe"
7z a save-game-backup-tool-win32-i386.zip "Save Game Backup Tool"
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q "Save Game Backup Tool"
del *.spec
