from dataclasses import dataclass

@dataclass(frozen=True)
class CommonConst:
    # 役割ごとのフォルダ定義
    ROLE_MAP = {
        "entity": "entity",
        "repository": "repository",
        "service": "service",
        "controller": "controller"
    }