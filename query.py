"""Running queries against the flight database."""
import re
from datetime import datetime


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    invalid = {
        "query": query,
        "error": "INVALID_QUERY",
        "matches": []
    }

    if not isinstance(query, dict):
        return invalid

    record_keys = {
        "flight_id",
        "origin",
        "destination",
        "departure_datetime",
        "arrival_datetime",
        "price"
    }

    allowed_keys = record_keys | {
        "min_price", "sort_by", "order", "limit"
    }

    for key, value in query.items():
        if key not in allowed_keys:
            return invalid

        if key in ("flight_id", "origin", "destination"):
            if not isinstance(value, str):
                return invalid

        elif key in ("departure_datetime", "arrival_datetime"):
            if not isinstance(value, str):
                return invalid

            if not re.fullmatch(
                r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}",
                value
            ):
                return invalid

            try:
                datetime.strptime(value, "%Y-%m-%d %H:%M")
            except ValueError:
                return invalid

        elif key in ("price", "min_price"):
            if type(value) not in (int, float):
                return invalid

        elif key == "sort_by":
            if not isinstance(value, str) or value not in record_keys:
                return invalid

        elif key == "order":
            if value not in ("asc", "desc"):
                return invalid

        elif key == "limit":
            if type(value) is not int or value < 0:
                return invalid

    if "order" in query and "sort_by" not in query:
        return invalid

    matches = []

    for flight in db:
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            continue

        if "origin" in query and flight["origin"] != query["origin"]:
            continue

        if "destination" in query and flight["destination"] != query["destination"]:
            continue

        if "departure_datetime" in query:
            if flight["departure_datetime"] < query["departure_datetime"]:
                continue

        if "arrival_datetime" in query:
            if flight["arrival_datetime"] > query["arrival_datetime"]:
                continue

        if "price" in query and flight["price"] > query["price"]:
            continue

        if "min_price" in query and flight["price"] < query["min_price"]:
            continue

        matches.append(flight)

    if "sort_by" in query:
        matches = sorted(
            matches,
            key=lambda flight: flight[query["sort_by"]],
            reverse=query.get("order", "asc") == "desc"
        )

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        queries = [queries]

    return [run_query(db, query) for query in queries]
