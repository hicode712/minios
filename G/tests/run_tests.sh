#!/usr/bin/env bash
# Bộ test tự động cho ngôn ngữ G.
# Biên dịch & chạy từng ví dụ, so sánh stdout với tests/expected/<tên>.txt
# Dùng:  ./tests/run_tests.sh            (chạy test)
#        ./tests/run_tests.sh --bless    (cập nhật kết quả mong đợi)

set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GC="$ROOT/gc"
EXPECTED="$ROOT/tests/expected"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$EXPECTED"

GREEN='\033[32m'; RED='\033[1;31m'; YEL='\033[33m'; RST='\033[0m'
pass=0; fail=0; bless=0
[ "${1:-}" = "--bless" ] && bless=1

run_one() {
    local src="$1"
    local name; name="$(basename "$src" .g)"
    local bin="$TMP/$name"
    local got="$TMP/$name.out"
    local exp="$EXPECTED/$name.txt"

    if ! "$GC" "$src" -o "$bin" >"$TMP/$name.cc" 2>&1; then
        echo -e "${RED}BIÊN DỊCH LỖI${RST}  $name"
        cat "$TMP/$name.cc"
        fail=$((fail+1)); return
    fi
    "$bin" >"$got" 2>&1

    if [ "$bless" = "1" ]; then
        cp "$got" "$exp"
        echo -e "${YEL}BLESS${RST}        $name"
        return
    fi
    if [ ! -f "$exp" ]; then
        echo -e "${YEL}THIẾU KQ${RST}     $name (chạy --bless để tạo)"
        fail=$((fail+1)); return
    fi
    if diff -q "$exp" "$got" >/dev/null; then
        echo -e "${GREEN}PASS${RST}         $name"
        pass=$((pass+1))
    else
        echo -e "${RED}FAIL${RST}         $name"
        diff "$exp" "$got" | head -20
        fail=$((fail+1))
    fi
}

echo "=== Bộ test ngôn ngữ G ==="
for src in "$ROOT"/examples/*.g "$ROOT"/tests/cases/*.g; do
    [ -e "$src" ] || continue
    run_one "$src"
done

echo "-------------------------"
if [ "$bless" = "1" ]; then
    echo "Đã cập nhật kết quả mong đợi."
else
    echo -e "Kết quả: ${GREEN}$pass pass${RST}, ${RED}$fail fail${RST}"
fi
[ "$fail" -eq 0 ]
