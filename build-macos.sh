pyinstaller --noconsole BackupTool.py
cp MasterConfig.json dist
cp Test.json dist
cp Bully.json dist
cp *.command dist
cp -r Test dist/Test
rm -rf dist/BackupTool
7z a Save\ Game\ Backup\ Tool.zip ./dist/*