import re
import json
from typing import List, Dict


class CobolASTParser:
    def __init__(self, cobol_text: str):
        self.raw_text = cobol_text
        self.text = self._preprocess(cobol_text)
        self.lines = self.text.split("\n")

    # =========================
    # 前処理（重要）
    # =========================
    def _preprocess(self, text: str) -> str:
        # コメント除去（*行）
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            if not line.strip().startswith("*"):
                cleaned.append(line)
        text = "\n".join(cleaned)

        # 大文字統一
        text = text.upper()

        return text

    # =========================
    # メイン解析
    # =========================
    def parse(self) -> Dict:
        return {
            "program_id": self._parse_program_id(),
            "variables": self._parse_variables(),
            "procedures": self._parse_procedures(),
            "calls": self._parse_calls(),
            "conditions": self._parse_conditions(),
            "loops": self._parse_loops(),
            "file_io": self._parse_file_io()
        }

    # =========================
    # PROGRAM-ID
    # =========================
    def _parse_program_id(self) -> str:
        pattern = re.compile(r'PROGRAM-ID\.\s+([\w-]+)', re.IGNORECASE)
        for line in self.lines:
            m = pattern.search(line)
            if m:
                return m.group(1)
        return ""

    # =========================
    # 変数定義
    # =========================
    def _parse_variables(self) -> List[Dict]:
        pattern = re.compile(
            r'^\s*(\d+)\s+([\w-]+)\s+PIC\s+([X9V\(\)\.\+\-]+)',
            re.IGNORECASE
        )
        variables = []

        for line in self.lines:
            m = pattern.match(line)
            if m:
                variables.append({
                    "level": m.group(1),
                    "name": m.group(2),
                    "pic": m.group(3)
                })
        return variables

    # =========================
    # PROCEDURE
    # =========================
    def _parse_procedures(self) -> List[str]:
        pattern = re.compile(r'^\s*([\w-]+)\.\s*$', re.IGNORECASE)
        procedures = []

        for line in self.lines:
            m = pattern.match(line)
            if m:
                procedures.append(m.group(1))
        return procedures

    # =========================
    # PERFORM / CALL
    # =========================
    def _parse_calls(self) -> List[Dict]:
        calls = []

        perform_pattern = re.compile(r'PERFORM\s+([\w-]+)', re.IGNORECASE)
        call_pattern = re.compile(r'CALL\s+[\'"]?([\w-]+)[\'"]?', re.IGNORECASE)

        for line in self.lines:
            m1 = perform_pattern.search(line)
            if m1:
                calls.append({"type": "PERFORM", "target": m1.group(1)})

            m2 = call_pattern.search(line)
            if m2:
                calls.append({"type": "CALL", "target": m2.group(1)})

        return calls

    # =========================
    # IF条件
    # =========================
    def _parse_conditions(self) -> List[str]:
        pattern = re.compile(r'IF\s+(.+)', re.IGNORECASE)
        conditions = []

        for line in self.lines:
            m = pattern.search(line)
            if m:
                conditions.append(m.group(1).strip())

        return conditions

    # =========================
    # ループ（PERFORM UNTILなど）
    # =========================
    def _parse_loops(self) -> List[str]:
        pattern = re.compile(r'PERFORM\s+UNTIL\s+(.+)', re.IGNORECASE)
        loops = []

        for line in self.lines:
            m = pattern.search(line)
            if m:
                loops.append(m.group(1).strip())

        return loops

    # =========================
    # ファイル操作
    # =========================
    def _parse_file_io(self) -> List[Dict]:
        io_ops = []
        pattern = re.compile(r'\b(OPEN|READ|WRITE|CLOSE)\b\s+([\w-]+)', re.IGNORECASE)

        for line in self.lines:
            m = pattern.search(line)
            if m:
                io_ops.append({
                    "operation": m.group(1),
                    "target": m.group(2)
                })

        return io_ops


