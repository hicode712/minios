// sieve.g - sàng nguyên tố Eratosthenes (dùng mảng + con trỏ cấp phát động)
import std

fn main() -> int {
    let n: int = 50
    // C: cấp phát mảng động qua macro runtime g_alloc
    let mut sieve: *bool = g_alloc(bool, n)

    let mut i: int = 0
    while i < n {
        sieve[i] = true
        i += 1
    }

    let mut p: int = 2
    while p * p < n {
        if sieve[p] {
            let mut m: int = p * p
            while m < n {
                sieve[m] = false
                m += p
            }
        }
        p += 1
    }

    println("Số nguyên tố < {}:", n)
    for k in 2..n {
        if sieve[k] {
            print("{} ", k)
        }
    }
    println("")

    g_free(sieve)
    return 0
}
