import sqlite3

class UserTable:
    def __init__(self, db_path='data.db'):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def add_user(self, id, first_name, last_name, balance=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR IGNORE INTO users (id, first_name, last_name, balance)
            VALUES (?, ?, ?, ?)
            ''', (id, first_name, last_name, balance))
            conn.commit()

    def update_balance(self, id, amount):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE users
            SET balance = balance + ?
            WHERE id = ?
            ''', (amount, id))
            conn.commit()

    def get_user(self, id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'balance': row[3]
                }
            return None


    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            rows = cursor.fetchall()
            ll = []
            for row in rows:
                ll.append({
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'balance': row[3]
                })
            return ll

    def delete_user(self, id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (id,))
            conn.commit()
