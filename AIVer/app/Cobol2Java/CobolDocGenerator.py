import json
from typing import Dict, List


class CobolDocGenerator:
    def __init__(self, ast: Dict):
        self.ast = ast

    # =========================
    # メイン生成
    # =========================
    def generate(self) -> str:
        return f"""
【処理名】
{self._program_name()}

【入力】
{self._input()}

【出力】
{self._output()}

【処理概要】
{self._summary()}

【処理フロー】
{self._flow()}

【業務ルール】
{self._rules()}

【外部呼び出し】
{self._calls()}

【例外処理】
{self._exceptions()}
""".strip()

    # =========================
    # 各項目生成
    # =========================
    def _program_name(self) -> str:
        return self.ast.get("program_id", "UNKNOWN") 

    def _input(self) -> str:
        if self.ast.get("file_io"):
            return "ファイル入力あり"
        return "なし"

    def _output(self) -> str:
        if any("DISPLAY" in c for c in self.ast.get("conditions", [])):
            return "画面出力あり"
        return "なし"

    def _summary(self) -> str:
        if self.ast.get("conditions"):
            return "条件判定を伴うデータ処理を行う"
        return "単純なデータ処理"

    def _flow(self) -> str:
        steps = []
        step_no = 1

        # PERFORM
        for call in self.ast.get("calls", []):
            steps.append(f"{step_no}. {call['target']} を実行")
            step_no += 1

        # 条件
        for cond in self.ast.get("conditions", []):
            steps.append(f"{step_no}. IF {cond}")
            step_no += 1

        return "\n".join(steps) if steps else "処理なし"

    def _rules(self) -> str:
        rules = []
        for cond in self.ast.get("conditions", []):
            rules.append(f"・{cond} の条件で分岐")
        return "\n".join(rules) if rules else "なし"

    def _calls(self) -> str:
        calls = [c["target"] for c in self.ast.get("calls", [])]
        return "\n".join(set(calls)) if calls else "なし"

    def _exceptions(self) -> str:
        return "未定義（要補完）"


