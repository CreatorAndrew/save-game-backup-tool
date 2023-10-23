pyinstaller BackupTool.py
cp MasterConfig.json dist/BackupTool
cp Test.json dist/BackupTool
cp Bully.json dist/BackupTool
cp -r Test dist/BackupTool/Test
7z a Save\ Game\ Backup\ Tool.zip ./dist/BackupTool/*