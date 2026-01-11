#!/bin/bash
set -e

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Creating LMS backup utility..."

cat > /usr/local/bin/lms-backup << 'EOF'
#!/bin/bash

BACKUP_DIR="/tmp/lms_backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Starting LMS backup at $(date)"

tar -czf "$BACKUP_DIR/courses_$TIMESTAMP.tar.gz" /opt/lab/django-lms/

if [ -f /opt/lab/django-lms/db.sqlite3 ]; then
    sqlite3 /opt/lab/django-lms/db.sqlite3 ".backup $BACKUP_DIR/db_$TIMESTAMP.sql"
fi

echo "Backup completed: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"
EOF

chmod 4755 /usr/local/bin/lms-backup
chown root:root /usr/local/bin/lms-backup

cat > /etc/cron.d/lms-backup << EOF
*/30 * * * * root /usr/local/bin/lms-backup >/tmp/lms-backup.log 2>&1
EOF
chmod 644 /etc/cron.d/lms-backup
echo "Backup schedule installed (/etc/cron.d/lms-backup)."
