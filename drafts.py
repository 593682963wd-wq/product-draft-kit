from __future__ import annotations
import re
from typing import Any
PRODUCTS={}
def product_map():return PRODUCTS

BLOCKED_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"厂家直营|源头工厂|官方直营|官方旗舰", "不得虚构经营身份、授权或货源"),
    (r"补单|刷单|群补|小黄鱼|礼品单|虚拟单号|刷好评", "不得制造虚假交易、物流或评价"),
    (r"加\s*[Vv]|加微|微信|vx|V信|私下交易|平台外付款", "交易和沟通应留在平台内"),
    (r"自动养号|全自动发布|模拟真人|规避风控|防封|绕过.*监管", "不得规避平台风控或模拟真人操作"),
    (r"包过|百分之百通过|100%通过|绝对保证", "不得作无法核验的绝对承诺"),
)

WARNING_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"最低价|全网最低|仅剩|最后一天|秒杀", "价格或稀缺性表述必须有真实依据"),
    (r"缺货", "不得用虚构缺货 SKU 引流"),
    (r"返现|好评红包", "避免以利益诱导评价"),
    (r"https?://|www\.", "确认没有站外引流链接"),
    (r"\b1[3-9]\d{9}\b", "确认没有公开手机号或站外联系方式"),
)

AI_DISCLOSURES = ("工具辅助", "AI辅助", "人工复核", "人工检查")

def build_listing(product_id: str) -> dict[str, Any]:
    products = product_map()
    if product_id not in products:
        raise KeyError(product_id)
    product = products[product_id]
    body = "\n".join(
        [
            f"【能帮你做什么】\n{product['summary']}",
            f"【基础范围】\n{product['base_scope']}，基础价 {product['base_price']:.2f} 元。复杂情况先看脱敏样例再报价。",
            "【交付内容】\n" + "\n".join(f"- {item}" for item in product["deliverables"]),
            "【下单流程】\n1. 先在闲鱼聊天说明文件类型、数量和截止时间\n2. 发送脱敏样例，双方确认范围与价格后再下单\n3. 处理完成后先发预览，确认后交付可编辑文件",
            "【边界说明】\n" + "\n".join(f"- 不承接：{item}" for item in product["not_included"]),
            "【隐私与工具说明】\n请先删除身份证号、银行卡号、账号口令、客户名单和公司机密等敏感信息。处理过程可能使用 AI 或自动化工具辅助，最终由本人逐项人工复核；发布时请使用平台提供的 AI 内容声明/标识功能（如有）。",
            "【售后】\n包含 1 次原约定范围内的小调整。新增内容或改变口径会重新确认价格。沟通、付款和交付均在闲鱼平台内完成。",
        ]
    )
    report = scan_compliance(product["title"] + "\n" + body)
    return {
        "product_id": product_id,
        "name": product["name"],
        "title": product["title"],
        "price": product["base_price"],
        "body": body,
        "keywords": product["keywords"],
        "compliance": report,
    }

def scan_compliance(text: str) -> dict[str, Any]:
    blockers = []
    warnings = []
    for pattern, message in BLOCKED_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            blockers.append({"match": match.group(0), "message": message})
    for pattern, message in WARNING_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            warnings.append({"match": match.group(0), "message": message})
    if ("AI" in text or "人工智能" in text) and not any(marker in text for marker in AI_DISCLOSURES):
        warnings.append({"match": "AI", "message": "应说明 AI/工具只作辅助且由人工复核，并使用平台声明功能"})
    if len(text.strip()) < 40:
        warnings.append({"match": "内容过短", "message": "补充真实范围、交付物、价格和售后边界"})
    status = "禁止发布" if blockers else ("需人工复核" if warnings else "可进入人工发布")
    return {"status": status, "blockers": blockers, "warnings": warnings}

def calculate_quote(product_id: str, extra_units: int = 0, rush: bool = False, formula_repair: bool = False) -> dict[str, Any]:
    products = product_map()
    if product_id not in products:
        raise KeyError(product_id)
    product = products[product_id]
    extra_units = max(0, min(int(extra_units), 100))
    subtotal = float(product["base_price"]) + extra_units * float(product["extra_unit_price"])
    items = [{"label": product["base_scope"], "amount": float(product["base_price"])}]
    if extra_units:
        amount = extra_units * float(product["extra_unit_price"])
        items.append({"label": f"{product['extra_unit_label']} × {extra_units}", "amount": amount})
    if formula_repair and product_id.startswith("excel"):
        subtotal += 20.0
        items.append({"label": "公式检查/修复起步", "amount": 20.0})
    if rush:
        rush_fee = round(subtotal * 0.3, 2)
        subtotal += rush_fee
        items.append({"label": "加急预留（需人工确认档期）", "amount": rush_fee})
    total = round(subtotal, 2)
    return {
        "product_id": product_id,
        "product_name": product["name"],
        "items": items,
        "total": total,
        "note": "这是范围报价草案，不自动承诺接单或时效；需看脱敏样例后由本人确认。",
    }
