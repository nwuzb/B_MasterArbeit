#!/bin/bash

# 最终版LaTeX编译脚本 - 中文支持优化版
echo "🚀 开始编译LaTeX文档（中文支持版）..."

# 清理之前的编译文件
echo "🧹 清理旧文件..."
rm -f *.aux *.log *.bbl *.blg *.toc *.out *.synctex.gz *.fls *.fdb_latexmk

# 设置编译环境
export TEXINPUTS=.:./library:

# 第一次编译
echo "📝 第一次编译（生成目录和引用）..."
pdflatex -shell-escape -interaction=nonstopmode -halt-on-error main.tex

if [ $? -ne 0 ]; then
    echo "❌ 第一次编译失败，请检查LaTeX语法"
    exit 1
fi

# 编译参考文献
echo "📚 编译参考文献..."
bibtex main
if [ $? -ne 0 ]; then
    echo "⚠️ 参考文献编译有警告，但继续进行..."
fi

# 第二次编译
echo "📝 第二次编译（处理参考文献）..."
pdflatex -shell-escape -interaction=nonstopmode main.tex

# 第三次编译（确保所有引用正确）
echo "📝 第三次编译（完善交叉引用）..."
pdflatex -shell-escape -interaction=nonstopmode main.tex

# 检查最终结果
if [ -f "main.pdf" ]; then
    echo "✅ 编译成功完成！"
    echo "📄 生成文件: main.pdf"
    echo "📊 文件大小: $(du -h main.pdf | cut -f1)"
    echo "📄 页数: $(pdfinfo main.pdf 2>/dev/null | grep Pages | awk '{print $2}' || echo '未知')"
    
    # 检查中文字体是否正确嵌入
    echo "🔤 检查字体嵌入情况..."
    if pdffonts main.pdf > /dev/null 2>&1; then
        echo "✅ 字体信息正常"
        chinese_fonts=$(pdffonts main.pdf | grep -i "gb\|kai\|song\|hei" | wc -l)
        if [ $chinese_fonts -gt 0 ]; then
            echo "✅ 检测到 $chinese_fonts 个中文字体"
        else
            echo "⚠️ 未检测到中文字体，但这可能是正常的"
        fi
    else
        echo "⚠️ 无法检查字体信息，但编译成功"
    fi
    
else
    echo "❌ 编译失败，main.pdf未生成"
    echo "📋 请检查错误日志："
    if [ -f "main.log" ]; then
        echo "最后几行错误信息："
        tail -20 main.log
    fi
    exit 1
fi

# 可选：清理临时文件
read -p "🗑️  是否清理临时文件？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 清理临时文件..."
    rm -f *.aux *.log *.bbl *.blg *.toc *.out *.synctex.gz *.fls *.fdb_latexmk
    echo "✅ 清理完成"
else
    echo "📁 保留临时文件以便调试"
fi

echo "🎉 LaTeX编译流程完成！"
