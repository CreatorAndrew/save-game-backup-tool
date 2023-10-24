pyinstaller --hide-console hide-early BackupTool.py
copy MasterConfig.json dist\BackupTool
copy Test.json dist\BackupTool
copy Bully.json dist\BackupTool
robocopy Test dist\BackupTool\Test /e