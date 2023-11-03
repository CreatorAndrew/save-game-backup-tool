pyinstaller --noconsole --target-arch universal2 BackupTool.py
cp *.json dist
cp LICENSE dist
cp *.command dist
cp -r Test dist/Test
rm -rf dist/BackupTool
mv ./dist ./Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-darwin-universal2.zip ./Save\ Game\ Backup\ Tool
rm -rf ./Save\ Game\ Backup\ Tool ./build ./BackupTool.spec
