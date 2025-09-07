#!/bin/bash

echo "🚀 正在彻底修复LaTeX文件中的标点符号高亮问题..."

# 确保在正确目录
if [ ! -f "main.tex" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 备份当前设置
if [ -f ".vscode/settings.json" ]; then
    cp .vscode/settings.json .vscode/settings.json.backup
    echo "✅ 已备份现有设置到 settings.json.backup"
fi

# 创建彻底禁用所有检查的配置
cat > .vscode/settings_no_checks.json << 'EOF'
{
    "latex-workshop.latex.tools": [
        {
            "name": "pdflatex",
            "command": "pdflatex",
            "args": [
                "-output-directory=.output",
                "-synctex=1",
                "-interaction=nonstopmode",
                "%DOC%"
            ]
        },
        {
            "name": "bibtex",
            "command": "bibtex",
            "args": [
                ".output/%DOCFILE%"
            ]
        }
    ],
    "latex-workshop.latex.recipes": [
        {
            "name": "pdflatex -> bibtex -> pdflatex*2",
            "tools": [
                "pdflatex",
                "bibtex",
                "pdflatex",
                "pdflatex"
            ]
        }
    ],
    "latex-workshop.latex.outDir": ".output",
    "latex-workshop.latex.autoBuild.run": "never",
    "latex-workshop.latex.autoClean.run": "onBuilt",
    
    // 编辑器基本设置
    "editor.wordWrap": "on",
    "editor.wordWrapColumn": 80,
    "editor.rulers": [80, 120],
    
    // 彻底禁用所有LaTeX文件的检查和标记
    "[latex]": {
        "editor.wordWrap": "on",
        "editor.wordWrapColumn": 80,
        "editor.rulers": [80, 120],
        "editor.lineNumbers": "on",
        "editor.renderWhitespace": "boundary",
        "cSpell.enabled": false,
        "ltex.enabled": false,
        "editor.quickSuggestions": false,
        "editor.suggest.showWords": false,
        "editor.suggest.showSnippets": false,
        "problems.decorations.enabled": false,
        "editor.renderValidationDecorations": "off",
        "editor.wordBasedSuggestions": false,
        "editor.parameterHints.enabled": false,
        "editor.hover.enabled": false,
        "editor.lightbulb.enabled": false,
        "editor.semanticHighlighting.enabled": false,
        "editor.occurrencesHighlight": false,
        "editor.selectionHighlight": false,
        "editor.wordHighlight": false,
        "editor.colorDecorators": false
    },
    "[tex]": {
        "editor.wordWrap": "on",
        "editor.wordWrapColumn": 80,
        "editor.rulers": [80, 120],
        "editor.lineNumbers": "on",
        "editor.renderWhitespace": "boundary",
        "cSpell.enabled": false,
        "ltex.enabled": false,
        "editor.quickSuggestions": false,
        "editor.suggest.showWords": false,
        "editor.suggest.showSnippets": false,
        "problems.decorations.enabled": false,
        "editor.renderValidationDecorations": "off",
        "editor.wordBasedSuggestions": false,
        "editor.parameterHints.enabled": false,
        "editor.hover.enabled": false,
        "editor.lightbulb.enabled": false,
        "editor.semanticHighlighting.enabled": false,
        "editor.occurrencesHighlight": false,
        "editor.selectionHighlight": false,
        "editor.wordHighlight": false,
        "editor.colorDecorators": false
    },
    
    // 全局禁用所有可能的检查器
    "ltex.enabled": false,
    "ltex.checkFrequency": "manual",
    "latex-workshop.linting.enabled": false,
    "latex-workshop.intellisense.enabled": false,
    "latex-workshop.intellisense.triggers.latex": [],
    "problems.decorations.enabled": false,
    "editor.renderValidationDecorations": "off",
    "cSpell.enabled": false,
    "cSpell.autoFormatConfigFile": false,
    "cSpell.showStatus": false,
    "cSpell.showCommandsInEditorContextMenu": false,
    "grammarly.selectors": [],
    "languageToolLinter.enabled": false,
    "spellright.statusBarIndicator": false,
    "spellright.enabled": false,
    
    // 禁用所有装饰和高亮
    "editor.semanticHighlighting.enabled": false,
    "editor.occurrencesHighlight": false,
    "editor.selectionHighlight": false,
    "editor.wordHighlight": false,
    "editor.colorDecorators": false,
    "workbench.colorCustomizations": {
        "editorError.foreground": "#00000000",
        "editorWarning.foreground": "#00000000",
        "editorInfo.foreground": "#00000000",
        "editorHint.foreground": "#00000000"
    },
    "editor.tokenColorCustomizations": {
        "textMateRules": [
            {
                "scope": "invalid",
                "settings": {
                    "foreground": "",
                    "fontStyle": ""
                }
            }
        ]
    }
}
EOF

echo "📝 选择要应用的配置："
echo "1. 应用彻底禁用检查的配置（推荐）"
echo "2. 保持当前配置但重新加载"
echo "3. 恢复备份配置"

read -p "请选择 (1-3): " choice

case $choice in
    1)
        cp .vscode/settings_no_checks.json .vscode/settings.json
        echo "✅ 已应用彻底禁用检查的配置"
        ;;
    2)
        echo "✅ 保持当前配置"
        ;;
    3)
        if [ -f ".vscode/settings.json.backup" ]; then
            cp .vscode/settings.json.backup .vscode/settings.json
            echo "✅ 已恢复备份配置"
        else
            echo "❌ 未找到备份配置"
        fi
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🔄 现在请重新加载编辑器窗口："
echo "   方法1: 按 Cmd+Shift+P，输入 'Reload Window'"
echo "   方法2: 关闭并重新打开项目"
echo "   方法3: 重启编辑器应用程序"

echo ""
echo "🎯 如果仍有高亮问题，请尝试："
echo "   1. 禁用相关扩展（如LTeX、Grammarly等）"
echo "   2. 在命令面板中运行 'Developer: Reload With Extensions Disabled'"
echo "   3. 检查是否有其他语法检查扩展在运行"

echo ""
echo "✨ 配置完成！您的LaTeX文件现在应该没有任何标记和高亮了。"
