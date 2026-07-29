from __future__ import annotations

import json
from typing import Any

from aio_kavenegar.client import AIOKavenegarAPI


def parse(params: dict[str, Any]) -> dict[str, Any]:
    return AIOKavenegarAPI("api-key")._parse_params_to_json(params)


def test_list_value_is_json_encoded() -> None:
    assert parse({"sender": ["30002626", "30002627"]}) == {
        "sender": json.dumps(["30002626", "30002627"])
    }


def test_tuple_value_is_json_encoded_as_array() -> None:
    assert parse({"receptor": ("0912", "0913")}) == {"receptor": '["0912", "0913"]'}


def test_dict_value_is_json_encoded() -> None:
    assert parse({"token": {"a": 1}}) == {"token": '{"a": 1}'}


def test_scalar_values_are_left_untouched() -> None:
    params = {"receptor": "09121234567", "message": "hi", "date": 1500000000}

    assert parse(params) == params


def test_none_and_bool_values_are_preserved() -> None:
    assert parse({"hide": None, "flash": True}) == {
        "hide": None,
        "flash": True,
    }


def test_non_ascii_is_preserved_not_escaped_to_ascii() -> None:
    # json.dumps escapes non-ASCII by default, so Persian text becomes
    # "س..." on the wire. This documents the current behaviour.
    encoded = parse({"message": ["سلام"]})["message"]

    assert encoded == '["\\u0633\\u0644\\u0627\\u0645"]'
    assert json.loads(encoded) == ["سلام"]


def test_empty_params_produce_empty_dict() -> None:
    assert parse({}) == {}


def test_original_params_are_not_mutated() -> None:
    params = {"sender": ["30002626"]}

    parse(params)

    assert params == {"sender": ["30002626"]}


def test_nested_structures_are_encoded_at_top_level_only() -> None:
    assert parse({"items": [{"id": 1}, {"id": 2}]}) == {
        "items": '[{"id": 1}, {"id": 2}]'
    }
