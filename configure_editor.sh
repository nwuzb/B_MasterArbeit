#!/bin/bash

echo "🔧 配置编辑器中文支持..."

# 检查是否在正确的目录
if [ ! -f "main.tex" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 确保.vscode目录存在
mkdir -p .vscode

echo "✅ VSCode/Cursor配置文件已更新"
echo "📝 配置内容："
echo "   - 禁用LaTeX文件的拼写检查"
echo "   - 添加中文支持"
echo "   - 忽略中文标点符号"
echo "   - 添加技术术语词典"

echo ""
echo "🔄 请重新加载编辑器窗口以应用设置："
echo "   1. 按 Cmd+Shift+P (Mac) 或 Ctrl+Shift+P (Windows/Linux)"
echo "   2. 输入 'Reload Window' 并选择"
echo "   3. 或者关闭并重新打开项目"

echo ""
echo "🎯 推荐安装的扩展："
echo "   - LaTeX Workshop: LaTeX支持"
echo "   - Code Spell Checker: 拼写检查"
echo "   - Chinese (Simplified) Language Pack: 中文语言包"
echo "   - LTeX: 语法检查"

echo ""
echo "⚙️  如果仍然有标记问题，可以："
echo "   1. 右键点击标记的文本"
echo "   2. 选择 'Add to Dictionary' 或 'Ignore'"
echo "   3. 或者在设置中关闭特定的检查器"
