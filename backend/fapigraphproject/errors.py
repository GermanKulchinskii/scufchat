class ChatAlreadyExistsError(Exception):
    def __init__(self, message="Private chat with these members already exists"):
        self.message = message
        super().__init__(self.message)

class InvalidUserIdError(Exception):
    def __init__(self, message="User(s) with specified id(s) do(es) not exist"):
        self.message = message
        super().__init__(self.message)

class ChatWithSelfError(Exception):
    def __init__(self, message="Cannot start private chats with yourself"):
        self.message = message
        super().__init__(self.message)