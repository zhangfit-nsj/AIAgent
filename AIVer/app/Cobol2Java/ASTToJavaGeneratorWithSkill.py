from openai import OpenAI

class ASTToJavaGeneratorWithSkill:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def load_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_java(self,skill: str, ast_content: str) -> str:
        prompt = f"""
{skill}

【追加要件】
　・MyBatisを使用
　・ユーザ管理機能を生成

【入力AST】
{ast_content}
"""
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content
