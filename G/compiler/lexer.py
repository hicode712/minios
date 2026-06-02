"""
G Language - Lexer (Bộ phân tích từ vựng)
Chuyển source code thành chuỗi token, tự động chèn ';' kết thúc câu lệnh (kiểu Go).
"""

from dataclasses import dataclass


KEYWORDS = {
    "fn", "let", "mut", "struct", "enum", "if", "else", "while", "for",
    "return", "match", "defer", "asm", "import", "true", "false",
    "comptime", "break", "continue", "as", "null", "sizeof", "in",
    "loop", "impl", "const", "extern", "step",
}

# Toán tử 3 ký tự (kiểm tra trước 2 ký tự)
THREE_OPS = ["..=", "<<=", ">>="]

# Toán tử 2 ký tự (kiểm tra trước 1 ký tự)
MULTI_OPS = [
    "->", "=>", "==", "!=", "<=", ">=", "&&", "||", "<<", ">>",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "..", "::",
]
SINGLE_OPS = set("+-*/%=<>!&|^~.,;:(){}[]@?")


@dataclass
class Token:
    kind: str       # 'kw','id','int','float','str','char','op','eof'
    value: str
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, {self.line}:{self.col})"


class LexError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(msg)
        self.msg = msg
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, src: str, filename: str = "<input>"):
        self.src = src
        self.filename = filename
        self.i = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.depth = 0   # độ sâu ( ) [ ] để biết khi nào KHÔNG chèn ';' tự động

    def error(self, msg):
        raise LexError(msg, self.line, self.col)

    def peek(self, off=0):
        j = self.i + off
        return self.src[j] if j < len(self.src) else ""

    def advance(self):
        c = self.src[self.i]
        self.i += 1
        if c == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return c

    def add(self, kind, value, line, col):
        if value in ("(", "["):
            self.depth += 1
        elif value in (")", "]"):
            self.depth = max(0, self.depth - 1)
        self.tokens.append(Token(kind, value, line, col))

    # Token cuối có thể kết thúc một câu lệnh? (quy tắc chèn ';' kiểu Go)
    _STMT_END_KW = {"true", "false", "null", "break", "continue", "return"}

    def _auto_semi(self):
        if not self.tokens or self.depth > 0:
            return
        last = self.tokens[-1]
        eligible = (
            last.kind in ("id", "int", "float", "str", "char")
            or (last.kind == "kw" and last.value in self._STMT_END_KW)
            or (last.kind == "op" and last.value in (")", "]"))
        )
        if eligible:
            self.tokens.append(Token("op", ";", last.line, last.col))

    def tokenize(self):
        while self.i < len(self.src):
            c = self.peek()

            # Khoảng trắng (xuống dòng có thể kết thúc câu lệnh)
            if c in " \t\r\n":
                if c == "\n":
                    self._auto_semi()
                self.advance()
                continue

            # Comment dòng
            if c == "/" and self.peek(1) == "/":
                while self.i < len(self.src) and self.peek() != "\n":
                    self.advance()
                continue

            # Comment khối (cho phép lồng nhau - kiểu Rust)
            if c == "/" and self.peek(1) == "*":
                self.read_block_comment()
                continue

            line, col = self.line, self.col

            # Định danh / từ khóa
            if c.isalpha() or c == "_":
                s = self.read_ident()
                kind = "kw" if s in KEYWORDS else "id"
                self.add(kind, s, line, col)
                continue

            # Số
            if c.isdigit():
                self.read_number(line, col)
                continue

            # Chuỗi
            if c == '"':
                self.read_string(line, col)
                continue

            # Ký tự
            if c == "'":
                self.read_char(line, col)
                continue

            # Toán tử 3 ký tự
            three = self.src[self.i:self.i + 3]
            if three in THREE_OPS:
                self.advance(); self.advance(); self.advance()
                self.add("op", three, line, col)
                continue

            # Toán tử 2 ký tự
            two = self.src[self.i:self.i + 2]
            if two in MULTI_OPS:
                self.advance(); self.advance()
                self.add("op", two, line, col)
                continue

            # Toán tử đơn
            if c in SINGLE_OPS:
                self.advance()
                self.add("op", c, line, col)
                continue

            self.error(f"ký tự không hợp lệ: {c!r}")

        self._auto_semi()
        self.add("eof", "", self.line, self.col)
        return self.tokens

    def read_block_comment(self):
        self.advance(); self.advance()  # /*
        level = 1
        while self.i < len(self.src) and level > 0:
            if self.peek() == "/" and self.peek(1) == "*":
                self.advance(); self.advance(); level += 1
            elif self.peek() == "*" and self.peek(1) == "/":
                self.advance(); self.advance(); level -= 1
            else:
                self.advance()
        if level > 0:
            self.error("comment khối /* không được đóng")

    def read_ident(self):
        start = self.i
        while self.i < len(self.src) and (self.peek().isalnum() or self.peek() == "_"):
            self.advance()
        return self.src[start:self.i]

    def read_number(self, line, col):
        start = self.i
        # Tiền tố cơ số: 0x (hex), 0b (nhị phân), 0o (bát phân)
        if self.peek() == "0" and self.peek(1) in "xXbBoO":
            base = self.peek(1).lower()
            self.advance(); self.advance()
            digits = {
                "x": "0123456789abcdefABCDEF_",
                "b": "01_",
                "o": "01234567_",
            }[base]
            while self.peek() and self.peek() in digits:
                self.advance()
            raw = self.src[start:self.i].replace("_", "")
            # Chuẩn hoá về thập phân để C hiểu (0b không chuẩn C)
            val = int(raw, 0) if base != "b" else int(raw[2:], 2)
            self.add("int", str(val), line, col)
            return

        is_float = False
        while self.peek().isdigit() or self.peek() == "_":
            self.advance()
        if self.peek() == "." and self.peek(1).isdigit():
            is_float = True
            self.advance()
            while self.peek().isdigit() or self.peek() == "_":
                self.advance()
        if self.peek() in "eE":
            is_float = True
            self.advance()
            if self.peek() in "+-":
                self.advance()
            while self.peek().isdigit():
                self.advance()
        text = self.src[start:self.i].replace("_", "")
        self.add("float" if is_float else "int", text, line, col)

    def read_string(self, line, col):
        self.advance()  # bỏ "
        buf = []
        while self.i < len(self.src) and self.peek() != '"':
            c = self.advance()
            if c == "\\":
                buf.append(self.read_escape())
            else:
                buf.append(c)
        if self.i >= len(self.src):
            self.error("chuỗi không được đóng")
        self.advance()  # bỏ "
        self.add("str", "".join(buf), line, col)

    def read_char(self, line, col):
        self.advance()  # bỏ '
        if self.peek() == "\\":
            self.advance()
            ch = self.read_escape()
        else:
            ch = self.advance()
        if self.peek() != "'":
            self.error("ký tự không được đóng")
        self.advance()
        self.add("char", ch, line, col)

    def read_escape(self):
        c = self.advance()
        if c == "x":  # \xNN hex
            h = ""
            while len(h) < 2 and self.peek() in "0123456789abcdefABCDEF":
                h += self.advance()
            return chr(int(h, 16)) if h else "x"
        return {
            "n": "\n", "t": "\t", "r": "\r", "0": "\0",
            "\\": "\\", '"': '"', "'": "'", "a": "\a", "b": "\b",
            "f": "\f", "v": "\v",
        }.get(c, c)
