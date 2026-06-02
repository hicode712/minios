// features.g - trình diễn các tính năng nâng cao của G
import std

// hằng toàn cục
const PI: f64 = 3.14159265358979
const MAX_ITEMS: int = 5

fn grade(score: int) -> str {
    // match nhiều pattern + nhánh mặc định
    match score {
        9 | 10 => { return "Xuất sắc" }
        7 | 8  => { return "Khá" }
        5 | 6  => { return "Trung bình" }
        _      => { return "Yếu" }
    }
    return "?"
}

fn day_name(d: str) -> str {
    // match trên chuỗi (dùng strcmp)
    match d {
        "mon" => { return "Thứ Hai" }
        "tue" => { return "Thứ Ba" }
        _     => { return "Không rõ" }
    }
    return "?"
}

fn main() -> int {
    // mảng + len
    let nums: [5]int = [10, 20, 30, 40, 50]
    let mut total: int = 0
    for i in 0..len(nums) {
        total += nums[i]
    }
    println("Mảng có {} phần tử, tổng = {}", len(nums), total)

    // range bao gồm ..= và step
    print("Số chẵn 0..=10: ")
    for i in 0..=10 step 2 {
        print("{} ", i)
    }
    println("")

    // ternary
    let n: int = 7
    let parity: str = (n % 2 == 0) ? "chẵn" : "lẻ"
    println("{} là số {}", n, parity)

    // builtins min/max/abs
    println("min(3,9)={}, max(3,9)={}, abs(-42)={}", min(3, 9), max(3, 9), abs(-42))

    // hằng & float
    println("PI ≈ {f}, chu vi r=2 là {f}", PI, 2.0 * PI * 2.0)

    // gọi thư viện std
    println("gcd(48,36)={}, is_prime(97)={}, 2^10={ld}", gcd(48, 36), is_prime(97), ipow(2, 10))
    println("5! = {ld}", factorial(5))

    // match
    println("Điểm 8 -> {}", grade(8))
    println("'tue' -> {}", day_name("tue"))

    // loop + break
    let mut count: int = 0
    loop {
        count += 1
        if count >= MAX_ITEMS {
            break
        }
    }
    println("Đếm tới {} bằng loop", count)

    // assert
    assert(total == 150, "tổng phải bằng 150")
    println("assert OK!")

    return 0
}
