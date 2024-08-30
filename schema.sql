CREATE TABLE IF NOT EXISTS reading_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book TEXT NOT NULL,
    chapter TEXT NOT NULL,
    UNIQUE(user_id, book, chapter)
);