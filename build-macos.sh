pyinstaller --noconsole --target-arch universal2 --codesign-identity $certificate --icon=BackupTool.png BackupTool.py
cp *.command dist
cp *.json dist
cp LICENSE dist
cp -r Test dist/Test
rm -rf dist/BackupTool
mv ./dist/BackupTool.app ./dist/Save\ Game\ Backup\ Tool.app
mv ./dist ./Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-darwin-universal2.zip ./Save\ Game\ Backup\ Tool
rm -rf ./Save\ Game\ Backup\ Tool ./build
rm *.spec
