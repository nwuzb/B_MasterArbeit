#!/bin/bash

echo "检查中文字体支持情况..."

# 检查CJK包
echo "检查CJK包..."
if kpsewhich CJKutf8.sty > /dev/null 2>&1; then
    echo "✅ CJKutf8.sty 已安装"
else
    echo "❌ CJKutf8.sty 未安装"
fi

# 检查数学包
echo "检查数学包..."
if kpsewhich amsmath.sty > /dev/null 2>&1; then
    echo "✅ amsmath.sty 已安装"
else
    echo "❌ amsmath.sty 未安装"
fi

# 检查字体
echo "检查CJK字体文件..."
cjk_fonts=("c70gbsn.fd" "c70gkai.fd")
for font_file in "${cjk_fonts[@]}"; do
    if kpsewhich "$font_file" > /dev/null 2>&1; then
        echo "✅ $font_file 已安装"
    else
        echo "⚠️ $font_file 未找到"
    fi
done

echo "检查完成!"
