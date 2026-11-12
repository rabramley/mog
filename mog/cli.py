#!/usr/bin/env python3

import re
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console(markup=False)

LOG_RE = re.compile(
    r"^(?P<timestamp>\d{2}-[A-Za-z]{3}-\d{4}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"\[(?P<thread>[^\]]+)\]\s+"
    r"(?P<logger>\S+)\s+"
    r"(?P<message>.*)$"
)

LEVEL_COLOURS = {
    "INFO": "green",
    "WARN": "yellow",
    "WARNING": "yellow",
    "ERROR": "red",
    "SEVERE": "bold red",
    "DEBUG": "blue",
    "TRACE": "cyan",
    "FINE": "blue",
}


def print_log_entry(match):
    level = match.group("level")
    colour = LEVEL_COLOURS.get(level, "white")

    header = Text()
    header.append(level, style=colour)

    message = Text.from_ansi(match.group("message"))

    body = Text()
    body.append(match.group("timestamp"), style="cyan")
    body.append("\n")
    body.append(match.group("thread"), style="magenta")
    body.append("\n")
    body.append(match.group("logger"), style="bright_black")
    body.append("\n")
    body.append(message)


    console.print(
        Panel(
            body,
            border_style=colour,
            title=header,
            expand=True,
        )
    )


def print_stacktrace(line):
    console.print(line.rstrip(), style="dim")


def process_stream(fh):
    for line in fh:
        m = LOG_RE.match(line.rstrip())
        if m:
            print_log_entry(m)
        else:
            print_stacktrace(line)


def main():
    if len(sys.argv) == 2:
        with open(sys.argv[1], encoding="utf-8", errors="replace") as fh:
            process_stream(fh)

    elif not sys.stdin.isatty():
        process_stream(sys.stdin)

    else:
        print(
            f"Usage: {Path(sys.argv[0]).name} catalina.out\n"
            f"   or: cat catalina.out | {Path(sys.argv[0]).name}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
