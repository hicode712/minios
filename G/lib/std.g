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
