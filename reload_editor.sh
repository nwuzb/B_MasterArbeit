#!/bin/bash

echo "🔄 重新加载编辑器配置..."

# 检查是否在Cursor/VSCode中
if command -v cursor &> /dev/null; then
    echo "📱 检测到Cursor编辑器"
    echo "请手动重新加载：Cmd+Shift+P -> 'Reload Window'"
elif command -v code &> /dev/null; then
    echo "📱 检测到VSCode编辑器"
    echo "请手动重新加载：Ctrl+Shift+P -> 'Reload Window'"
else
    echo "📱 未检测到编辑器命令"
fi

echo ""
echo "🛠️  已完成配置更新："
echo "   ✅ 禁用了所有拼写检查"
echo "   ✅ 禁用了所有语法检查"
echo "   ✅ 禁用了所有错误装饰"
echo "   ✅ 隐藏了所有标记颜色"
echo "   ✅ 禁用了语义高亮"

echo ""
echo "🎯 如果重新加载后仍有问题："
echo "   1. 运行: ./fix_highlighting.sh"
echo "   2. 选择选项1（彻底禁用配置）"
echo "   3. 重启整个编辑器应用程序"

echo ""
echo "💡 提示：如果您使用的是其他扩展（如Grammarly、LanguageTool等），"
echo "   也可能导致标记。可以在扩展面板中临时禁用它们。"
