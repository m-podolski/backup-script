import app.io as appio
from app.globals import OutputMode
from app.locations import Location, Source, Target


def check_path(location: Source | Target, output_mode: OutputMode) -> Source | Target:
    if location.path_is_initialized:
        if location.exists:
            return location
        else:
            path_in: str = appio.get_path_input(
                location.location_messages["INVALID"],
                output_mode,
            )
            location.path = path_in
            return check_path(location, output_mode)
    else:
        path_in = appio.get_path_input(location.messages["NO_PATH_GIVEN"], output_mode)
        location.path = path_in
        return check_path(location, output_mode)


def select_media_dir(source: Location, target: Location, output_mode: OutputMode) -> Location:
    appio.render(
        "select_directory.jinja2",
        {
            "source": str(source.path),
            "target": str(target.path),
            "target_content": [*target.content, "-> Rescan Directory"],
        },
    )
    selected_option: int = int(appio.get_input("Number: ", output_mode))
    selected_option_is_rescan: bool = selected_option == len(target.content) + 1

    if selected_option_is_rescan:
        return select_media_dir(source, target, output_mode)
    else:
        selected_dir: str = target.content[selected_option - 1]
        target.path = target.path / selected_dir
        return target
