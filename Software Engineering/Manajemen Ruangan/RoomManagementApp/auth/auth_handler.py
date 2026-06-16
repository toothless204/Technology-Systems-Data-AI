class AuthHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler
    
    def authenticate(self, username, password):
        """Authenticate user"""
        user = self.db_handler.get_user(username)
        if user and user[2] == password:  # user[2] is password
            return {
                'id': user[0],
                'username': user[1],
                'role': user[3],
                'email': user[4]
            }
        return None
    
    def get_user_role(self, username):
        """Get user role"""
        user = self.db_handler.get_user(username)
        if user:
            return user[3]  # user[3] is role
        return None
