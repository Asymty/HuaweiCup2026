# Word 前置页

正式提交模式使用官网 Word 模板生成前置页：

```text
官方封面 + 摘要 + 关键词
        ↓
frontmatter.pdf
```

将 Word 导出的文件保存为：

```text
paper/Latex/frontmatter/frontmatter.pdf
```

要求：

- 封面不显示页码。
- 摘要页从页码 1 开始。
- 不改变官网 Word 模板的版式、字体、标识或页面尺寸。
- 每次修改摘要、关键词、论文题目或队伍信息后，都要重新导出。
- 如果摘要占 1 页，`BodyOnly.tex` 中 `\BodyStartPage` 设为 2。
- 如果摘要占 2 页，`BodyOnly.tex` 中 `\BodyStartPage` 设为 3。
- `frontmatter.pdf` 是导出产物，不进入 Git；官方 Word 模板和最终 PDF 由 Google Drive 管理。

本目录不提供伪造或空白的 `frontmatter.pdf`。
