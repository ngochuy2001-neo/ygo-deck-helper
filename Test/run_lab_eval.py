#!/usr/bin/env python3
"""
Đánh giá Judge Lab qua API — đọc Test/Questions.md, gọi POST /api/v1/lab/chat.

Chấm điểm theo rubric ngữ nghĩa (keyword/concept), không yêu cầu khớp từng chữ.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = REPO_ROOT / "Test" / "Questions.md"
DEBUG_LOG = REPO_ROOT / ".cursor" / "debug-f2d066.log"
DEFAULT_API = "http://localhost:8000/api/v1/lab/chat"


@dataclass
class Rubric:
    """Nhóm keyword bắt buộc / cấm để chấm reply."""

    must_any: list[list[str]] = field(default_factory=list)
    """Mỗi nhóm: ít nhất 1 keyword (OR trong nhóm)."""

    must_all: list[str] = field(default_factory=list)
    """Tất cả keyword phải có (AND)."""

    must_not: list[str] = field(default_factory=list)
    """Không được xuất hiện."""

    ruling: str | None = None
    """denied | allowed | depends — kiểm tra phán quyết mở đầu không mâu thuẫn."""


@dataclass
class QuestionCase:
    id: int
    title: str
    message: str
    rubric: Rubric
    expected_summary: str


def _debug_log(message: str, data: dict, hypothesis_id: str = "eval") -> None:
    # region agent log
    payload = {
        "sessionId": "f2d066",
        "timestamp": int(time.time() * 1000),
        "location": "Test/run_lab_eval.py",
        "message": message,
        "data": data,
        "hypothesisId": hypothesis_id,
        "runId": data.get("run_id", "eval"),
    }
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DEBUG_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    # endregion


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _contains_any(text: str, keywords: list[str]) -> bool:
    hay = _normalize(text)
    for kw in keywords:
        if ".*" in kw or kw.startswith("("):
            if re.search(kw, hay, re.IGNORECASE):
                return True
        elif kw.lower() in hay:
            return True
    return False


def _contains_all(text: str, keywords: list[str]) -> bool:
    hay = _normalize(text)
    return all(k.lower() in hay for k in keywords)


def _first_line(text: str) -> str:
    return text.strip().split("\n")[0].strip()


def _check_ruling_opener(reply: str, expected: str) -> list[str]:
    """Phát hiện phán quyết mở đầu mâu thuẫn (False Positive Yes/No)."""
    issues: list[str] = []
    first = _normalize(_first_line(reply))
    body = _normalize(reply[:800])

    contradictory_yes = bool(
        re.match(r"^có[\.\s,]", first)
        and re.search(
            r"ngăn cản|không.*(được|thể).*(kích hoạt|activate)|cannot activate|not allowed|sẽ không",
            body,
        )
    )
    if contradictory_yes:
        issues.append('Mâu thuẫn: mở đầu "Có" nhưng giải thích là không được phép')

    if expected == "denied":
        ok = bool(
            re.search(r"không được phép|\(no\)", first)
            or re.match(r"^không[\.\s]", first)
        )
        if re.search(r"được phép \(yes\)|^có[\.\s,]", first) and not ok:
            issues.append("Phán quyết đầu phải là KHÔNG ĐƯỢC PHÉP (NO), không phải Có/YES")
    elif expected == "allowed":
        ok = bool(re.search(r"được phép \(yes\)|\(yes\)", first) or re.match(r"^có[\.\s]", first))
        if re.search(r"không được phép|\(no\)", first):
            issues.append("Phán quyết đầu phải là ĐƯỢC PHÉP (YES)")

    return issues


def _score_reply(reply: str, rubric: Rubric) -> tuple[bool, list[str]]:
    issues: list[str] = []
    hay = _normalize(reply)

    if rubric.ruling:
        issues.extend(_check_ruling_opener(reply, rubric.ruling))

    for kw in rubric.must_all:
        if kw.lower() not in hay:
            issues.append(f"Thiếu bắt buộc: {kw}")

    for index, group in enumerate(rubric.must_any, start=1):
        if not _contains_any(reply, group):
            issues.append(f"Thiếu nhóm OR #{index}: {group}")

    for kw in rubric.must_not:
        if kw.lower() in hay:
            issues.append(f"Không được có: {kw}")

    return len(issues) == 0, issues


def _extract_section(block: str, heading: str) -> str:
    pattern = rf"### {re.escape(heading)}\s*\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, block, re.DOTALL)
    return match.group(1).strip() if match else ""


def _parse_questions_md(path: Path) -> list[QuestionCase]:
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n---\n", text)
    cases: list[QuestionCase] = []

    rubrics: dict[int, Rubric] = {
        1: Rubric(
            must_any=[
                ["b", "hiệu ứng b", "category 1", "hạng mục 1", "mandatory", "bắt buộc"],
                ["d", "hiệu ứng d", "category 2"],
                ["c", "hiệu ứng c", "category 3"],
                ["a", "hiệu ứng a", "category 4"],
                ["không", "no", "không có quyền", "cannot", "không được hoán", "không được quyền", "nghiêm ngặt", "cố định"],
            ],
        ),
        2: Rubric(
            must_any=[
                ["cost", "chi phí", "trục xuất", "banish", "không.*hoàn", "không.*trả lại"],
                ["target", "mục tiêu", "chỉ định", "không.*thay", "không thay đổi", "không đổi", "khóa"],
            ],
        ),
        3: Rubric(
            must_any=[
                ["không", "no"],
                ["and if you do", "if you do"],
                ["then"],
                ["đồng thời", "simultaneous", "cùng lúc"],
                ["tuần tự", "sequential", "miss timing", "lỡ"],
            ],
        ),
        4: Rubric(
            must_any=[
                ["không", "no", "without effect", "resolve without", "thất bại", "vô hiệu", "không làm gì"],
                ["continuous", "liên tục", "trên sân", "face-up", "field"],
            ],
        ),
        5: Rubric(
            must_any=[
                ["không", "no", "cannot", "không thể"],
                ["continuous", "liên tục", "non-activated", "không kích hoạt", "không mở chain", "tự động", "activation"],
                [":", "semicolon", "chấm phẩy", "hai chấm", "dấu", "kích hoạt"],
            ],
        ),
        6: Rubric(
            ruling="denied",
            must_any=[
                ["continuous", "liên tục", "continuous effect"],
                ["trigger", "kích hoạt", "triệu hồi", "summoned", "activation"],
                ["ngăn cản", "không.*kích hoạt", "cannot activate", "không được phép", "chain"],
            ],
            must_not=[],
        ),
    }

    for block in blocks:
        header = re.search(r"## Câu hỏi (\d+): (.+)", block)
        if not header:
            continue
        qid = int(header.group(1))
        title = header.group(2).strip()
        situation = _extract_section(block, "Tình huống")
        question = _extract_section(block, "Câu hỏi")
        expected = _extract_section(block, "Câu trả lời kỳ vọng (Expected Output)")

        message_parts = [p for p in [situation, question] if p]
        message = "\n\n".join(message_parts)

        cases.append(
            QuestionCase(
                id=qid,
                title=title,
                message=message,
                rubric=rubrics.get(qid, Rubric()),
                expected_summary=expected[:400],
            )
        )

    return sorted(cases, key=lambda c: c.id)


def _call_lab_chat(
    api_url: str,
    message: str,
    *,
    rag_limit: int = 5,
    timeout: float = 180.0,
) -> dict:
    body = json.dumps(
        {
            "message": message,
            "use_rag": True,
            "use_query_analyzer": True,
            "rag_limit": rag_limit,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_eval(
    *,
    api_url: str = DEFAULT_API,
    question_ids: list[int] | None = None,
    rag_limit: int = 5,
) -> int:
    cases = _parse_questions_md(QUESTIONS_PATH)
    if question_ids:
        cases = [c for c in cases if c.id in question_ids]

    if not cases:
        print("Không parse được câu hỏi từ Questions.md", file=sys.stderr)
        return 1

    passed = 0
    results: list[dict] = []

    print(f"Chạy {len(cases)} câu hỏi → {api_url}\n")

    for case in cases:
        print(f"[Q{case.id}] {case.title}...")
        t0 = time.time()
        try:
            response = _call_lab_chat(api_url, case.message, rag_limit=rag_limit)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"  HTTP {exc.code}: {detail[:300]}")
            _debug_log(
                "lab_chat_http_error",
                {"qid": case.id, "status": exc.code, "detail": detail[:500]},
                hypothesis_id="H1",
            )
            results.append({"id": case.id, "pass": False, "error": detail[:300]})
            continue
        except Exception as exc:  # noqa: BLE001
            print(f"  Lỗi: {exc}")
            results.append({"id": case.id, "pass": False, "error": str(exc)})
            continue

        elapsed = round(time.time() - t0, 1)
        reply = response.get("reply", "")
        ok, issues = _score_reply(reply, case.rubric)

        _debug_log(
            "lab_eval_result",
            {
                "qid": case.id,
                "pass": ok,
                "issues": issues,
                "rag_used": response.get("rag_used"),
                "rag_scope": response.get("rag_scope"),
                "rag_hits_count": len(response.get("rag_hits") or []),
                "reply_len": len(reply),
                "reply_preview": reply[:500],
                "elapsed_s": elapsed,
            },
            hypothesis_id="H2" if ok else "H3",
        )

        if ok:
            passed += 1
            print(f"  PASS ({elapsed}s) rag={response.get('rag_used')} scope={response.get('rag_scope')}")
        else:
            print(f"  FAIL ({elapsed}s): {'; '.join(issues)}")
            print(f"  Reply preview: {reply[:280]}…")

        results.append(
            {
                "id": case.id,
                "pass": ok,
                "issues": issues,
                "rag_used": response.get("rag_used"),
                "rag_scope": response.get("rag_scope"),
                "elapsed_s": elapsed,
            }
        )

    print(f"\n{'=' * 60}")
    print(f"Kết quả: {passed}/{len(cases)} PASS")
    _debug_log("lab_eval_summary", {"passed": passed, "total": len(cases), "results": results})

    return 0 if passed == len(cases) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Đánh giá Judge Lab qua API")
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--ids", type=str, default="", help="VD: 1,3,5")
    parser.add_argument("--rag-limit", type=int, default=5)
    args = parser.parse_args()

    ids = [int(x.strip()) for x in args.ids.split(",") if x.strip()] or None
    return run_eval(api_url=args.api, question_ids=ids, rag_limit=args.rag_limit)


if __name__ == "__main__":
    raise SystemExit(main())
