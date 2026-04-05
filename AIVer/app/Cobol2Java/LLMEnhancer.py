import json
from openai import OpenAI

# =========================
# ② LLM補完
# =========================
class LLMEnhancer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def enhance(self, skill: str, template_text: str, ast: dict) -> str:
        prompt = f"""
要件
{skill}

入力ドキュメント：
{template_text}

補足情報（AST）：
{json.dumps(ast, indent=2, ensure_ascii=False)}
"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",  # 軽量でOK
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content

    def enhanceMd(self, template_text, ast):
        prompt = f"""
あなたは業務システムの設計書作成者です。

以下のドキュメントを改善してください。

制約：
- フォーマットは変更しない
- 各項目に自然な説明を追加
- 業務的に意味のある文章にする
- 推測は最小限
- 各処理間の関連図を追加

入力ドキュメント：
{template_text}

補足情報（AST）：
{json.dumps(ast, indent=2, ensure_ascii=False)}
"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",  # 軽量でOK
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content

