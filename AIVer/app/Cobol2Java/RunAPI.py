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

        md_file_path = "c:/AIVer/makedown/doc.md"
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
        md_file_path = "c:/AIVer/makedown/doc.md"
        md = generator.load_md(md_file_path)
         #skillは、ASTからJavaコードを生成するための要件定義（.mdや.yamlなど）を想定
        skill = CommonUtil.load_file("c:/AIVer/skills/ast-to-springboot-nsb.md")
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
        generator = ASTToJavaGeneratorWithSkill.ASTToJavaGeneratorWithSkill("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")
        #astファイルを生成すること
        generateAST()
        #astファイル読み込み
        ast_file_path = "c:/AIVer/ast/ast.json"
        ast = generator.load_file(ast_file_path)
        #生成したASTを確認すること
        print(f"ast={ast}")
        skill = generator.load_file("c:/AIVer/skills/ast-to-springboot.yaml")
        print(f"skill={skill}")
        java_code = generator.generate_java(skill, ast)
        print(f"java={java_code}")
        #ASTファイルよりJavaソースを生成する。（各層のクラス内容を１つファイルに出力すること）
        java_file_path = "c:/AIVer/springboot/GeneratedJavaWithSkill.java"
        CommonUtil.write_text_to_file(java_code, java_file_path)

        #上記生成したJavaファイルをクラス単位で分割し、生成すること。
        CommonUtil.split_java_classes(java_file_path, "c:/AIVer/springboot/")

        print("step1")
        with open(java_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print("step2")
        xml_blocks = CommonUtil.extract_xml_blocks(content)
        print("step3")
        if not xml_blocks:
            print("⚠ XMLが見つかりません")
            return
        print("step4")
        CommonUtil.save_xml_files(xml_blocks, "c:/AIVer/springboot/nsj/resources/mapper/")
        print("step5")
        #処理終了
        return f"Java(ASTより)生成正常終了-Skillあり-000"