import logging
import sqlite3
from datetime import datetime
from logging import Handler, LogRecord
import atexit
import os

class SQLiteHandler(Handler):
    def __init__(self, db_path='app_logs.db', max_db_size_mb=5, retention_days=90):
        super().__init__()
        self.db_path = db_path
        self.max_db_size = max_db_size_mb * 1024 * 1024 if max_db_size_mb else None
        self.retention_days = retention_days
        self.conn = sqlite3.connect(db_path)
        self._ensure_table()
        atexit.register(self.conn.close)

    def _ensure_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created TEXT,
                level TEXT,
                message TEXT,
                pathname TEXT,
                lineno INTEGER,
                funcname TEXT
            )
        ''')
        self.conn.commit()
        self._rotate()

    def emit(self, record: LogRecord):
        try:
            msg = self.format(record)  # only gets message, not full metadata unless included in formatter
            self.conn.execute('''
                INSERT INTO logs (created, level, message, pathname, lineno, funcname)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.fromtimestamp(record.created).isoformat(),
                record.levelname,
                record.getMessage(),
                record.pathname,
                record.lineno,
                record.funcName,
            ))
            self.conn.commit()
        except Exception:
            self.handleError(record)
            
    def _rotate(self):
        if self.max_db_size and os.path.getsize(self.db_path) > self.max_db_size:
            self.conn.execute(f'''
                DELETE FROM logs
                WHERE created < datetime('now', '-{self.retention_days} days');
            ''')
            self.conn.commit()

def setup_logger(name="app", db_path='app_logs.db', level=logging.DEBUG, max_db_size_mb: int = 5, retention_days: int = 90,):
    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    logger.handlers.clear()  # Avoid duplicates on reruns in Streamlit

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s: %(message)s'))
    
    # SQLite Handler
    sqlite_handler = SQLiteHandler(db_path=db_path, max_db_size_mb=max_db_size_mb, retention_days=retention_days)
    sqlite_handler.setLevel(logging.DEBUG)
    sqlite_handler.setFormatter(logging.Formatter('%(message)s'))  # Store only the message in DB

    logger.addHandler(console_handler)
    logger.addHandler(sqlite_handler)

    return logger
