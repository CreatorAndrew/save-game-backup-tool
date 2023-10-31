pyinstaller BackupTool.py
cp MasterConfig.json dist/BackupTool
cp Test.json dist/BackupTool
cp Bully.json dist/BackupTool
cp LICENSE dist/BackupTool
cp -r Test dist/BackupTool/Test
mv ./dist/BackupTool ./dist/Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-linux-amd64.zip ./dist/Save\ Game\ Backup\ Tool/
rm -rf ./dist ./build ./BackupTool.spec
