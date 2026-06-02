// oop.g - phương thức (impl) kiểu Rust trên struct
import std

struct Rect {
    w: int,
    h: int,
}

impl Rect {
    // 'self' tự suy ra là *Rect
    fn area(self) -> int {
        return self.w * self.h
    }

    fn scale(self, k: int) {
        self.w = self.w * k     // self là con trỏ -> tự dùng '->'
        self.h = self.h * k
    }

    fn is_square(self) -> bool {
        return self.w == self.h
    }
}

fn main() -> int {
    let mut r: Rect = Rect { w: 3, h: 4 }
    println("Diện tích = {}", r.area())
    println("Vuông? {}", r.is_square())   // in true/false tự động

    r.scale(2)
    println("Sau scale(2): {}x{}, diện tích = {}", r.w, r.h, r.area())

    let s: Rect = Rect { w: 5, h: 5 }
    println("s vuông? {}", s.is_square())
    return 0
}
