import app.io as appio
from app.globals import OutputMode
from app.locations import Destination, Location, Source


def check_path(
    location: Source | Destination, output_mode: OutputMode = OutputMode.NORMAL
) -> Source | Destination:
    if location.path_is_initialized:
        if location.exists:
            return location
        else:
            path_in: str = appio.read_path(
                location.location_messages["INVALID"],
                output_mode,
            )
            location.path = path_in
            return check_path(location, output_mode)
    else:
        path_in = appio.read_path(location.messages["NO_PATH_GIVEN"], output_mode)
        location.path = path_in
        return check_path(location, output_mode)


def select_media_dir(source: Location, destination: Location) -> Location:
    appio.render(
        "select_directory.jinja2",
        {
            "source": str(source.path),
            "destination": str(destination.path),
            "destination_content": [*destination.content, "-> Rescan Directory"],
        },
    )
    selected_option: int = int(input("Number: "))
    selected_option_is_rescan: bool = selected_option == len(destination.content) + 1

    if selected_option_is_rescan:
        return select_media_dir(source, destination)
    else:
        selected_dir: str = destination.content[selected_option - 1]
        destination.path = destination.path / selected_dir
        return destination
