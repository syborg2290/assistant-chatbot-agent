import sqlite3
import json


class SqliteDataService:
    def __init__(self, db_name="crew_agent.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crew_agent (
                obj_id TEXT PRIMARY KEY,
                data TEXT
            )
        """
        )
        self.conn.commit()

    def save(self, obj_id, data):
        json_data = json.dumps(data)
        self.conn.execute(
            "INSERT OR REPLACE INTO crew_agent (obj_id, data) VALUES (?, ?)",
            (obj_id, json_data),
        )
        self.conn.commit()

    def get(self, obj_id):
        cursor = self.conn.execute(
            "SELECT data FROM crew_agent WHERE obj_id = ?", (obj_id,)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

    def update(self, obj_id, new_data):
        if self.get(obj_id):
            self.save(obj_id, new_data)
            return True
        return False

    def delete(self, obj_id):
        self.conn.execute("DELETE FROM crew_agent WHERE obj_id = ?", (obj_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
