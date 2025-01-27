# import sqlite3
#
# class UserTable:
#     def __init__(self, db_path='data.db'):
#         self.db_path = db_path
#
#     def get_connection(self):
#         return sqlite3.connect(self.db_path)
#
#     def add_user(self, id, first_name, last_name, balance=0):
#         with self.get_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#             INSERT OR IGNORE INTO users (id, first_name, last_name, balance)
#             VALUES (?, ?, ?, ?)
#             ''', (id, first_name, last_name, balance))
#             conn.commit()
#
#     def update_balance(self, id, amount):
import psycopg2

class UserTable:
    def __init__(self, db_params):
        # db_params should be a dictionary with keys: dbname, user, password, host, port
        self.db_params = db_params

    def get_connection(self):
        return psycopg2.connect(**self.db_params)

    def add_user(self, id, first_name, last_name, balance=0):
        # Ensure id is exactly 10 characters
        id = str(id).ljust(10)[:10]  # Pad with spaces or truncate to 10 characters
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO users (id, first_name, last_name, balance)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            ''', (id, first_name, last_name, balance))
            conn.commit()

    def update_balance(self, id, amount):
        # Ensure id is exactly 10 characters
        id = str(id).ljust(10)[:10]
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE users
            SET balance = balance + %s
            WHERE id = %s
            ''', (amount, id))
            conn.commit()

    def get_user(self, id):
        # Ensure id is exactly 10 characters
        id = str(id).ljust(10)[:10]
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
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
            return [{
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'balance': row[3]
            } for row in rows]

    def delete_user(self, id):
        # Ensure id is exactly 10 characters
        id = str(id).ljust(10)[:10]
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = %s', (id,))
            conn.commit()

    def delete_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users')
            conn.commit()
