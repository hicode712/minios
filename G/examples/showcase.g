// showcase.g - trình diễn toàn bộ tính năng ngôn ngữ G
// Kết hợp: ASM + C + C++ + Rust + Zig

import std

// --- C: struct & con trỏ ---
struct Point {
    x: int,
    y: int,
}

// --- Rust: enum ---
enum Color {
    Red,
    Green,
    Blue,
}

// --- Zig: comptime (sinh thành static inline) ---
comptime fn square(n: int) -> int {
    return n * n
}

// Inline ASM (cảm hứng từ Assembly): chèn lệnh máy thô vào hàm.
// asm { } sinh ra __asm__ basic-asm của GCC/Clang.
fn add_asm(a: int, b: int) -> int {
    // 'nop' = no-operation: minh họa lệnh máy được nhúng trực tiếp
    asm {
        "nop"
        "nop"
    }
    return a + b
}

fn classify(n: int) -> str {
    // Rust: match
    match n {
        0 => { return "không" }
        1 => { return "một" }
        _ => { return "nhiều" }
    }
    return "?"
}

fn main() -> int {
    // Rust: let bất biến mặc định, let mut khi cần thay đổi
    let greeting: str = "=== Ngôn ngữ G ==="
    println("{s}", greeting)

    // Zig: defer chạy theo thứ tự LIFO khi rời hàm
    defer println("[defer] tạm biệt!")
    defer println("[defer] dọn dẹp xong")

    // C: struct literal + truy cập trường
    let p: Point = Point { x: 3, y: 4 }
    println("Điểm p = ({}, {})", p.x, p.y)

    // comptime square
    println("square(5) = {}", square(5))

    // vòng lặp for theo khoảng (Rust style a..b)
    let mut tong: int = 0
    for i in 1..6 {
        tong += i
    }
    println("Tổng 1..5 = {}", tong)

    // while + match
    let mut k: int = 0
    while k < 3 {
        println("classify({}) = {s}", k, classify(k))
        k += 1
    }

    // Con trỏ kiểu C
    let mut val: int = 42
    let ptr: *int = &val
    *ptr = 100
    println("Giá trị qua con trỏ = {}", val)

    // Enum
    let c: Color = Green
    println("Color Green = {}", c as int)

    // Inline ASM
    println("add_asm(20, 22) = {}", add_asm(20, 22))

    return 0
}
