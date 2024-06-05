import psycopg2.extensions


async def create_session(db_conn: psycopg2.extensions.connection, user_id: str) -> int:
    with db_conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO sessions (user_id) VALUES (%s) RETURNING id", (user_id,))
        session_id = cursor.fetchone()[0]
        db_conn.commit()
        return session_id


async def add_message(db_conn: psycopg2.extensions.connection, session_id: int, message: str) -> int:
    with db_conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO messages (session_id, message) VALUES (%s, %s) RETURNING id", (session_id, message))
        message_id = cursor.fetchone()[0]
        db_conn.commit()
        return message_id


async def get_session_history(db_conn: psycopg2.extensions.connection, session_id: int):
    with db_conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, message, timestamp FROM messages WHERE session_id = %s ORDER BY timestamp", (session_id,))
        messages = cursor.fetchall()
        return [{"id": row[0], "message": row[1], "timestamp": row[2]} for row in messages]
