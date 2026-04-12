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

    #ASTファイルのプレフィックス
    AST_BUCKET_PREFIX = 'download/ast/'  # ← バケット直下のフォルダ

    #テンプレートファイルのプレフィックス
    TPL_BUCKET_PREFIX = 'download/template/'  # ← バケット直下のフォルダ

    #マークダウンファイルのプレフィックス
    MD_BUCKET_PREFIX = 'download/markdown/'  # ← バケット直下のフォルダ

    #API KEY
    API_KEY = "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"