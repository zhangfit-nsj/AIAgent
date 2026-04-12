       IDENTIFICATION DIVISION.
       PROGRAM-ID. ORDERPROC.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ORDER-FILE ASSIGN TO 'ORDER.DAT'.
           SELECT CUSTOMER-FILE ASSIGN TO 'CUSTOMER.DAT'.

       DATA DIVISION.
       FILE SECTION.

       FD  ORDER-FILE.
       01  ORDER-REC.
           05 OR-ID              PIC 9(10).
           05 OR-CUSTOMER-ID     PIC 9(10).
           05 OR-AMOUNT          PIC 9(7)V99.

       FD CUSTOMER-FILE.
       01 CUSTOMER-REC.
           05 CU-ID              PIC 9(10).
           05 CU-NAME            PIC X(50).
           05 CU-TYPE            PIC X(10).

       WORKING-STORAGE SECTION.

       01 WS-END-FLAG            PIC X VALUE 'N'.
       01 WS-COUNT               PIC 9(5) VALUE 0.
       01 WS-TOTAL               PIC 9(10)V99 VALUE 0.
       01 WS-CURRENT-CUSTOMER    PIC 9(10).
       01 WS-VIP-FLAG            PIC X VALUE 'N'.

       01 WS-TEMP-VAR-1          PIC X(50).
       01 WS-TEMP-VAR-2          PIC X(50).
       01 WS-TEMP-VAR-3          PIC X(50).
       01 WS-TEMP-VAR-4          PIC X(50).
       01 WS-TEMP-VAR-5          PIC X(50).

       PROCEDURE DIVISION.

       MAIN-PROCESS.
           PERFORM INIT-PROCESS
           PERFORM READ-ORDER
           PERFORM UNTIL WS-END-FLAG = 'Y'
               PERFORM PROCESS-ORDER
               PERFORM READ-ORDER
           END-PERFORM
           PERFORM END-PROCESS
           STOP RUN.

       INIT-PROCESS.
           OPEN INPUT ORDER-FILE
           OPEN INPUT CUSTOMER-FILE
           MOVE 0 TO WS-COUNT
           MOVE 0 TO WS-TOTAL
           DISPLAY "SYSTEM START".

       READ-ORDER.
           READ ORDER-FILE
               AT END
                   MOVE 'Y' TO WS-END-FLAG
           END-READ.

       PROCESS-ORDER.
           ADD 1 TO WS-COUNT
           MOVE OR-CUSTOMER-ID TO WS-CURRENT-CUSTOMER
           PERFORM FIND-CUSTOMER
           PERFORM CHECK-VIP
           PERFORM CALC-TOTAL
           PERFORM OUTPUT-ORDER.

       FIND-CUSTOMER.
           MOVE SPACES TO WS-TEMP-VAR-1
           READ CUSTOMER-FILE
               AT END
                   MOVE "UNKNOWN" TO WS-TEMP-VAR-1
           END-READ.

       CHECK-VIP.
           IF CU-TYPE = "VIP"
               MOVE 'Y' TO WS-VIP-FLAG
           ELSE
               MOVE 'N' TO WS-VIP-FLAG
           END-IF.

       CALC-TOTAL.
           ADD OR-AMOUNT TO WS-TOTAL.

       OUTPUT-ORDER.
           DISPLAY "ORDER ID:" OR-ID
           DISPLAY "CUSTOMER:" CU-NAME
           DISPLAY "AMOUNT:" OR-AMOUNT.

       END-PROCESS.
           DISPLAY "TOTAL COUNT:" WS-COUNT
           DISPLAY "TOTAL AMOUNT:" WS-TOTAL
           CLOSE ORDER-FILE
           CLOSE CUSTOMER-FILE
           DISPLAY "SYSTEM END".

*> ------------------------------------------------------------
*> 以下はダミーの業務ロジックを増やして500行以上にする
*> ------------------------------------------------------------

       EXTRA-PROC-001.
           MOVE "STEP001" TO WS-TEMP-VAR-1.
       EXTRA-PROC-002.
           MOVE "STEP002" TO WS-TEMP-VAR-2.
       EXTRA-PROC-003.
           MOVE "STEP003" TO WS-TEMP-VAR-3.
       EXTRA-PROC-004.
           MOVE "STEP004" TO WS-TEMP-VAR-4.
       EXTRA-PROC-005.
           MOVE "STEP005" TO WS-TEMP-VAR-5.

*> 以下同様パターンを繰り返し