pyinstaller BackupTool.py
cp *.json dist/BackupTool
cp .BackupTool.desktop dist/BackupTool
cp *.ico dist/BackupTool
cp LICENSE dist/BackupTool
cp -r Test dist/BackupTool/Test
mv ./dist/BackupTool ./dist/Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-linux-amd64.zip ./dist/Save\ Game\ Backup\ Tool/
rm -rf ./dist ./build
