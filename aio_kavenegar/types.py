from typing import TypedDict


class KavenegarResponseReturn(TypedDict):
    status: int
    message: str


# Functional syntax: "return" is a keyword and can't be a class-body field name.
KavenegarResponse = TypedDict(
    "KavenegarResponse", {"return": KavenegarResponseReturn, "entries": dict}
)
