"""
G Language - Code Generator: dịch AST (đã gắn kiểu) sang mã C.

Nơi 5 ngôn ngữ hội tụ:
  - Frontend Rust/Zig (let/mut, match, defer, comptime, loop)
  - Backend C/C++ (mọi thứ -> C -> mã máy)
  - ASM (inline assembly)
Tận dụng thông tin kiểu để: print tự chọn định dạng, auto-deref con trỏ, gọi method.
"""

from . import ast_nodes as A
from . import types as T


# Ánh xạ tên kiểu G -> C (cho khai báo theo cú pháp)
TYPE_MAP = {
    "int": "int", "i8": "int8_t", "i16": "int16_t", "i32": "int32_t", "i64": "int64_t",
    "u8": "uint8_t", "u16": "uint16_t", "u32": "uint32_t", "u64": "uint64_t",
    "usize": "size_t", "isize": "ptrdiff_t",
    "f32": "float", "f64": "double", "float": "float", "double": "double",
    "bool": "bool", "char": "char", "void": "void", "str": "const char*",
}


class CodegenError(Exception):
    pass


class Codegen:
    def __init__(self, program: A.Program):
        self.prog = program
        self.out = []
        self.indent = 0
        self.struct_names = set()
        self.enum_names = set()
        self.defers = []
        self._tmp = 0

    # ---------- tiện ích ----------
    def w(self, line=""):
        self.out.append("    " * self.indent + line)

    def tmp(self, base="_g"):
        self._tmp += 1
        return f"{base}{self._tmp}"

    def c_type(self, t: A.Type) -> str:
        base = TYPE_MAP.get(t.name, t.name)
        base += "*" * t.ptr
        return base

    def gtype_of(self, e) -> T.GType:
        return getattr(e, "gtype", T.UNKNOWN)

    def emit_var_decl(self, name, t: A.Type, init_c=None, const=False):
        cv = self.c_type(t)
        q = " const" if const else ""
        if t.array == "dyn":
            cv = cv + "*"   # []T -> con trỏ
            decl = f"{cv}{q} {name}"
        elif t.array is not None:
            decl = f"{cv}{q} {name}[{t.array}]"
        else:
            decl = f"{cv}{q} {name}"
        if init_c is not None:
            decl += f" = {init_c}"
        return decl + ";"

    # ---------- điểm vào ----------
    def generate(self) -> str:
        self.w("// === Sinh tự động bởi trình biên dịch G ===")
        self.w('#include "g_runtime.h"')
        self.w("")

        for it in self.prog.items:
            if isinstance(it, A.StructDef):
                self.struct_names.add(it.name)
            elif isinstance(it, A.EnumDef):
                self.enum_names.add(it.name)

        # 1) struct & enum
        for it in self.prog.items:
            if isinstance(it, A.StructDef):
                self.gen_struct(it)
            elif isinstance(it, A.EnumDef):
                self.gen_enum(it)

        # 2) biến toàn cục
        for it in self.prog.items:
            if isinstance(it, A.GlobalVar):
                self.gen_global(it)
        self.w("")

        # 3) nguyên mẫu hàm + method
        for it in self.prog.items:
            if isinstance(it, A.Function):
                self.w(self.fn_signature(it) + ";")
            elif isinstance(it, A.Impl):
                for m in it.methods:
                    self.w(self.fn_signature(m) + ";")
        self.w("")

        # 4) định nghĩa hàm + method
        for it in self.prog.items:
            if isinstance(it, A.Function):
                if it.body is not None:
                    self.gen_fn(it)
                    self.w("")
            elif isinstance(it, A.Impl):
                for m in it.methods:
                    if m.body is not None:
                        self.gen_fn(m)
                        self.w("")

        return "\n".join(self.out)

    # ---------- struct / enum / global ----------
    def gen_struct(self, s: A.StructDef):
        self.w(f"typedef struct {s.name} {{")
        self.indent += 1
        for f in s.fields:
            self.w(self.emit_var_decl(f.name, f.type))
        self.indent -= 1
        self.w(f"}} {s.name};")
        self.w("")

    def gen_enum(self, e: A.EnumDef):
        parts = []
        for vname, vval in e.variants:
            if vval is not None:
                parts.append(f"{vname} = {self.gen_expr(vval)}")
            else:
                parts.append(vname)
        self.w(f"typedef enum {{ {', '.join(parts)} }} {e.name};")
        self.w("")

    def gen_global(self, g: A.GlobalVar):
        init = self.gen_expr(g.value) if g.value is not None else None
        if g.type is not None:
            base = self.emit_var_decl(g.name, g.type, init, const=g.is_const)
            self.w("static " + base)
        else:
            q = "const " if g.is_const else ""
            self.w(f"static {q}__auto_type {g.name} = {init};")

    # ---------- hàm / method ----------
    def mangle(self, fn: A.Function) -> str:
        return f"{fn.recv}__{fn.name}" if fn.recv else fn.name

    def fn_signature(self, fn: A.Function) -> str:
        parts = []
        for p in fn.params:
            parts.append(f"{self.c_type(p.type)} {p.name}")
        params = ", ".join(parts) if parts else "void"
        ret = self.c_type(fn.ret)
        qual = ""
        if fn.is_comptime:
            qual = "static inline "
        elif fn.is_extern:
            qual = "extern "
        return f"{qual}{ret} {self.mangle(fn)}({params})"

    def gen_fn(self, fn: A.Function):
        self.w(self.fn_signature(fn) + " {")
        self.indent += 1
        saved = self.defers
        self.defers = []
        for st in fn.body:
            self.gen_stmt(st)
        self.flush_defers()
        self.defers = saved
        self.indent -= 1
        self.w("}")

    def flush_defers(self):
        for d in reversed(self.defers):
            self.gen_stmt(d, is_defer_flush=True)

    # ---------- câu lệnh ----------
    def gen_stmt(self, st, is_defer_flush=False):
        if isinstance(st, A.Let):
            self.gen_let(st)
        elif isinstance(st, A.Return):
            for d in reversed(self.defers):
                self.gen_stmt(d, is_defer_flush=True)
            if st.value is not None:
                self.w(f"return {self.gen_expr(st.value)};")
            else:
                self.w("return;")
        elif isinstance(st, A.If):
            self.gen_if(st)
        elif isinstance(st, A.While):
            self.w(f"while ({self.gen_expr(st.cond)}) {{")
            self.gen_body(st.body)
            self.w("}")
        elif isinstance(st, A.Loop):
            self.w("for (;;) {")
            self.gen_body(st.body)
            self.w("}")
        elif isinstance(st, A.For):
            self.gen_for(st)
        elif isinstance(st, A.Match):
            self.gen_match(st)
        elif isinstance(st, A.Defer):
            if is_defer_flush:
                self.gen_stmt(st.stmt, is_defer_flush=True)
            else:
                self.defers.append(st.stmt)
        elif isinstance(st, A.Asm):
            self.gen_asm(st)
        elif isinstance(st, A.Break):
            self.w("break;")
        elif isinstance(st, A.Continue):
            self.w("continue;")
        elif isinstance(st, A.Assign):
            self.w(f"{self.gen_expr(st.target)} {st.op} {self.gen_expr(st.value)};")
        elif isinstance(st, A.ExprStmt):
            self.w(f"{self.gen_expr(st.expr)};")
        else:
            raise CodegenError(f"câu lệnh chưa hỗ trợ: {st}")

    def gen_body(self, body):
        self.indent += 1
        for s in body:
            self.gen_stmt(s)
        self.indent -= 1

    def gen_let(self, st: A.Let):
        const = not st.mutable
        # mảng literal: int a[N] = {...}
        if isinstance(st.value, A.ArrayLit):
            gt = self.gtype_of(st.value)
            if st.type is not None:
                cv = self.c_type(A.Type(st.type.name, ptr=st.type.ptr))
                n = st.type.array if st.type.array not in (None, "dyn") else len(st.value.elements)
            else:
                cv = T.c_type(gt.elem) if gt.kind == "array" else "int"
                n = len(st.value.elements)
            init = "{ " + ", ".join(self.gen_expr(x) for x in st.value.elements) + " }"
            q = "const " if const else ""
            self.w(f"{q}{cv} {st.name}[{n}] = {init};")
            return

        init_c = self.gen_expr(st.value) if st.value is not None else None
        if st.type is not None:
            self.w(self.emit_var_decl(st.name, st.type, init_c, const=const))
        else:
            if init_c is None:
                self.w(f"int {st.name};")
            else:
                q = "const " if const else ""
                self.w(f"{q}__auto_type {st.name} = {init_c};")

    def gen_if(self, st: A.If):
        self.w(f"if ({self.gen_expr(st.cond)}) {{")
        self.gen_body(st.then)
        if st.els is not None:
            self.w("} else {")
            self.gen_body(st.els)
        self.w("}")

    def gen_for(self, st: A.For):
        start = self.gen_expr(st.start)
        end = self.gen_expr(st.end)
        v = st.var
        cmp = "<=" if st.inclusive else "<"
        step = f"{v} += {self.gen_expr(st.step)}" if st.step is not None else f"{v}++"
        self.w(f"for (long {v} = {start}; {v} {cmp} {end}; {step}) {{")
        self.gen_body(st.body)
        self.w("}")

    def gen_match(self, st: A.Match):
        subj_t = self.gtype_of(st.subject)
        is_str = subj_t.kind == "str" or (subj_t.kind == "ptr" and subj_t.elem and subj_t.elem.kind == "char")
        tmp = self.tmp("_gm")
        ctype = T.c_type(subj_t) if subj_t.kind != "unknown" else "__auto_type"
        if ctype == "__auto_type":
            self.w(f"{{ __auto_type {tmp} = {self.gen_expr(st.subject)};")
        else:
            self.w(f"{{ {ctype} {tmp} = {self.gen_expr(st.subject)};")
        self.indent += 1

        def cond_for(pats):
            tests = []
            for p in pats:
                pc = self.gen_expr(p)
                if is_str:
                    tests.append(f"strcmp({tmp}, {pc}) == 0")
                else:
                    tests.append(f"{tmp} == {pc}")
            return " || ".join(tests)

        first = True
        default_body = None
        for pats, body in st.arms:
            if pats is None:
                default_body = body
                continue
            kw = "if" if first else "else if"
            first = False
            self.w(f"{kw} ({cond_for(pats)}) {{")
            self.gen_body(body)
            self.w("}")
        if default_body is not None:
            self.w("else {" if not first else "{")
            self.gen_body(default_body)
            self.w("}")
        self.indent -= 1
        self.w("}")

    def gen_asm(self, st: A.Asm):
        lines = [l.strip() for l in st.code.split("\n") if l.strip()]
        joined = "\\n\\t".join(lines)
        vol = " __volatile__" if st.volatile else ""
        self.w(f'__asm__{vol}("{joined}");')

    # ---------- biểu thức ----------
    def gen_expr(self, e) -> str:
        if isinstance(e, A.IntLit):
            return e.value
        if isinstance(e, A.FloatLit):
            return e.value
        if isinstance(e, A.StrLit):
            return self.c_string(e.value)
        if isinstance(e, A.CharLit):
            return self.c_char(e.value)
        if isinstance(e, A.BoolLit):
            return "true" if e.value else "false"
        if isinstance(e, A.NullLit):
            return "NULL"
        if isinstance(e, A.Ident):
            return e.name
        if isinstance(e, A.Binary):
            return f"({self.gen_expr(e.left)} {e.op} {self.gen_expr(e.right)})"
        if isinstance(e, A.Unary):
            return f"({e.op}{self.gen_expr(e.operand)})"
        if isinstance(e, A.Ternary):
            return f"({self.gen_expr(e.cond)} ? {self.gen_expr(e.then)} : {self.gen_expr(e.els)})"
        if isinstance(e, A.Call):
            return self.gen_call(e)
        if isinstance(e, A.Index):
            return f"{self.gen_expr(e.base)}[{self.gen_expr(e.index)}]"
        if isinstance(e, A.FieldAccess):
            arrow = getattr(e, "auto_deref", False)
            sep = "->" if arrow else "."
            return f"{self.gen_expr(e.base)}{sep}{e.field}"
        if isinstance(e, A.Cast):
            return f"(({self.c_type(e.type)})({self.gen_expr(e.expr)}))"
        if isinstance(e, A.SizeOf):
            return f"sizeof({self.c_type(e.type)})"
        if isinstance(e, A.ArrayLit):
            return "{ " + ", ".join(self.gen_expr(x) for x in e.elements) + " }"
        if isinstance(e, A.StructLit):
            return self.gen_struct_lit(e)
        raise CodegenError(f"biểu thức chưa hỗ trợ: {e}")

    def gen_call(self, e: A.Call):
        # method call (đã phân giải trong checker)
        if getattr(e, "is_method", False):
            recv_c = self.gen_expr(e.recv)
            recv_ptr = recv_c if e.recv_is_ptr else f"&({recv_c})"
            args = [recv_ptr] + [self.gen_expr(a) for a in e.args]
            return f"{e.struct}__{e.method}({', '.join(args)})"
        # builtin
        if isinstance(e.func, A.Ident):
            name = e.func.name
            if name in ("print", "println", "eprint", "eprintln"):
                return self.gen_print(e, name)
            if name == "len":
                return self.gen_len(e)
            if name == "assert":
                return self.gen_assert(e)
            if name == "panic":
                msg = self.gen_expr(e.args[0]) if e.args else '"panic"'
                return f"g_panic({msg})"
            if name in ("min", "max"):
                a, b = self.gen_expr(e.args[0]), self.gen_expr(e.args[1])
                op = "<" if name == "min" else ">"
                return f"(({a}) {op} ({b}) ? ({a}) : ({b}))"
            if name == "abs":
                a = self.gen_expr(e.args[0])
                return f"(({a}) < 0 ? -({a}) : ({a}))"
            if name in ("g_alloc", "g_realloc"):
                args = ", ".join(self.gen_expr(a) for a in e.args)
                return f"{name}({args})"
        fn = self.gen_expr(e.func)
        args = ", ".join(self.gen_expr(a) for a in e.args)
        return f"{fn}({args})"

    def gen_len(self, e: A.Call):
        arg = e.args[0]
        c = self.gen_expr(arg)
        gt = self.gtype_of(arg)
        if gt.kind == "array":
            return f"(sizeof({c}) / sizeof(({c})[0]))"
        if gt.kind == "str":
            return f"strlen({c})"
        return f"(sizeof({c}) / sizeof(({c})[0]))"

    def gen_assert(self, e: A.Call):
        cond = self.gen_expr(e.args[0])
        if len(e.args) > 1:
            msg = self.gen_expr(e.args[1])
        else:
            msg = self.c_string(f"assertion failed: {cond}")
        return f"(({cond}) ? (void)0 : g_panic({msg}))"

    def gen_print(self, e: A.Call, name):
        stream = "stderr" if name.startswith("e") else "stdout"
        newline = name.endswith("ln")
        if not e.args:
            return f'fprintf({stream}, "{chr(92)}n")' if newline else f'fprintf({stream}, "")'
        first = e.args[0]
        if isinstance(first, A.StrLit):
            template = first.value
            value_args = e.args[1:]
        else:
            template = "{}"
            value_args = e.args
        fmt, c_args = self.build_format(template, value_args)
        if newline:
            fmt = fmt[:-1] + '\\n"'
        if c_args:
            return f"fprintf({stream}, {fmt}, {', '.join(c_args)})"
        return f"fprintf({stream}, {fmt})"

    SPEC_MAP = {
        "d": "%d", "ld": "%lld", "u": "%u", "lu": "%llu",
        "f": "%g", "lf": "%lf", "e": "%e",
        "s": "%s", "c": "%c", "x": "%x", "X": "%X",
        "o": "%o", "p": "%p", "b": "%s",
    }

    def build_format(self, raw, value_args):
        """Sinh chuỗi định dạng C + danh sách biểu thức C tương ứng.
        Placeholder rỗng {} => tự suy ra theo kiểu của tham số."""
        result = []
        c_args = []
        ai = 0
        i = 0
        n = len(raw)
        while i < n:
            ch = raw[i]
            if ch == "{" and i + 1 < n and raw[i + 1] == "{":
                result.append("{"); i += 2; continue
            if ch == "}" and i + 1 < n and raw[i + 1] == "}":
                result.append("}"); i += 2; continue
            if ch == "{":
                j = raw.find("}", i)
                if j == -1:
                    result.append("{"); i += 1; continue
                key = raw[i + 1:j]
                arg = value_args[ai] if ai < len(value_args) else None
                ai += 1
                if key == "" or key == "v":
                    gt = self.gtype_of(arg) if arg is not None else T.UNKNOWN
                    spec, is_bool = T.printf_spec(gt)
                    if is_bool and arg is not None:
                        c_args.append(f"(({self.gen_expr(arg)}) ? \"true\" : \"false\")")
                    elif arg is not None:
                        c_args.append(self.gen_expr(arg))
                    result.append(spec)
                else:
                    spec = self.SPEC_MAP.get(key, "%d")
                    if key == "b" and arg is not None:
                        c_args.append(f"(({self.gen_expr(arg)}) ? \"true\" : \"false\")")
                    elif arg is not None:
                        c_args.append(self.gen_expr(arg))
                    result.append(spec)
                i = j + 1
            elif ch == "%":
                result.append("%%"); i += 1
            else:
                result.append(ch); i += 1
        return self.c_string("".join(result)), c_args

    def gen_struct_lit(self, e: A.StructLit):
        parts = [f".{name} = {self.gen_expr(val)}" for name, val in e.fields]
        return f"(({e.name}){{ {', '.join(parts)} }})"

    # ---------- literal helpers ----------
    def c_string(self, s: str) -> str:
        out = ['"']
        for ch in s:
            out.append(self._esc(ch))
        out.append('"')
        return "".join(out)

    def _esc(self, ch):
        table = {"\n": "\\n", "\t": "\\t", "\r": "\\r", '"': '\\"',
                 "\\": "\\\\", "\0": "\\0", "\a": "\\a", "\b": "\\b",
                 "\f": "\\f", "\v": "\\v"}
        if ch in table:
            return table[ch]
        if ord(ch) < 32:
            return f"\\x{ord(ch):02x}"
        return ch

    def c_char(self, ch: str) -> str:
        m = {"\n": "\\n", "\t": "\\t", "\r": "\\r", "\0": "\\0",
             "'": "\\'", "\\": "\\\\"}
        return f"'{m.get(ch, ch)}'"
