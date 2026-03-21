/**
 * vulnerable.c
 * テスト用サンプル — 意図的に脆弱なCコード
 * 全検出パターンを含む
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* --- REQ-S1: フラグ未初期化 --- */
static int g_initialized;  /* 未初期化のまま使用される */

/* --- REQ-M1: NULLチェック漏れ --- */
void process_data(char *data) {
    /* data が NULL かどうかチェックしていない */
    printf("Data: %s\n", data);
    int len = strlen(data);
    printf("Length: %d\n", len);
}

/* --- REQ-M2: 未初期化変数 --- */
int calculate_sum(int count) {
    int total;  /* 未初期化 */
    for (int i = 0; i < count; i++) {
        total += i;
    }
    return total;
}

/* --- REQ-M3: malloc戻り値未確認 --- */
char* create_buffer(size_t size) {
    char *buf = malloc(size);
    /* malloc の戻り値チェックなし */
    memset(buf, 0, size);
    return buf;
}

/* --- REQ-M4: free忘れ (メモリリーク) --- */
void leaky_function(void) {
    char *temp = malloc(256);
    if (temp == NULL) return;
    strcpy(temp, "hello");
    printf("%s\n", temp);
    /* free(temp) がない — メモリリーク */
    return;
}

/* --- REQ-M5: 二重free --- */
void double_free_example(void) {
    int *p = malloc(sizeof(int));
    if (p == NULL) return;
    *p = 42;
    free(p);
    /* ... 他の処理 ... */
    free(p);  /* 二重 free */
}

/* --- REQ-A1: buffer overflow --- */
void buffer_overflow_example(void) {
    char small_buf[10];
    strcpy(small_buf, "This string is way too long for the buffer");
}

/* --- REQ-A2: 境界チェック不足 --- */
int access_array(int *arr, int index) {
    /* index の範囲チェックなし */
    return arr[index];
}

/* --- REQ-R1: 戻り値未確認 --- */
void file_operations(void) {
    FILE *fp = fopen("/tmp/test.txt", "r");
    /* fopen の戻り値チェックなし */
    char buf[100];
    fgets(buf, sizeof(buf), fp);
    fclose(fp);
}

/* --- REQ-S2: 状態遷移抜け --- */
typedef enum {
    STATE_INIT,
    STATE_RUNNING,
    STATE_PAUSED,
    STATE_STOPPED
} State;

void handle_state(State state) {
    switch (state) {
        case STATE_INIT:
            printf("Initializing\n");
            break;
        case STATE_RUNNING:
            printf("Running\n");
            break;
        /* STATE_PAUSED と STATE_STOPPED が処理されていない */
    }
}

int main(void) {
    /* g_initialized チェックなしで使用 */
    if (g_initialized) {
        printf("Already initialized\n");
    }

    process_data(NULL);  /* NULL を渡す */

    int sum = calculate_sum(10);
    printf("Sum: %d\n", sum);

    char *buf = create_buffer(1024);
    /* buf が NULL の可能性を考慮していない */
    printf("Buffer: %p\n", (void*)buf);

    leaky_function();
    double_free_example();
    buffer_overflow_example();

    int arr[] = {1, 2, 3};
    int val = access_array(arr, 100);  /* 範囲外アクセス */
    printf("Value: %d\n", val);

    file_operations();
    handle_state(STATE_PAUSED);  /* 未処理の状態 */

    return 0;
}
