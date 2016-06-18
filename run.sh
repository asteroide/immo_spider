
echo Starting Database server...
spider_db &

echo Staring APIViewer server...
spider_viewer &

echo Syncing database...
spider_shell sync

echo Results:
spider_shell get