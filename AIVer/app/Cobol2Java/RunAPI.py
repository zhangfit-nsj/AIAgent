import ast
import shutil

from fastapi import FastAPI
from fastapi import APIRouter
from app.Cobol2Java import CobolASTParser
from app.Cobol2Java import CobolDocGenerator
from app.Cobol2Java import LLMEnhancer
from app.Cobol2Java import MdToJavaGenerator
from app.Cobol2Java import ASTToJavaGenerator
from app.Cobol2Java import ASTToJavaGeneratorWithSkill
from app.util.CommonUtil import CommonUtil

import json
import boto3
import zipfile
import os   
import pandas as pd
router = APIRouter()

@router.get("/cobol2ast")
def generateAST():
    # =========================
    # 実行例
    # =========================
    print("__name__", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        file_path = "c:/AIVer/cobol/sample_large.cob"
        with open(file_path, "r", encoding="utf-8") as f:
            cobol_code = f.read()

        parser = CobolASTParser.CobolASTParser(cobol_code)
        ast = parser.parse()

        #ASTファイル出力
        ast_file_path = "c:/AIVer/ast/ast.json"
        CommonUtil.write_json_to_file(ast, ast_file_path)
        #print(json.dumps(ast, indent=2, ensure_ascii=False))
        return f"処理正常終了"

@router.get("/ast2tpl")
def generateTpl():
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        #入力：ASTファイル
        ast_file_path = "c:/AIVer/ast/ast.json"
        ast = CommonUtil.read_json_from_file(ast_file_path)

        #出力：ドキュメント
        tpl_file_path = "c:/AIVer/template/template.tpl"
        generator = CobolDocGenerator.CobolDocGenerator(ast)
        doc = generator.generate()

        print(doc)
        CommonUtil.write_text_to_file(doc, tpl_file_path)

        #処理終了ークライアントへの返却値
        return  f"テンプレート正常生成終了"

@router.get("/tpl2md")
def generateMd():
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        # ② LLM補完
        api_key="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"
        tpl_file_path = "c:/AIVer/template/template.tpl"
        ast_file_path = "c:/AIVer/ast/ast.json"
        template = CommonUtil.read_json_from_file(tpl_file_path)
        ast = CommonUtil.read_json_from_file(ast_file_path)

        enhancer = LLMEnhancer.LLMEnhancer(api_key)

        md_file_path = "c:/AIVer/markdown/doc.md"
        result = enhancer.enhanceMd(template, ast)
        CommonUtil.write_text_to_file(result, md_file_path)
        return f"LLM補完完了（MDファイ生成）"

#MDファイルよりJavaソースを生成する。（各層のクラス内容を１つファイルに出力すること）
@router.get("/md2java")
def generateJava():
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        generator = MdToJavaGenerator.MdToJavaGenerator("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")
        md_file_path = "c:/AIVer/markdown/doc.md"
        md = generator.load_md(md_file_path)
         #skillは、ASTからJavaコードを生成するための要件定義（.mdや.yamlなど）を想定
        skill = CommonUtil.load_file("c:/AIVer/skills/ast-to-springboot-nsb.md")
        print(f"マークダウンファイル＝c:/AIVer/skills/ast-to-springboot-nsb.md")
        print(f"マークダウン内容＝{skill}")
        java_code = generator.generate_java(skill,md)

        #MDファイルよりJavaソースを生成する。（各層のクラス内容を１つファイルに出力すること）
        java_file_path = "c:/AIVer/springboot/GeneratedJava.java"
        CommonUtil.write_text_to_file(java_code, java_file_path)

        #上記生成したJavaファイルをクラス単位で分割し、生成すること。
        #Javaファイル読み取り
        with open(java_file_path, "r", encoding="utf-8") as f:
            text = f.read()
        #ファイル分割
        file_list = CommonUtil.split_java_files(text)
        #ファイル存在チェック
        if not file_list:
            return (f"Javaコードが見つかりませんでした")
        #分割した各層のJavaクラスを保存すること。
        CommonUtil.save_files("c:/AIVer/springboot/", file_list)

        return f"Java生成正常終了-000"

#自動生成ルールマップ：cobol->ast->template->md->java
@router.get("/cobol2java")
def generateJavaFromCobol():
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        #① CobolコードからAST生成
        generateAST()
        #② LLM補完（テンプレート生成）
        generateTpl()
        #③ LLM補完（MDファイル生成）
        generateMd()
        #④ MDファイルからJavaコード生成
        generateJava()

        return f"Java(Cobolより)生成正常終了-000"

#自動生成ルールマップ：cobol->ast->java
#skill(.mk)を使用して、ASTからJavaコードを生成するAPI
@router.get("/ast2java")
def generateJavaFromAST():
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        generator = ASTToJavaGenerator.ASTToJavaGenerator("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")
        #astファイルを生成すること
        generateAST()
        #astファイル読み込み
        ast_file_path = "c:/AIVer/ast/ast.json"
        ast = generator.load_ast(ast_file_path)
        print(f"ast={ast}")
        #skill読取
        skill = generator.load_file("c:/AIVer/skills/ast-to-springboot.md")
        print(f"skill={skill}")
        java_code = generator.generate_java(skill, ast)
        print(f"java={java_code}")
        #ASTファイルよりJavaソースを生成する。（各層のクラス内容を１つファイルに出力すること）
        java_file_path = "c:/AIVer/springboot/GeneratedJavaNew.java"
        CommonUtil.write_text_to_file(java_code, java_file_path)

        #上記生成したJavaファイルをクラス単位で分割し、生成すること。
        CommonUtil.split_java_classes(java_file_path, "c:/AIVer/springboot/")

        #処理終了
        return f"Java(ASTより)生成正常終了-000"

#自動生成ルールマップ：cobol->ast->java
#skill(yml)を使用して、ASTからJavaコードを生成するAPI
@router.get("/ast2javaWithSkill")
def generateJavaFromASTWithSkill():
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        s3 = boto3.client('s3')
        bucket_name = 'cobol-to-java-migration'
        prefix = 'upload/'  # ← バケット直下のフォルダ
        generator = ASTToJavaGeneratorWithSkill.ASTToJavaGeneratorWithSkill("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")
        skill = generator.load_file("c:/AIVer/skills/ast-to-springboot.yaml")
        # ファイル一覧取得
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )
        # ファイル読み込み
        for obj in response.get('Contents', []):
            key = obj['Key']
            
            # フォルダ自身はスキップ
            if key.endswith('/'):
                continue

            print(f"読み込み中: {key}")

            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            content = file_obj['Body'].read().decode('utf-8')
            #content = pd.read_csv(file_obj['Body'])

            # 'upload/' を除去
            key = key[7:] # 'upload/' の文字数分をスライスして削除

            #print(content)
            #CobolコードからAST生成
            parser = CobolASTParser.CobolASTParser(content)
            ast = parser.parse()

            # AST内容を整形して表示すること。
            ast_format = json.dumps(
                ast,
                ensure_ascii=False,
                indent=2   # ★ ここを追加（インデント）
            )

            #AST内容をS3にアップロードすること。
            s3_key = f"download/ast/{key}.json"
            print(f"AST内容をS3にアップロード: {s3_key}")
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=ast_format.encode('utf-8')
            )
            #ASTファイル＆SkillをベースでJavaコードを生成すること。
            java_code = generator.generate_java(skill, ast_format)

            #JavaコードをS3にアップロードすること。
            s3_key = f"download/java/{key}.java"
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=java_code.encode('utf-8'),
                ContentType='text/x-java-source'  # または 'text/plain'
            )
            #java_file_path = "c:/AIVer/springboot/GeneratedJavaWithSkill.java"

            #生成したJavaコードをローカルファイルに保存すること。
            #CommonUtil.write_text_to_file(java_code, java_file_path)

            #上記生成したJavaファイルをクラス単位で分割し、生成すること。
            CommonUtil.split_java_classes_to_zip(java_code, "c:/AIVer/springboot/")

            #分割したJavaファイルをクラス単位で保存すること。
            #with open(java_file_path, "r", encoding="utf-8") as f:
            #    content = f.read()

            #JavaファイルからXMLブロックを抽出すること。
            xml_blocks = CommonUtil.extract_xml_blocks(java_code)

            #XMLブロックが存在するか確認すること。
            if not xml_blocks:
                print("⚠ XMLが見つかりません")
                return
            
            #抽出したXMLブロックをファイルに保存すること。
            CommonUtil.save_xml_files(xml_blocks, "c:/AIVer/springboot/nsj/resources/mapper/")

            # ① ローカルファイルをZIP圧縮
            local_file_path = "c:/AIVer/springboot/"   
            zip_file_folder = f"c:/AIVer/zip/"
            zip_file_path = f"{zip_file_folder}{key}.zip"
            s3_key = f"download/java/{key}.zip"
            #with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            #    zipf.write(local_file_path, arcname=os.path.basename(local_file_path))
            # ② S3へアップロード
            #with open(zip_file_path, "rb") as f:
            #    s3.put_object(
            #        Bucket=bucket_name,
            #        Key=s3_key,
            #        Body=f,
            #        ContentType='application/zip'
            #    )
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(local_file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, local_file_path)
                        zipf.write(full_path, arcname)

            # ② S3へアップロード
            with open(zip_file_path, "rb") as f:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=f,
                    ContentType='application/zip'
                )

            #生成したソース＆ZIPファイルを削除すること。
            folder_path = local_file_path + "nsj"
            shutil.rmtree(folder_path)
            os.remove(zip_file_path)

        if 1==1 :
            #処理終了
            return f"Java(ASTより)生成正常終了-Skillあり-000"
        
        generator = ASTToJavaGeneratorWithSkill.ASTToJavaGeneratorWithSkill("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")
        #astファイルを生成すること
        #generateAST()
        #astファイル読み込み
        #ast_file_path = "c:/AIVer/ast/ast.json"
        #ast = generator.load_file(ast_file_path)

        #生成したASTを確認すること
        #print(f"ast={ast}")
        skill = generator.load_file("c:/AIVer/skills/ast-to-springboot.yaml")
        #skill = generator.load_file("c:/AIVer/skills/ast-to-springboot-nsb.md")
        #print(f"skill(ast2javaWithSkill)={skill}")
        java_code = generator.generate_java(skill, ast)
        #print(f"java={java_code}")
        #ASTファイルよりJavaソースを生成する。（各層のクラス内容を１つファイルに出力すること）
        java_file_path = "c:/AIVer/springboot/GeneratedJavaWithSkill.java"
        CommonUtil.write_text_to_file(java_code, java_file_path)

        #上記生成したJavaファイルをクラス単位で分割し、生成すること。
        CommonUtil.split_java_classes(java_file_path, "c:/AIVer/springboot/")

        #print("step1")
        with open(java_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        #print("step2")
        xml_blocks = CommonUtil.extract_xml_blocks(content)
        #print("step3")
        if not xml_blocks:
            print("⚠ XMLが見つかりません")
            return
        #print("step4")
        CommonUtil.save_xml_files(xml_blocks, "c:/AIVer/springboot/nsj/resources/mapper/")
        #print("step5")
        #処理終了
        return f"Java(ASTより)生成正常終了-Skillあり-000"