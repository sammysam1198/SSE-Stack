def create_user(email, username, password, role):
    import bcrypt

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    print(f"""
INSERT INTO users (
    email,
    username,
    password_hash,
    role,
    is_active,
    is_locked,
    email_verified,
    created_at,
    updated_at
)
VALUES (
    '{email}',
    '{username}',
    '{hashed}',
    '{role}',
    TRUE,
    FALSE,
    TRUE,
    NOW(),
    NOW()
);
""")


create_user("michaelphillip667@gmail.com", "4nzek", "PoopstorePlus69!", "artist")