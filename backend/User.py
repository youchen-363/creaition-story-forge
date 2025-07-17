class User:
    def __init__(self, username=None, email=None, credits=999, id=None, created_at=None, updated_at=None):
        self.id = id  # UUID primary key
        self.username = username
        self.email = email
        self.credits = credits  # Default 999 credits
        self.created_at = created_at
        self.updated_at = updated_at