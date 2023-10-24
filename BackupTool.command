#!/bin/bash
cd "${0%/*}"
export PYTHONWARNINGS="ignore"
clear
./BackupTool.app/Contents/MacOS/BackupTool --no-gui
