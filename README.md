# LaTeX 论文项目

这个项目包含了您的硕士论文的LaTeX源代码。

## 项目结构

```text
MasterArbeit/
├── main.tex              # 主文档
├── chapters/             # 章节文件
│   ├── 01_Introduction.tex
│   └── 02_motivation.tex
├── library/              # 参考文献
│   └── citations.bib
├── pictures/             # 图片文件
├── .output/              # 编译输出目录（辅助文件）
├── compile.sh            # 编译脚本
├── Makefile              # Make编译配置
├── .latexmkrc            # latexmk配置
└── README.md             # 本文件
```

## 编译方法

### 方法1：使用编译脚本（推荐）

```bash
./compile.sh
```

这个脚本会：

- 自动创建 `.output` 目录
- 将辅助文件输出到 `.output` 目录
- 运行完整的编译流程（pdflatex + bibtex + pdflatex + pdflatex）
- 将最终的PDF复制到主目录

### 方法2：使用Makefile

```bash
make
```

或者查看所有可用命令：

```bash
make help
```

### 方法3：使用latexmk

```bash
latexmk -pdf main.tex
```

## 输出目录配置

所有的LaTeX辅助文件（`.aux`, `.log`, `.bbl`, `.blg` 等）都会自动保存到 `.output/` 目录中，这样可以：

1. **保持主目录整洁** - 只有源代码文件在主目录
2. **便于版本控制** - 辅助文件被 `.gitignore` 忽略
3. **避免文件冲突** - 辅助文件集中管理
4. **自动清理空文件** - 编译完成后自动删除空文件，保持输出目录整洁

## 清理文件

### 清理辅助文件

```bash
make clean
```

### 清理所有文件（包括PDF）

```bash
make cleanall
```

## 注意事项

- 编译过程中产生的所有辅助文件都会保存在 `.output/` 目录中
- 最终的PDF文件会同时保存在主目录和 `.output/` 目录中
- 如果遇到编译错误，可以查看 `.output/main.log` 文件获取详细信息
- 确保 `library/citations.bib` 文件存在且包含正确的参考文献条目

## 故障排除

如果遇到编译问题：

1. 检查 `.output/main.log` 文件中的错误信息
2. 运行 `make clean` 清理所有辅助文件后重新编译
3. 确保所有引用的图片文件都在 `pictures/` 目录中
4. 检查参考文献文件 `library/citations.bib` 的格式是否正确.
