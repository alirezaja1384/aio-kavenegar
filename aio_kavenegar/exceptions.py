class APIException(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(f"APIException[{status}] {message}")


class HTTPException(Exception):
    pass
