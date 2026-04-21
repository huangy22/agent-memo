import argparse
import json
from pathlib import Path

from ..core.trace_writer import append_trace


def write_note(repo_root: Path, note_type: str, title: str, body: dict[str, list[str]]) -> None:
    if note_type == "error_fixed":
        heading = "Error Fixed"
    elif note_type == "decision_made":
        heading = "Decision Made"
    else:
        raise ValueError(f"Unsupported note_type: {note_type}")
    append_trace(Path(repo_root), heading=heading, body=body)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--type", required=True, dest="note_type")
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", required=True)
    args = parser.parse_args()

    body = json.loads(Path(args.body_file).read_text(encoding="utf-8"))
    if not isinstance(body, dict):
        raise ValueError("body-file must contain a JSON object")
    normalized_body = {
        str(key): [str(item) for item in value]
        for key, value in body.items()
        if isinstance(value, list)
    }
    write_note(Path(args.repo), args.note_type, args.title, normalized_body)


if __name__ == "__main__":
    main()
