#!/bin/bash
cd "${0%/*}"
python -m PyInstaller --onefile backup_tool.py -n BackupTool
cp *.ico dist
cp *.json dist
cp LICENSE.md dist
cp -r Test dist/Test
mv dist Save\ Game\ Backup\ Tool
7z a save-game-backup-tool-linux.zip Save\ Game\ Backup\ Tool
rm -rf Save\ Game\ Backup\ Tool build *.spec
