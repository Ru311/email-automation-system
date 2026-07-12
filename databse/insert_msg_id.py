from sqlalchemy import text
from .database_helper import engine

def mark_processed(message_id, thread_id):
    """Insert a processed message record if it does not already exist."""

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                INSERT INTO processed_messages
                (message_id, thread_id)
                VALUES (:message_id, :thread_id)
                ON CONFLICT (message_id)
                DO NOTHING
            """),
            {
                "message_id": message_id,
                "thread_id": thread_id
            }
        )

        conn.commit()

        return result.rowcount > 0
