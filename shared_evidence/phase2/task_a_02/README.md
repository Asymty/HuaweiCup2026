# TASK-A-02 最小审核证据

本包对应 `coordination/A_ALGORITHM_DESIGN.md` 的**方案规范审查**，不是候选算法运行记录。A-02 只定义两条可实现、可证伪的路线和未来小 pilot 预算；本任务生成候选 plan 数、调用官方 evaluator 次数、训练次数均为 **0**。不得把文档内的受控图数值或 B 的随机 stub pilot 写成新算法成绩。

## 文件与审核方法

- `review_matrix.json`：逐项定位 A-02 任务卡要求、来源、设计中的处理办法与尚未验证之处。
- `evidence_manifest.json`：任务来源提交、官方只读文件和 Phase 1 L2 来源 SHA-256、本文及审核矩阵 SHA-256、生成方法与 L3 状态。
- 主产物位于 `coordination/A_ALGORITHM_DESIGN.md`。它是本包的审核对象，未在 L2 复制一份，避免两个版本分叉。

审核者可先读 manifest 的 `source_files` 与 `l2_files`，核对设计文档第 1–8 节与 `review_matrix.json`。对 Git 管理的文本文件，SHA-256 计算前把 CRLF 规范成 LF，以便 Windows/Linux checkout 得到同值；对官方只读附件计算原始字节 SHA-256。manifest 不记录自己的哈希，也不预填尚未生成的 A-02 commit。

## 证据边界

- Q2 `800→400`、Q3 `1200→1124` 和 `705→705` 来自 C-01 的**受控图**；B-01 的八图 runtime/画像来自已有官方随机 stub，不属于 A-02 原型实验。
- 设计中的 32/64 Op、0.8 容量软保护、1.25 负载保护和 60 秒/20 分钟预算是预注册的候选参数，未做调参或正式验证。
- L3：`not_applicable`。A-02 没有大体量原始结果、Trace 或运行日志；所有审查材料均在 Git 的文档和本目录。
- 正式方案是否合法、哪条路线更优、Q2 spill 抵消和 Q3 正式图 L2 收益，均留待 B 实现、官方 evaluator 与 C 独立审计。
