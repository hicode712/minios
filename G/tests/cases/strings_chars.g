// Kiểm tra chuỗi, ký tự, escape, literal cơ số
fn main() -> int {
    let s: str = "G\tlang\n"
    print("{s}", s)

    let c: char = 'A'
    println("char {} = mã {}", c, c as int)

    let hexv: int = 0xFF
    let binv: int = 0b1010
    let octv: int = 0o17
    println("hex 0xFF={}, bin 0b1010={}, oct 0o17={}", hexv, binv, octv)

    let big: i64 = 1000000000000
    println("i64 lớn = {ld}", big)

    let flag: bool = true
    println("not {} = {}", flag, !flag)
    return 0
}
