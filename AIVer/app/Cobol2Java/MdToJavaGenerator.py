from openai import OpenAI

class MdToJavaGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def load_md(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_java(self, skill: str, md_content: str) -> str:
        prompt = f"""
要件
{skill}

設計書：
{md_content}
"""

        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content
