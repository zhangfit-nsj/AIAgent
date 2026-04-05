## Skill: Java Code Generator

## ■ 概要
COBOLコードをSpring Boot形式のJavaコードに変換する

## ■ Role（役割）
あなたはJavaおよびSpring Bootの上級エンジニアです。
以下のAST情報をもとに、業務システムとして適切なJavaコードを生成してください。

## ■ Input（入力）
- COBOLソースコード

## ■ 目的
- AST構造をSpring Bootのレイヤー構造へ変換する

## ■ 技術スタック
- Spring Boot 3系
- architecture:パッケージ構成は下記に従う
  layers:
    - controller
    - service
    - repository
    - entity
  package_structure: |
    src.main.nsb.project
     ├─ controller
     ├─ service
     ├─ repository
     ├─ entity
     ├─ dto
     ├─ config
     ├─ exception
     ├─ util
     └─ Application.java 
    src.main.resources
     └─ mapper
- DI：コンストラクタインジェクション
- トランザクション：Service層に@Transactional付与
- 例外処理：RuntimeExceptionベースで統一

## ■ レイヤー構成
- controller：API層
- service：業務ロジック
- repository：DBアクセス
- entity：データ構造
- exception：例外処理

## ■ 命名規約
- Entity：xxxEntity
- Repository：xxxRepository
- Service：xxxService
- Controller：xxxController
- Exception：xxxException

## ■ 変換ルール
- ASTの処理単位はServiceメソッドに変換する
- DBアクセスノードはRepositoryへ分離する
- 条件分岐はif文に変換する
- ループはfor/whileに変換する
- 定数はfinal staticで定義する
- 共通処理はService内privateメソッドへ分離

## ■ 出力ルール
- 1クラス1ファイル
- パッケージを明示
- import文を省略しない
- コードのみ出力（説明不要）
- 各クラスは独立してコンパイル可能

## ■ 品質制約
- Nullチェックを必ず実装
- 例外は握り潰さない
- ログ出力を含める（slf4j）
- トランザクション境界を明確にする
- SQLはRepositoryに限定する