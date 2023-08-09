def run_backup(sourcepath, backup_mode):
    print("run_backup")
    if sourcepath is not None:
        validate_sourcepath(sourcepath)
    else:
        read_sourcepath()


def validate_sourcepath(path):
    print("validate_sourcepath")
    return True


def read_sourcepath():
    print("Enter your source directory (absolute path): ")
