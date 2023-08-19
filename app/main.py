from cement import App, TestApp, CaughtSignal, init_defaults, Handler  # pyright: ignore

from app.controllers.base import Base
from app.exceptions import ScarabException

CONFIG = init_defaults("scarab")  # pyright: ignore
CONFIG["scarab"]["otherProp"] = "otherValue"


class Scarab(App):
    class Meta:  # pyright: ignore
        label: str = "scarab"
        handlers = [
            Base,
        ]
        extensions = [
            "yaml",
            "jinja2",
            "colorlog",
        ]
        config_defaults = CONFIG  # pyright: ignore
        config_handler = "yaml"
        config_file_suffix = ".yml"
        output_handler = "jinja2"
        template_dir = "./app/templates"
        log_handler = "colorlog"
        close_on_exit = True


class ScarabTest(TestApp, Scarab):  # pyright: ignore
    class Meta:  # pyright: ignore
        label: str = "scarabTest"


def main() -> None:
    with Scarab() as app:
        try:
            app.run()

        except ScarabException as e:
            print("\n%s" % e)
            app.exit_code = 0

        except AssertionError as e:
            print("AssertionError > %s" % e.args[0])
            app.exit_code = 1
            if app.debug is True:  # pyright: ignore
                import traceback

                traceback.print_exc()

        except CaughtSignal as e:
            print("\n%s" % e)
            app.exit_code = 0


if __name__ == "__main__":
    main()
