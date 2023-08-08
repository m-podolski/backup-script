from cement import App, CaughtSignal, init_defaults
from .controllers.base import Base

CONFIG = init_defaults("scarab")
CONFIG["scarab"]["prop"] = "otherValue"


class Scarab(App):
    class Meta:
        label = "scarab"
        config_defaults = CONFIG
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


def main():
    with Scarab() as app:
        try:
            app.run()

        except AssertionError as e:
            print("AssertionError > %s" % e.args[0])
            app.exit_code = 1
            if app.debug is True:
                import traceback

                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print("\n%s" % e)
            app.exit_code = 0


if __name__ == "__main__":
    main()
