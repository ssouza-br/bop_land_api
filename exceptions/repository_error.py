class RepositoryError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def to_dict(self):
        return {"message": self.message}