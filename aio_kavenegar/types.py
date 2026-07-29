from typing import TypedDict


class KavenegarResponseReturn(TypedDict):
    status: int
    message: str


KavenegarResponse = TypedDict(
    "KavenegarResponse", {"return": KavenegarResponseReturn, "entries": dict}
)
