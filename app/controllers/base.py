from cement import Controller, ex, get_version

from app.services.backup import run_backup

VERSION = (0, 5, 0, "alpha", 0)
VERSION_BANNER = """
scarab-backup v%s
""" % get_version(
    VERSION
)


class Base(Controller):
    class Meta:
        label = "base"
        arguments = [
            (["-v", "--version"], {"action": "version", "version": VERSION_BANNER}),
        ]

    def _default(self):
        self.app.args.print_help()

    @ex(
        help="Back up from from a sourcepath to an external drive",
        arguments=[
            (
                ["-s", "--source"],
                {"help": "The sourcepath", "action": "store", "dest": "sourcepath"},
            ),
            (
                ["-c", "--create"],
                {
                    "help": "Create a new backup",
                    "action": "store_const",
                    "const": "CREATE",
                    "dest": "backup_mode",
                },
            ),
            (
                ["-u", "--update"],
                {
                    "help": "Update an existig backup",
                    "action": "store_const",
                    "const": "UPDATE",
                    "dest": "backup_mode",
                },
            ),
        ],
    )
    def backup(self):
        run_backup(self.app.pargs.sourcepath, self.app.pargs.backup_mode)
