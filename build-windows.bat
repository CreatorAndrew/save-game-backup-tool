pyinstaller -w BackupTool.py
copy *.json dist\BackupTool
copy BackupTool.bat dist\BackupTool
copy LICENSE dist\BackupTool
mkdir dist\BackupTool\Test
copy Test\Test.txt dist\BackupTool\Test
move dist\BackupTool .\"Save Game Backup Tool"
pyinstaller BackupTool.py
copy dist\BackupTool\BackupTool.exe "Save Game Backup Tool\BackupTool (Console).exe"
7z a save-game-backup-tool-win32-i386.zip "Save Game Backup Tool"
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q "Save Game Backup Tool"
del BackupTool.spec
