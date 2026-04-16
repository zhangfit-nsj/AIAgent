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

    # S3バケット名
    BUCKET_NAME = 'cobol-to-java-migration'

    # S3のプレフィックス(Cobolソール)
    BUCKET_PREFIX = 'upload/'  # ← バケット直下のフォルダ
    
    #downloadフォルダーのプレフィックス
    DOWNLOAD_BUCKET_PREFIX = 'download/'  # ← バケット直下のフォルダ

    #ASTファイルのプレフィックス
    AST_BUCKET_PREFIX = 'download/ast/'  # ← バケット直下のフォルダ

    #テンプレートファイルのプレフィックス
    TPL_BUCKET_PREFIX = 'download/template/'  # ← バケット直下のフォルダ

    #マークダウンファイルのプレフィックス
    MD_BUCKET_PREFIX = 'download/markdown/'  # ← バケット直下のフォルダ

    #処理済のCobolファイル格納為のプレフィックス
    COMPLETED_BUCKET_PREFIX = 'completed/'  # ← バケット直下のフォルダ

    #skillファイルのプレフィックス
    SKILL_BUCKET_PREFIX = 'skills/'  # ← バケット直下のフォルダ
    
    #生成したJavaコード(圧縮ファイル)の格納先
    ZIP_FILE_FOLDER = "c:/AIVer/zip/"

    #生成したJavaコードの格納先
    JAVA_SOURCE_PATH = "c:/AIVer/springboot/"