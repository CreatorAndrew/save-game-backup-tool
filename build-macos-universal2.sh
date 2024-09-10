python -m PyInstaller --noconsole --target-arch universal2 --icon=BackupTool.png backup_tool.py -n BackupTool
cp *.command dist
cp *.ico dist/BackupTool.app/Contents/Resources
cp *.json dist
cp LICENSE.md dist
cp -r Test dist/Test
rm -rf dist/BackupTool
mv dist/BackupTool.app dist/Save\ Game\ Backup\ Tool.app
mv dist Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-darwin-universal2.zip Save\ Game\ Backup\ Tool
rm -rf Save\ Game\ Backup\ Tool build *.spec
