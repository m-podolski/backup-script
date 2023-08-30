from typing import Any, Literal, TypeAlias

from jinja2 import Environment, PackageLoader, Template

from app.globals import OutputMode, ScarabOptionError

env = Environment(loader=PackageLoader("app"))

Style: TypeAlias = Literal[
    "NONE", "OK", "WARN", "ERROR", "HEADING", "EMPH", "OPTION", "OPT_EMPH", "END"
]
STYLES: dict[Style, str] = {
    "NONE": "",
    "OK": "\033[1;32m",
    "WARN": "\033[1;33m",
    "ERROR": "\033[1;91m",
    "HEADING": "\033[1m",
    "EMPH": "\033[1m",
    "OPTION": "\033[34m",
    "OPT_EMPH": "\033[1;34m",
    "END": "\033[0m",
}


def render(file: str, content: dict[str, Any], style: Style = "NONE") -> None:
    template: Template = env.get_template(file)
    styled: str = _escape_string(template.render(content), style)
    print(styled)


def get_input(prompt: str, output_mode: OutputMode) -> str:
    if output_mode is OutputMode.QUIET:
        raise ScarabOptionError("Cannot receive input in quiet mode")
    return input(prompt)


def get_path_input(prompt_message: str, output_mode: OutputMode) -> str:
    render("input_prompt.jinja2", {"message": prompt_message})
    return get_input("Path: ", output_mode)


def _escape_string(content: str, style: Style) -> str:
    return f"{STYLES[style]}{content}{STYLES['END']}"


# Template Filters


def _style(value: str, style: Style) -> str:
    return _escape_string(value, style)


env.filters["style"] = _style  # pyright: ignore
