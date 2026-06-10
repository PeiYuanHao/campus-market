from typing import List

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Campus Market AI Service", version="1.0.0")


class AIGenerateRequest(BaseModel):
    title: str
    category_name: str
    condition_level: str
    original_price: float = 0
    expected_price: float = 0


class AIGenerateResponse(BaseModel):
    description: str
    highlights: List[str]
    suggested_price_text: str


CONDITION_TEXT = {
    "new": "几乎全新，使用痕迹很轻",
    "good": "成色良好，功能正常",
    "fair": "有一定使用痕迹，但不影响正常使用",
}


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-service"}


@app.post("/api/ai/generate-description", response_model=AIGenerateResponse)
def generate_description(payload: AIGenerateRequest):
    condition_text = CONDITION_TEXT.get(payload.condition_level, "整体状态稳定，可正常使用")
    highlights = [
        f"{payload.category_name}类目，适合校园内当面交易",
        condition_text,
        "支持先看实物再决定，降低交易顾虑",
    ]

    price_text = "价格可小刀，欢迎理性沟通"
    if payload.original_price > 0 and payload.expected_price > 0:
        ratio = payload.expected_price / payload.original_price
        if ratio <= 0.35:
            price_text = "参考定价偏实惠，适合快速出手"
        elif ratio <= 0.65:
            price_text = "参考定价处于常见二手区间，接受度较高"
        else:
            price_text = "参考定价略高，建议强调成色和配件完整度"

    description = (
        f"{payload.title}准备转手，商品目前{condition_text}。"
        f"日常使用和功能表现都比较稳定，适合校内同学自提或当面验货。"
        f"如果你正在找一件靠谱的{payload.category_name}用品，这件会是比较省心的选择。"
        f"{price_text}。"
    )

    return AIGenerateResponse(
        description=description,
        highlights=highlights,
        suggested_price_text=price_text,
    )
