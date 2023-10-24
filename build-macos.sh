pyinstaller --noconsole --target-arch universal2 BackupTool.py
cp MasterConfig.json dist
cp Test.json dist
cp Bully.json dist
cp *.command dist
cp -r Test dist/Test
rm -rf dist/BackupTool
mv ./dist ./Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-darwin-universal2.zip ./Save\ Game\ Backup\ Tool