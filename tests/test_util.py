from typing import Annotated
from swarm.util import function_to_json


def test_basic_function():
    def basic_function(arg1, arg2):
        return arg1 + arg2

    result = function_to_json(basic_function)
    assert result == {
        "type": "function",
        "function": {
            "name": "basic_function",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                    "arg1": {"type": "string"},
                    "arg2": {"type": "string"},
                },
                "required": ["arg1", "arg2"],
                "additionalProperties": False,
            },
        },
    }


def test_complex_function():
    def complex_function_with_types_and_descriptions(
        arg1: int, arg2: str, arg3: float = 3.14, arg4: bool = False
    ):
        """This is a complex function with a docstring."""
        pass

    result = function_to_json(complex_function_with_types_and_descriptions)
    assert result == {
        "type": "function",
        "function": {
            "name": "complex_function_with_types_and_descriptions",
            "description": "This is a complex function with a docstring.",
            "parameters": {
                "type": "object",
                "properties": {
                    "arg1": {"type": "integer"},
                    "arg2": {"type": "string"},
                    "arg3": {"type": "number"},
                    "arg4": {"type": "boolean"},
                },
                "required": ["arg1", "arg2"],
                "additionalProperties": False,
            },
        },
    }


def test_list_and_annotated_function():
    def list_annotated_function(
        arg1: list[int],
        arg2: list[str],
        arg3: Annotated[int, "an integer"],
        arg4: Annotated[list[int], "a list of integers"],
        arg5: Annotated[bool, 33],  # unsupported
        arg6: str | None = None,
        arg7: Annotated[int | None, "an optional integer"] = None,
    ):
        """This is an annotated function."""
        pass

    result = function_to_json(list_annotated_function)
    assert result == {
        "type": "function",
        "function": {
            "name": "list_annotated_function",
            "description": "This is an annotated function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "arg1": {"items": {"type": "integer"}, "type": "array"},
                    "arg2": {"items": {"type": "string"}, "type": "array"},
                    "arg3": {"description": "an integer", "type": "integer"},
                    "arg4": {
                        "description": "a list of integers",
                        "items": {"type": "integer"},
                        "type": "array",
                    },
                    "arg5": {"type": "string"},
                    "arg6": {"type": "string"},
                    "arg7": {
                        "description": "an optional integer",
                        "type": "integer",
                    },
                },
                "required": ["arg1", "arg2", "arg3", "arg4", "arg5"],
                "additionalProperties": False,
            },
        },
    }
