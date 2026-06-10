from sqlalchemy import text


def migrate_database(engine) -> None:
    with engine.begin() as connection:
        if engine.dialect.name == "sqlite":
            columns = connection.execute(text("PRAGMA table_info(users)")).mappings().all()
            column_names = {column["name"] for column in columns}
            if "role" not in column_names:
                connection.execute(
                    text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'student'")
                )
                connection.execute(text("UPDATE users SET role = 'student' WHERE role IS NULL OR role = ''"))
            if "status" not in column_names:
                connection.execute(
                    text("ALTER TABLE users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'")
                )
                connection.execute(text("UPDATE users SET status = 'active' WHERE status IS NULL OR status = ''"))

        connection.execute(
            text(
                "UPDATE users SET role = 'admin' "
                "WHERE username IN ('admin', 'market_admin')"
            )
        )
        connection.execute(text("UPDATE users SET status = 'active' WHERE role = 'admin'"))
