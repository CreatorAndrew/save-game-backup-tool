python -m PyInstaller backup_tool.py -n BackupTool
cp .BackupTool.desktop dist/BackupTool
cp *.json dist/BackupTool
cp *.ico dist/BackupTool
cp LICENSE.md dist/BackupTool
cp -r Test dist/BackupTool/Test
mv dist/BackupTool dist/Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-linux-i386.zip dist/Save\ Game\ Backup\ Tool/
rm -rf dist build *.spec
