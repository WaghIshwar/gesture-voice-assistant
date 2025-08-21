from db import get_connection

def save_to_db(gesture, voice, action):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO commands (gesture, voice, action) VALUES (%s, %s, %s)"
        values = (gesture, voice, action)
        cursor.execute(sql, values)
        conn.commit()
        print("✅ Data inserted successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()
