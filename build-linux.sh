pyinstaller --onefile BackupTool.py
cp .BackupTool.desktop dist
cp *.json dist
cp *.ico dist
cp LICENSE dist
cp -r Test dist/Test
mv ./dist ./Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-linux-amd64.zip ./Save\ Game\ Backup\ Tool
rm -rf ./Save\ Game\ Backup\ Tool ./build
rm *.spec
