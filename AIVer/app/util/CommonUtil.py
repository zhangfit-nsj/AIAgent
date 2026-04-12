import json
import re
import os
import boto3
import yaml
from  app.util.CommonConst import CommonConst

class CommonUtil:

    @staticmethod
    def write_json_to_file(data, file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"{file_path} に書き込み完了")
        except Exception as e:
            print(f"エラー：{e}")
    

    @staticmethod
    def read_json_from_file(file_path: str) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ast = json.load(f)
            # 必須キー確認
            required_keys = ["program_id", "variables", "procedures"]
            for key in required_keys:
                if key not in ast:
                    raise ValueError(f"キー不足: {key}")

            return ast
        except FileNotFoundError:
            print(f"ファイルが存在しません: {file_path}")
            return {}
        except json.JSONDecodeError:
            print("JSON形式が不正です")
            return {}
        except Exception as e:
            print(f"エラー: {e}")
            return {}

    @staticmethod
    def write_text_to_file(text: str, file_path: str):
        """テキスト/MD形式でファイルに書き込み（改行を保持）"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"{file_path} に書き込み完了")
        except Exception as e:
            print(f"エラー: {e}")

    @staticmethod
    def json_to_md(json_path, md_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                ast = json.load(f)

            # 必須キー確認
            required_keys = ["program_id", "variables", "procedures"]
            for key in required_keys:
                if key not in ast:
                    raise ValueError(f"キー不足: {key}")
                
            lines = []
            lines.append("# 解析結果\n\n")

            for key, value in ast.items():
                lines.append(f"## {key}\n")
                lines.append(f"{value}\n\n")

            with open(md_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
                
        except FileNotFoundError:
            print(f"ファイルが存在しません: {file_path}")
            return {}
        except json.JSONDecodeError:
            print("JSON形式が不正です")
            return {}
        except Exception as e:
            print(f"エラー: {e}")
            return {}

    @staticmethod        
    def split_java_files(text):
        """
        「### ファイル名.java」と```java```ブロックをペアで抽出
        """
        pattern = r"###\s*(\S+\.java).*?```java(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        return matches
    
    @staticmethod
    def detect_role(code):
        """
        パッケージ or アノテーションから役割判定
        """
        # packageベース（最優先）
        pkg_match = re.search(r'package\s+([\w\.]+);', code)
        if pkg_match:
            package = pkg_match.group(1)
            for key in CommonConst.ROLE_MAP:
                if key in package:
                    return CommonConst.ROLE_MAP[key]

        # アノテーションで判定（補助）
        if "@Entity" in code:
            return "entity"
        if "JpaRepository" in code:
            return "repository"
        if "@Service" in code:
            return "service"
        if "@RestController" in code:
            return "controller"

        return "others"
    
    @staticmethod
    def get_package_path(code):
        match = re.search(r'package\s+([\w\.]+);', code)
        if match:
            return match.group(1).replace('.', '/')
        return ""
    
    @staticmethod
    def save_files(out_path:str, file_list):
        for filename, code in file_list:
            role = CommonUtil.detect_role(code)
            package_path = CommonUtil.get_package_path(code)

            # フォルダ構成：output/role/package構造
            dir_path = os.path.join(out_path, package_path)
            os.makedirs(dir_path, exist_ok=True)
            filepath = os.path.join(dir_path, filename)

            # 前後の空白除去
            code = code.strip()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)

            print(f"出力: {filepath}")

    @staticmethod
    def split_java_classes(input_file: str, output_root: str):
        print("Step1: ファイル読み込み")
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # --------------------------------
        # importは全体から取得（共通）
        # --------------------------------
        imports = re.findall(r'import\s+[\w\.\*]+;', content)

        # --------------------------------
        # クラス開始検出
        # --------------------------------
        class_pattern = re.finditer(
            r'(public\s+)?(class|interface|enum)\s+(\w+)',
            content
        )

        class_list = []

        print("Step2: クラス抽出")

        for match in class_pattern:
            class_name = match.group(3)
            start_index = match.start()

            # --------------------------------
            # ★ 直前の package を取得
            # --------------------------------
            package_name = ""
            before_text = content[:start_index]

            package_matches = list(re.finditer(r'package\s+([\w\.]+);', before_text))
            if package_matches:
                package_name = package_matches[-1].group(1)

            package_path = package_name.replace('.', os.sep) if package_name else ""

            # --------------------------------
            # { } の対応を取る
            # --------------------------------
            brace_count = 0
            i = start_index
            in_class = False

            while i < len(content):
                if content[i] == '{':
                    brace_count += 1
                    in_class = True
                elif content[i] == '}':
                    brace_count -= 1
                    if in_class and brace_count == 0:
                        end_index = i + 1
                        class_text = content[start_index:end_index]
                        class_list.append((class_name, class_text, package_name, package_path))
                        break
                i += 1

        print(f"Step3: {len(class_list)} クラス検出")

        # --------------------------------
        # 出力処理
        # --------------------------------
        for class_name, class_body, package_name, package_path in class_list:

            # ディレクトリ作成
            output_dir = os.path.join(output_root, package_path)
            os.makedirs(output_dir, exist_ok=True)

            # ヘッダ作成
            header = ""

            if package_name:
                header += f"package {package_name};\n\n"

            if imports:
                header += "\n".join(sorted(set(imports))) + "\n\n"

            final_text = header + class_body

            output_file = os.path.join(output_dir, f"{class_name}.java")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_text)

            print(f"出力: {output_file}")

    @staticmethod
    def extract_xml_blocks(text):
        """
        ```xml ～ ``` をすべて抽出
        """
        pattern = r"```xml(.*?)```"
        return re.findall(pattern, text, re.DOTALL)

    @staticmethod
    def extract_namespace(xml_text):
        """
        namespace からファイル名を決定
        例：com.example.project.repository.OrderRepository
            → OrderMapper.xml
        """
        match = re.search(r'namespace="([^"]+)"', xml_text)
        if not match:
            return "UnknownMapper.xml"

        full_name = match.group(1)
        class_name = full_name.split(".")[-1]

        # Repository → Mapper に変換
        if class_name.endswith("Repository"):
            class_name = class_name.replace("Repository", "Mapper")

        return f"{class_name}.xml"


    @staticmethod
    def save_xml_files(xml_blocks, output_root: str):
        os.makedirs(output_root, exist_ok=True)

        for xml in xml_blocks:
            xml = xml.strip()
            file_name = CommonUtil.extract_namespace(xml)
            file_path = os.path.join(output_root, file_name)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(xml)

            print(f"✅ 出力: {file_path}")

    @staticmethod
    def load_file(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
        
    @staticmethod
    def split_java_classes_to_zip(content: str, output_root: str):
        # --------------------------------
        # importは全体から取得（共通）
        # --------------------------------
        imports = re.findall(r'import\s+[\w\.\*]+;', content)

        # --------------------------------
        # クラス開始検出
        # --------------------------------
        class_pattern = re.finditer(
            r'(public\s+)?(class|interface|enum)\s+(\w+)',
            content
        )

        class_list = []

        print("Step2: クラス抽出")

        for match in class_pattern:
            class_name = match.group(3)
            start_index = match.start()

            # --------------------------------
            # ★ 直前の package を取得
            # --------------------------------
            package_name = ""
            before_text = content[:start_index]

            package_matches = list(re.finditer(r'package\s+([\w\.]+);', before_text))
            if package_matches:
                package_name = package_matches[-1].group(1)

            package_path = package_name.replace('.', os.sep) if package_name else ""

            # --------------------------------
            # { } の対応を取る
            # --------------------------------
            brace_count = 0
            i = start_index
            in_class = False

            while i < len(content):
                if content[i] == '{':
                    brace_count += 1
                    in_class = True
                elif content[i] == '}':
                    brace_count -= 1
                    if in_class and brace_count == 0:
                        end_index = i + 1
                        class_text = content[start_index:end_index]
                        class_list.append((class_name, class_text, package_name, package_path))
                        break
                i += 1

        print(f"Step3: {len(class_list)} クラス検出")

        # --------------------------------
        # 出力処理
        # --------------------------------
        for class_name, class_body, package_name, package_path in class_list:

            # ディレクトリ作成
            output_dir = os.path.join(output_root, package_path)
            os.makedirs(output_dir, exist_ok=True)

            # ヘッダ作成
            header = ""

            if package_name:
                header += f"package {package_name};\n\n"

            if imports:
                header += "\n".join(sorted(set(imports))) + "\n\n"

            final_text = header + class_body

            output_file = os.path.join(output_dir, f"{class_name}.java")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_text)

            print(f"出力: {output_file}")

    @staticmethod
    def read_json_from_s3(bucket_name: str, key: str) -> dict:
        try:
            s3 = boto3.client("s3")

            # S3からオブジェクト取得
            response = s3.get_object(Bucket=bucket_name, Key=key)

            # Bodyはバイナリなのでデコード
            content = response["Body"].read().decode("utf-8")

            ast = json.loads(content)

            # 必須キー確認
            required_keys = ["program_id", "variables", "procedures"]
            for k in required_keys:
                if k not in ast:
                    raise ValueError(f"キー不足: {k}")

            return ast

        except s3.exceptions.NoSuchKey:
            print(f"S3にファイルが存在しません: {key}")
            return {}

        except json.JSONDecodeError:
            print("JSON形式が不正です")
            return {}

        except Exception as e:
            print(f"エラー: {e}")
            return {}

    @staticmethod
    def move_file(bucket_name, source_key, dest_key):
        s3 = boto3.client('s3')
        # コピー元情報
        copy_source = {
            'Bucket': bucket_name,
            'Key': source_key
        }

        # ① コピー
        s3.copy_object(
            Bucket=bucket_name,
            CopySource=copy_source,
            Key=dest_key
        )

        # ② 元ファイル削除
        s3.delete_object(
            Bucket=bucket_name,
            Key=source_key
        )

        print(f"Moved: {source_key} -> {dest_key}")

    @staticmethod
    def get_openai_api_key() -> str:
        # AWS Secrets Managerクライアントの初期化
        client = boto3.client("secretsmanager", region_name="ap-northeast-1")

        # AWS Secrets ManagerからAPI KEYを取得すること。
        response = client.get_secret_value(
            SecretId="cobol2java/openai/api-key"
        )

        #AWS Secrets ManagerからAPI KEYを取得すること。
        secret = json.loads(response["SecretString"])
        #OpenAPIのAPI KEYを返すこと。
        return secret["OPENAI_API_KEY"]
    
    @staticmethod
    def copy_s3_folder(bucket_name, source_prefix, dest_prefix):
        s3 = boto3.client('s3')
        paginator = s3.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket=bucket_name, Prefix=source_prefix):
            if 'Contents' not in page:
                continue

            for obj in page['Contents']:
                source_key = obj['Key']

                # フォルダ（サイズ0のキー）はスキップ（必要に応じて）
                if source_key.endswith('/'):
                    continue

                # コピー先キー生成（構造維持）
                dest_key = source_key.replace(source_prefix, dest_prefix, 1)

                print(f"Copy: {source_key} -> {dest_key}")

                s3.copy_object(
                    Bucket=bucket_name,
                    CopySource={'Bucket': bucket_name, 'Key': source_key},
                    Key=dest_key
                )

    @staticmethod
    def delete_files_keep_folders(bucket_name, prefix):
        s3 = boto3.client('s3')
        if not prefix.endswith('/'):
            prefix += '/'

        paginator = s3.get_paginator('list_objects_v2')

        delete_keys = []

        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' not in page:
                continue

            for obj in page['Contents']:
                key = obj['Key']

                # フォルダキーは削除しない（末尾が /）
                if key.endswith('/'):
                    print(f"Keep folder: {key}")
                    continue

                print(f"Delete file: {key}")
                delete_keys.append({'Key': key})

                # 1000件単位で削除
                if len(delete_keys) == 1000:
                    s3.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': delete_keys}
                    )
                    delete_keys = []

        # 残り削除
        if delete_keys:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_keys}
            )

        print("Delete completed (folders kept)")
    
    @staticmethod
    def get_skill(bucket_name, key):
        # S3からSkillファイルを取得すること。skillは、ASTからJavaコードを生成するための要件定義（.mdや.yamlなど）を想定
        # S3のハンドルを取得すること。
        s3 = boto3.client("s3")
        # S3からオブジェクト取得
        response = s3.get_object(Bucket=bucket_name, Key=key)
        # Bodyはバイナリなのでデコード
        skill_content = response["Body"].read().decode("utf-8")
        # ファイル形式に応じて、適切にパースすること。
        if key.endswith('.yml'):
            skill_content = yaml.safe_load(skill_content)

        #パースした内容を返すこと。
        return skill_content