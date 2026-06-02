// Kiểm tra con trỏ, hoán đổi qua std, cấp phát động
import std

fn main() -> int {
    let mut a: int = 1
    let mut b: int = 99
    swap_int(&a, &b)
    println("sau swap: a={}, b={}", a, b)

    // cấp phát động + ghi/đọc
    let mut buf: *int = g_alloc(int, 4)
    for i in 0..4 {
        buf[i] = (i + 1) * 10
    }
    let mut sum: int = 0
    for i in 0..4 {
        sum += buf[i]
    }
    println("tổng buffer = {}", sum)
    g_free(buf)
    return 0
}
