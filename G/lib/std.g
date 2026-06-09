// std.g - thư viện chuẩn của G (viết bằng chính ngôn ngữ G)
// Dùng:  import std

// Ước số chung lớn nhất (thuật toán Euclid)
fn gcd(a: int, b: int) -> int {
    let mut x: int = abs(a)
    let mut y: int = abs(b)
    while y != 0 {
        let t: int = y
        y = x % y
        x = t
    }
    return x
}

// Bội số chung nhỏ nhất
fn lcm(a: int, b: int) -> int {
    if a == 0 || b == 0 {
        return 0
    }
    return abs(a / gcd(a, b) * b)
}

// Luỹ thừa số nguyên: base^exp
fn ipow(base: int, exp: int) -> i64 {
    let mut result: i64 = 1
    let mut b: i64 = base as i64
    let mut e: int = exp
    while e > 0 {
        if e % 2 == 1 {
            result = result * b
        }
        b = b * b
        e = e / 2
    }
    return result
}

// Kiểm tra số nguyên tố
fn is_prime(n: int) -> bool {
    if n < 2 {
        return false
    }
    let mut i: int = 2
    while i * i <= n {
        if n % i == 0 {
            return false
        }
        i += 1
    }
    return true
}

// Giai thừa
fn factorial(n: int) -> i64 {
    let mut r: i64 = 1
    for i in 2..=n {
        r = r * (i as i64)
    }
    return r
}

// Hoán đổi hai số nguyên qua con trỏ
fn swap_int(a: *int, b: *int) {
    let t: int = *a
    *a = *b
    *b = t
}

// Dấu của số nguyên: -1, 0, hoặc 1
fn sign(x: int) -> int {
    if x > 0 { return 1 }
    if x < 0 { return -1 }
    return 0
}

fn is_even(n: int) -> bool { return n % 2 == 0 }
fn is_odd(n: int) -> bool { return n % 2 != 0 }

// Căn bậc hai nguyên (làm tròn xuống) — thuật toán Newton
fn isqrt(n: int) -> int {
    if n < 2 { return n }
    let mut x: int = n
    let mut y: int = (x + 1) / 2
    while y < x {
        x = y
        y = (x + n / x) / 2
    }
    return x
}

// Fibonacci lặp (nhanh, không tràn stack như đệ quy)
fn fib(n: int) -> i64 {
    let mut a: i64 = 0
    let mut b: i64 = 1
    for _i in 0..n {
        let t: i64 = a + b
        a = b
        b = t
    }
    return a
}

// Tổng các phần tử của một mảng động (truyền kèm độ dài)
fn sum_slice(a: *int, n: int) -> i64 {
    let mut s: i64 = 0
    for i in 0..n {
        s = s + (a[i] as i64)
    }
    return s
}

// ---- Chuỗi: tái dùng thư viện C qua 'extern' ----
extern fn strcmp(a: str, b: str) -> int
extern fn strlen(s: str) -> usize

// Hai chuỗi bằng nhau?
fn streq(a: str, b: str) -> bool {
    return strcmp(a, b) == 0
}

// Độ dài chuỗi (số byte)
fn str_len(s: str) -> usize {
    return strlen(s)
}

// ---- Chuỗi nâng cao (runtime g_runtime.h; bản cấp phát heap -> nhớ g_free) ----
extern fn g_str_dup(s: str) -> str
extern fn g_str_concat(a: str, b: str) -> str
extern fn g_substr(s: str, start: isize, len: isize) -> str
extern fn g_str_eq(a: str, b: str) -> bool
extern fn g_str_index(hay: str, needle: str) -> isize
extern fn g_str_contains(hay: str, needle: str) -> bool
extern fn g_str_starts_with(s: str, pre: str) -> bool
extern fn g_str_ends_with(s: str, suf: str) -> bool
extern fn g_parse_int(s: str) -> i64
extern fn g_parse_float(s: str) -> f64
extern fn g_int_to_str(v: i64) -> str

// Nối hai chuỗi -> chuỗi mới trên heap (nhớ g_free)
fn str_concat(a: str, b: str) -> str { return g_str_concat(a, b) }

// Cắt chuỗi con an toàn (chỉ số/độ dài tự kẹp về biên)
fn substr(s: str, start: int, len: int) -> str {
    return g_substr(s, start as isize, len as isize)
}

// Chuỗi a có chứa b không?
fn str_contains(hay: str, needle: str) -> bool { return g_str_contains(hay, needle) }

// Chuỗi bắt đầu/kết thúc bằng tiền tố/hậu tố?
fn starts_with(s: str, pre: str) -> bool { return g_str_starts_with(s, pre) }
fn ends_with(s: str, suf: str) -> bool { return g_str_ends_with(s, suf) }

// Phân tích số nguyên/thực từ chuỗi (lỗi -> 0)
fn parse_int(s: str) -> i64 { return g_parse_int(s) }
fn parse_float(s: str) -> f64 { return g_parse_float(s) }

// Chuyển số nguyên thành chuỗi mới (heap; nhớ g_free)
fn int_to_str(v: i64) -> str { return g_int_to_str(v) }

// ---- Số học bổ sung ----

// Luỹ thừa modulo: (base^exp) mod m — nhanh, tránh tràn cho số vừa phải
fn powmod(base: i64, exp: i64, m: i64) -> i64 {
    if m == 1 { return 0 }
    let mut result: i64 = 1
    let mut b: i64 = base % m
    let mut e: i64 = exp
    while e > 0 {
        if e % 2 == 1 {
            result = (result * b) % m
        }
        e = e / 2
        b = (b * b) % m
    }
    return result
}

// Số lớn nhất trong ba số
fn max3(a: int, b: int, c: int) -> int {
    return max(a, max(b, c))
}

// Số nhỏ nhất trong ba số
fn min3(a: int, b: int, c: int) -> int {
    return min(a, min(b, c))
}

// Đếm số bit 1 (popcount)
fn popcount(x: u64) -> int {
    let mut n: u64 = x
    let mut count: int = 0
    while n != 0 {
        count += (n & 1) as int
        n = n >> 1
    }
    return count
}

// Số Fibonacci thứ n có vượt quá đệ quy? Dùng bản lặp 'fib' ở trên.

// Hoán đổi hai phần tử trong mảng động
fn swap_at(a: *int, i: int, j: int) {
    let t: int = a[i]
    a[i] = a[j]
    a[j] = t
}

// Sắp xếp nổi bọt mảng động tăng dần (tại chỗ)
fn bubble_sort(a: *int, n: int) {
    let mut i: int = 0
    while i < n {
        let mut j: int = 0
        while j < n - i - 1 {
            if a[j] > a[j + 1] {
                swap_at(a, j, j + 1)
            }
            j += 1
        }
        i += 1
    }
}

// Tìm kiếm nhị phân trên mảng đã sắp xếp; trả về chỉ số hoặc -1
fn binary_search(a: *int, n: int, target: int) -> int {
    let mut lo: int = 0
    let mut hi: int = n - 1
    while lo <= hi {
        let mid: int = lo + (hi - lo) / 2
        if a[mid] == target {
            return mid
        }
        if a[mid] < target {
            lo = mid + 1
        } else {
            hi = mid - 1
        }
    }
    return -1
}

// Tổng tích luỹ lớn nhất của một dãy con liên tiếp (Kadane)
fn max_subarray(a: *int, n: int) -> i64 {
    if n <= 0 { return 0 }
    let mut best: i64 = a[0] as i64
    let mut cur: i64 = a[0] as i64
    for i in 1..n {
        let v: i64 = a[i] as i64
        cur = max(v, cur + v) as i64
        best = max(best, cur) as i64
    }
    return best
}

// ============================================================================
//  Toán học dấu phẩy động — cầu nối tới libm qua 'extern' (đã liên kết -lm)
// ============================================================================
extern fn sqrt(x: f64) -> f64
extern fn cbrt(x: f64) -> f64
extern fn pow(base: f64, e: f64) -> f64
extern fn floor(x: f64) -> f64
extern fn ceil(x: f64) -> f64
extern fn round(x: f64) -> f64
extern fn trunc(x: f64) -> f64
extern fn fabs(x: f64) -> f64
extern fn fmod(x: f64, y: f64) -> f64
extern fn sin(x: f64) -> f64
extern fn cos(x: f64) -> f64
extern fn tan(x: f64) -> f64
extern fn atan2(y: f64, x: f64) -> f64
extern fn exp(x: f64) -> f64
extern fn log(x: f64) -> f64
extern fn log2(x: f64) -> f64
extern fn log10(x: f64) -> f64
extern fn hypot(x: f64, y: f64) -> f64

const G_PI: f64 = 3.14159265358979323846
const G_E:  f64 = 2.71828182845904523536

// Nội suy tuyến tính giữa a và b theo t∈[0,1]
fn lerp(a: f64, b: f64, t: f64) -> f64 { return a + (b - a) * t }

// Kẹp số thực vào [lo, hi]
fn clampf(x: f64, lo: f64, hi: f64) -> f64 {
    if x < lo { return lo }
    if x > hi { return hi }
    return x
}

// Đổi độ <-> radian
fn deg2rad(d: f64) -> f64 { return d * G_PI / 180.0 }
fn rad2deg(r: f64) -> f64 { return r * 180.0 / G_PI }

// ============================================================================
//  Tiện ích số nguyên
// ============================================================================

// Tổng các chữ số (theo trị tuyệt đối)
fn sum_digits(n: int) -> int {
    let mut x: int = abs(n)
    let mut s: int = 0
    while x > 0 { s += x % 10; x = x / 10 }
    return s
}

// Số chữ số (0 có 1 chữ số)
fn count_digits(n: int) -> int {
    let mut x: int = abs(n)
    let mut c: int = 1
    while x >= 10 { c += 1; x = x / 10 }
    return c
}

// Đảo ngược các chữ số (giữ dấu): reverse_int(-123) = -321
fn reverse_int(n: int) -> int {
    let mut x: int = abs(n)
    let mut r: int = 0
    while x > 0 { r = r * 10 + x % 10; x = x / 10 }
    return sign(n) * r
}

// Số có đối xứng (palindrome) không? (chỉ xét số không âm)
fn is_palindrome_int(n: int) -> bool {
    return n >= 0 && reverse_int(n) == n
}

// ============================================================================
//  Tiện ích mảng động (truyền con trỏ + độ dài). 'array_min/max' cần n >= 1.
// ============================================================================

// Gán mọi phần tử bằng v
fn fill(a: *int, n: int, v: int) {
    for i in 0..n { a[i] = v }
}

// Sao chép n phần tử từ src sang dst
fn array_copy(dst: *int, src: *int, n: int) {
    for i in 0..n { dst[i] = src[i] }
}

// Đảo ngược mảng tại chỗ
fn reverse(a: *int, n: int) {
    let mut i: int = 0
    let mut j: int = n - 1
    while i < j {
        swap_at(a, i, j)
        i += 1
        j -= 1
    }
}

// Phần tử lớn nhất / nhỏ nhất
fn array_max(a: *int, n: int) -> int {
    let mut m: int = a[0]
    for i in 1..n { if a[i] > m { m = a[i] } }
    return m
}
fn array_min(a: *int, n: int) -> int {
    let mut m: int = a[0]
    for i in 1..n { if a[i] < m { m = a[i] } }
    return m
}

// Vị trí xuất hiện đầu tiên của target, hoặc -1
fn index_of(a: *int, n: int, target: int) -> int {
    for i in 0..n { if a[i] == target { return i } }
    return -1
}

// Mảng có chứa target không?
fn contains(a: *int, n: int, target: int) -> bool {
    return index_of(a, n, target) >= 0
}

// Đếm số lần target xuất hiện
fn count_val(a: *int, n: int, target: int) -> int {
    let mut c: int = 0
    for i in 0..n { if a[i] == target { c += 1 } }
    return c
}

// Mảng đã sắp xếp tăng dần chưa?
fn is_sorted(a: *int, n: int) -> bool {
    for i in 1..n { if a[i - 1] > a[i] { return false } }
    return true
}

// Sắp xếp chèn (insertion sort) tăng dần, tại chỗ — ổn định, tốt cho mảng nhỏ
fn insertion_sort(a: *int, n: int) {
    let mut i: int = 1
    while i < n {
        let key: int = a[i]
        let mut j: int = i - 1
        while j >= 0 && a[j] > key {
            a[j + 1] = a[j]
            j -= 1
        }
        a[j + 1] = key
        i += 1
    }
}

// ============================================================================
//  Hàm bậc cao (truyền CON TRỎ HÀM) — map / filter / fold / any / all ...
// ============================================================================

// Áp f cho từng phần tử src, ghi vào dst (n phần tử)
fn map_into(dst: *int, src: *int, n: int, f: fn(int) -> int) {
    for i in 0..n { dst[i] = f(src[i]) }
}

// Lọc phần tử thoả pred vào dst; trả về số phần tử giữ lại
fn filter_into(dst: *int, src: *int, n: int, pred: fn(int) -> bool) -> int {
    let mut k: int = 0
    for i in 0..n {
        if pred(src[i]) {
            dst[k] = src[i]
            k += 1
        }
    }
    return k
}

// Gộp toàn mảng bằng f, bắt đầu từ init: fold(a,n,0,add) = tổng
fn fold(a: *int, n: int, init: int, f: fn(int, int) -> int) -> int {
    let mut acc: int = init
    for i in 0..n { acc = f(acc, a[i]) }
    return acc
}

// Đếm số phần tử thoả pred
fn count_if(a: *int, n: int, pred: fn(int) -> bool) -> int {
    let mut c: int = 0
    for i in 0..n { if pred(a[i]) { c += 1 } }
    return c
}

// Có ít nhất một / tất cả phần tử thoả pred?
fn any(a: *int, n: int, pred: fn(int) -> bool) -> bool {
    for i in 0..n { if pred(a[i]) { return true } }
    return false
}
fn all(a: *int, n: int, pred: fn(int) -> bool) -> bool {
    for i in 0..n { if !pred(a[i]) { return false } }
    return true
}

// Chỉ số phần tử đầu tiên thoả pred, hoặc -1
fn find_first(a: *int, n: int, pred: fn(int) -> bool) -> int {
    for i in 0..n { if pred(a[i]) { return i } }
    return -1
}

// ============================================================================
//  Chuỗi nâng cao (runtime; bản cấp phát heap -> nhớ g_free)
// ============================================================================
extern fn g_str_rev(s: str) -> str
extern fn g_str_upper(s: str) -> str
extern fn g_str_lower(s: str) -> str
extern fn g_str_repeat(s: str, k: isize) -> str
extern fn g_str_count(s: str, c: char) -> isize

// Đảo ngược chuỗi -> chuỗi mới (heap)
fn str_rev(s: str) -> str { return g_str_rev(s) }

// Chuyển HOA / thường -> chuỗi mới (heap)
fn to_upper(s: str) -> str { return g_str_upper(s) }
fn to_lower(s: str) -> str { return g_str_lower(s) }

// Lặp chuỗi k lần -> chuỗi mới (heap)
fn str_repeat(s: str, k: int) -> str { return g_str_repeat(s, k as isize) }

// Đếm số lần ký tự c xuất hiện trong chuỗi
fn count_char(s: str, c: char) -> int { return g_str_count(s, c) as int }

// Vị trí xuất hiện đầu tiên của 'needle' trong 'hay', hoặc -1
fn str_index(hay: str, needle: str) -> int { return g_str_index(hay, needle) as int }
