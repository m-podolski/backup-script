from cement import App, CaughtSignal, TestApp, init_defaults  # pyright: ignore

import app.io as appio
from app.controller import Base
from app.globals import ScarabException

CONFIG = init_defaults("scarab")  # pyright: ignore
CONFIG["scarab"]["otherProp"] = "otherValue"


class Scarab(App):
    class Meta:  # pyright: ignore
        label: str = "scarab"
        handlers: list[type[Base]] = [
            Base,
        ]
        extensions: list[str] = [
            "yaml",
            "colorlog",
        ]
        config_defaults = CONFIG  # pyright: ignore
        config_handler: str = "yaml"
        config_file_suffix: str = ".yml"
        log_handler: str = "colorlog"
        close_on_exit = True


class ScarabTest(TestApp, Scarab):  # pyright: ignore
    class Meta:  # pyright: ignore
        label: str = "scarabTest"


def main() -> None:
    with Scarab() as app:
        try:
            app.run()

        except ScarabException as e:
            appio.print_styled(str(e), "ERROR")
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
