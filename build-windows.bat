python -m PyInstaller --onefile --hide-console hide-early --icon=BackupTool.ico backup_tool.py -n BackupTool
copy BackupTool.bat dist
copy *.ico dist
copy *.json dist
copy LICENSE.md dist
mkdir dist\Test
copy Test\Test.txt dist\Test
rename dist "Save Game Backup Tool"
7z a save-game-backup-tool-win32.zip "Save Game Backup Tool"
rmdir /s /q "Save Game Backup Tool"
rmdir /s /q build
del *.spec
