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

/* ---- min/max/abs/clamp: statement-expression, đánh giá đối số đúng MỘT lần.
 *      (Trình sinh mã G nội tuyến phiên bản riêng; các macro này tiện cho asm/C.) */
#define g_min(a, b)      ({ __auto_type _ga = (a); __auto_type _gb = (b); _ga < _gb ? _ga : _gb; })
#define g_max(a, b)      ({ __auto_type _ga = (a); __auto_type _gb = (b); _ga > _gb ? _ga : _gb; })
#define g_abs(x)         ({ __auto_type _gx = (x); _gx < 0 ? -_gx : _gx; })
#define g_clamp(x, lo, hi) ({ __auto_type _gc = (x); __auto_type _gl = (lo); __auto_type _gh = (hi); \
                              _gc < _gl ? _gl : (_gc > _gh ? _gh : _gc); })
#define g_swap(T, a, b)  do { T _gt = (a); (a) = (b); (b) = _gt; } while (0)

/* ---- giá trị nhỏ nhất/lớn nhất theo kiểu (tiện cho comptime) ---- */
#define G_I8_MAX   127
#define G_I8_MIN   (-128)
#define G_I16_MAX  32767
#define G_I16_MIN  (-32768)
#define G_I32_MAX  2147483647
#define G_I32_MIN  (-2147483647 - 1)
#define G_I64_MAX  9223372036854775807LL
#define G_I64_MIN  (-9223372036854775807LL - 1)
#define G_U8_MAX   255u
#define G_U16_MAX  65535u
#define G_U32_MAX  4294967295u
#define G_U64_MAX  18446744073709551615ULL

#endif /* G_RUNTIME_H */
