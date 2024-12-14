# backup.py

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 環境変数の取得
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DATABASE_URL").split('/')[-1]
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
FULL_BACKUP_INTERVAL_DAYS = int(os.getenv("FULL_BACKUP_INTERVAL_DAYS", "7"))
INCREMENTAL_BACKUP_DIR = os.path.join(BACKUP_DIR, "incremental")
FULL_BACKUP_DIR = os.path.join(BACKUP_DIR, "full")

# 環境変数の設定（pg_dump時にパスワードを使用するため）
os.environ['PGPASSWORD'] = DB_PASSWORD

def ensure_directories():
    """
    バックアップディレクトリが存在しない場合は作成します。
    """
    os.makedirs(INCREMENTAL_BACKUP_DIR, exist_ok=True)
    os.makedirs(FULL_BACKUP_DIR, exist_ok=True)

def perform_full_backup():
    """
    フルバックアップを実行します。
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = os.path.join(FULL_BACKUP_DIR, f"full_backup_{timestamp}.sql")
    
    command = [
        "pg_dump",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-F", "c",
        "-b",
        "-v",
        "-f", backup_file,
        DB_NAME
    ]
    
    print(f"Starting full backup: {backup_file}")
    try:
        subprocess.run(command, check=True)
        print("Full backup completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Full backup failed: {e}")

def perform_incremental_backup():
    """
    増分バックアップを実行します。
    PostgreSQL自体はネイティブな増分バックアップをサポートしていないため、
    トランザクションログを使用したポイントインタイムリカバリー（PITR）を実装します。
    ここでは簡易的なスクリプトを提供します。
    """
    # トランザクションログのアーカイブ設定が必要です。
    # このスクリプトはトランザクションログをコピーする例です。
    archive_dir = os.getenv("ARCHIVE_DIR", "/var/lib/postgresql/archived_logs")
    os.makedirs(archive_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = os.path.join(INCREMENTAL_BACKUP_DIR, f"incremental_backup_{timestamp}.tar.gz")
    
    # トランザクションログの圧縮と保存
    command = [
        "tar",
        "-czvf",
        log_file,
        "-C", "/var/lib/postgresql/archived_logs",
        "."
    ]
    
    print(f"Starting incremental backup: {log_file}")
    try:
        subprocess.run(command, check=True)
        print("Incremental backup completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Incremental backup failed: {e}")

def main():
    ensure_directories()
    today = datetime.now().day
    last_full_backup_day = today % FULL_BACKUP_INTERVAL_DAYS
    
    if last_full_backup_day == 0:
        perform_full_backup()
    else:
        perform_incremental_backup()

if __name__ == "__main__":
    main()
