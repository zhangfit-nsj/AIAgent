       IDENTIFICATION DIVISION.
       PROGRAM-ID. SALESBATCH.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT INFILE ASSIGN TO 'INPUT.DAT'
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT OUTFILE ASSIGN TO 'OUTPUT.DAT'
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.

       FILE SECTION.

       FD  INFILE.
       01  IN-REC.
           05 IN-ID        PIC 9(5).
           05 IN-AMOUNT    PIC 9(7).
           05 IN-TYPE      PIC X.

       FD  OUTFILE.
       01  OUT-REC         PIC X(50).

       WORKING-STORAGE SECTION.

       EXEC SQL BEGIN DECLARE SECTION END-EXEC.
       01 DB-ID            PIC 9(5).
       01 DB-NAME          PIC X(20).
       01 DB-STATUS        PIC X(10).
       EXEC SQL END DECLARE SECTION END-EXEC.

       01 WS-EOF           PIC X VALUE 'N'.
       01 WS-TOTAL         PIC 9(9) VALUE 0.
       01 WS-COUNT         PIC 9(5) VALUE 0.

       PROCEDURE DIVISION.

       MAIN-PROC.
           PERFORM INIT-PROC
           PERFORM UNTIL WS-EOF = 'Y'
               PERFORM READ-PROC
               IF WS-EOF = 'N'
                   PERFORM PROCESS-PROC
               END-IF
           END-PERFORM
           PERFORM END-PROC
           STOP RUN.

       INIT-PROC.
           OPEN INPUT INFILE
                OUTPUT OUTFILE.

       READ-PROC.
           READ INFILE
               AT END
                   MOVE 'Y' TO WS-EOF
               NOT AT END
                   ADD 1 TO WS-COUNT
           END-READ.

       PROCESS-PROC.

           *> 合計計算
           ADD IN-AMOUNT TO WS-TOTAL

           *> 条件分岐（IF）
           IF IN-AMOUNT > 100000
               MOVE 'HIGH' TO DB-STATUS
           ELSE
               MOVE 'NORMAL' TO DB-STATUS
           END-IF

           *> 種別分岐（EVALUATE）
           EVALUATE IN-TYPE
               WHEN 'A'
                   PERFORM TYPE-A-PROC
               WHEN 'B'
                   PERFORM TYPE-B-PROC
               WHEN OTHER
                   PERFORM TYPE-OTHER-PROC
           END-EVALUATE

           *> DBアクセス（SELECT）
           MOVE IN-ID TO DB-ID

           EXEC SQL
               SELECT NAME
                 INTO :DB-NAME
                 FROM CUSTOMER
                WHERE ID = :DB-ID
           END-EXEC

           *> 出力編集
           STRING
               IN-ID DELIMITED BY SIZE
               SPACE
               DB-NAME DELIMITED BY SIZE
               SPACE
               DB-STATUS DELIMITED BY SIZE
               INTO OUT-REC
           END-STRING

           WRITE OUT-REC.

       TYPE-A-PROC.
           ADD 100 TO WS-TOTAL.

       TYPE-B-PROC.
           ADD 200 TO WS-TOTAL.

       TYPE-OTHER-PROC.
           CONTINUE.

       END-PROC.
           CLOSE INFILE OUTFILE

           DISPLAY "TOTAL:" WS-TOTAL
           DISPLAY "COUNT:" WS-COUNT.
       *> ===============================
       *> エラーハンドリング処理
       *> ===============================
       ERROR-HANDLING.

           IF SQLCODE NOT = 0
               DISPLAY "SQL ERROR CODE:" SQLCODE
               PERFORM LOG-ERROR
               PERFORM ROLLBACK-PROC
           END-IF.

       LOG-ERROR.
           DISPLAY "ERROR OCCURRED FOR ID:" DB-ID.

       ROLLBACK-PROC.
           EXEC SQL
               ROLLBACK
           END-EXEC.

       COMMIT-PROC.
           EXEC SQL
               COMMIT
           END-EXEC.

       *> ===============================
       *> 更新処理（DB UPDATE）
       *> ===============================
       UPDATE-PROC.

           EXEC SQL
               UPDATE CUSTOMER
                  SET STATUS = :DB-STATUS
                WHERE ID = :DB-ID
           END-EXEC

           PERFORM ERROR-HANDLING.

       *> ===============================
       *> 登録処理（INSERT）
       *> ===============================
       INSERT-PROC.

           EXEC SQL
               INSERT INTO LOG_TABLE
               (ID, STATUS, CREATED_AT)
               VALUES
               (:DB-ID, :DB-STATUS, CURRENT TIMESTAMP)
           END-EXEC

           PERFORM ERROR-HANDLING.

       *> ===============================
       *> 削除処理（DELETE）
       *> ===============================
       DELETE-PROC.

           EXEC SQL
               DELETE FROM TEMP_TABLE
                WHERE ID = :DB-ID
           END-EXEC

           PERFORM ERROR-HANDLING.

       *> ===============================
       *> 業務ロジック（複雑版）
       *> ===============================
       BUSINESS-LOGIC-PROC.

           *> 金額ランク分け
           IF IN-AMOUNT >= 500000
               MOVE 'VIP' TO DB-STATUS
           ELSE IF IN-AMOUNT >= 100000
               MOVE 'GOLD' TO DB-STATUS
           ELSE IF IN-AMOUNT >= 50000
               MOVE 'SILVER' TO DB-STATUS
           ELSE
               MOVE 'BRONZE' TO DB-STATUS
           END-IF

           *> 種別＋金額複合条件
           EVALUATE TRUE
               WHEN IN-TYPE = 'A' AND IN-AMOUNT > 100000
                   ADD 1000 TO WS-TOTAL
               WHEN IN-TYPE = 'B' AND IN-AMOUNT > 50000
                   ADD 500 TO WS-TOTAL
               WHEN OTHER
                   ADD 100 TO WS-TOTAL
           END-EVALUATE.

       *> ===============================
       *> 大量ダミーループ処理（負荷テスト用）
       *> ===============================
       STRESS-TEST-PROC.

           PERFORM VARYING WS-COUNTER FROM 1 BY 1 UNTIL WS-COUNTER > 100
               PERFORM INNER-LOOP
           END-PERFORM.

       INNER-LOOP.
           COMPUTE WS-TOTAL = WS-TOTAL + WS-COUNTER.

       *> ===============================
       *> 出力詳細化処理
       *> ===============================
       FORMAT-OUTPUT.

           MOVE SPACES TO OUT-REC

           STRING
               "ID:" DELIMITED BY SIZE
               IN-ID DELIMITED BY SIZE
               " NAME:" DELIMITED BY SIZE
               DB-NAME DELIMITED BY SIZE
               " STATUS:" DELIMITED BY SIZE
               DB-STATUS DELIMITED BY SIZE
               INTO OUT-REC
           END-STRING.

       *> ===============================
       *> 追加ダミー処理（行数拡張）
       *> ===============================
       DUMMY-PROC-001.
           CONTINUE.
       DUMMY-PROC-002.
           CONTINUE.
       DUMMY-PROC-003.
           CONTINUE.
       DUMMY-PROC-004.
           CONTINUE.
       DUMMY-PROC-005.
           CONTINUE.
       DUMMY-PROC-006.
           CONTINUE.
       DUMMY-PROC-007.
           CONTINUE.
       DUMMY-PROC-008.
           CONTINUE.
       DUMMY-PROC-009.
           CONTINUE.
       DUMMY-PROC-010.
           CONTINUE.

       *> さらにダミー拡張
       DUMMY-PROC-011.
           ADD 1 TO WS-TOTAL.
       DUMMY-PROC-012.
           ADD 2 TO WS-TOTAL.
       DUMMY-PROC-013.
           ADD 3 TO WS-TOTAL.
       DUMMY-PROC-014.
           ADD 4 TO WS-TOTAL.
       DUMMY-PROC-015.
           ADD 5 TO WS-TOTAL.
       DUMMY-PROC-016.
           ADD 6 TO WS-TOTAL.
       DUMMY-PROC-017.
           ADD 7 TO WS-TOTAL.
       DUMMY-PROC-018.
           ADD 8 TO WS-TOTAL.
       DUMMY-PROC-019.
           ADD 9 TO WS-TOTAL.
       DUMMY-PROC-020.
           ADD 10 TO WS-TOTAL.

       *> ===============================
       *> 終了前集計処理
       *> ===============================
       SUMMARY-PROC.

           DISPLAY "====================="
           DISPLAY "  BATCH RESULT       "
           DISPLAY "====================="
           DISPLAY "TOTAL COUNT :" WS-COUNT
           DISPLAY "TOTAL AMOUNT:" WS-TOTAL
           DISPLAY "=====================".

       *> ===============================
       *> メイン処理へ組み込み（例）
       *> ===============================
       EXTENDED-PROC.

           PERFORM BUSINESS-LOGIC-PROC
           PERFORM UPDATE-PROC
           PERFORM INSERT-PROC
           PERFORM DELETE-PROC
           PERFORM STRESS-TEST-PROC
           PERFORM FORMAT-OUTPUT
           PERFORM SUMMARY-PROC.