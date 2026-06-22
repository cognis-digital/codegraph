"""A backup CLI with two subcommands, `snapshot` and `restore`.

Diagramming the call tree under `main` is a fast way to document a CLI's
dispatch for a README or an architecture review.
"""

import argparse

from cmdtool.commands import cmd_restore, cmd_snapshot


def main(argv=None):
    """Parse args and dispatch to the selected subcommand."""
    parser = argparse.ArgumentParser(prog="cmdtool")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot")
    p_restore = sub.add_parser("restore")
    p_restore.add_argument("snapshot_id")
    args = parser.parse_args(argv)
    if args.command == "snapshot":
        return cmd_snapshot()
    return cmd_restore(args.snapshot_id)
