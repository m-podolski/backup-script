from cement import App, TestApp, CaughtSignal, init_defaults  # pyright: ignore
from app.controllers.base import Base

CONFIG = init_defaults("scarab")  # pyright: ignore
CONFIG["scarab"]["prop"] = "otherValue"


class Scarab(App):
    class Meta:  # pyright: ignore
        label: str = "scarab"
        config_defaults = CONFIG  # pyright: ignore[reportUnknownVariableType]
        close_on_exit = True
        # extensions = [
        #     "yaml",
        #     "colorlog",
        #     "jinja2",
        # ]
        # config_handler = "yaml"
        # config_file_suffix = ".yml"
        # log_handler = "colorlog"
        # output_handler = "jinja2"
        handlers = [
            Base,
        ]


class ScarabTest(TestApp, Scarab):  # pyright: ignore
    class Meta:  # pyright: ignore
        label: str = "scarabTest"


def main() -> None:
    with Scarab() as app:
        try:
            app.run()

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
