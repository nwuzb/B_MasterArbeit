# PDF反向搜索设置指南

## 什么是反向搜索？
反向搜索允许您在PDF中点击引用数字、公式或任何文本，自动跳转到LaTeX源代码的对应位置，方便编辑和修改。

## 已启用的功能
✅ 编译脚本已经启用了SyncTeX支持（`-synctex=1`参数）
✅ 编译时会生成`main.synctex.gz`文件
✅ 清理临时文件时会保留SyncTeX文件

## 不同PDF查看器的设置方法

### 1. Skim (macOS推荐)
**最佳选择 - 专为LaTeX设计**

1. 下载安装：https://skim-app.sourceforge.io/
2. 打开Skim → 偏好设置 → 同步
3. 设置：
   - PDF-TeX Sync support: ✅ 勾选
   - Preset: "Custom"
   - Command: `/usr/local/bin/code` (如果使用VS Code)
   - Arguments: `-g "%file:%line"`

**使用方法：**
- Cmd + Shift + 点击PDF中的任意位置 → 跳转到源码
- 在源码中 Cmd + Shift + 点击 → 跳转到PDF

### 2. VS Code + LaTeX Workshop
**如果您使用VS Code编辑LaTeX**

1. 安装扩展：LaTeX Workshop
2. 设置中搜索"latex-workshop.synctex"
3. 确保启用：
   ```json
   "latex-workshop.synctex.afterBuild.enabled": true
   ```

**使用方法：**
- 在PDF中 Ctrl+点击 → 跳转到源码
- 在源码中 Ctrl+Alt+J → 跳转到PDF

### 3. Preview (macOS自带)
**基本功能，但支持有限**

Preview对SyncTeX的支持较弱，建议使用Skim或专业LaTeX编辑器。

### 4. Zathura (Linux用户)
```bash
# 安装
sudo apt-get install zathura

# 配置文件 ~/.config/zathura/zathurarc
set synctex true
set synctex-editor-command "code -g %{input}:%{line}"
```

### 5. SumatraPDF (Windows用户)
1. 下载：https://www.sumatrapdfreader.org/
2. 设置 → 选项
3. 设置反向搜索命令行：
   ```
   "C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe" -g "%f:%l"
   ```

## 测试反向搜索

1. 使用修改后的编译脚本编译文档：
   ```bash
   ./compile_final.sh
   ```

2. 确认生成了`main.synctex.gz`文件

3. 在PDF查看器中测试：
   - 点击引用数字（如[1], [2]）
   - 点击公式编号
   - 点击图表标题
   - 点击任意文本段落

## 故障排除

### 问题1：SyncTeX文件未生成
- 检查编译命令是否包含`-synctex=1`
- 确保没有编译错误
- 检查文件权限

### 问题2：点击PDF无反应
- 确认PDF查看器支持SyncTeX
- 检查编辑器路径设置是否正确
- 尝试使用Cmd+Shift+点击（macOS）或Ctrl+点击

### 问题3：跳转位置不准确
- 重新完整编译文档（删除所有临时文件后重新编译）
- 确保源文件没有被移动或重命名

## 推荐工作流程

1. **编辑器**: VS Code + LaTeX Workshop 扩展
2. **PDF查看器**: Skim (macOS) 或 SumatraPDF (Windows)
3. **编译**: 使用提供的`compile_final.sh`脚本
4. **工作流程**:
   - 在VS Code中编辑LaTeX
   - 运行编译脚本
   - 在Skim中查看PDF
   - 点击PDF中的内容直接跳转到VS Code中的对应位置

这样您就可以实现高效的"PDF点击 → 源码定位 → 快速修改"的工作流程！
