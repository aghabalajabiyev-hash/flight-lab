"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import argparse
import json
import logging
import os
from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251ADB102"
FIRST_NAME = "Aghabala"
LAST_NAME = "Jabiyev"


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE")
    source.add_argument("-d", metavar="FOLDER")
    source.add_argument("-j", metavar="FILE")

    parser.add_argument("-a", metavar="FILE")
    parser.add_argument("-o", metavar="FILE")
    parser.add_argument("-q", metavar="FILE")
    parser.add_argument("-r", metavar="FOLDER", default=".")

    try:
        args = parser.parse_args(argv)

        if (args.i is not None or args.d is not None) and args.a is None:
            parser.error("-a is required with -i or -d")

        if args.j is not None and args.o is not None:
            parser.error("-o is not allowed with -j")

    except SystemExit as exc:
        return exc.code

    logger = logging.getLogger("flight_parser")
    handler = None

    try:
        if args.j is not None:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list) or not all(
                isinstance(record, dict) for record in db
            ):
                raise ValueError("Invalid JSON database shape")

        else:
            if args.i is not None:
                paths = [args.i]
            else:
                paths = [
                    os.path.join(args.d, name)
                    for name in sorted(os.listdir(args.d))
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, name))
                ]

                if not paths:
                    raise ValueError("No CSV files found")

            output_path = args.o if args.o is not None else "db.json"
            log_path = os.path.join(
                os.path.dirname(output_path), "errors.log"
            )

            logger.setLevel(logging.INFO)

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"
            )

            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))

            logger.addHandler(handler)

            airports = load_airports(args.a)
            db, errors = parse_files(paths, airports)

            for error in errors:
                logger.warning(error)

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(db, file, indent=2)

        if args.q is not None:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if not isinstance(queries, dict):
                if not isinstance(queries, list) or not all(
                    isinstance(query, dict) for query in queries
                ):
                    raise ValueError("Invalid query file shape")

            responses = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            response_name = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_"
                f"{LAST_NAME}_{timestamp}.json"
            )

            response_path = os.path.join(args.r, response_name)

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(responses, file, indent=2)

        return 0

    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
