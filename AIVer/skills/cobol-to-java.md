---
name: cobol-to-java-migration
description: COBOLソースコードをSpring Boot（Java）へ自動変換するスキル。コントローラー・サービス・リポジトリ・エンティティ・DTO・例外クラス等を指定パッケージ構成に従って生成する。「COBOLをJavaに変換」「マイグレーション」「Spring Boot生成」などのトリガーで使用。
---

# COBOL → Java（Spring Boot）自動生成スキル

## 概要

このスキルは、COBOLのプログラム・コピーブック・JCLを解析し、Spring Bootアーキテクチャに従ったJavaソースコードを自動生成します。

---

## パッケージ構成

生成するすべてのソースコードは、以下のパッケージ構成に従うこと。

```
src/main/java/nsb/project/
├─ controller/       # REST APIエンドポイント（@RestController）
├─ service/          # ビジネスロジック（@Service, @Transactional）
├─ repository/       # データアクセス（MyBatisMapper または JPA Repository）
├─ entity/           # DB対応エンティティクラス
├─ dto/              # リクエスト・レスポンスのデータ転送オブジェクト
├─ config/           # 設定クラス（@Configuration）
├─ exception/        # カスタム例外クラス（RuntimeExceptionベース）
├─ util/             # 共通ユーティリティクラス
└─ Application.java  # Spring Bootエントリーポイント

src/main/resources/
└─ mapper/           # MyBatis XMLマッパーファイル（*Mapper.xml）
```

---

## 設計規約（必ず遵守すること）

### 1. DIはコンストラクタインジェクションで統一

```java
// NG: フィールドインジェクション
@Autowired
private UserService userService;

// OK: コンストラクタインジェクション
private final UserService userService;

public UserController(UserService userService) {
    this.userService = userService;
}
```

Lombokを使用する場合は `@RequiredArgsConstructor` + `private final` フィールドで代替可。

### 2. トランザクションはService層に付与

```java
@Service
@Transactional
public class UserService {
    // クラスレベルに @Transactional を付与（デフォルト：読み書き両用）
    // 参照系メソッドのみ @Transactional(readOnly = true) で個別上書き可
}
```

### 3. 例外処理はRuntimeExceptionベースで統一

```java
// exception/ パッケージ配下に以下を生成する
public class BusinessException extends RuntimeException {
    private final String errorCode;
    public BusinessException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }
    public String getErrorCode() { return errorCode; }
}

public class SystemException extends RuntimeException {
    public SystemException(String message, Throwable cause) {
        super(message, cause);
    }
}

// @RestControllerAdvice でグローバルハンドリング
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException ex) { ... }

    @ExceptionHandler(SystemException.class)
    public ResponseEntity<ErrorResponse> handleSystemException(SystemException ex) { ... }
}
```

---

## COBOLからJavaへの変換マッピング

| COBOLの要素 | Javaの対応要素 | 配置パッケージ |
|---|---|---|
| PROGRAM-ID | クラス名のベース | service/ or controller/ |
| COPY句（コピーブック） | Entity / DTO | entity/ or dto/ |
| WORKING-STORAGE SECTION | フィールド変数またはDTO | dto/ |
| PROCEDURE DIVISION | メソッド実装 | service/ |
| EXEC SQL | MyBatisマッパー or JPAクエリ | repository/ + mapper/ |
| PERFORM 段落 | privateメソッド分割 | service/ |
| EVALUATE / WHEN | switch / if-else | service/ |
| COMPUTE / MOVE | 算術処理・代入 | service/ or util/ |
| DISPLAY / WRITE | ログ出力（SLF4J） | service/ |
| ABEND / STOP RUN | BusinessException / SystemException | exception/ |
| JCL STEP | バッチ処理（Spring Batch） | config/ or service/ |

---

## 生成手順（エージェントへの指示）

ユーザーからCOBOLソースが提示された場合、以下の順序でJavaソースを生成すること。

### ステップ1：COBOL解析レポートの出力

提示されたCOBOLソースを解析し、以下を日本語で箇条書きにする。

- プログラムの目的・処理概要
- 入出力データ（COPY句・WORKING-STORAGE）
- 主要処理フロー（PROCEDURE DIVISION）
- SQL処理の有無と内容
- 分岐・ループ・エラー処理の概要

### ステップ2：生成ファイル一覧の提示

生成するクラス・ファイルの一覧をパッケージとともに提示し、ユーザーの確認を得る。

例：
```
生成予定ファイル：
  nsb.project.controller.UserController
  nsb.project.service.UserService
  nsb.project.repository.UserMapper（MyBatis）
  nsb.project.entity.User
  nsb.project.dto.UserRequest
  nsb.project.dto.UserResponse
  nsb.project.exception.BusinessException
  nsb.project.exception.GlobalExceptionHandler
  src/main/resources/mapper/UserMapper.xml
```

### ステップ3：各クラスの生成

以下の順序でコードを生成する。

1. **Entity**（COBOLのコピーブック・DB項目から生成）
2. **DTO**（Request / Response）
3. **Repository**（MyBatis Mapperインターフェース or JPA Repository）
4. **MyBatis XMLマッパー**（EXEC SQLから変換）
5. **Service**（PROCEDURE DIVISIONのビジネスロジック）
6. **Controller**（HTTPエンドポイントの定義）
7. **Exception**（BusinessException / SystemException / GlobalExceptionHandler）
8. **Config**（必要な場合のみ）

---

## 生成コードのテンプレート

### Controller テンプレート

```java
package nsb.project.controller;

import nsb.project.dto.XxxRequest;
import nsb.project.dto.XxxResponse;
import nsb.project.service.XxxService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/xxx")
@RequiredArgsConstructor
public class XxxController {

    private final XxxService xxxService;

    @PostMapping
    public ResponseEntity<XxxResponse> create(@RequestBody XxxRequest request) {
        return ResponseEntity.ok(xxxService.create(request));
    }
}
```

### Service テンプレート

```java
package nsb.project.service;

import nsb.project.dto.XxxRequest;
import nsb.project.dto.XxxResponse;
import nsb.project.entity.Xxx;
import nsb.project.exception.BusinessException;
import nsb.project.repository.XxxMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class XxxService {

    private final XxxMapper xxxMapper;

    public XxxResponse create(XxxRequest request) {
        // バリデーション
        if (request.getId() == null) {
            throw new BusinessException("E001", "IDが指定されていません");
        }
        // ビジネスロジック（COBOLのPROCEDURE DIVISIONから変換）
        Xxx entity = toEntity(request);
        xxxMapper.insert(entity);
        return toResponse(entity);
    }

    @Transactional(readOnly = true)
    public XxxResponse findById(Long id) {
        return xxxMapper.findById(id)
            .map(this::toResponse)
            .orElseThrow(() -> new BusinessException("E002", "データが見つかりません: " + id));
    }

    private Xxx toEntity(XxxRequest request) { ... }
    private XxxResponse toResponse(Xxx entity) { ... }
}
```

### Repository（MyBatis）テンプレート

```java
package nsb.project.repository;

import nsb.project.entity.Xxx;
import org.apache.ibatis.annotations.Mapper;
import java.util.Optional;

@Mapper
public interface XxxMapper {
    Optional<Xxx> findById(Long id);
    int insert(Xxx entity);
    int update(Xxx entity);
    int deleteById(Long id);
}
```

### MyBatis XML テンプレート（src/main/resources/mapper/XxxMapper.xml）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="nsb.project.repository.XxxMapper">

    <resultMap id="xxxResultMap" type="nsb.project.entity.Xxx">
        <id property="id" column="ID"/>
        <result property="name" column="NAME"/>
    </resultMap>

    <select id="findById" resultMap="xxxResultMap">
        SELECT ID, NAME FROM XXX_TABLE WHERE ID = #{id}
    </select>

    <insert id="insert" parameterType="nsb.project.entity.Xxx">
        INSERT INTO XXX_TABLE (ID, NAME) VALUES (#{id}, #{name})
    </insert>

</mapper>
```

### Entity テンプレート

```java
package nsb.project.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class Xxx {
    private Long id;
    private String name;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

### DTO テンプレート

```java
package nsb.project.dto;

import lombok.Data;

// リクエストDTO
@Data
public class XxxRequest {
    private Long id;
    private String name;
}

// レスポンスDTO
@Data
public class XxxResponse {
    private Long id;
    private String name;
    private String message;
}
```

---

## バッチ処理（JCL対応）

JCLのSTEPをSpring Batchに変換する場合は以下の方針に従う。

- `JOB` → `@SpringBootApplication` + `BatchConfig`（config/）
- `STEP` → `Step` Bean（config/BatchConfig.java）
- `PGM=xxxxx` → `Tasklet` or `ItemReader/ItemProcessor/ItemWriter`（service/ 配下）
- `DD` → `FlatFileItemReader` or `FlatFileItemWriter`（リソースパス指定）

---

## 出力形式のルール

1. 各クラスは **ファイルパスを明示** した上でコードブロック（```java）で出力する
2. 変換の理由・注意点があれば **コード直前に日本語で補足** する
3. COBOLの段落名・変数名を **コメントで残す**（追跡可能にする）
4. 未変換・要確認箇所は `// TODO: [COBOL] 元の処理: <段落名>` 形式でマーク
5. 生成完了後、**動作確認チェックリスト**（単体テスト観点）を出力する

---

## 使用例

```
ユーザー：
以下のCOBOLプログラムをJavaに変換してください。
[COBOLソースを貼り付け]

エージェント：
1. COBOL解析レポートを出力
2. 生成ファイル一覧を提示
3. 各クラスをパッケージ構成に従って順番に生成
4. 動作確認チェックリストを出力
```
