# -*- coding: utf-8 -*-
# 解析后业务校验：用 Pydantic 模型做字段类型/枚举/默认值兜底
from pydantic import BaseModel, field_validator, ValidationError


class UserInfo(BaseModel):
    name: str
    age: int
    city: str = "未知"          # 选填字段，给默认值兜底
    vip_level: str = "normal"

    @field_validator("age")
    def age_reasonable(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError(f"年龄不合法: {v}")
        return v

    @field_validator("vip_level")
    def vip_enum(cls, v: str) -> str:
        allowed = {"normal", "silver", "gold", "platinum"}
        if v not in allowed:
            return "normal"   # 非法枚举值降级为默认
        return v


def parse_user(raw: dict):
    try:
        user = UserInfo(**raw)
        return user.model_dump(), None
    except ValidationError as e:
        # 关键字段缺失 -> 触发补问；非关键字段 -> 用默认值
        missing = [err["loc"][0] for err in e.errors() if err["type"] == "missing"]
        return None, f"缺少必填字段: {missing}，请补问用户"


# 测试：模型返回的 JSON 缺 city、age 离谱、vip_level 瞎写
bad_data = {"name": "张三", "age": 999, "vip_level": "钻五"}
result, err = parse_user(bad_data)
print(err)     # None（缺的是选填，不报错）
print(result)  # {'name':'张三', 'age':999, 'city':'未知', 'vip_level':'normal'}
