#!/bin/bash

# GitHub上传脚本
# 使用方法: ./upload_to_github.sh YOUR_GITHUB_USERNAME REPOSITORY_NAME

if [ $# -ne 2 ]; then
    echo "使用方法: $0 <GitHub用户名> <仓库名>"
    echo "例如: $0 binzeng MasterArbeit"
    exit 1
fi

GITHUB_USERNAME=$1
REPOSITORY_NAME=$2

echo "准备上传到GitHub..."
echo "用户名: $GITHUB_USERNAME"
echo "仓库名: $REPOSITORY_NAME"

# 检查是否已经初始化Git
if [ ! -d ".git" ]; then
    echo "初始化Git仓库..."
    git init
    git add .
    git commit -m "Initial commit: LaTeX thesis project with output directory management"
fi

# 设置主分支名称
git branch -M main

# 添加远程仓库
echo "添加远程仓库..."
git remote add origin https://github.com/$GITHUB_USERNAME/$REPOSITORY_NAME.git

# 推送到GitHub
echo "推送到GitHub..."
git push -u origin main

echo "✅ 上传完成！"
echo "您的仓库地址: https://github.com/$GITHUB_USERNAME/$REPOSITORY_NAME"
echo ""
echo "后续更新命令:"
echo "  git add ."
echo "  git commit -m '您的提交信息'"
echo "  git push" 