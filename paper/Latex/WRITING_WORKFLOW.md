# LaTeX 多 Codex 写作流程

1. 三个 Codex 不直接同时修改 `MathModel.tex`。
2. 各 Codex 优先修改自己负责的独立 `sections/` 文件。
3. `MathModel.tex` 主文件只由论文整合负责人修改。
4. 避免多个 Codex 同时修改 `ref.bib`；需要集中合并引用变更。
5. 新增引用前先检查 citation key，禁止重复 key 或擅自修改已有 key。
6. 新增图片放入 `figures/q1/`、`q2/`、`q3/`、`q4/` 或 `common/` 对应目录。
7. 每次修改后必须使用 XeLaTeX 编译并检查生成的 PDF。
8. PR 合并前检查 label 是否重复，且所有 `\ref`、`\cite` 均可解析。
9. 禁止通过复制粘贴制造重复章节；新增内容应写入唯一的责任文件。
10. 论文中的数值、图表和结论必须与代码输出及正式实验结果一致。
11. 新增或大幅修改正文前，必须先读取 `skill/paper_writing/README.md` 及当前任务对应指南：模型写作读取 `skill/paper_writing/model_writing.md`，实验结果读取 `skill/paper_writing/experiment_results.md`，图表读取 `skill/paper_writing/figures_tables.md`，摘要读取 `skill/paper_writing/abstract.md`，全文审查读取 `skill/paper_writing/final_review.md`。

## 建议边界

- Codex A：假设、符号说明、问题一/二模型。
- Codex B：问题重述、问题一/二实验及数据相关段落。
- Codex C：验证、敏感性、问题三/四、结论、优缺点及图表结果核查。

以上是协作边界建议，不构成论文正文，也可由整合负责人按赛题调整。

新增 figure、table 或 equation 时必须使用全局唯一 label，推荐格式为 `fig:q1_xxx`、`tab:q1_xxx`、`eq:q1_xxx`。新增 bibitem/citation key 也必须全局唯一。提交 PR 前必须运行 `build.ps1`，不得忽略 duplicate label 警告。
## 最终论文模式

正式模式采用“官方 Word 前置页 + LaTeX 正文 + PDF 合并”：

1. 使用官网 Word 模板填写封面、摘要和关键词，导出为 `frontmatter/frontmatter.pdf`。
2. 三个 Codex 主要编辑各自负责的 `sections/**` 文件。
3. 运行 `build_body.ps1` 生成 `BodyOnly.pdf`。
4. 根据 Word 摘要页数，在 `BodyOnly.tex` 中只调整 `\BodyStartPage`。
5. 运行 `merge.ps1` 生成正式提交候选 `FinalPaper.pdf`。

备用模式为 Full LaTeX：运行 `build.ps1`，由 `MathModel.tex` 生成完整 `MathModel.pdf`。

一般不直接修改 `MathModel.tex`、`BodyOnly.tex` 或 `body_content.tex`；这三个入口由论文整合负责人维护。`frontmatter.pdf`、`BodyOnly.pdf` 与 `FinalPaper.pdf` 均为产物，不进入 Git。前置页或正文每次变化后，都必须重新编译并检查最终合并 PDF。
