"""OpenAI API 用量與費用記錄。"""
import csv
from pathlib import Path

FIELDNAMES = [
    "date",
    "model",
    "papers_analyzed",
    "prompt_tokens",
    "completion_tokens",
    "reasoning_tokens",
    "total_tokens",
    "estimated_cost_usd",
    "estimated_cost_twd",
]


def summarize_usage(usage_records: list[dict]) -> dict:
    """加總每篇論文分析呼叫回傳的 token 用量。"""
    return {
        "prompt_tokens": sum(r.get("prompt_tokens") or 0 for r in usage_records),
        "completion_tokens": sum(r.get("completion_tokens") or 0 for r in usage_records),
        "reasoning_tokens": sum(r.get("reasoning_tokens") or 0 for r in usage_records),
        "total_tokens": sum(r.get("total_tokens") or 0 for r in usage_records),
    }


def estimate_cost(usage: dict, pricing: dict) -> dict:
    """依 config.yaml 的 pricing 設定換算費用；未填單價時回傳 None（不亂猜價格）。"""
    input_rate = (pricing or {}).get("input_per_1m_usd") or 0
    output_rate = (pricing or {}).get("output_per_1m_usd") or 0
    usd_to_twd = (pricing or {}).get("usd_to_twd") or 0

    if not input_rate and not output_rate:
        return {"cost_usd": None, "cost_twd": None}

    cost_usd = (
        usage["prompt_tokens"] / 1_000_000 * input_rate
        + usage["completion_tokens"] / 1_000_000 * output_rate
    )
    cost_twd = cost_usd * usd_to_twd if usd_to_twd else None
    return {
        "cost_usd": round(cost_usd, 4),
        "cost_twd": round(cost_twd, 2) if cost_twd is not None else None,
    }


def append_usage_log(
    log_path: Path,
    date: str,
    model: str,
    papers_analyzed: int,
    usage: dict,
    cost: dict,
) -> None:
    """把這次執行的用量／預估費用追加寫入 CSV（檔案不存在時自動建立並加表頭）。"""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not log_path.exists()
    with open(log_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if is_new:
            writer.writeheader()
        writer.writerow({
            "date": date,
            "model": model,
            "papers_analyzed": papers_analyzed,
            "prompt_tokens": usage["prompt_tokens"],
            "completion_tokens": usage["completion_tokens"],
            "reasoning_tokens": usage["reasoning_tokens"],
            "total_tokens": usage["total_tokens"],
            "estimated_cost_usd": cost["cost_usd"] if cost["cost_usd"] is not None else "",
            "estimated_cost_twd": cost["cost_twd"] if cost["cost_twd"] is not None else "",
        })
