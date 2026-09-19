# 数学建模论文写作 Skill

## 目标与边界

本 Skill 用于华为杯/中国研究生数学建模竞赛正文的撰写、修改与投稿前审查。它统一三个 Codex 的论证结构、证据标准和 LaTeX 表达，但不替代建模与实验：模型必须存在于实际方案或代码中，数值必须来自可追溯输出，引用必须能够核验。

参考论文只用于归纳结构和写法。禁止复制原句、替换同义词式改写或沿用参考论文的题目答案。

## 使用前必须读取

1. 题目与当前章节；
2. 对应代码、配置、数据说明和正式结果；
3. 本 README 及章节对应指南；
4. `paper/Latex/WRITING_WORKFLOW.md` 和当前符号、label、citation 体系。

## 推荐读取顺序

- 写模型：README → `problem_analysis.md` → `assumptions_notation.md` → `model_writing.md` → `language_style.md`
- 写实验：README → `experiment_results.md` → `figures_tables.md` → `language_style.md`
- 写摘要：README → `abstract.md` → `conclusion.md` → `final_review.md`
- 全文审查：README → `final_review.md`

## 三个 Codex 的协作方式

- 各自只改责任范围内的独立 `sections/**` 文件，不同时编辑主入口。
- 写作前声明依据的代码、结果文件、指标和符号；缺失时列出缺口，不补造内容。
- 同一结论只保留一个权威表述位置，其他章节引用或压缩，不复制出多个版本。
- 修改后运行项目 LaTeX Gate；引用、label、数值和图表由整合负责人交叉核验。

## 最低证据标准

每个重要判断应至少关联一种证据：数学推导、程序输出、表格数值、图中趋势、对比实验、约束可行性或文献依据。不能回答“证据来自哪里”的句子，不应写成正式结论。
