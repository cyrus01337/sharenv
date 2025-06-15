# TODO: Prefer Typer over Argparse
# TODO: Setup Poetry
import argparse
import pathlib
import os
import re
import typing

type Shell = typing.Literal["bash"] | typing.Literal["fish"]

PARSER = argparse.ArgumentParser(prog="sharenv")
ENVIRONMENT_VARIABLE_PATTERN = (
    r"^\s*(?P<exported>export\s)?(?P<name>[a-zA-Z0-9_]+)\s*=\s*(?P<value>(?:\"[^\"]*\")|(?:'[^']*')|.*)$"
)

PARSER.add_argument("--shell", "-s", choices=["bash", "fish"], dest="shell")


class CustomNamespace(argparse.Namespace):
    shell: Shell


class ConfigurationError(Exception):
    pass


class ParsedEnvironmentVariable(typing.TypedDict):
    exported: str
    name: str
    value: str


def find_configuration_files() -> list[pathlib.Path]:
    directory = pathlib.Path("~/.config/sharenv").expanduser()
    files = list(path for path in directory.rglob("*.env") if path.is_file())

    if not (directory.exists() and directory.is_dir() and len(files) > 0):
        configuration = directory / "variables.env"

        directory.mkdir(exist_ok=True)
        configuration.touch()
        exit(0)

    return files


def generate_shell_command_for(match: re.Match[str], shell: Shell) -> str:
    parsed = ParsedEnvironmentVariable(**match.groupdict())
    name = parsed["name"]
    value = parsed["value"]
    exported = parsed["exported"] or ""

    if shell == "bash":
        return f"{exported}{name}={value}"

    flag = "-x " if exported else ""

    return f"set {flag}{name} {value}"


def parse_configuration_for_shell(file: pathlib.Path, shell: Shell) -> str:
    commands = ""

    with file.open("r") as file_header:
        matches = [
            match_found
            for match_found in map(
                lambda line: re.match(ENVIRONMENT_VARIABLE_PATTERN, line, flags=re.MULTILINE), file_header.readlines()
            )
            if match_found
        ]

        for match in matches:
            command = generate_shell_command_for(match, shell)
            commands += f"{command}\n"

    return commands


def main():
    arguments = PARSER.parse_args(namespace=CustomNamespace())

    if typing.cast(Shell | None, arguments.shell) is None:
        auto_detected_shell: Shell | str = os.environ.get("SHELL", "")[-4:]

        if auto_detected_shell not in ["bash", "fish"]:
            raise ConfigurationError(f"unsupported shell: {auto_detected_shell}")

        arguments.shell_type = typing.cast(Shell, auto_detected_shell)

    files = find_configuration_files()

    if not files:
        configuration_file = pathlib.Path("~/.config/sharenv/variables.env")

        configuration_file.mkdir(parents=True, exist_ok=True)
        configuration_file.touch(exist_ok=True)

        return

    output = ""

    for configuration in files:
        result = parse_configuration_for_shell(configuration, arguments.shell)

        if not result:
            continue

        output += f"{result}\n"

    if len(output) > 0:
        print(output[:-1])


if __name__ == "__main__":
    main()
