// Kiểm tra vòng lặp foreach (for x in mảng / chuỗi) + break/continue
fn main() -> int {
    let nums: [5]int = [3, 1, 4, 1, 5]

    // duyệt mảng tĩnh, cộng dồn
    let mut tong: int = 0
    for x in nums {
        tong += x
    }
    println("tổng mảng = {}", tong)

    // foreach + continue (bỏ số chẵn) + break
    print("số lẻ: ")
    for x in nums {
        if x % 2 == 0 {
            continue
        }
        if x > 4 {
            break
        }
        print("{} ", x)
    }
    println("")

    // duyệt từng ký tự trong chuỗi
    let mut hoa: int = 0
    for c in "Hello, G!" {
        if c >= 'A' && c <= 'Z' {
            hoa += 1
        }
    }
    println("số chữ hoa = {}", hoa)

    // foreach lồng nhau
    let a: [2]int = [10, 20]
    let b: [3]int = [1, 2, 3]
    let mut s: int = 0
    for i in a {
        for j in b {
            s += i * j
        }
    }
    println("tích chéo = {}", s)
    return 0
}
