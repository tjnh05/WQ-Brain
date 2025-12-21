【新人科普】BRAIN 平台上的四类Alpha（RA, ATOM, PPAC, SA）
Followed by 83 people

MH33574
Expert consultant
7 months ago
在 WorldQuant BRAIN 平台上，根据表达式复杂度、字段来源以及检测机制的不同，BRAIN 平台将 Alpha 分为四类：Regular Alpha（RA）、ATOM Alpha、PPAC Alpha 和 Super Alpha（SA）。本文将为新人系统性介绍这四类 Alpha 的核心特征、检测规则及策略建议。

1. Regular Alpha（RA）——最基础也最严谨的 Alpha 类型
对于 Regular Consultant（非 IQC）来说，Regular Alpha（RA） 是最早接触、也是最常使用的一类 Alpha。

✅ 特点：
表达式内的操作符和数据字段数量只要不超过 64 个，就可以提交；

几乎没有其他限制，是最自由的表达方式；

需要通过 所有的 Alpha 检测标准。

🧪 关键检测机制：
IS Ladder Testing：查看 Alpha 在过去 10 年是否每年都有稳定 Sharpe，防止因子过拟合于局部时期。

Sub-Universe Testing：验证 Alpha 在不同Universe子集下的表现一致性。

Weight Concentration Testing：防止 Alpha 只在极少数股票上集中信号，影响实盘效果。

Product Correlation Testing：检测 Alpha 是否和已有产品的表现高度重合，避免“重复造轮子”。

 2. ATOM Alpha —— 来自单一数据集的“纯净信号”
ATOM Alpha 是自 2024 年开始引入的新类型，最初用于特定 Alpha 比赛, 后推广持续沿用。更多信息请见：

https://platform.worldquantbrain.com/learn/documentation/consultant-information/single-dataset-alphas

✅ 判定标准：
所有使用的数据字段必须来自同一个数据集；

常见的 group 字段如 industry、country 等是豁免字段，不计入数据集数量限制；

提交后页面上会出现“Single Dataset Alpha”标签。

🧪 特别检测机制：
放松了 IS Ladder Testing 要求；

仅要求通过最近两年的 2-Year Sharpe 检测。

💡 设计逻辑：同一数据集下的数据字段类型更统一，降低混信号风险，更利于 OS 稳定性提升，从而提升 VF（Value Factor）得分。

⚡ 3. PPAC Alpha ——轻量但高效的入门路径
PPAC（PowerPoolAlpha）Alpha 是更简单直接的信号，比RA少了“修饰的”sub expression。源自于2025年的PPAC比赛，寻求pool内alpha的低自相关。

✅ 提交条件（非常宽松）：
最多使用 3 个数据字段；

最多使用 8 个操作符（包含加减乘除等基础运算符）；

同样，常见的 group 字段如 industry、country 不计入字段/操作符数量。

25年11月更新，PPA alpha 需要是风险中性化中的一种（RAM, STATISTICAL, CROWDING, FAST, SLOW,SLOW_AND_FAST） 才可以提交
数量限制
新顾问前三个月对于PPA没有限制
三个月后，如果一个Alpha 符合 PPA + ATOM 或 PPA + REGULAR 或  PPA + ATOM + REGULAR 无限制
三个月后，如果一个alpha 仅有PPA，则一天只能提交1个，且一个月在一个region只能由10个quota
提交后会显示标签：“PowerPoolAlpha”。

🧪 简化检测机制：
只要求 Sharpe > 1；

通过 Sub-Universe 检测；

所在地区的 PPAC Pool（不含非PPAC）需满足：

自相关性低于 50%，或

表现领先于 10% 以上。

⚠️ 尽管检测标准大幅降低，但这对提交者的自我克制能力提出了更高要求。
提交数量上升后，要特别注意 分散性与质量平衡，建议早期尽量使用不同模板和数据源，避免高自相关性。

🚀 4. Super Alpha（SA）——属于进阶顾问的 Alpha 策略组合
Super Alpha（SA） 是平台为有一定alpha积累的顾问推出的进阶功能。更多内容请见：

https://platform.worldquantbrain.com/learn/documentation/superalpha/superalpha-overview

✅ 启用条件：
顾问提交的 Alpha 总数达到 100 个；

可以从自己已提交的 Alpha 中组合构建；

高级顾问（Genius 等级）还可选择 其他人的 Alpha 作为基础组件。

💰 权益优势：
每天可单独提交 1 个 Super Alpha；

不计入每日 4 个常规 Alpha 限额；

可获得每日额外 $1~$60 的收益（与表现挂钩）；

Super Alpha 是 Alpha 组合优化领域，对自己本身的regular alpha如果很好，SA也会很好。建议VF高了以后提交，会有更高的收益加成，更容易拿到60USD

🎓 新手建议：优先提交 PPAC + ATOM Alpha
对于刚加入 BRAIN 的新顾问，推荐策略如下：

多做 PPAC Alpha：结构简单，利于练习表达式思维；

符合 ATOM 条件的 PPAC Alpha 优先提交（双标签）；

前期应着重积累高质量且分散的信号，为后期组合打下基础；

有经济学意义的模版永远是重要的，不要混信号！

希望这篇文章能帮助你在 BRAIN Alpha 的旅程中更快起步，逐步掌握从表达到组合的核心技能。🎯

也希望可以点赞评论!


关于PPAC的相关性，根据今天webinar会上的问答，补充以下两点：

1. 生产相关性尽管不作为提交标准，但依然会影响 Performance。

Q：No prod correlation, will it be still considered in combined  power pool performance or not?
A：yes

2. 自相关比生产相关有更高权重

Q：Regarding combined power pool performance, does the self-corr has more weight than prod-corr?
A：Yes, combined powerpool performance will be combo of just your alphas, hence diversifying using self-corr as a metric will be more helpful than prod-corr.

补充一个各类alpha的意义
各类Alpha的实际投资意义分析
Regular Alpha (RA)

意义：作为最严谨的Alpha，RA通过全面的历史回测和风险检测，适合构建稳健的量化策略基础。其多维度验证（如分域测试、权重集中度测试）能确保因子在不同市场环境下的普适性，降低过拟合风险，适合长期投资组合的核心配置。

ATOM Alpha

意义：单一数据集的要求减少了信号噪声，提升了因子的可解释性和实盘稳定性（OS）。这类Alpha更可能捕捉到特定数据源（如财务、另类数据）中的纯净信号，适合作为组合中的差异化补充，尤其在数据驱动的细分领域有潜力。

PPAC Alpha

意义：低复杂度和宽松检测使其成为快速验证投资假设的工具。PPAC的轻量化特性适合高频迭代和策略发散性测试，但需警惕自相关性风险。实际应用中，可作为“信号种子”与其他Alpha结合，或在市场快速变化时灵活调整仓位。

Super Alpha (SA)

意义：通过组合已有Alpha，SA实现了风险分散和收益增强，类似“因子合成”。其经济价值在于利用不同Alpha的低相关性优化夏普比率，适合构建多策略对冲组合。对机构投资者而言，SA是提升资金容量和稳定性的高阶工具。