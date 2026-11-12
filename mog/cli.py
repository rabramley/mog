#!/usr/bin/env python3

import re
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

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
    header.append(match.group("timestamp"), style="cyan")
    header.append("\n")
    header.append(level.ljust(8), style=colour)
    header.append(" ")
    header.append(match.group("thread"), style="magenta")
    header.append("\n")
    header.append(match.group("logger"), style="bright_black")

    console.print(header)

    console.print(
        Panel(
            match.group("message"),
            border_style=colour,
            title=level,
            expand=False,
        )
    )


def print_stacktrace(line):
    console.print(line.rstrip(), style="dim")


def process_file(filename):
    with open(filename, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = LOG_RE.match(line.rstrip())

            if m:
                print_log_entry(m)
            else:
                print_stacktrace(line)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} catalina.out")
        sys.exit(1)

    process_file(sys.argv[1])

if __name__ == "__main__":
    main()
