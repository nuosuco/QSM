# extract_stream.awk: stream.w → 形态A单行 (527360 逗号值, 行尾无逗号)
/^=== / { next }
/^META / { next }
/^C[0-9]+:/ {
    sub(/^C[0-9]+: */, "")
    sub(/,[ \t\r]*$/, "")     # 去本行尾逗号
    buf = buf $0 ","
    next
}
END {
    sub(/,$/, "", buf)        # 去最末尾逗号
    printf "%s\n", buf
}
