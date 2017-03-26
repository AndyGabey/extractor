Database Backup/Restore
=======================

The database is located in `Extractor/db/extractor.db`. There are two shell scripts in here:
`db_backup.sh` and `db_restore.sh`. Before and after major changes to the database are run (e.g. adding
new datasets/variables), the backup script should be run.
