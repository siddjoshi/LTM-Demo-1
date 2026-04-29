from __future__ import annotations

import argparse
import json
import sys

from ltm_demo.store import LTMStore, StoreError


def _comma_list(value: str) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ltm", description="Local long-term memory demo")
    # argparse only supports global options before the subcommand.
    # To keep UX friendly, we also add --store to each subcommand.
    parser.add_argument("--store", default="./ltm.json", help="Path to JSON store file")

    sub = parser.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add", help="Add a new memory")
    add.add_argument("text")
    add.add_argument("--store", default=None, help=argparse.SUPPRESS)
    add.add_argument("--tags", default="", help="Comma-separated tags")
    add.add_argument("--pinned", action="store_true")
    add.add_argument("--meta", default="{}", help="JSON dict for extra metadata")

    ls = sub.add_parser("list", help="List memories")
    ls.add_argument("--tag", default=None)
    ls.add_argument("--json", action="store_true", help="Output JSON")
    ls.add_argument("--store", default=None, help=argparse.SUPPRESS)

    search = sub.add_parser("search", help="Search memories")
    search.add_argument("query")
    search.add_argument("--tag", default=None)
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--json", action="store_true")
    search.add_argument("--store", default=None, help=argparse.SUPPRESS)

    upd = sub.add_parser("update", help="Update an existing memory")
    upd.add_argument("id")
    upd.add_argument("--text", default=None)
    upd.add_argument("--tags", default=None, help="Comma-separated tags")
    upd.add_argument("--pinned", default=None, choices=["true", "false"])
    upd.add_argument("--meta", default=None, help="JSON dict for extra metadata")
    upd.add_argument("--store", default=None, help=argparse.SUPPRESS)

    rm = sub.add_parser("delete", help="Delete a memory")
    rm.add_argument("id")
    rm.add_argument("--store", default=None, help=argparse.SUPPRESS)

    stats = sub.add_parser("stats", help="Show store stats")
    stats.add_argument("--json", action="store_true")
    stats.add_argument("--store", default=None, help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    store_path = args.store
    if getattr(args, "store", None) is None and hasattr(args, "cmd"):
        store_path = "./ltm.json"
    if getattr(args, "cmd", None) and getattr(args, "store", None):
        store_path = args.store
    if getattr(args, "cmd", None) and getattr(args, "store", None) is None:
        # subcommands may set args.store to None; fall back to global
        store_path = getattr(parser.parse_args(argv[: argv.index(args.cmd)]), "store", "./ltm.json") if argv and args.cmd in argv else store_path

    store = LTMStore(store_path)
    try:
        if args.cmd == "add":
            meta = json.loads(args.meta)
            mem = store.add(args.text, tags=_comma_list(args.tags), pinned=args.pinned, meta=meta)
            store.save()
            print(mem.id)
            return 0

        if args.cmd == "list":
            memories = store.list(tag=args.tag)
            if args.json:
                print(json.dumps([m.__dict__ for m in memories], indent=2, sort_keys=True))
            else:
                for m in memories:
                    tag_str = ",".join(m.tags)
                    pin = "*" if m.pinned else " "
                    print(f"{pin} {m.id} [{tag_str}] {m.text}")
            return 0

        if args.cmd == "search":
            memories = store.search(args.query, tag=args.tag, limit=args.limit)
            if args.json:
                print(json.dumps([m.__dict__ for m in memories], indent=2, sort_keys=True))
            else:
                for m in memories:
                    tag_str = ",".join(m.tags)
                    pin = "*" if m.pinned else " "
                    print(f"{pin} {m.id} [{tag_str}] {m.text}")
            return 0

        if args.cmd == "update":
            pinned = None
            if args.pinned is not None:
                pinned = args.pinned == "true"
            tags = None if args.tags is None else _comma_list(args.tags)
            meta = None if args.meta is None else json.loads(args.meta)
            mem = store.update(args.id, text=args.text, tags=tags, pinned=pinned, meta=meta)
            store.save()
            print(mem.id)
            return 0

        if args.cmd == "delete":
            store.delete(args.id)
            store.save()
            return 0

        if args.cmd == "stats":
            s = store.stats()
            if args.json:
                print(json.dumps(s, indent=2, sort_keys=True))
            else:
                print(f"count: {s['count']}")
                print(f"pinned: {s['pinned']}")
                for tag, count in s["tags"].items():
                    print(f"tag:{tag} {count}")
            return 0

        parser.error("Unknown command")
        return 2
    except (StoreError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
