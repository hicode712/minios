"""
G Language - Semantic Analyzer / Type Checker.
- Phân giải kiểu cho mọi biểu thức (gắn node.gtype).
- Kiểm tra: biến chưa khai báo, gán vào biến bất biến, sai số tham số,
  trường/method/kiểu không tồn tại.
- Phân giải lời gọi method (recv.method(...)).
"""

from . import ast_nodes as A
from . import types as T


class CheckError(Exception):
    def __init__(self, msg, line=0, col=0):
        super().__init__(msg)
        self.msg = msg
        self.line = line
        self.col = col


BUILTINS = {"print", "println", "eprint", "eprintln", "printf",
            "len", "assert", "panic", "min", "max", "abs",
            "g_alloc", "g_free", "g_realloc"}


def count_placeholders(fmt: str) -> int:
    """Đếm số placeholder {...} trong chuỗi định dạng (bỏ qua {{ và }})."""
    n = 0
    i = 0
    L = len(fmt)
    while i < L:
        c = fmt[i]
        if c == "{" and i + 1 < L and fmt[i + 1] == "{":
            i += 2; continue
        if c == "}" and i + 1 < L and fmt[i + 1] == "}":
            i += 2; continue
        if c == "{":
            j = fmt.find("}", i)
            if j != -1:
                n += 1
                i = j + 1
                continue
        i += 1
    return n


class Checker:
    def __init__(self, program: A.Program):
        self.prog = program
        self.structs = {}        # name -> {field: GType}
        self.struct_order = {}   # name -> [field names]
        self.enums = {}          # name -> {variant: value_int}
        self.enum_of_variant = {}  # variant -> enum name
        self.methods = {}        # struct -> {method: Function}
        self.funcs = {}          # name -> GType(func)
        self.globals = {}        # name -> (GType, mutable)
        self.scopes = []         # ngăn xếp scope cục bộ
        self.cur_ret = T.VOID

    # ---------- API ----------
    def check(self):
        self.collect_types()
        self.collect_signatures()
        for it in self.prog.items:
            if isinstance(it, A.Function) and it.body is not None:
                self.check_function(it)
            elif isinstance(it, A.Impl):
                for m in it.methods:
                    if m.body is not None:
                        self.check_function(m)
        return self.prog

    # ---------- thu thập khai báo ----------
    def collect_types(self):
        for it in self.prog.items:
            if isinstance(it, A.StructDef):
                self.structs[it.name] = {}
                self.struct_order[it.name] = []
        for it in self.prog.items:
            if isinstance(it, A.StructDef):
                for f in it.fields:
                    self.structs[it.name][f.name] = self.resolve(f.type)
                    self.struct_order[it.name].append(f.name)
            elif isinstance(it, A.EnumDef):
                table = {}
                nxt = 0
                for vname, vval in it.variants:
                    if vval is not None and isinstance(vval, A.IntLit):
                        nxt = int(vval.value, 0)
                    table[vname] = nxt
                    self.enum_of_variant[vname] = it.name
                    nxt += 1
                self.enums[it.name] = table

    def collect_signatures(self):
        for it in self.prog.items:
            if isinstance(it, A.Function):
                self.register_func(it)
            elif isinstance(it, A.Impl):
                self.methods.setdefault(it.struct, {})
                for m in it.methods:
                    self.methods[it.struct][m.name] = m
            elif isinstance(it, A.GlobalVar):
                gt = self.resolve(it.type) if it.type else (
                    self.infer(it.value) if it.value is not None else T.INT)
                self.globals[it.name] = (gt, it.mutable and not it.is_const)

    def register_func(self, fn: A.Function):
        params = tuple(self.resolve(p.type) for p in fn.params)
        ret = self.resolve(fn.ret)
        self.funcs[fn.name] = T.GType("func", params=params, ret=ret)

    # ---------- phân giải kiểu cú pháp -> GType ----------
    def resolve(self, ty: A.Type) -> T.GType:
        if ty is None:
            return T.UNKNOWN
        base = ty.name
        if base in T.PRIMITIVES:
            g = T.PRIMITIVES[base]
        elif base in self.structs:
            g = T.GType("struct", name=base)
        elif base in self.enums:
            g = T.GType("enum", name=base)
        else:
            # cho phép kiểu chưa biết (vd extern) thay vì lỗi cứng
            g = T.GType("struct", name=base)
        # mảng
        if ty.array is not None:
            g = T.array_of(g, ty.array)
        # con trỏ
        for _ in range(ty.ptr):
            g = T.ptr_of(g)
        return g

    # ---------- scope ----------
    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def declare(self, name, gt, mutable):
        self.scopes[-1][name] = (gt, mutable)

    def lookup(self, name):
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        if name in self.globals:
            return self.globals[name]
        return None

    # ---------- kiểm tra hàm ----------
    def check_function(self, fn: A.Function):
        self.push()
        for p in fn.params:
            self.declare(p.name, self.resolve(p.type), True)
        self.cur_ret = self.resolve(fn.ret)
        self.check_block(fn.body)
        self.pop()

    def check_block(self, body):
        self.push()
        for st in body:
            self.check_stmt(st)
        self.pop()

    def check_stmt(self, st):
        if isinstance(st, A.Let):
            val_t = self.infer(st.value) if st.value is not None else None
            gt = self.resolve(st.type) if st.type else (val_t or T.INT)
            st.resolved_type = gt
            self.declare(st.name, gt, st.mutable)
        elif isinstance(st, A.Return):
            if st.value is not None:
                self.infer(st.value)
        elif isinstance(st, A.If):
            self.infer(st.cond)
            self.check_block(st.then)
            if st.els is not None:
                self.check_block(st.els)
        elif isinstance(st, A.While):
            self.infer(st.cond)
            self.check_block(st.body)
        elif isinstance(st, A.Loop):
            self.check_block(st.body)
        elif isinstance(st, A.For):
            self.infer(st.start)
            self.infer(st.end)
            if st.step is not None:
                self.infer(st.step)
            self.push()
            self.declare(st.var, T.INT, True)
            for s in st.body:
                self.check_stmt(s)
            self.pop()
        elif isinstance(st, A.Match):
            self.infer(st.subject)
            for pats, body in st.arms:
                if pats:
                    for p in pats:
                        self.infer(p)
                self.check_block(body)
        elif isinstance(st, A.Defer):
            self.check_stmt(st.stmt)
        elif isinstance(st, A.Assign):
            self.check_assign(st)
        elif isinstance(st, A.ExprStmt):
            self.infer(st.expr)
        # Break/Continue/Asm: không cần gì

    def check_assign(self, st: A.Assign):
        self.infer(st.value)
        tgt = st.target
        self.infer(tgt)
        if isinstance(tgt, A.Ident):
            info = self.lookup(tgt.name)
            if info is None:
                raise CheckError(f"biến chưa khai báo: '{tgt.name}'", tgt.line, tgt.col)
            gt, mutable = info
            if not mutable:
                raise CheckError(
                    f"không thể gán cho '{tgt.name}' (bất biến — dùng 'let mut')",
                    st.line, st.col)

    # ---------- suy luận kiểu biểu thức ----------
    def infer(self, e) -> T.GType:
        t = self._infer(e)
        try:
            e.gtype = t
        except Exception:
            pass
        return t

    def _infer(self, e) -> T.GType:
        if isinstance(e, A.IntLit):
            return T.INT
        if isinstance(e, A.FloatLit):
            return T.F64
        if isinstance(e, A.StrLit):
            return T.STR
        if isinstance(e, A.CharLit):
            return T.CHAR
        if isinstance(e, A.BoolLit):
            return T.BOOL
        if isinstance(e, A.NullLit):
            return T.NULL
        if isinstance(e, A.Ident):
            return self.infer_ident(e)
        if isinstance(e, A.Binary):
            return self.infer_binary(e)
        if isinstance(e, A.Unary):
            return self.infer_unary(e)
        if isinstance(e, A.Ternary):
            self.infer(e.cond)
            a = self.infer(e.then)
            self.infer(e.els)
            return a
        if isinstance(e, A.Call):
            return self.infer_call(e)
        if isinstance(e, A.Index):
            return self.infer_index(e)
        if isinstance(e, A.FieldAccess):
            return self.infer_field(e)
        if isinstance(e, A.Cast):
            return self.resolve(e.type)
        if isinstance(e, A.SizeOf):
            return T.USIZE
        if isinstance(e, A.ArrayLit):
            elem = self.infer(e.elements[0]) if e.elements else T.INT
            for el in e.elements[1:]:
                self.infer(el)
            return T.array_of(elem, len(e.elements))
        if isinstance(e, A.StructLit):
            return self.infer_struct_lit(e)
        return T.UNKNOWN

    def infer_ident(self, e: A.Ident):
        info = self.lookup(e.name)
        if info is not None:
            return info[0]
        if e.name in self.enum_of_variant:
            return T.GType("enum", name=self.enum_of_variant[e.name])
        if e.name in self.funcs:
            return self.funcs[e.name]
        if e.name in BUILTINS:
            return T.UNKNOWN
        if e.name in T.PRIMITIVES or e.name in self.structs:
            return T.UNKNOWN  # tên kiểu dùng làm giá trị (vd trong g_alloc)
        raise CheckError(f"định danh chưa khai báo: '{e.name}'", e.line, e.col)

    def infer_binary(self, e: A.Binary):
        lt = self.infer(e.left)
        rt = self.infer(e.right)
        op = e.op
        if op in ("&&", "||"):
            return T.BOOL
        if op in ("==", "!=", "<", ">", "<=", ">="):
            return T.BOOL
        if op in ("<<", ">>", "&", "|", "^"):
            return lt if lt.kind == "int" else T.INT
        # số học
        if lt.is_pointerish() and rt.is_integer():
            return lt
        if rt.is_pointerish() and lt.is_integer():
            return rt
        if lt.is_numeric() and rt.is_numeric():
            return T.common_numeric(lt, rt)
        return lt if lt.kind != "unknown" else rt

    def infer_unary(self, e: A.Unary):
        ot = self.infer(e.operand)
        if e.op == "!":
            return T.BOOL
        if e.op == "&":
            return T.ptr_of(ot)
        if e.op == "*":
            if ot.kind == "ptr":
                return ot.elem
            if ot.kind == "str":
                return T.CHAR
            return T.UNKNOWN
        return ot  # - , ~

    def infer_index(self, e: A.Index):
        bt = self.infer(e.base)
        self.infer(e.index)
        if bt.kind in ("array", "ptr"):
            return bt.elem
        if bt.kind == "str":
            return T.CHAR
        return T.UNKNOWN

    def infer_field(self, e: A.FieldAccess):
        bt = self.infer(e.base)
        e.auto_deref = (bt.kind == "ptr")
        sname = None
        if bt.kind == "struct":
            sname = bt.name
        elif bt.kind == "ptr" and bt.elem and bt.elem.kind == "struct":
            sname = bt.elem.name
        if sname and sname in self.structs:
            if e.field in self.structs[sname]:
                return self.structs[sname][e.field]
            # có thể là method dùng như giá trị — để cho infer_call xử lý
            if sname in self.methods and e.field in self.methods[sname]:
                return T.UNKNOWN
            raise CheckError(
                f"struct '{sname}' không có trường '{e.field}'", e.line, e.col)
        return T.UNKNOWN

    def infer_struct_lit(self, e: A.StructLit):
        if e.name not in self.structs:
            raise CheckError(f"struct chưa định nghĩa: '{e.name}'", e.line, e.col)
        fields = self.structs[e.name]
        for fname, val in e.fields:
            self.infer(val)
            if fname not in fields:
                raise CheckError(
                    f"struct '{e.name}' không có trường '{fname}'", e.line, e.col)
        return T.GType("struct", name=e.name)

    def infer_call(self, e: A.Call):
        # ----- method call: recv.method(args) -----
        if isinstance(e.func, A.FieldAccess):
            recv = e.func.base
            mname = e.func.field
            bt = self.infer(recv)
            sname = bt.name if bt.kind == "struct" else (
                bt.elem.name if bt.kind == "ptr" and bt.elem and bt.elem.kind == "struct" else None)
            if sname and sname in self.methods and mname in self.methods[sname]:
                e.is_method = True
                e.recv = recv
                e.method = mname
                e.struct = sname
                e.recv_is_ptr = (bt.kind == "ptr")
                for a in e.args:
                    self.infer(a)
                m = self.methods[sname][mname]
                return self.resolve(m.ret)
            # không phải method -> coi như field là con trỏ hàm (hiếm)
        # ----- builtin -----
        if isinstance(e.func, A.Ident) and e.func.name in BUILTINS:
            return self.infer_builtin(e)
        # ----- hàm thường -----
        ft = self.infer(e.func)
        for a in e.args:
            self.infer(a)
        if isinstance(e.func, A.Ident) and e.func.name in self.funcs:
            fdef = self.funcs[e.func.name]
            # kiểm tra số tham số (bỏ qua nếu là extern variadic)
            if len(e.args) != len(fdef.params):
                raise CheckError(
                    f"hàm '{e.func.name}' cần {len(fdef.params)} tham số "
                    f"nhưng nhận {len(e.args)}", e.line, e.col)
            return fdef.ret
        if ft.kind == "func":
            return ft.ret
        return T.UNKNOWN

    def infer_builtin(self, e: A.Call):
        name = e.func.name
        if name == "g_alloc":
            # g_alloc(T, n): tham số đầu là TÊN KIỂU
            if e.args and isinstance(e.args[0], A.Ident):
                tn = e.args[0].name
                if tn in T.PRIMITIVES:
                    elem = T.PRIMITIVES[tn]
                elif tn in self.structs:
                    elem = T.GType("struct", name=tn)
                else:
                    elem = T.INT
                if len(e.args) > 1:
                    self.infer(e.args[1])
                return T.ptr_of(elem)
            return T.ptr_of(T.VOID)
        if name == "g_realloc":
            for a in e.args:
                self.infer(a)
            return self.infer(e.args[0]) if e.args else T.ptr_of(T.VOID)
        if name in ("min", "max"):
            a = self.infer(e.args[0]) if e.args else T.INT
            for x in e.args[1:]:
                self.infer(x)
            return a
        if name == "abs":
            return self.infer(e.args[0]) if e.args else T.INT
        if name == "len":
            if e.args:
                self.infer(e.args[0])
            return T.USIZE
        if name in ("print", "println", "eprint", "eprintln"):
            for a in e.args:
                self.infer(a)
            # kiểm tra số placeholder khớp số đối số
            if e.args and isinstance(e.args[0], A.StrLit):
                want = count_placeholders(e.args[0].value)
                got = len(e.args) - 1
                if want != got:
                    raise CheckError(
                        f"chuỗi định dạng có {want} placeholder nhưng nhận {got} đối số",
                        e.line, e.col)
            return T.VOID
        # printf/assert/panic/g_free và khác
        for a in e.args:
            self.infer(a)
        return T.VOID
