// fib.g - dãy Fibonacci bằng đệ quy
fn fib(n: int) -> int {
    if n < 2 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

fn main() -> int {
    println("Dãy Fibonacci:")
    for i in 0..15 {
        print("{} ", fib(i))
    }
    println("")
    return 0
}
