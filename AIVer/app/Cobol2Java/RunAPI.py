import ast
import shutil

from fastapi import FastAPI
from fastapi import APIRouter
from openai import api_key
from app.Cobol2Java import CobolASTParser
from app.Cobol2Java import CobolDocGenerator
from app.Cobol2Java import LLMEnhancer
from app.Cobol2Java import MdToJavaGenerator
from app.Cobol2Java import ASTToJavaGenerator
from app.Cobol2Java import ASTToJavaGeneratorWithSkill
from app.util.CommonUtil import CommonUtil
from app.util.CommonConst import CommonConst

import json
import boto3
import zipfile
import os   
import pandas as pd
from datetime import datetime
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
        tpl_file_path = "c:/AIVer/template/template.tpl"
        ast_file_path = "c:/AIVer/ast/ast.json"
        template = CommonUtil.read_json_from_file(tpl_file_path)
        ast = CommonUtil.read_json_from_file(ast_file_path)
        #apikeyを取得すること。
        api_key = CommonUtil.get_openai_api_key()
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
        generator = MdToJavaGenerator.MdToJavaGenerator("###")
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
@router.get("/cobol2javaN")
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
        generator = ASTToJavaGenerator.ASTToJavaGenerator("###")
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
def generateJavaFromASTWithSkill(skill_file_name: str, userId: str):
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        s3 = boto3.client('s3')
        bucket_name = CommonConst.BUCKET_NAME
        prefix = f"{userId}/{CommonConst.BUCKET_PREFIX}"   # ← バケット直下のフォルダ
        #apikeyを取得すること。
        apiKey = CommonUtil.get_openai_api_key()
        #ジェネレートクラスのインスタンスを生成すること。
        generator = ASTToJavaGeneratorWithSkill.ASTToJavaGeneratorWithSkill(apiKey)
        #Skillを読み取ること。skillは、ASTからJavaコードを生成するための要件定義（.mdや.yamlなど）を想定
        #skill = generator.load_file("c:/AIVer/skills/ast-to-springboot-nsb.md")
        skill = CommonUtil.get_skill(bucket_name, f"{CommonConst.SKILL_BUCKET_PREFIX}{skill_file_name}")
        #print(f"skill={skill}")
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

            # 'upload/' を除去 
            key = key[12:] # '{userid}/upload/' の文字数分をスライスして削除

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
            s3_key = f"{userId}/download/ast/{key}.json"
            print(f"AST内容をS3にアップロード: {s3_key}")
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=ast_format.encode('utf-8')
            )
            #ASTファイル＆SkillをベースでJavaコードを生成すること。
            java_code = generator.generate_java(skill, ast_format)

            #システム日時取得。
            now = datetime.now()
            formatted = now.strftime("%Y%m%d%H%M%S.%f")[:-3]

            #生成したJavaソースの格納先を設定すること。
            #java_source_path = f"c:/AIVer/springboot/{formatted}"
            java_source_path = f"{CommonConst.JAVA_SOURCE_PATH}{formatted}/"
            #上記生成したJavaファイルをクラス単位で分割し、生成すること。
            CommonUtil.split_java_classes_to_zip(java_code, java_source_path)

            #JavaファイルからXMLブロックを抽出すること。
            xml_blocks = CommonUtil.extract_xml_blocks(java_code)

            #XMLブロックが存在するか確認すること。
            if not xml_blocks:
                print("⚠ XMLが見つかりません")
            else:
                #抽出したXMLブロックをファイルに保存すること。
                CommonUtil.save_xml_files(xml_blocks, f"{java_source_path}/nsj/resources/mapper/")
            
            # ① ローカルファイルをZIP圧縮
            zip_file_folder = CommonConst.ZIP_FILE_FOLDER
            zip_file_path = f"{zip_file_folder}{key}.zip"
            s3_key = f"{userId}/download/java/{key}.zip"

            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(java_source_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, java_source_path)
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
            shutil.rmtree(java_source_path)
            os.remove(zip_file_path)

        #処理完了後に、処理対象ファイルを処理済のフォルダーへ移動すること。(upload -> completed/upload/)
        CommonUtil.copy_s3_folder(bucket_name, 
            f"{userId}/{CommonConst.BUCKET_PREFIX}", 
            f"{userId}/{CommonConst.COMPLETED_BUCKET_PREFIX}{CommonConst.BUCKET_PREFIX}")
        #処理完了後に、処理対象ファイルを処理済のフォルダーへ移動すること。(download -> completed/)
        CommonUtil.copy_s3_folder(bucket_name, 
            f"{userId}/{CommonConst.DOWNLOAD_BUCKET_PREFIX}", 
            f"{userId}/{CommonConst.COMPLETED_BUCKET_PREFIX}{CommonConst.DOWNLOAD_BUCKET_PREFIX}")
        #「upload/」フォルダー配下のファイル（サブフォルダ―も含む）を全て削除すること。
        CommonUtil.delete_files_keep_folders(bucket_name, 
            f"{userId}/{CommonConst.BUCKET_PREFIX}")
        #「download/」フォルダー配下のファイル（サブフォルダ―も含む）を全て削除すること。
        CommonUtil.delete_files_keep_folders(bucket_name, 
            f"{userId}/{CommonConst.DOWNLOAD_BUCKET_PREFIX}")

        #処理終了
        return f"Java(AST+Skillより)生成正常終了-000"

##CobolコードからAST生成し、S3にアップロードすること。
def generateASTWithCobol(userId: str):
    # =========================
    # 実行例
    # =========================
    print("__name__", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        #S3のハンドルを取得
        s3 = boto3.client('s3')
        #バッケト名
        bucket_name = CommonConst.BUCKET_NAME
        #バッケト直下のフォルダー名
        prefix = f"{userId}/{CommonConst.BUCKET_PREFIX}"    # ← バケット直下のフォルダ
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
            # 'upload/' を除去
            key = key[12:] # '{userId}/upload/' の文字数分をスライスして削除
            s3_key = f"{userId}/download/ast/{key}.json"
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=ast_format.encode('utf-8')
            )

def generateTplWithAST(userId: str):
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        #S3のハンドルを取得
        s3 = boto3.client('s3')
        #バッケト名
        bucket_name = CommonConst.BUCKET_NAME
        #バッケト直下のフォルダー名
        prefix = f"{userId}/{CommonConst.AST_BUCKET_PREFIX}"    # ← バケット直下のフォルダ
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

            #ASTファイルを読み取ること。
            ast = CommonUtil.read_json_from_s3(bucket_name, key)
  
            #テンプレート生成ためのジェネレートクラスインスタンスを生成すること。
            generator = CobolDocGenerator.CobolDocGenerator(ast)
            #テンプレート内容を生成すること。
            tpl_content = generator.generate()

            # 'download/ast/' を除去
            key = key[18:-5] # '{userId}/download/ast/' の文字数分をスライスして削除
            #テンプレート内容をS3にアップロードすること。
            s3_key = f"{userId}/download/template/{key}.tpl"
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=tpl_content.encode('utf-8')
            )

        #処理終了ークライアントへの返却値
        return  f"テンプレート正常生成終了"

def generateMdWithTpl(userId):
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        #S3のハンドルを取得
        s3 = boto3.client('s3')
        #バッケト名
        bucket_name = CommonConst.BUCKET_NAME
        #バッケト直下のフォルダー名
        prefix = f"{userId}/{CommonConst.TPL_BUCKET_PREFIX}"    # ← バケット直下のフォルダ
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

            #テンプレートファイルを読み取ること。
            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            tpl_content = file_obj['Body'].read().decode('utf-8')

            #ASTファイルを読み取ること。
            print(f"key={key}")
            print(f"ASTファイルを読み取ること。key={userId}/download/ast/{key[23:-4]}.json")
            ast_content = CommonUtil.read_json_from_s3(bucket_name, f"{userId}/download/ast/{key[23:-4]}.json") 

            #apikeyを取得すること。
            apiKey = CommonUtil.get_openai_api_key()
            #生成したテンプレート内容とAST内容をベースにマークダウンファイルを生成するためのAI自動生成クラスのインスタンスを生成すること。
            enhancer = LLMEnhancer.LLMEnhancer(apiKey)
            #生成したテンプレート内容とAST内容をベースにマークダウンファイルを生成すること。
            md_content = enhancer.enhanceMd(tpl_content, ast_content)
  
            #マークダウン内容をS3にアップロードすること。
            s3_key = f"{userId}/download/markdown/{key[23:-4]}.md"
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=md_content.encode('utf-8')
            )

        #処理終了ークライアントへの返却値
        return  f"マークダウンファイルを正常生成終了"

def generateJavaWithMd(skill_file_name: str, userId: str):
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        #S3のハンドルを取得
        s3 = boto3.client('s3')
        #バッケト名
        bucket_name = CommonConst.BUCKET_NAME
        #バッケト直下のフォルダー名
        prefix = f"{userId}/{CommonConst.MD_BUCKET_PREFIX}"    # ← バケット直下のフォルダ
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

            print(f"MD読み込み中: {key}")

            #マークダウンファイルを読み取ること。
            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            md_content = file_obj['Body'].read().decode('utf-8')
            
            #skillは、マークダウンファイルからJavaコードを生成するための要件定義（.mdや.yamlなど）を想定
            #skill = CommonUtil.load_file("c:/AIVer/skills/ast-to-springboot-nsb.md")
            skill = CommonUtil.get_skill(bucket_name, f"{CommonConst.SKILL_BUCKET_PREFIX}{skill_file_name}")

            #apikeyを取得すること。
            apiKey = CommonUtil.get_openai_api_key()
            #生成したマークダウン内容をベースにJavaコードを生成するためのAI自動生成クラスのインスタンスを生成すること。
            generator = MdToJavaGenerator.MdToJavaGenerator(apiKey)
            #生成したマークダウン内容をベースにJavaコードを生成すること。
            java_code = generator.generate_java(skill, md_content)
            
            #システム日時取得。
            now = datetime.now()
            formatted = now.strftime("%Y%m%d%H%M%S.%f")[:-3]

            #生成したJavaソースの格納先を設定すること。
            #java_source_path = f"./../zip/springboot/{formatted}/"
            java_source_path = f"{CommonConst.JAVA_SOURCE_PATH}{formatted}/"
            #ファイル分割
            file_list = CommonUtil.split_java_classes_to_zip(java_code, java_source_path)

            #JavaファイルからXMLブロックを抽出すること。
            xml_blocks = CommonUtil.extract_xml_blocks(java_code)

            #XMLブロックが存在するか確認すること。
            if not xml_blocks:
                print("⚠ XMLが見つかりません")
            else:
                #抽出したXMLブロックをファイルに保存すること。
                CommonUtil.save_xml_files(xml_blocks, f"{CommonConst.JAVA_SOURCE_PATH}nsj/resources/mapper/")
            
            # 'download/markdown/' を除去
            key = key[23:-3] # '{userId}/download/markdown/' の文字数分をスライスして削除

            # ① ローカルファイルをZIP圧縮
            #local_file_path = "c:/AIVer/springboot/"   
            #zip_file_folder = f"c:/AIVer/zip/"
            zip_file_folder = CommonConst.ZIP_FILE_FOLDER
            zip_file_path = f"{zip_file_folder}{key}.zip"
            s3_key = f"{userId}/download/java/{key}.zip"
            print(f"JavaコードをZIP圧縮: {zip_file_path}")
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(java_source_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, java_source_path)
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
            folder_path = java_source_path
            shutil.rmtree(folder_path)
            os.remove(zip_file_path)
            
        print("圧縮ファイルのアップロードまでは完了しました")
        #処理完了後に、処理対象ファイルを処理済のフォルダーへ移動すること。(upload -> completed/upload/)
        CommonUtil.copy_s3_folder(bucket_name, 
            f"{userId}/{CommonConst.BUCKET_PREFIX}", 
            f"{userId}/{CommonConst.COMPLETED_BUCKET_PREFIX}{CommonConst.BUCKET_PREFIX}")  
        #処理完了後に、処理対象ファイルを処理済のフォルダーへ移動すること。(download -> completed/)
        CommonUtil.copy_s3_folder(bucket_name, 
            f"{userId}/{CommonConst.DOWNLOAD_BUCKET_PREFIX}", 
            f"{userId}/{CommonConst.COMPLETED_BUCKET_PREFIX}{CommonConst.DOWNLOAD_BUCKET_PREFIX}")
        #「upload/」フォルダー配下のファイル（サブフォルダ―も含む）を全て削除すること。
        CommonUtil.delete_files_keep_folders(bucket_name, 
            f"{userId}/{CommonConst.BUCKET_PREFIX}")
        #「download/」フォルダー配下のファイル（サブフォルダ―も含む）を全て削除すること。
        CommonUtil.delete_files_keep_folders(bucket_name, 
            f"{userId}/{CommonConst.DOWNLOAD_BUCKET_PREFIX}")

        #処理終了ークライアントへの返却値
        return  f"Javaファイルを正常生成終了"

#自動生成ルールマップ：cobol->ast->java
#skill(yml)を使用して、ASTからJavaコードを生成するAPI
@router.get("/Cobol2Java")
def generateJavaFromAST(skill_file_name: str, userId: str):
    # =========================
    # 使用例
    # =========================
    print(f"__name__ is", __name__)
    if __name__ == "app.Cobol2Java.RunAPI":
        #ASTファイルを生成すること。
        generateASTWithCobol(userId)
 
        #ASTファイルよりテンプレート内容を生成すること。
        generateTplWithAST(userId)

        #生成したテンプレート内容&AST内容をベースにマークダウンファイルを生成すること。
        generateMdWithTpl(userId)

        #生成したマークダウン内容をベースにJavaコードを生成すること。
        generateJavaWithMd(skill_file_name, userId)

        #処理終了
        return f"生成正常終了-000"