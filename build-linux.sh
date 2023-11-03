pyinstaller BackupTool.py
cp *.json dist/BackupTool
cp LICENSE dist/BackupTool
cp -r Test dist/BackupTool/Test
mv ./dist/BackupTool ./dist/Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-linux-i386.zip ./dist/Save\ Game\ Backup\ Tool/
rm -rf ./dist ./build ./BackupTool.spec
