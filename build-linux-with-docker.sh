#!/bin/bash
cd "${0%/*}"
docker build -t save-game-backup-tool .
docker run -it --rm --name save-game-backup-tool -v $(pwd):/save-game-backup-tool save-game-backup-tool
