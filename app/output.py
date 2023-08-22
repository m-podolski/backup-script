from app.exceptions import ScarabOptionError
from app.globals import OutputMode

from jinja2 import Environment, PackageLoader, Template

env = Environment(loader=PackageLoader("app"))


def _render(file: str, content: dict[str, str]) -> None:
    template: Template = env.get_template(file)
    print(template.render(content))


def read_path(prompt_message: str, output_mode: OutputMode) -> str:
    if output_mode is OutputMode.QUIET:
        raise ScarabOptionError("Cannot receive input in quiet mode")
    _render("input_prompt.jinja2", {"message": prompt_message})
    return input("Path: ")
