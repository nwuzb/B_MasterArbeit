#!/bin/bash

# LaTeX编译脚本 - 支持中文
# 使用pdfLaTeX编译包含中文内容的文档

echo "正在编译包含中文的LaTeX文档..."

# 设置编译环境
export TEXINPUTS=.:./library:

# 第一次编译
echo "第一次编译..."
pdflatex -shell-escape -interaction=nonstopmode main.tex

# 编译参考文献
echo "编译参考文献..."
bibtex main

# 第二次编译
echo "第二次编译..."
pdflatex -shell-escape -interaction=nonstopmode main.tex

# 第三次编译（确保交叉引用正确）
echo "第三次编译..."
pdflatex -shell-escape -interaction=nonstopmode main.tex

# 检查编译结果
if [ -f "main.pdf" ]; then
    echo "✅ 编译成功！生成了 main.pdf"
    echo "📊 文件大小: $(du -h main.pdf | cut -f1)"
else
    echo "❌ 编译失败，请检查错误信息"
    exit 1
fi

# 清理临时文件（可选）
echo "清理临时文件..."
rm -f *.aux *.log *.bbl *.blg *.toc *.out *.synctex.gz

echo "编译完成！"
