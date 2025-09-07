# 中文字体设置指南

## 1. 系统要求

确保您的系统已安装以下中文字体：

### macOS系统
```bash
# 检查是否有中文字体
fc-list | grep -i chinese
fc-list | grep -i sim
```

### Linux系统 (Ubuntu/Debian)
```bash
# 安装中文字体包
sudo apt-get update
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
sudo apt-get install latex-cjk-chinese latex-cjk-chinese-arphic

# 或者安装更完整的字体包
sudo apt-get install fonts-noto-cjk
```

## 2. 字体文件检查

如果系统提示字体缺失，您可以：

### 方案1：使用系统字体
```latex
% 在main.tex中已配置的字体:
% gbsn = 宋体 (SimSun)
% gkai = 楷体 (KaiTi)
```

### 方案2：下载并安装字体
下载常用中文字体并放置在系统字体目录：

**macOS:**
- 路径: `/System/Library/Fonts/` 或 `~/Library/Fonts/`

**Linux:**
- 路径: `/usr/share/fonts/` 或 `~/.fonts/`

## 3. LaTeX中文包检查

确保已安装CJK相关包：

```bash
# 检查是否安装CJK包
kpsewhich CJKutf8.sty
kpsewhich CJK.sty

# 如果没有安装，通过包管理器安装
# Ubuntu/Debian:
sudo apt-get install texlive-lang-chinese

# macOS (使用MacTeX):
# CJK包通常已包含在MacTeX中
```

## 4. 编译方法

### 方法1：使用提供的脚本
```bash
chmod +x compile_with_chinese.sh
./compile_with_chinese.sh
```

### 方法2：手动编译
```bash
pdflatex -shell-escape main.tex
bibtex main
pdflatex -shell-escape main.tex
pdflatex -shell-escape main.tex
```

## 5. 常见问题解决

### 问题1：CJK包未找到
```bash
# 解决方案：安装完整的LaTeX中文支持
sudo apt-get install texlive-full
# 或
sudo apt-get install texlive-lang-chinese texlive-fonts-recommended
```

### 问题2：字体未找到
如果编译时提示字体错误，修改main.tex中的字体设置：

```latex
% 替换为系统可用的字体
\AtBeginDocument{\begin{CJK}{UTF8}{min}}  % 使用min字体
% 或
\AtBeginDocument{\begin{CJK}{UTF8}{song}} % 使用song字体
```

### 问题3：编译速度慢
中文支持会增加编译时间，这是正常现象。

## 6. 测试字体

编译成功后，PDF中的中文应该能正确显示。如果仍有问题，请检查：

1. 系统是否安装了中文字体
2. LaTeX是否安装了CJK包
3. 文件编码是否为UTF-8

## 7. 字体命令使用

在LaTeX文档中使用中文：

```latex
% 直接输入中文（推荐）
这是中文文本

% 使用字体命令
\heiti{这是黑体文本}
\songti{这是宋体文本}

% 加粗中文
\zhbold{加粗的中文}
```
