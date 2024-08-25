python -m PyInstaller --windowed --icon=BackupTool.ico backup_tool.py -n BackupTool
copy BackupTool-2.7.bat dist\BackupTool\BackupTool.bat
copy *.json dist\BackupTool
copy *.ico dist\BackupTool
copy LICENSE.md dist\BackupTool
mkdir dist\BackupTool\Test
copy Test\Test.txt dist\BackupTool\Test
move dist\BackupTool .\"Save Game Backup Tool"
python -m PyInstaller --icon=BackupTool.ico backup_tool.py -n "BackupTool (Console)"
copy "dist\BackupTool (Console)\BackupTool (Console).*" .\"Save Game Backup Tool"
7z a save-game-backup-tool-win32.zip "Save Game Backup Tool"
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q "Save Game Backup Tool"
del *.spec
