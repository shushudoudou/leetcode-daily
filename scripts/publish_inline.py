#!/usr/bin/env python3
"""Generate missing LeetCode C++17 explanations into the standalone Pages HTML.

Requires OPENAI_API_KEY in GitHub Actions Secrets; never stores credentials
in the repository or in the deployed browser code.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "index.html"
START = dt.date(2026, 10, 26)
TZ = ZoneInfo("Asia/Shanghai")
PREFIX = "window.__CURRICULUM__="
MIDDLE = ";window.__SOLUTIONS__="
SUFFIX = ";</script>"
CLASSES = {146: "LRUCache", 155: "MinStack", 208: "Trie"}


def read_data():
    html = FILE.read_text(encoding="utf-8")
    a = html.index(PREFIX) + len(PREFIX)
    b = html.index(MIDDLE, a)
    c = html.index(SUFFIX, b)
    return html, b + len(MIDDLE), c, json.loads(html[a:b]), json.loads(html[b + len(MIDDLE):c])


def generate(problem):
    key = os.environ["OPENAI_API_KEY"]
    model = os.environ.get("OPENAI_MODEL") or "gpt-4.1-mini"
    class_name = CLASSES.get(int(problem["id"]), "Solution")
    keys = ["idea", "code", "complexity", "pitfall", "alternative", "pattern"]
    schema = {"type": "object", "properties": {k: {"type": "string"} for k in keys},
              "required": keys, "additionalProperties": False}
    prompt = (
        f'LeetCode {problem["id"]} {problem["title"]} '
        f'(https://leetcode.cn/problems/{problem["slug"]}/). '
        f'题意：{problem["summary"]}。题型：{problem["topic"]}。'
        f'输入输出示例：{json.dumps(problem.get("example", {}), ensure_ascii=False)}。'
        f'严格生成适配官方函数签名和约束的 C++17 可提交答案；使用 class {class_name}。'
        '平台 ListNode/TreeNode 类型不要重复定义。'
        'idea 用中文4-6句（至少180个汉字）解释为什么采用此解法、核心步骤、'
        '必要不变量或正确性理由，以及相对于暴力算法的优势，不要仅写算法名称。'
        'complexity写时间空间并明确是否含输出，'
        'pitfall写至少两个关键边界或易错点，'
        'alternative写一条替代解法及其复杂度，'
        'pattern给出一句话可迁移的题型识别套路。'
        'code中包含必要标准库头文件和完整提交代码，不要 Markdown 代码围栏。'
        '对于设计题使用官方类名，构造函数和全部方法签名完整。'
        '特别核查输入输出示例与 C++17 解法逻辑一致。'
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是谨慎的 C++17 算法讲师，检查数据类型、边界条件和复杂度。"},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "leetcode_solution", "strict": True, "schema": schema}},
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=130) as res:
        response = json.load(res)
    obj = json.loads(response["choices"][0]["message"]["content"])
    if not all(isinstance(obj.get(k), str) and obj[k].strip() for k in keys):
        raise RuntimeError("Generated explanation is incomplete")
    if not re.search(r"\bclass\s+" + re.escape(class_name) + r"\b", obj["code"]):
        raise RuntimeError("Generated C++ does not declare expected class")
    if "```" in obj["code"]:
        raise RuntimeError("Generated code contains Markdown fences")
    return obj


def main():
    now = dt.datetime.now(TZ)
    day = (now.date() - START).days + 1
    if day < 1 or now.hour < 19:
        print("Not within evening publication window")
        return
    html, start, end, curriculum, answers = read_data()
    ids = curriculum["pairs"][(day - 1) % 50]
    missing = [int(i) for i in ids if str(i) not in answers["solutions"]]
    print(f"Day {day}, questions {ids}, missing {missing}")
    if not missing:
        return
    for ident in missing:
        p = curriculum["problems"][str(ident)]
        answers["solutions"][str(ident)] = generate(p)
        answers["editorialUpdatedThroughDay"] = max(
            day, int(answers.get("editorialUpdatedThroughDay", 0)))
        # Inline JSON in an HTML script needs '<' escaped to avoid </script> injection.
        safe_json = json.dumps(answers, ensure_ascii=False, indent=2).replace("<", "\\u003c")
        html = html[:start] + safe_json + html[end:]
        FILE.write_text(html, encoding="utf-8")
        html, start, end, curriculum, answers = read_data()
        print(f"Saved solution for #{ident}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Failed publishing nightly editorial:", exc, file=sys.stderr)
        sys.exit(1)
