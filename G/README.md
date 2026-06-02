# Ngôn ngữ lập trình G

**G** là một ngôn ngữ lập trình biên dịch (compiled), hệ thống (systems), kết hợp tinh hoa của **5 ngôn ngữ** — với **type-checker**, **suy luận kiểu**, **method (impl)**, **module**, **thư viện chuẩn** và **chẩn đoán lỗi đẹp**.

| Ảnh hưởng | Đóng góp cho G |
|-----------|----------------|
| **Assembly** | Khối `asm { }` chèn lệnh máy thô |
| **C** | Con trỏ, struct, kiểu thấp cấp, cấp phát thủ công, làm *backend* |
| **C++** | Biên dịch qua trình C/C++ tối ưu, `static inline`, prototype |
| **Rust** | `let` bất biến mặc định, `let mut`, `match`, `for i in a..b`, `impl`, `loop` |
| **Zig** | `defer` (LIFO), `comptime`, định dạng in `{}`/`{d}`/`{s}`, tường minh |

Triết lý: **frontend hiện đại (Rust/Zig) → type-check → biên dịch xuống C → mã máy native qua GCC/Clang.**

```
 source.g ─► Lexer ─► Parser ─► [gộp module] ─► Checker (kiểu) ─► Codegen ─► gcc/clang ─► mã máy
            (+ASI)    (AST)       (import)        (suy luận)        (C)
```

---

## Cài đặt & chạy

Cần `python3` và `gcc` hoặc `clang`.

```bash
cd G
./gc examples/showcase.g --run      # biên dịch + chạy
./gc examples/oop.g -o oop && ./oop # tạo file thực thi
./gc examples/fib.g --emit-c        # xem mã C trung gian
./tests/run_tests.sh                # chạy bộ test
```

### Tùy chọn của `gc`

| Cờ | Ý nghĩa |
|----|---------|
| `-o <file>` | Tên file thực thi đầu ra |
| `-r`, `--run` | Biên dịch xong chạy luôn |
| `--emit-c` | Chỉ in/ghi mã C |
| `--keep-c` | Giữ lại file `.c` trung gian |
| `--check` | Chỉ kiểm tra kiểu, không sinh mã |
| `--tokens` | In danh sách token (debug lexer) |
| `--ast` | In cây cú pháp AST (debug parser) |
| `--cc <cc>` | Chọn trình biên dịch C |
| `-O <0..3>` | Mức tối ưu (mặc định 2) |

---

## Tính năng & cú pháp

### Hàm, biến, kiểu
```g
fn add(a: int, b: int) -> int { return a + b }

let x: int = 10          // bất biến (const)
let mut y = 0            // thay đổi được, kiểu tự suy luận
const PI: f64 = 3.14159  // hằng toàn cục
```
Kiểu: `int i8..i64 u8..u64 usize isize f32 f64 bool char str void`, con trỏ `*T`, mảng `[N]T` / `[]T`.

### Điều khiển luồng
```g
if c { } else if d { } else { }
while cond { }
loop { ... break }                 // vòng lặp vô hạn (Rust)
for i in 0..10 { }                 // 0..9
for i in 0..=10 step 2 { }         // bao gồm 10, bước 2
let p = (n % 2 == 0) ? "chẵn" : "lẻ"   // ternary
```

### `match` (Rust) — nhiều pattern, khớp chuỗi, mặc định
```g
match score {
    9 | 10 => { return "Xuất sắc" }
    7 | 8  => { return "Khá" }
    _      => { return "Yếu" }
}
match cmd {                 // tự dùng strcmp cho chuỗi
    "quit" => { ... }
    _      => { ... }
}
```

### `struct`, `enum`, và `impl` (method)
```g
struct Rect { w: int, h: int }
enum Color { Red, Green = 5, Blue }

impl Rect {
    fn area(self) -> int { return self.w * self.h }  // self: *Rect, '.' tự thành '->'
    fn scale(self, k: int) { self.w = self.w * k }
}

let mut r = Rect { w: 3, h: 4 }
println("{}", r.area())   // -> 12
r.scale(2)
```

### Con trỏ & bộ nhớ động
```g
let mut v = 42
let p: *int = &v
*p = 100                     // v == 100

let mut buf: *int = g_alloc(int, 100)   // calloc
buf[0] = 1
g_free(buf)
```

### Mảng
```g
let nums: [5]int = [10, 20, 30, 40, 50]
for i in 0..len(nums) { ... }    // len() dùng được cho mảng tĩnh
```

### `defer` (Zig) — chạy khi rời hàm theo thứ tự LIFO
```g
defer println("chạy thứ 2")
defer println("chạy thứ 1")    // in trước
```

### Inline Assembly
```g
asm { "nop" "nop" }
```

### `comptime` (Zig) — gợi ý tính/inline lúc biên dịch
```g
comptime fn square(n: int) -> int { return n * n }
```

### In ra màn hình — định dạng kiểu Zig (tự suy luận theo kiểu)
`print` / `println` (stdout) và `eprint` / `eprintln` (stderr).

| Placeholder | Ý nghĩa |
|-------------|---------|
| `{}` | **Tự suy luận** theo kiểu đối số (kể cả `bool` → `true`/`false`) |
| `{d}` `{ld}` | số nguyên / 64-bit |
| `{u}` `{lu}` | unsigned / 64-bit |
| `{f}` | số thực |
| `{s}` `{c}` | chuỗi / ký tự |
| `{x}` `{X}` `{o}` | hex / HEX / bát phân |
| `{b}` | bool → true/false |
| `{{` `}}` | dấu `{` `}` literal |

> Compiler **kiểm tra số placeholder khớp số đối số** và báo lỗi nếu lệch.

### Builtins
`len(x)` · `assert(cond[, msg])` · `panic(msg)` · `min(a,b)` · `max(a,b)` · `abs(x)` · `g_alloc(T,n)` · `g_realloc(p,T,n)` · `g_free(p)`.

### Module / `import`
```g
import std            // nạp lib/std.g
import "helpers.g"    // nạp file cùng thư mục
```
`lib/std.g` cung cấp: `gcd lcm ipow is_prime factorial swap_int`.

---

## Hệ thống kiểu & chẩn đoán

G có một **type-checker** chạy trước khi sinh mã:
- Suy luận kiểu cho mọi biểu thức (dùng cho định dạng `print`, auto-deref, phân giải method).
- Bắt lỗi: biến/định danh chưa khai báo, gán vào biến bất biến, sai số tham số, trường/struct/kiểu không tồn tại, lệch placeholder.

Lỗi hiển thị kèm dòng nguồn và con trỏ `^`:
```
bad.g:3:5: lỗi kiểu/ngữ nghĩa: không thể gán cho 'x' (bất biến — dùng 'let mut')
    3 |     x = 10
      |     ^
```

---

## Cấu trúc dự án

```
G/
├── gc                      # trình biên dịch (điểm vào)
├── README.md
├── compiler/
│   ├── lexer.py            # từ vựng + tự chèn ';' (ASI kiểu Go)
│   ├── ast_nodes.py        # định nghĩa nút AST
│   ├── parser.py           # cú pháp -> AST
│   ├── types.py            # hệ thống kiểu (GType, ánh xạ C, printf spec)
│   ├── checker.py          # phân tích ngữ nghĩa + suy luận kiểu
│   ├── codegen.py          # sinh mã C
│   └── driver.py           # pipeline + module + chẩn đoán + gọi cc
├── runtime/g_runtime.h     # runtime (g_alloc, g_panic, ...)
├── lib/std.g               # thư viện chuẩn (viết bằng G)
├── examples/               # hello, showcase, fib, sieve, oop, features
└── tests/
    ├── run_tests.sh        # bộ test (so sánh output; --bless để cập nhật)
    ├── cases/              # test case riêng
    └── expected/           # kết quả mong đợi
```

---

## Quy tắc kết thúc câu lệnh

Như Go/Zig, G **tự động kết thúc câu lệnh ở cuối dòng** — không cần `;`.
Khi cần trải biểu thức nhiều dòng, để toán tử ở **cuối dòng**:
```g
let x = a +
        b        // OK
```

---

## Giới hạn hiện tại

- `match` so khớp bằng `==`/`strcmp` (chưa destructuring/range pattern).
- `asm` là *basic asm* GCC (chưa ràng buộc toán tử `%0/%1`).
- Chưa có generic, trait, ownership/borrow-checker đầy đủ.
- `defer` ở mức hàm (chưa mức block lồng).

Một nền tảng vững để mở rộng tiếp. 🚀
