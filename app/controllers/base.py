from cement import Controller, ex, get_version

VERSION = (0, 0, 1, "alpha", 0)
VERSION_BANNER = """
cement-script v%s
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
        help="example sub command1",
        arguments=[
            (["-f", "--foo"], {"help": "notorious foo option", "action": "store", "dest": "foo"}),
        ],
    )
    def command1(self):
        print("Inside Base.command1")

        if self.app.pargs.foo is not None:
            print("Foo Argument > %s" % self.app.pargs.foo)
