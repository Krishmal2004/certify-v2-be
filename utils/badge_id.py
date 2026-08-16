import secrets

def generate_badge_id(length: int = 12) -> str:
    return secrets.token_hex(length // 2).upper()
