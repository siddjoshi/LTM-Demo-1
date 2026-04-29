from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class StoreError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Memory:
    id: str
    text: str
    tags: tuple[str, ...]
    created_at: str
    updated_at: str
    pinned: bool = False
    meta: dict[str, Any] = dataclasses.field(default_factory=dict)


def _utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat()


def _normalize_tags(tags: Iterable[str] | None) -> tuple[str, ...]:
    if not tags:
        return ()
    normalized: list[str] = []
    for tag in tags:
        if tag is None:
            continue
        t = str(tag).strip().lower()
        if not t:
            continue
        normalized.append(t)
    return tuple(sorted(set(normalized)))


class LTMStore:
    """A small local long-term memory store.

    Features:
    - JSON persistence
    - Add/update/delete/list memories
    - Tagging, pinning
    - Simple search over text/tags
    """

    def __init__(self, path: str | os.PathLike[str] = "./ltm.json") -> None:
        self.path = Path(path)
        self._memories: dict[str, Memory] = {}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        if not self.path.exists():
            self._memories = {}
            self._loaded = True
            return
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        memories = raw.get("memories", [])
        if not isinstance(memories, list):
            raise StoreError("Invalid store format: memories must be a list")
        loaded: dict[str, Memory] = {}
        for item in memories:
            if not isinstance(item, dict):
                continue
            mem = Memory(
                id=str(item.get("id")),
                text=str(item.get("text", "")),
                tags=_normalize_tags(item.get("tags")),
                created_at=str(item.get("created_at", "")),
                updated_at=str(item.get("updated_at", "")),
                pinned=bool(item.get("pinned", False)),
                meta=dict(item.get("meta") or {}),
            )
            if not mem.id:
                continue
            loaded[mem.id] = mem
        self._memories = loaded
        self._loaded = True

    def save(self) -> None:
        self.load()
        payload = {
            "version": 1,
            "updated_at": _utc_now_iso(),
            "memories": [self._to_dict(m) for m in self.list()],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_path.replace(self.path)

    def add(self, text: str, tags: Iterable[str] | None = None, *, pinned: bool = False, meta: dict[str, Any] | None = None) -> Memory:
        self.load()
        now = _utc_now_iso()
        mem_id = uuid.uuid4().hex
        memory = Memory(
            id=mem_id,
            text=text.strip(),
            tags=_normalize_tags(tags),
            created_at=now,
            updated_at=now,
            pinned=bool(pinned),
            meta=dict(meta or {}),
        )
        self._memories[mem_id] = memory
        return memory

    def get(self, mem_id: str) -> Memory:
        self.load()
        try:
            return self._memories[mem_id]
        except KeyError as exc:
            raise StoreError(f"Memory not found: {mem_id}") from exc

    def update(
        self,
        mem_id: str,
        *,
        text: str | None = None,
        tags: Iterable[str] | None = None,
        pinned: bool | None = None,
        meta: dict[str, Any] | None = None,
    ) -> Memory:
        current = self.get(mem_id)
        updated = Memory(
            id=current.id,
            text=current.text if text is None else str(text).strip(),
            tags=current.tags if tags is None else _normalize_tags(tags),
            created_at=current.created_at,
            updated_at=_utc_now_iso(),
            pinned=current.pinned if pinned is None else bool(pinned),
            meta=current.meta if meta is None else dict(meta),
        )
        self._memories[mem_id] = updated
        return updated

    def delete(self, mem_id: str) -> None:
        self.load()
        if mem_id not in self._memories:
            raise StoreError(f"Memory not found: {mem_id}")
        del self._memories[mem_id]

    def list(self, *, tag: str | None = None, pinned_first: bool = True) -> list[Memory]:
        self.load()
        memories = list(self._memories.values())
        if tag:
            t = tag.strip().lower()
            memories = [m for m in memories if t in m.tags]

        def sort_key(m: Memory) -> tuple[int, str]:
            return (0 if (pinned_first and m.pinned) else 1, m.created_at)

        return sorted(memories, key=sort_key)

    def search(self, query: str, *, tag: str | None = None, limit: int = 20) -> list[Memory]:
        self.load()
        q = query.strip().lower()
        if not q and not tag:
            return []
        candidates = self.list(tag=tag)

        def score(m: Memory) -> int:
            hay = (m.text + " " + " ".join(m.tags)).lower()
            if q and q not in hay:
                return 0
            if not q:
                return 1
            return hay.count(q)

        ranked = [(score(m), m) for m in candidates]
        ranked = [(s, m) for (s, m) in ranked if s > 0]
        ranked.sort(key=lambda x: (-x[0], 0 if x[1].pinned else 1, x[1].created_at))
        return [m for _, m in ranked[: max(1, int(limit))]]

    def stats(self) -> dict[str, Any]:
        self.load()
        by_tag: dict[str, int] = {}
        pinned = 0
        for m in self._memories.values():
            pinned += 1 if m.pinned else 0
            for t in m.tags:
                by_tag[t] = by_tag.get(t, 0) + 1
        top_tags = sorted(by_tag.items(), key=lambda kv: (-kv[1], kv[0]))
        return {
            "count": len(self._memories),
            "pinned": pinned,
            "tags": dict(top_tags),
        }

    @staticmethod
    def _to_dict(m: Memory) -> dict[str, Any]:
        return {
            "id": m.id,
            "text": m.text,
            "tags": list(m.tags),
            "created_at": m.created_at,
            "updated_at": m.updated_at,
            "pinned": m.pinned,
            "meta": m.meta,
        }

