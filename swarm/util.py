import inspect
from datetime import datetime
from typing import Annotated, Any, get_args, get_origin


def debug_print(debug: bool, *args: str) -> None:
    if not debug:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = " ".join(map(str, args))
    print(f"\033[97m[\033[90m{timestamp}\033[97m]\033[90m {message}\033[0m")


def merge_fields(target, source):
    for key, value in source.items():
        if isinstance(value, str):
            target[key] += value
        elif value is not None and isinstance(value, dict):
            merge_fields(target[key], value)


def merge_chunk(final_response: dict, delta: dict) -> None:
    delta.pop("role", None)
    merge_fields(final_response, delta)

    tool_calls = delta.get("tool_calls")
    if tool_calls and len(tool_calls) > 0:
        index = tool_calls[0].pop("index")
        merge_fields(final_response["tool_calls"][index], tool_calls[0])


def function_to_json(func) -> dict:
    """
    Converts a Python function into a JSON-serializable dictionary
    that describes the function's signature, including its name,
    description, and parameters.

    Args:
        func: The function to be converted.

    Returns:
        A dictionary representing the function's signature in JSON format.
    """
    type_map = {
        str: "string",
        str | None: "string",
        int: "integer",
        int | None: "integer",
        float: "number",
        float | None: "number",
        bool: "boolean",
        bool | None: "boolean",
        list: "array",
        list | None: "array",
        dict: "object",
        dict | None: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        parameters[param.name] = {}
        annotation = param.annotation
        param_type: str | None = None
        if annotation is inspect.Parameter.empty:
            param_type = "string"
        else:
            if get_origin(annotation) is Annotated:
                if len(annotation.__metadata__) == 1 and isinstance(
                    annotation.__metadata__[0], str
                ):
                    parameters[param.name]["description"] = annotation.__metadata__[0]
                    annotation = annotation.__origin__
            param_type = type_map.get(get_origin(annotation)) or type_map.get(
                annotation
            )
            if param_type == "array":
                args = get_args(annotation)
                if args:
                    if len(args) == 1 and (arg := type_map.get(args[0])):
                        parameters[param.name]["items"] = {"type": arg}
                    else:
                        raise TypeError(f"Parameter type {annotation} not supported")
            elif param_type is None:
                param_type = "string"

        parameters[param.name]["type"] = param_type

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect.Parameter.empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
                "additionalProperties": False,
            },
        },
    }
