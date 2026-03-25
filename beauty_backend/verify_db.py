from sqlalchemy import create_engine, text

# Using the database URL from settings
engine = create_engine("mysql+mysqlconnector://baDB:Panda24685l%24@www.dcs5604.com:3306/beauty_assisant")

with engine.connect() as connection:
    # Check users
    print("--- USERS TABLE ---")
    result = connection.execute(text("SELECT id, email, guest_token, is_guest, created_at FROM users ORDER BY id DESC LIMIT 5"))
    for row in result:
        print(f"ID: {row[0]}, Email: {row[1]}, Token: {row[2]}, IsGuest: {row[3]}, Created: {row[4]}")

    # Check sessions
    print("\n--- SESSIONS TABLE ---")
    result = connection.execute(text("SELECT id, user_id, season_id, created_at FROM recommendation_sessions ORDER BY id DESC LIMIT 5"))
    for row in result:
        print(f"ID: {row[0]}, UserID: {row[1]}, SeasonID: {row[2]}, Created: {row[3]}")
