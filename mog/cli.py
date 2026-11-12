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

EXCEPTION_RE = re.compile(
    r'^([a-zA-Z0-9_.]+(?:Exception|Error))'
)

FRAME_RE = re.compile(
    r'^\s*at\s+'
)

CAUSED_BY_RE = re.compile(
    r'^Caused by:'
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


def append_trace(body, trace_lines):
    if trace_lines:
        body.append("\n\n")
        body.append("Exception\n", style="bold red")

        for line in trace_lines:

            if CAUSED_BY_RE.match(line):
                body.append(line + "\n", style="bold red")

            elif FRAME_RE.match(line):
                body.append(line + "\n", style="cyan")

            elif EXCEPTION_RE.match(line):
                body.append(line + "\n", style="red")

            else:
                body.append(line + "\n", style="dim")

def append_exception_to_header(header, trace_lines):
    if trace_lines:
        for line in trace_lines:
            m = EXCEPTION_RE.match(line)
            if m:
                exception_name = m.group(1).split('.')[-1]
                header.append(f" | {exception_name}", style="red")
                break

def render_entry(match, trace_lines):
    level = match.group("level")
    colour = LEVEL_COLOURS.get(level, "white")

    header = Text()
    header.append(level, style=colour)

    append_exception_to_header(header, trace_lines)

    message = Text.from_ansi(match.group("message"))

    body = Text()
    body.append(match.group("timestamp"), style="cyan")
    body.append("\n")
    body.append(match.group("thread"), style="magenta")
    body.append("\n")
    body.append(match.group("logger"), style="bright_black")
    body.append("\n")
    body.append(message)

    append_trace(body, trace_lines)

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
    current_match = None
    current_trace = []

    for line in fh:
        m = LOG_RE.match(line.rstrip())
        if m:
            if current_match:
                render_entry(current_match, current_trace)

            current_match = m
            current_trace = []

        else:
            current_trace.append(line.rstrip())

    if current_match:
        render_entry(current_match, current_trace)

def main():
    try:
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
    except KeyboardInterrupt:
        sys.exit(130)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
