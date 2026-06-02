/* === G Language Runtime ===
 * Header nền tảng tự động include vào mọi chương trình G.
 * Cầu nối tới thư viện chuẩn C + các tiện ích lấy cảm hứng từ Rust/Zig.
 */
#ifndef G_RUNTIME_H
#define G_RUNTIME_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stddef.h>
#include <math.h>

/* ---- Cấp phát bộ nhớ (Zig/Rust style) ---- */
#define g_alloc(T, n)        ((T*)calloc((size_t)(n), sizeof(T)))
#define g_realloc(p, T, n)   ((T*)realloc((p), sizeof(T) * (size_t)(n)))
#define g_free(p)            free((void*)(p))

/* ---- panic: dừng chương trình (giống Rust) ---- */
static inline void g_panic(const char* msg) {
    fprintf(stderr, "\033[1;31mG panic:\033[0m %s\n", msg);
    exit(101);
}

/* ---- giá trị nhỏ nhất/lớn nhất kiểu (tiện cho comptime) ---- */
#define G_I32_MAX  2147483647
#define G_I32_MIN  (-2147483647 - 1)
#define G_U32_MAX  4294967295u

#endif /* G_RUNTIME_H */
