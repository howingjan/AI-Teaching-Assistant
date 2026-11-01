# 新旧课件覆盖报告：10_decision_tree.pdf / 10 讲义.pdf

> 本报告为 AI 辅助审核结果，不构成完全覆盖证明；请逐项检查原文证据。

## T001 决策树分类的基本概念 — 已覆盖

决策树通过一系列问题将观测映射到目标值，可视为if/else语句的层次结构；非叶节点标注属性并对应属性值测试，叶节点标注类别；模型直观可解释，简单树的集成效果也很好。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.95

**最新学校课件证据**
- 10_decision_tree.pdf · 第 5 页 · `10_decision_tree_d8e30e66_4_0`：Decision tree classification
– Maps observations to a target value by
asking a series of questions
– Can be viewed as hierarchy of if/else
statements. – Each non-leaf node is labelled with an
attribute and corresponds to a test for
the values of an attribute
– Each leaf node is labelled with a class
– Resulting model is intuitive and
interpretable. – Ensembles of simple trees can do very
https://d

**往期补习课件证据**
- 10 讲义.pdf · 第 2 页 · `10_讲义_d344dc1e_1_0`：1. 决策树
决策树（Decision Tree）是一种常用的机器学习算法，广泛应用于分类和回归问题。 决策树通过树状结构来表示决策过程，每个内部节点代表一个特征或属性的测试，每个分支代表测试的结
果，每个叶节点代表一个类别或值。 1. 1 参数模型与非参数模型
参数模型 (Parametric Models) 和 非参数模型 (Non-Parametric Models) 的核心区别在于：模型在训练前是
否预先假设了固定的函数形式和参数数量。 1. 1. 1 参数模型 (Parametric Models)
参数模型在训练开始前就预先定义了模型的结构（函数形式）和参数的数量。 无论你的数据集有多大，模
型的参数数量大致保持不变。 线性回归 (Linear Regression):
l 假设：数据符合直线或超平面关系。 l 参数：权重 θ 和截距 α 。 无论数据有 100 行还是 100
- 10 讲义.pdf · 第 3 页 · `10_讲义_d344dc1e_2_0`：1. 2 基本概念
节点（Node）：树中的每个点称为节点。 根节点是树的起点，内部节点是决策点，叶节点是最终的决策结
果。 分支（Branch）：从一个节点到另一个节点的路径称为分支。 分裂（Split）：根据某个特征将数据集分成多个子集的过程。 纯度（Purity）：衡量一个子集中样本的类别是否一致。 纯度越高，说明子集中的样本越相似。 1. 3 决策树的优缺点
优点
l 易于理解和解释：决策树的结构直观，易于理解和解释。 l 处理多种数据类型：可以处理数值型和类别型数据。 l 不需要数据标准化：决策树不需要对数据进行标准化或归一化处理。 缺点
l 容易过拟合：决策树容易过拟合，特别是在数据集较小或树深度较大时。 l 对噪声敏感：决策树对噪声数据较为敏感，可能导致模型性能下降。 l 不稳定：数据的小变化可能导致生成完全不同的树。 1. 4 工作原理
决策树的构建过程通常被称为 “分而治

## T002 ID3贪心决策树归纳算法 — 已覆盖

从包含全部训练样例的单一根节点开始；若节点样例同属一类则标为叶节点；否则对剩余候选属性计算启发式/统计度量（如信息增益），选最佳属性标注当前节点并分裂样例：类别属性每个值一个分支，连续属性选分裂点a（如A<a、A≥a）；对子节点重复；停止条件为样例同属一类或无属性剩余（标为多数类）。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.90

**最新学校课件证据**
- 10_decision_tree.pdf · 第 6 页 · `10_decision_tree_d8e30e66_5_0`：A greedy ID3 algorithm for decision tree induction
– Start with a single root node containing all training examples
– For each node:
– If all examples at this node belong to the same class:
• mark this node as a leaf and label it with that class
– Otherwise:
• Compute heuristic or statistical measure (e. g. Information Gain) for each remaining candidate attributes
• Select the best attribute (e. g
- 10_decision_tree.pdf · 第 6 页 · `10_decision_tree_d8e30e66_5_1`：g. with the highest IG)
• Label the current node with that attribute
• Split the examples into child nodes:
– Categorical attributes: one branch per value
– Continues attributes: choose a split point a (e. g. 𝐴 < 𝑎, 𝐴 ≥ 𝑎)
– Repeat the process for each child node
– Stop when:
– All examples at a node belong to the same class; or
– no attributes remain → label with majority class
The University of 
- 10_decision_tree.pdf · 第 6 页 · `10_decision_tree_d8e30e66_5_2`：g. 𝐴 < 𝑎, 𝐴 ≥ 𝑎)
– Repeat the process for each child node
– Stop when:
– All examples at a node belong to the same class; or
– no attributes remain → label with majority class
The University of Sydney Page 6

**往期补习课件证据**
- 10 讲义.pdf · 第 5 页 · `10_讲义_d344dc1e_4_0`：2. 4 基尼不纯度 (Gini Impurity)
CART 算法选择基尼系数进行划分
3. ID3 算法
ID3（Iterative Dichotomiser 3）采用信息增益（Information Gain）选择划分属性。 3. 1 算法步骤（贪心、自顶向下递归）
分而治之（Divide-and-conquer:）思想：递归划分数据，直到子集纯净（全属同一类）
1. 从根节点开始，所有训练样本都在根节点。 2. 若当前节点样本全部属于同一类别，则停止，标记为叶节点。 3. 否则，计算每个特征的信息增益，选择信息增益最大的特征作为当前节点的划分特征。 4. 根据该特征的每个取值，将样本划分到子节点。 5. 对每个子节点递归执行上述步骤。 5. 停止条件：
- 所有样本属于同一类。 - 没有剩余特征可划分（用多数投票确定叶节点类别）。 - 树深度达到预设值。 3. 2 优缺点
优点
l
- 10 讲义.pdf · 第 3 页 · `10_讲义_d344dc1e_2_1`：l 分割数据集：根据选定的特征将数据集分成多个子集。 l 递归构建子树：对每个子集重复上述过程，直到满足停止条件（如所有样本属于同一类别、达到最大
深度等）。 l 生成叶节点：当满足停止条件时，生成叶节点并赋予类别或值。

## T003 决策树的分治构建过程 — 已覆盖

采用分治策略：选择属性将数据划分为子集，检查子集是否纯（全True或全False），纯则停止，否则重复；示例中先尝试选择Level属性进行划分。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.90

**最新学校课件证据**
- 10_decision_tree.pdf · 第 8 页 · `10_decision_tree_d8e30e66_7_0`：Training examples:9 True/ 5 False Class label
Decision Tree
Applicant Level Lang Tweets PhD Interviewedwell
A1 Senior Java No No False
A2 Senior Java No Yes False
– Divide-and-conquer:
A3 Mid Java No No True
– Choose attributes to split
A4 Junior Python No No True
the data into subsets A5 Junior R Yes No True
A6 Junior R Yes Yes False
– Are they pure? (all True or
A7 Mid R Yes Yes True
all False)

- 10_decision_tree.pdf · 第 8 页 · `10_decision_tree_d8e30e66_7_1`：Training examples:9 True/ 5 False Class label
Decision Tree
Applicant Level Lang Tweets PhD Interviewedwell
A1 Senior Java No No False
A2 Senior Java No Yes False
– Divide-and-conquer:
A3 Mid Java No No True
– Choose attributes to split
A4 Junior Python No No True
the data into subsets A5 Junior R Yes No True
A6 Junior R Yes Yes False
– Are they pure? (all True or
A7 Mid R Yes Yes True
all False)

- 10_decision_tree.pdf · 第 8 页 · `10_decision_tree_d8e30e66_7_2`：(all True or
A7 Mid R Yes Yes True
all False)
A8 Senior Python No No False
• If yes: stop
A9 Senior R Yes No True
• Otherwise: repeat A10 Junior Python Yes No True
A11 Senior Python Yes Yes True
– Which attributes to choose? A12 Mid Python No Yes True
– Let’s try selecting “Level”
A13 Mid Java Yes No True
attribute first. A14 Junior Python No Yes False
New data: A15 Senior R No No ? The University
- 10_decision_tree.pdf · 第 8 页 · `10_decision_tree_d8e30e66_7_3`：A14 Junior Python No Yes False
New data: A15 Senior R No No ? The University of Sydney Page 8

**往期补习课件证据**
- 10 讲义.pdf · 第 3 页 · `10_讲义_d344dc1e_2_1`：l 分割数据集：根据选定的特征将数据集分成多个子集。 l 递归构建子树：对每个子集重复上述过程，直到满足停止条件（如所有样本属于同一类别、达到最大
深度等）。 l 生成叶节点：当满足停止条件时，生成叶节点并赋予类别或值。
- 10 讲义.pdf · 第 5 页 · `10_讲义_d344dc1e_4_0`：2. 4 基尼不纯度 (Gini Impurity)
CART 算法选择基尼系数进行划分
3. ID3 算法
ID3（Iterative Dichotomiser 3）采用信息增益（Information Gain）选择划分属性。 3. 1 算法步骤（贪心、自顶向下递归）
分而治之（Divide-and-conquer:）思想：递归划分数据，直到子集纯净（全属同一类）
1. 从根节点开始，所有训练样本都在根节点。 2. 若当前节点样本全部属于同一类别，则停止，标记为叶节点。 3. 否则，计算每个特征的信息增益，选择信息增益最大的特征作为当前节点的划分特征。 4. 根据该特征的每个取值，将样本划分到子节点。 5. 对每个子节点递归执行上述步骤。 5. 停止条件：
- 所有样本属于同一类。 - 没有剩余特征可划分（用多数投票确定叶节点类别）。 - 树深度达到预设值。 3. 2 优缺点
优点
l
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_0`：3. 3. 3 继续划分
Level = Mid
划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior
Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG：
计算 Junior 子集的熵：
PhD 特征：
PhD=Yes: 2 个 (0 True, 2 False) → 熵 0
PhD=No: 3 个 (3 True, 0 False) → 熵 0
条件熵 = 0，IG = 0. 97
Tweets 特征：
Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92
Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1
条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
Lang 

## T004 决策树构建示例（应聘者数据） — 已覆盖

以14条应聘者训练数据（9 True/5 False）为例，特征为Level、Lang、Tweets、PhD，类标签为Interviewed well；按Level划分后各分支纯度不同，再对Junior分支用PhD划分，最终得到完整决策树并对新样本A15（Senior, R, No, No）预测为False。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.90

**最新学校课件证据**
- 10_decision_tree.pdf · 第 7 页 · `10_decision_tree_d8e30e66_6_0`：Training examples:9 True/ 5 False Class label
Example
Applicant Level Lang Tweets PhD Interviewedwell
A1 Senior Java No No False
A2 Senior Java No Yes False
– Training data: interviewee
A3 Mid Java No No True
data. A4 Junior Python No No True
– Features: Level , Lang, Tweets, A5 Junior R Yes No True
PhD. A6 Junior R Yes Yes False
A7 Mid R Yes Yes True
– Class label: Interviewed well. A8 Senior Pyt
- 10_decision_tree.pdf · 第 7 页 · `10_decision_tree_d8e30e66_6_1`：A6 Junior R Yes Yes False
A7 Mid R Yes Yes True
– Class label: Interviewed well. A8 Senior Python No No False
– New applicant: A15 (Senior,
A9 Senior R Yes No True
R, No, No). A10 Junior Python Yes No True
– We want to predict whether A11 Senior Python Yes Yes True
A12 Mid Python No Yes True
A15 Interviewed well or not
A13 Mid Java Yes No True
A14 Junior Python No Yes False
New data: A15 Senior R 
- 10_decision_tree.pdf · 第 7 页 · `10_decision_tree_d8e30e66_6_2`：A10 Junior Python Yes No True
– We want to predict whether A11 Senior Python Yes Yes True
A12 Mid Python No Yes True
A15 Interviewed well or not
A13 Mid Java Yes No True
A14 Junior Python No Yes False
New data: A15 Senior R No No ? The University of Sydney Page 7
- 10_decision_tree.pdf · 第 9 页 · `10_decision_tree_d8e30e66_8_0`：Training examples:9 True/ 5 False Class label
Decision Tree
Applicant Level Lang Tweets PhD Interviewedwell
A1 Senior Java No No False
A2 Senior Java No Yes False
A3 Mid Java No No True
A4 Junior Python No No True
9True/5False
A5 Junior R Yes No True
Level? A6 Junior R Yes Yes False
Junior
Mid A7 Mid R Yes Yes True
Senior
A8 Senior Python No No False
A9 Senior R Yes No True
A10 Junior Python Yes N
- 10_decision_tree.pdf · 第 10 页 · `10_decision_tree_d8e30e66_9_0`：Decision Tree
Level Lang Tweets PhD Interviewedwell
Senior Java No No False
9True/5False
Senior Java No Yes False
Level? Senior Python No No False
Junior
Mid Senior R Yes No True
Senior
Senior Python Yes Yes True
Mid Java No No True
4True
Mid R Yes Yes True
3True/2False
3False/2True
Mid Python No Yes True
Pure
Mid Java Yes No True
Junior Python No No True
Mixed
Junior R Yes No True
Junior Python Y
- 10_decision_tree.pdf · 第 11 页 · `10_decision_tree_d8e30e66_10_0`：Level Lang Tweets PhD Interviewedwell
Decision Tree
Senior Java No No False
Senior Java No Yes False
Senior Python No No False
9True/5False
Senior R Yes No True
Level? Senior Python Yes Yes True
Senior Junior
Mid Mid Java No No True
Mid R Yes Yes True
True
Tweets Mid Python No Yes True
PhD? 3False/2True
Mid Java Yes No True
3True/2False
Yes No No Yes Junior Python No No True
Junior R Yes No True
T
- 10_decision_tree.pdf · 第 12 页 · `10_decision_tree_d8e30e66_11_0`：Resulting Tree Applicant Level Lang Tweets PhD Interviewedwell
A1 Senior Java No No False
A2 Senior Java No Yes False
A3 Mid Java No No True
A4 Junior Python No No True
Level? Senior Junior A5 Junior R Yes No True
Mid
A6 Junior R Yes Yes False
True A7 Mid R Yes Yes True
Tweets
PhD? A8 Senior Python No No False
A9 Senior R Yes No True
Yes No Yes
No
A10 Junior Python Yes No True
A11 Senior Python Ye

**往期补习课件证据**
- 10 讲义.pdf · 第 6 页 · `10_讲义_d344dc1e_5_0`：3. 3 示例：面试者数据集
目标：预测新申请人 A15（Senior, R, No, No）是否面试好。 3. 3. 1 依靠直觉进行划分
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_0`：3. 3. 3 继续划分
Level = Mid
划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior
Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG：
计算 Junior 子集的熵：
PhD 特征：
PhD=Yes: 2 个 (0 True, 2 False) → 熵 0
PhD=No: 3 个 (3 True, 0 False) → 熵 0
条件熵 = 0，IG = 0. 97
Tweets 特征：
Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92
Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1
条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
Lang 
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_1`：95，IG ≈ 0. 02
因此 Junior 节点选择 PhD 划分，得到两个纯节点（PhD=Yes 全 False，PhD=No 全 True）。 Level=Senior
Level=Senior 节点（5 个：2 True, 3 False）可继续划分（可能选 Tweets 等），最终得到如 PDF 中的树。 3. 3. 4 预测 A15
A15 (Senior, R, No, No) 按照树：Level=Senior 分支，再根据其他特征到达叶节点，
最终预测为 False。
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_2`：3. 4 预测 A15
A15 (Senior, R, No, No) 按照树：Level=Senior 分支，再根据其他特征到达叶节点，
最终预测为 False。

## T005 ID3属性选择与信息增益思想 — 已覆盖

ID3选择信息增益最高的属性；在每个非叶节点询问哪个属性带来最大的不确定性减少；信息增益是分裂前不确定性与分裂后不确定性之差，增益越高分裂越好；不确定性用熵度量。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.90

**最新学校课件证据**
- 10_decision_tree.pdf · 第 14 页 · `10_decision_tree_d8e30e66_13_0`：How does ID3 choose an attribute and split
– It chooses the attribute with the highest information gain. – At each non-leaf node, the algorithm asks:
– Which attribute gives the biggest reduction in uncertainty? – Information Gain is calculated as the difference between the
uncertainty before the split and the uncertainty after the split. – Higher Information Gain means a better split
– Uncertaint
- 10_decision_tree.pdf · 第 14 页 · `10_decision_tree_d8e30e66_13_1`：– Information Gain is calculated as the difference between the
uncertainty before the split and the uncertainty after the split. – Higher Information Gain means a better split
– Uncertainty is measured by entropy
The University of Sydney Page 14

**往期补习课件证据**
- 10 讲义.pdf · 第 4 页 · `10_讲义_d344dc1e_3_0`：2. 纯度
2. 1 熵 Entropy
信息熵是用来衡量“不确定性”或“混乱程度”的指标。 2. 2 条件熵 Conditional Entropy:
2. 3 信息增益 Information Gain (IG)
信息增益表示划分后信息熵 entropy的程度。 ID3与C4. 5选择信息增益最大的特征进行划分。
- 10 讲义.pdf · 第 5 页 · `10_讲义_d344dc1e_4_0`：2. 4 基尼不纯度 (Gini Impurity)
CART 算法选择基尼系数进行划分
3. ID3 算法
ID3（Iterative Dichotomiser 3）采用信息增益（Information Gain）选择划分属性。 3. 1 算法步骤（贪心、自顶向下递归）
分而治之（Divide-and-conquer:）思想：递归划分数据，直到子集纯净（全属同一类）
1. 从根节点开始，所有训练样本都在根节点。 2. 若当前节点样本全部属于同一类别，则停止，标记为叶节点。 3. 否则，计算每个特征的信息增益，选择信息增益最大的特征作为当前节点的划分特征。 4. 根据该特征的每个取值，将样本划分到子节点。 5. 对每个子节点递归执行上述步骤。 5. 停止条件：
- 所有样本属于同一类。 - 没有剩余特征可划分（用多数投票确定叶节点类别）。 - 树深度达到预设值。 3. 2 优缺点
优点
l
- 10 讲义.pdf · 第 7 页 · `10_讲义_d344dc1e_6_0`：3. 3. 2 依靠信息增益进行划分
总样本熵
总样本14个，true9个，false5个
条件熵 Level
Level 信息增益最大，故根节点按 Level 划分。

## T006 信息增益的形式定义 — 部分覆盖

IG(Y|X)=H(Y)−H(Y|X)，其中Y为类标签、X为属性；H(Y)为分裂前Y的熵（不确定性），H(Y|X)为给定X后Y的条件熵（分裂后不确定性）。

差异：补习资料提到信息增益表示划分后信息熵降低的程度，并在习题中要求计算IG(Y|X)，但未给出IG(Y|X)=H(Y)−H(Y|X)的显式形式定义及各项含义说明。
建议：补充信息增益的显式公式定义及H(Y)、H(Y|X)含义。
置信度（仅供排序）：0.70

**最新学校课件证据**
- 10_decision_tree.pdf · 第 15 页 · `10_decision_tree_d8e30e66_14_0`：Information Gain (IG)
– Formally IG calculates the change in entropy after making a
split based on the value of an attribute. 𝐼𝐺(𝑌|𝑋) = 𝐻(𝑌) – 𝐻(𝑌|𝑋)
– Where:
– 𝑌 is a class label. – 𝑋 is an attribute. – 𝐻(𝑌) is the entropy of 𝑌: uncertainty before splitting
– 𝐻(𝑌|𝑋) is the conditional entropy of 𝑌 given 𝑋: uncertainty after
splitting
The University of Sydney Page 15
- 10_decision_tree.pdf · 第 15 页 · `10_decision_tree_d8e30e66_14_1`：– 𝑋 is an attribute. – 𝐻(𝑌) is the entropy of 𝑌: uncertainty before splitting
– 𝐻(𝑌|𝑋) is the conditional entropy of 𝑌 given 𝑋: uncertainty after
splitting
The University of Sydney Page 15

**往期补习课件证据**
- 10 讲义.pdf · 第 4 页 · `10_讲义_d344dc1e_3_0`：2. 纯度
2. 1 熵 Entropy
信息熵是用来衡量“不确定性”或“混乱程度”的指标。 2. 2 条件熵 Conditional Entropy:
2. 3 信息增益 Information Gain (IG)
信息增益表示划分后信息熵 entropy的程度。 ID3与C4. 5选择信息增益最大的特征进行划分。
- 10 讲义.pdf · 第 18 页 · `10_讲义_d344dc1e_17_0`：6. 课后习题
案例一：信息增益与决策树分裂（手算）
数据集： 判断是否适合户外运动（Outdoor），基于两个特征：天气（Weather）和风力（Windy）。 1. 计算整个数据集关于目标变量 Outdoor 的熵 𝐻(𝑌)。 2. 分别计算以 Weather 和 Windy 为分裂属性的条件熵 𝐻(𝑌 ∣𝑋)。 3. 计算两个特征各自的信息增益 𝐼𝐺(𝑌 ∣𝑋)。 4. 根据信息增益，应该选择哪个特征作为根节点？ 为什么？ 5. 如果选择 Weather 作为根节点，请画出根节点分裂后的子节点，并判断每个子节点是否还需要继续
分裂（假设当节点中所有样本的 Outdoor 一致时停止）。

## T007 熵的定义与解释 — 部分覆盖

H(Y)=−Σ p_i log2(p_i)，p_i=p(Y=y_i)，m为类别数；熵越高不确定性越大；熵范围从0（完全纯）到log2(k)（k为类别数）；二分类最大熵为1。

差异：补习资料仅定性说明信息熵衡量不确定性，未给出H(Y)=−Σp_i log2(p_i)公式、熵范围0到log2(k)及二分类最大熵为1的说明。
建议：补充熵的数学定义、取值范围及二分类最大熵结论。
置信度（仅供排序）：0.70

**最新学校课件证据**
- 10_decision_tree.pdf · 第 16 页 · `10_decision_tree_d8e30e66_15_0`：Entropy
– To measure the uncertainty associated with data:
𝑚
𝐻 𝑌 = − ෍ 𝑝 log (𝑝 )
𝑖 2 𝑖
𝑖=1
– Where 𝑝 = 𝑝(𝑌 = 𝑦 ), and 𝑚 is the number of classes. 𝑖 𝑖
– Interpretation:
– Higher entropy => higher uncertainty. – Lower entropy => lower uncertainty. – Entropy ranges from 0 (completely pure) to 𝑙𝑜𝑔 𝑘 ,where 𝑘 is the
2
number of classes. – For binary classification, the maximum entropy is 1
The Univers
- 10_decision_tree.pdf · 第 16 页 · `10_decision_tree_d8e30e66_15_1`：– Entropy ranges from 0 (completely pure) to 𝑙𝑜𝑔 𝑘 ,where 𝑘 is the
2
number of classes. – For binary classification, the maximum entropy is 1
The University of Sydney Page 16

**往期补习课件证据**
- 10 讲义.pdf · 第 4 页 · `10_讲义_d344dc1e_3_0`：2. 纯度
2. 1 熵 Entropy
信息熵是用来衡量“不确定性”或“混乱程度”的指标。 2. 2 条件熵 Conditional Entropy:
2. 3 信息增益 Information Gain (IG)
信息增益表示划分后信息熵 entropy的程度。 ID3与C4. 5选择信息增益最大的特征进行划分。
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_0`：3. 3. 3 继续划分
Level = Mid
划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior
Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG：
计算 Junior 子集的熵：
PhD 特征：
PhD=Yes: 2 个 (0 True, 2 False) → 熵 0
PhD=No: 3 个 (3 True, 0 False) → 熵 0
条件熵 = 0，IG = 0. 97
Tweets 特征：
Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92
Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1
条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
Lang 

## T008 熵计算示例（二分类） — 未发现

示例数据中Y为50% Yes、50% No时，H(Y)=−(0.5*log2(0.5)+0.5*log2(0.5))=1。

差异：补习资料无50%Yes/50%No时H(Y)=1的二分类熵计算示例。
建议：补充二分类均衡分布熵计算示例。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 10_decision_tree.pdf · 第 17 页 · `10_decision_tree_d8e30e66_16_0`：Example: binary classification
𝑚
X Y
𝐻 𝑌 = − ෍ 𝑝 log (𝑝 )
𝑖 2 𝑖
𝑖=1 Math Yes
– Where 𝑝 = 𝑝(𝑌 = 𝑦 ), and 𝑚 is the number of
𝑖 𝑖 History No
classes
CS Yes
– Example: The entropy of Y:
Math No
– 50% of Yes and 50% of No Math No
– 𝐻(𝑌) = −(0. 5 ∗ log (0. 5) + 0. 5 ∗ log (0. 5) ) = 1 CS Yes
2 2
History No
P(Y= Yes) P(Y= No) Math Yes
The University of Sydney Page 17
- 10_decision_tree.pdf · 第 17 页 · `10_decision_tree_d8e30e66_16_1`：5 ∗ log (0. 5) ) = 1 CS Yes
2 2
History No
P(Y= Yes) P(Y= No) Math Yes
The University of Sydney Page 17

**往期补习课件证据**
- 未检索到可引用证据。

## T009 条件熵H(Y|X) — 部分覆盖

H(Y|X)=Σ p(X=v_i)*H(Y|X=v_i)，即Y的平均条件熵；由数据计算p(X=v_i)，例如p(X=Math)=4/8=0.5、p(X=History)=0.25、p(X=CS)=0.25。

差异：补习资料提及条件熵概念并在Level划分中计算条件熵，但未给出H(Y|X)=Σp(X=v_i)H(Y|X=v_i)的显式公式及p(X=Math)=0.5等具体概率示例。
建议：补充条件熵加权公式及具体概率计算示例。
置信度（仅供排序）：0.65

**最新学校课件证据**
- 10_decision_tree.pdf · 第 18 页 · `10_decision_tree_d8e30e66_17_0`：Conditional Entropy: H(Y|X)
– H(Y|X): the average conditional entropy of Y. X Y
𝐻(𝑌|𝑋) = ෍ 𝑝 𝑋 = 𝑣 ∗ 𝐻(𝑌|𝑋 = 𝑣 ) Math Yes
𝑖 𝑖
𝑖
History No
– From data, we calculate 𝑝 𝑋 = 𝑣 :
𝑖
CS Yes
– 𝑝 𝑋 = Math = 4Τ = 0. 5
8
Math No
– 𝑝 𝑋 = History = 2Τ = 0. 25
8
Math No
– 𝑝 𝑋 = CS = 2Τ = 0. 25
8
CS Yes
𝒗 𝒑(𝑿 = 𝒗 ) 𝑯(𝒀|𝑿 = 𝒗 ) History No
𝒊 𝒊 𝒊
Math Yes
Math 0. 5 ? For history and CS, the Y
History 0. 25 ? value
- 10_decision_tree.pdf · 第 18 页 · `10_decision_tree_d8e30e66_17_1`：25 ? likely
The University of Sydney Page 18

**往期补习课件证据**
- 10 讲义.pdf · 第 4 页 · `10_讲义_d344dc1e_3_0`：2. 纯度
2. 1 熵 Entropy
信息熵是用来衡量“不确定性”或“混乱程度”的指标。 2. 2 条件熵 Conditional Entropy:
2. 3 信息增益 Information Gain (IG)
信息增益表示划分后信息熵 entropy的程度。 ID3与C4. 5选择信息增益最大的特征进行划分。
- 10 讲义.pdf · 第 7 页 · `10_讲义_d344dc1e_6_0`：3. 3. 2 依靠信息增益进行划分
总样本熵
总样本14个，true9个，false5个
条件熵 Level
Level 信息增益最大，故根节点按 Level 划分。
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_0`：3. 3. 3 继续划分
Level = Mid
划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior
Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG：
计算 Junior 子集的熵：
PhD 特征：
PhD=Yes: 2 个 (0 True, 2 False) → 熵 0
PhD=No: 3 个 (3 True, 0 False) → 熵 0
条件熵 = 0，IG = 0. 97
Tweets 特征：
Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92
Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1
条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
Lang 

## T010 特定条件熵H(Y|X=v_i) — 部分覆盖

H(Y|X=v_i)是仅X取值为v_i的记录中Y的熵；示例中H(Y|X=Math)=1、H(Y|X=History)=0、H(Y|X=CS)=0。

差异：补习资料在Junior子集计算中展示了按PhD取值分组的熵（如PhD=Yes熵0），体现特定条件熵思想，但未给出H(Y|X=v_i)的定义及Math/History/CS示例。
建议：补充特定条件熵定义及对应示例。
置信度（仅供排序）：0.60

**最新学校课件证据**
- 10_decision_tree.pdf · 第 19 页 · `10_decision_tree_d8e30e66_18_0`：Specific Conditional Entropy: H(Y|X=v )
i
– 𝐻(𝑌|𝑋 = 𝑣 ): entropy of Y among only those records in which X has value 𝑣 . 𝑖 𝑖
X Y X Y X Y
Math Yes History No CS Yes
Math No CS Yes
History No
Math No
Math Yes For history and CS, the Y
value is certain, For math,
– From the data, we obtain:
the yes and no are equally
– 𝐻 𝑌 𝑋 = Math = − 2Τ ∗ log (2Τ ) + 2Τ ∗ log (2Τ ) = 1 likely
4 2 4 4 2 4
– 𝐻 𝑌 𝑋 = H
- 10_decision_tree.pdf · 第 19 页 · `10_decision_tree_d8e30e66_18_1`：Specific Conditional Entropy: H(Y|X=v )
i
– 𝐻(𝑌|𝑋 = 𝑣 ): entropy of Y among only those records in which X has value 𝑣 . 𝑖 𝑖
X Y X Y X Y
Math Yes History No CS Yes
Math No CS Yes
History No
Math No
Math Yes For history and CS, the Y
value is certain, For math,
– From the data, we obtain:
the yes and no are equally
– 𝐻 𝑌 𝑋 = Math = − 2Τ ∗ log (2Τ ) + 2Τ ∗ log (2Τ ) = 1 likely
4 2 4 4 2 4
– 𝐻 𝑌 𝑋 = H

**往期补习课件证据**
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_0`：3. 3. 3 继续划分
Level = Mid
划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior
Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG：
计算 Junior 子集的熵：
PhD 特征：
PhD=Yes: 2 个 (0 True, 2 False) → 熵 0
PhD=No: 3 个 (3 True, 0 False) → 熵 0
条件熵 = 0，IG = 0. 97
Tweets 特征：
Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92
Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1
条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
Lang 

## T011 条件熵与信息增益计算示例 — 未发现

示例中H(Y|X)=0.5*1+0.25*0+0.25*0=0.5；由H(Y)=1得IG(Y|X)=1−0.5=0.5。

差异：补习资料无H(Y|X)=0.5*1+0.25*0+0.25*0=0.5及IG=1−0.5=0.5的完整计算示例。
建议：补充该条件熵与信息增益数值计算示例。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 10_decision_tree.pdf · 第 20 页 · `10_decision_tree_d8e30e66_19_0`：Conditional Entropy: H(Y|X)
𝒗 𝒑(𝑿 = 𝒗 ) 𝑯(𝒀|𝑿 = 𝒗 )
𝒊 𝒊 𝒊
Math 0. 5 1
History 0. 25 0
CS 0. 25 0
𝐻 𝑌 𝑋 = ෍ 𝑝 𝑋 = 𝑣 ∗ 𝐻 𝑌 𝑋 = 𝑣
𝑖 𝑖
𝑖
= 0. 5 ∗ 1 + 0. 25 ∗ 0 + 0. 25 ∗ 0
= 0. 5
The University of Sydney Page 20
- 10_decision_tree.pdf · 第 21 页 · `10_decision_tree_d8e30e66_20_0`：Information Gain (IG)
𝐼𝐺 𝑌 𝑋 = 𝐻 𝑌 – 𝐻 𝑌 𝑋
– From the example:
– 𝐻(𝑌) = 1
– 𝐻(𝑌|𝑋) = 0. 5
– Thus:
– 𝐼𝐺(𝑌|𝑋) = 1 – 0. 5 = 0. 5
The University of Sydney Page 21

**往期补习课件证据**
- 未检索到可引用证据。

## T012 熵与信息增益的理解检验 — 未发现

通过选择题检验：类别均匀混合时熵高；全部同类时熵为0；二分类熵在正负均衡时最高；一个子节点纯的分裂能减少部分不确定性；数值特征不应总在中位数分裂，最佳阈值应最大程度降低类别不确定性；平衡分裂不一定优于降低不确定性更多的分裂。

差异：补习资料无针对熵与信息增益理解的选择题检验内容。
建议：补充相应理解检验题。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 10_decision_tree.pdf · 第 22 页 · `10_decision_tree_d8e30e66_21_0`：Test your understanding
– A decision tree node contains 20 training examples: 10 positive
and 10 negative. What can we say about its entropy? – A. It is 0 because the node has many examples
– B. It is high because the classes are evenly mixed
– C. It is low because there are only two classes
– D. It depends only on the number of features
1
− 0. 5 ∗ 𝑙𝑜𝑔 0. 5 + 0. 5 ∗ 𝑙𝑜𝑔 0. 5 = − 𝑙𝑜𝑔 = − − = 1
2 2 
- 10_decision_tree.pdf · 第 23 页 · `10_decision_tree_d8e30e66_22_0`：Test your understanding
– A node contains 15 examples, all belonging to the same class. What is its entropy? – A. 0
– B. 0. 5
– C. 1
– D. Cannot be determined
The University of Sydney Page 23
- 10_decision_tree.pdf · 第 24 页 · `10_decision_tree_d8e30e66_23_0`：Test your understanding
– For a binary class label, when is entropy highest? – A. when all examples are positive
– B. when all examples are negative
– C. when positive and negative examples are equally balanced
– D. when there are more positive than negative
The University of Sydney Page 24
- 10_decision_tree.pdf · 第 25 页 · `10_decision_tree_d8e30e66_24_0`：Test your understanding
– A node has 100 examples: 50 positive and 50 negative. Which
split is likely better? – A. Left: 25 positive, 25 negative; Right: 25 positive, 25 negative
– B. Left: 50 positive, 0 negative; Right: 0 positive, 50 negative
– C. Left: 45 positive, 45 negative; Right: 5 positive, 5 negative
– D. Left: 30 positive, 30 negative; Right: 20 positive, 20 negative
The University of 
- 10_decision_tree.pdf · 第 26 页 · `10_decision_tree_d8e30e66_25_0`：Test your understanding
– A split produces:
– Left child: 10 positive, 0 negative
– Right child: 40 positive, 50 negative
– Which statement is most accurate? – A. The split is useless because it is unbalance
– B. The split reduces some uncertainty because one child is pure
– C. The split must be the best split because one child is pure
– D. The split has zero information gain
The University of Syd
- 10_decision_tree.pdf · 第 27 页 · `10_decision_tree_d8e30e66_26_0`：Test your understanding
– For a numeric feature in a decision tree, should we always split
at the median value? – A. Yes, because it creates equal-sized groups
– B. Yes, because equal-sized groups always maximise information gain
– C. No, because the best threshold is the one that most reduces class
uncertainty
– D. No, because decision trees cannot use numeric features
The University of Sydney Pa
- 10_decision_tree.pdf · 第 28 页 · `10_decision_tree_d8e30e66_27_0`：Test your understanding
– A node has 100 examples: 50 positive and 50 negative. – Split A:
The information gain
• Left: 50 examples, 25 positive / 25 negative
of split A is 0
• Right: 50 examples, 25 positive / 25 negative
For split B, the entropy
– Split B:
of left child is 0
• Left: 20 examples, 20 positive / 0 negative
• Right: 80 examples, 30 positive / 50 negative
For split B, the
– Which is 

**往期补习课件证据**
- 未检索到可引用证据。

## T013 用信息增益验证属性选择（Level） — 部分覆盖

计算H(Interviewed well)=H(9,5)=0.94；H(Interviewed well|Level)=0.36*0.97+0.29*0+0.36*0.97≈0.7；IG(Interviewed well|Level)=0.94−0.7=0.24；对比Tweets(0.15)、PhD(0.048)、Lang(0.029)，Level信息增益最高，故选择该属性是合理的。

差异：补习资料说明Level信息增益最大故根节点按Level划分，但未给出H(9,5)=0.94、H(Y|Level)≈0.7、IG=0.24及与Tweets/PhD/Lang对比的具体数值。
建议：补充Level信息增益的完整数值计算与属性对比。
置信度（仅供排序）：0.65

**最新学校课件证据**
- 10_decision_tree.pdf · 第 30 页 · `10_decision_tree_d8e30e66_29_0`：Calculation
– 𝐻 Interviewed well = 𝐻 9,5 = − 9Τ log 9Τ + 5Τ log 5Τ = 0. 94
14 2 14 14 2 14
– 𝐻 Interviewed well Level = σ 𝑝 Level = 𝑣 ∗ 𝐻 Interviewed well Level = 𝑣
𝑖 𝑖 𝑖
𝒗 𝒑(Level = 𝒗 ) 𝑯(Interviewed well |Level = 𝒗 )
𝒊 𝒊 𝒊
5
Senior ൗ = 0. 36 𝐻 2,3 = − 2 ൗ ∗ log 2 ൗ + 3 ൗ ∗ log 3 ൗ = 0. 97
14 5 2 5 5 2 5
Mid 4 ൗ = 0. 29 𝐻 4,0 = − 4 ൗ ∗ log 4 ൗ + 0 ൗ ∗ log 0 ൗ = 0
14 4 2 4 4 2 4
Junior 5 3 3 2 2
ൗ
- 10_decision_tree.pdf · 第 30 页 · `10_decision_tree_d8e30e66_29_1`：3 ∗ 0. 97 = 0. 7
– Thus:
– 𝐼𝐺 Interviewed well Level = 𝐻 Interviewed well –𝐻 Interviewed well Level
= 0. 94 − 0. 7 = 0. 24
The University of Sydney Page 30
- 10_decision_tree.pdf · 第 31 页 · `10_decision_tree_d8e30e66_30_0`：Calculation
– Similarly:
– 𝐼𝐺 Interviewed well Tweets
= 𝐻 Interviewed well –𝐻 Interviewed well Tweets = 0. 15
– 𝐼𝐺 Interviewed well PhD
= 𝐻 Interviewed well –𝐻 Interviewed well PhD = 0. 048
– 𝐼𝐺 Interviewed well Lang
= 𝐻 Interviewed well –𝐻 Interviewed well Lang = 0. 029
– Level has the highest information gain, therefore it was good
to choose that attribute. The University of Sydney Page 31
- 10_decision_tree.pdf · 第 31 页 · `10_decision_tree_d8e30e66_30_1`：029
– Level has the highest information gain, therefore it was good
to choose that attribute. The University of Sydney Page 31

**往期补习课件证据**
- 10 讲义.pdf · 第 7 页 · `10_讲义_d344dc1e_6_0`：3. 3. 2 依靠信息增益进行划分
总样本熵
总样本14个，true9个，false5个
条件熵 Level
Level 信息增益最大，故根节点按 Level 划分。
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_0`：3. 3. 3 继续划分
Level = Mid
划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior
Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG：
计算 Junior 子集的熵：
PhD 特征：
PhD=Yes: 2 个 (0 True, 2 False) → 熵 0
PhD=No: 3 个 (3 True, 0 False) → 熵 0
条件熵 = 0，IG = 0. 97
Tweets 特征：
Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92
Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1
条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
Lang 

## T014 用信息增益验证属性选择（PhD） — 已覆盖

在Junior层级的5条记录子集上，H(Interviewed well)=H(3,2)=0.97，按PhD划分后条件熵为0，IG=0.97，高于Tweets(0.02)和Lang(0.02)，故下一步选择PhD属性是合理的。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.85

**最新学校课件证据**
- 10_decision_tree.pdf · 第 33 页 · `10_decision_tree_d8e30e66_32_0`：PhD attribute – subset of 5 records with Junior level
Level Lang Tweets PhD Interviewedwell
4 Junior Python No No True
5 Junior R Yes No True
6 Junior R Yes Yes False
10 Junior Python Yes No True
14 Junior Python No Yes False
– 𝐻 Interviewed well = 𝐻 3,2 = − 3Τ log 3Τ + 2Τ log 2Τ = 0. 97
5 2 5 5 2 5
– 𝐻 Interviewed well PhD = σ 𝑝 PhD = 𝑣 ∗ 𝐻 Interviewed well PhD = 𝑣
𝑖 𝑖 𝑖
𝒗 𝒑(PhD = 𝒗 ) 𝑯 Interview
- 10_decision_tree.pdf · 第 33 页 · `10_decision_tree_d8e30e66_32_1`：4 𝐻 0,2 = 0
5
No 3 𝐻 3,0 = 0
ൗ = 0. 6
5
– Then: 𝐻 Interviewed well PhD = 0
The University of Sydney Page 33
- 10_decision_tree.pdf · 第 34 页 · `10_decision_tree_d8e30e66_33_0`：Calculation
– Then, the Information gain for each attribute:
– 𝐼𝐺 Interviewed well PhD
= 𝐻 Interviewed well –𝐻 Interviewed well PhD = 0. 97
– 𝐼𝐺 Interviewed well Tweets
= 𝐻 Interviewed well –𝐻 Interviewed well Tweets = 0. 02
– 𝐼𝐺 Interviewed well Lang
= 𝐻 Interviewed well –𝐻 Interviewed well Lang = 0. 02
– PhD has the highest information gain, therefore it was good to
choose that attribute next fo
- 10_decision_tree.pdf · 第 34 页 · `10_decision_tree_d8e30e66_33_1`：02
– PhD has the highest information gain, therefore it was good to
choose that attribute next for the Junior Level. The University of Sydney Page 34

**往期补习课件证据**
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_0`：3. 3. 3 继续划分
Level = Mid
划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior
Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG：
计算 Junior 子集的熵：
PhD 特征：
PhD=Yes: 2 个 (0 True, 2 False) → 熵 0
PhD=No: 3 个 (3 True, 0 False) → 熵 0
条件熵 = 0，IG = 0. 97
Tweets 特征：
Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92
Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1
条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
Lang 
- 10 讲义.pdf · 第 8 页 · `10_讲义_d344dc1e_7_1`：95，IG ≈ 0. 02
因此 Junior 节点选择 PhD 划分，得到两个纯节点（PhD=Yes 全 False，PhD=No 全 True）。 Level=Senior
Level=Senior 节点（5 个：2 True, 3 False）可继续划分（可能选 Tweets 等），最终得到如 PDF 中的树。 3. 3. 4 预测 A15
A15 (Senior, R, No, No) 按照树：Level=Senior 分支，再根据其他特征到达叶节点，
最终预测为 False。

## T015 多类别信息增益计算示例 — 未发现

四类等概率数据（熵log2(4)=2）按A/B与C/D划分后，各分支条件熵为1，加权后为1，IG=2−1=1。

差异：补习资料无四类等概率数据按A/B与C/D划分、IG=2−1=1的多类别示例。
建议：补充多类别信息增益计算示例。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 10_decision_tree.pdf · 第 36 页 · `10_decision_tree_d8e30e66_35_0`：Test your understanding
– A dataset has four equally common classes: A, B, C and D. At
the root node, a split produces:
– Left branch: examples from classes A and B only
– Right branch: examples from classes C and D only
– Which statement is most accurate? – A. This is useless because each branch still contains more than one class
– B. This gives some information gain because each branch is less
u
- 10_decision_tree.pdf · 第 37 页 · `10_decision_tree_d8e30e66_36_0`：Let’s calculate the IG
– Entropy before the split
– 𝑙𝑜𝑔 4 = 2
2
– Entropy after the split:
– 0. 5 *1 + 0. 5*1 = 1
– IG = 2-1 = 1
Branch Probability of Conditional
landing in this Entropy
branch
Left 0. 5 1
right 0. 5 1
The University of Sydney Page 37
- 10_decision_tree.pdf · 第 37 页 · `10_decision_tree_d8e30e66_36_1`：5 1
right 0. 5 1
The University of Sydney Page 37

**往期补习课件证据**
- 未检索到可引用证据。

## T016 scikit-learn决策树分类器参数 — 未发现

重要参数包括max_depth（树最大深度）、criterion（gini：最小化误分类；entropy：最小化总不确定性）、splitter（best：为每个特征选最优阈值；random：选最佳随机阈值）。

差异：补习资料未涉及scikit-learn决策树分类器的max_depth、criterion、splitter等参数说明。
建议：补充sklearn决策树分类器主要参数。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 10_decision_tree.pdf · 第 35 页 · `10_decision_tree_d8e30e66_34_0`：Train a decision tree classifier in scikit-learn
Some important parameters:
– max_depth: the maximum depth of the tree. – criterion:
– gini: choose splits that minimise misclassification. – entropy: choose splits that minimise total uncertainty. – splitter:
– best: choose the optimal threshold for each feature. – random: choose the best random threshold for each feature. The University of Sydney P
- 10_decision_tree.pdf · 第 35 页 · `10_decision_tree_d8e30e66_34_1`：– random: choose the best random threshold for each feature. The University of Sydney Page 35

**往期补习课件证据**
- 未检索到可引用证据。

## T017 为何需要评估决策树 — 部分覆盖

ID3等算法是贪心的，只选当前步骤局部最优分裂，不保证全局最优树；决策树可能过拟合（持续分裂直到训练数据完全分类，可能捕捉噪声而非模式）；模型依赖训练数据，不同样本产生不同树，结果可能无法泛化到新数据；真正目标是在未见数据上表现良好。

差异：补习资料说明决策树易过拟合、需评估泛化能力，但未明确说明ID3的贪心性（局部最优不保证全局最优）及模型依赖训练数据导致不稳定的原因。
建议：补充ID3贪心性与模型依赖训练数据的说明。
置信度（仅供排序）：0.65

**最新学校课件证据**
- 10_decision_tree.pdf · 第 39 页 · `10_decision_tree_d8e30e66_38_0`：Why do we need to evaluate a decision tree
– Like many other machine learning algorithms, decision tree algorithms like
ID3 is greedy
– Choose the best split locally ( at the current step)
– Does not guarantee a globally optimal tree
– Decision tress can overfit
– Keep splitting until training data is perfectly classified
– may capture noise instead of patterns
– Model depends on training data
– D
- 10_decision_tree.pdf · 第 39 页 · `10_decision_tree_d8e30e66_38_1`：Why do we need to evaluate a decision tree
– Like many other machine learning algorithms, decision tree algorithms like
ID3 is greedy
– Choose the best split locally ( at the current step)
– Does not guarantee a globally optimal tree
– Decision tress can overfit
– Keep splitting until training data is perfectly classified
– may capture noise instead of patterns
– Model depends on training data
– D

**往期补习课件证据**
- 10 讲义.pdf · 第 9 页 · `10_讲义_d344dc1e_8_0`：4. 评估设置 EVALUATION SETUP
4. 1 可靠评估的重要性
需防止过拟合，确保模型泛化能力。 常用方法：训练/测试划分、交叉验证。 4. 2 模型复杂度与数据量
l 简单模型（如线性）在数据少时可能更好；复杂模型（如深度树）需要更多数据才能发挥优势。 l 训练误差随模型复杂度降低，测试误差先降后升（过拟合）。 l 数据量小，则复杂度较低的模型 1 更优。 数据量多，模型 2 最终会胜出。 l 即使拥有比现有数据更多的数据，两个模型的性能也不会有显著提升。 4. 3 泛化误差
l 目标是找到测试误差最低的点（欠拟合与过拟合的平衡）。 l 必须使用独立的测试集（或交叉验证）来估计泛化误差。 4. 4 剪枝 Pruning
决策树非常容易过拟合 (Overfitting)，即树长得太深、太复杂，把训练数据中的噪声也学进去了，导致在
新数据上表现很差。 剪枝可以降低模型复杂度。 
- 10 讲义.pdf · 第 15 页 · `10_讲义_d344dc1e_14_0`：5. 1. 3 为什么随机森林不容易过拟合？ 单一决策树如果很深，几乎可以把训练集完全拟合（准确率 100%），但在测试集上表现差。 但随机森林通过两个手段控制方差：
l Bagging：取平均/投票平滑了各棵树的极端输出。 l 特征随机：打破了最强的特征对每棵树的“垄断”，各棵树犯的错不相关，平均后
就抵消了。 一句话总结：每棵树单独看可能都在过拟合，但它们的错误方向不同，彼此抵消后，整体模
型的泛化能力反而很强。 “100 个偏激的专家，如果偏激的方向各不相同，投票结果反而可能是最公允的。 ”
5. 2 AdaBoost (Adaptive Boosting)
AdaBoost 是 Boosting 家族的开创者，其思想非常直观。 核心原理：调整样本权重
1. 初始化时，所有训练样本的权重相同。 2. 训练第一个弱分类器（通常是决策树桩，即只有一层的决策树）。 3. 根据分类结果，提高

## T018 训练准确率与测试准确率及复杂度控制 — 部分覆盖

训练表现不足够；高训练准确率与低测试准确率可能表明过拟合；控制树复杂度可用max_depth、min_samples_leaf（分裂后每个叶节点最少样本数）、min_samples_split（节点允许分裂前的最少样本数）；这些参数可通过交叉验证尝试不同组合来调优；示例中很深的树训练1.00/测试0.70，较小的树0.85/0.80。

差异：补习资料提及过拟合、训练/测试误差及交叉验证调参，但未给出max_depth、min_samples_leaf、min_samples_split的具体含义及深树1.00/0.70与较小树0.85/0.80的示例。
建议：补充复杂度控制参数定义及训练/测试准确率对比示例。
置信度（仅供排序）：0.60

**最新学校课件证据**
- 10_decision_tree.pdf · 第 40 页 · `10_decision_tree_d8e30e66_39_0`：Training Accuracy vs Test Accuracy
– Training performance is not enough
– High training accuracy and low test accuracy can indicate overfitting
– Controlling complexity of a tree
– max_depth
– min_samples_leaf: The minimum number of samples that each leaf node must contain after
a split. – min_samples_split: The minimum number of samples required at a node before the tree is
allowed to split it. –
- 10_decision_tree.pdf · 第 40 页 · `10_decision_tree_d8e30e66_39_1`：– Those parameters can be tuned by trying various parameter combinations
with cross-validation to choose the best combination
Model Training accuracy Test accuracy
Very deep tree 1. 00 0. 70
Smaller tree 0. 85 0. 80
The University of Sydney Page 40
- 10_decision_tree.pdf · 第 40 页 · `10_decision_tree_d8e30e66_39_2`：85 0. 80
The University of Sydney Page 40

**往期补习课件证据**
- 10 讲义.pdf · 第 9 页 · `10_讲义_d344dc1e_8_0`：4. 评估设置 EVALUATION SETUP
4. 1 可靠评估的重要性
需防止过拟合，确保模型泛化能力。 常用方法：训练/测试划分、交叉验证。 4. 2 模型复杂度与数据量
l 简单模型（如线性）在数据少时可能更好；复杂模型（如深度树）需要更多数据才能发挥优势。 l 训练误差随模型复杂度降低，测试误差先降后升（过拟合）。 l 数据量小，则复杂度较低的模型 1 更优。 数据量多，模型 2 最终会胜出。 l 即使拥有比现有数据更多的数据，两个模型的性能也不会有显著提升。 4. 3 泛化误差
l 目标是找到测试误差最低的点（欠拟合与过拟合的平衡）。 l 必须使用独立的测试集（或交叉验证）来估计泛化误差。 4. 4 剪枝 Pruning
决策树非常容易过拟合 (Overfitting)，即树长得太深、太复杂，把训练数据中的噪声也学进去了，导致在
新数据上表现很差。 剪枝可以降低模型复杂度。 
- 10 讲义.pdf · 第 11 页 · `10_讲义_d344dc1e_10_1`：优点：
提供更稳健的性能评估
通过多次评估取平均，交叉验证能有效减少因单次随机划分带来的偶然性波动，得到更接近模型真实性能
的估计。 有效防止过拟合
过拟合是指模型在训练数据上表现很好，但在未知数据上表现很差。 交叉验证通过在多个不同的数据子集
上进行验证，能更好地检验模型的泛化能力，帮助发现过拟合问题。 指导模型选择与超参数调优
当需要在不同模型（如决策树 vs. 支持向量机）或不同超参数（如正则化系数）之间做选择时，交叉验证
提供了一个公平的“竞技场”。 我们可以比较它们在相同交叉验证设置下的平均表现，从而选出最优方案。

## T019 二分类混淆矩阵与评价指标 — 已覆盖

混淆矩阵展示分类器犯的错误类型（TP、FN、FP、TN）；Accuracy=(TP+TN)/(TP+FN+FP+TN)；Precision=TP/(TP+FP)（预测为好应聘者中实际为好的比例）；Recall=TP/(TP+FN)（所有好应聘者中被模型找到的比例）；F1=2*Precision*Recall/(Precision+Recall)。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.90

**最新学校课件证据**
- 10_decision_tree.pdf · 第 41 页 · `10_decision_tree_d8e30e66_40_0`：Confusion matrix in binary classifier
– Confusion matrix shows what kinds of mistakes a classifier make
Interviewed well:
Predicted True Predicted False
Actual True True Positive (TP) False Negative (FN)
Actual False False Positive (FP) True Negative (TN)
𝑇𝑃+𝑇𝑁
Accuracy=
𝑇𝑃+𝐹𝑁+𝐹𝑃+𝑇𝑁
𝑇𝑃
Precision = among predicted good applicants, how
𝑇𝑃+𝐹𝑃
𝑇𝑃 many were actually good? Recall =
𝑇𝑃+𝐹𝑁
2∗𝑃𝑟𝑒𝑐𝑖𝑠𝑖𝑜𝑛∗𝑅𝑒𝑐
- 10_decision_tree.pdf · 第 41 页 · `10_decision_tree_d8e30e66_40_1`：Confusion matrix in binary classifier
– Confusion matrix shows what kinds of mistakes a classifier make
Interviewed well:
Predicted True Predicted False
Actual True True Positive (TP) False Negative (FN)
Actual False False Positive (FP) True Negative (TN)
𝑇𝑃+𝑇𝑁
Accuracy=
𝑇𝑃+𝐹𝑁+𝐹𝑃+𝑇𝑁
𝑇𝑃
Precision = among predicted good applicants, how
𝑇𝑃+𝐹𝑃
𝑇𝑃 many were actually good? Recall =
𝑇𝑃+𝐹𝑁
2∗𝑃𝑟𝑒𝑐𝑖𝑠𝑖𝑜𝑛∗𝑅𝑒𝑐

**往期补习课件证据**
- 10 讲义.pdf · 第 10 页 · `10_讲义_d344dc1e_9_0`：后剪枝 (Post-pruning)：先让树充分生长，再砍掉多余的分支。 l 方法：REP (错误率降低剪枝)、PEP (悲观错误剪枝)。 l 优点：通常比预剪枝效果更好，但计算成本高。 4. 4 混淆矩阵 confusion matrix
混淆矩阵（Confusion Matrix）是评估分类模型性能的核心工具。 它通过一个表格，清晰地展示模型预测结
果与真实情况的对比，让我们能直观地看到模型“混淆”了哪些类别，从而进行更深入的诊断。 准确率 (Accuracy)
公式：(TP + TN) / (TP + TN + FP + FN)
含义：模型所有预测中，正确的比例是多少？ 注意：在样本类别不平衡时（如99%正常，1%欺诈），准确率会具有欺骗性。 精确率 (Precision)
公式：TP / (TP + FP)
含义：在所有被模型预测为正例的样本中，有多少是真正的正例？ 它关心的是预测
- 10 讲义.pdf · 第 10 页 · `10_讲义_d344dc1e_9_1`：F1分数 (F1-Score)
公式：2 * (Precision * Recall) / (Precision + Recall)
含义：精确率和召回率的调和平均数。 当需要同时兼顾精确率和召回率时，这是一个很好的综合指标。 只看单一的准确率指标，可能会掩盖模型的真实问题。 混淆矩阵的价值在于：
揭示类别不平衡下的真相
一个模型在欺诈检测任务中，即使总是预测“无欺诈”，也能获得 99%的准确率（如果只有 1%的欺诈样
本）。 但它的混淆矩阵会显示，它一个欺诈行为都没抓到（TP=0, FN=全部欺诈样本）。 指导不同场景下的决策权衡
不同类型的错误，其代价天差地别。 混淆矩阵帮助我们根据业务需求做出权衡。
- 10 讲义.pdf · 第 19 页 · `10_讲义_d344dc1e_18_0`：案例二：混淆矩阵与评估指标计算
场景： 一个二分类模型用于预测病人是否患有某种疾病（Disease = Positive / Negative）。 模型在测试集上
的预测结果如下表（混淆矩阵）：
1. 计算模型的准确率 (Accuracy)。 2. 计算精确率 (Precision) 与召回率 (Recall)。 3. 计算 F1 分数。 4. 如果该疾病患病率很低（大约 10%），且漏诊（实际有病却预测为无病）的代价极高，你会更看重精
确率还是召回率？ 为什么？ 5. 假设我们调整分类阈值，使得模型变得更容易预测为 Positive（即更多样本被判为有病）。 那么精确
率和召回率会如何变化？ （只需定性说明）

## T020 多分类混淆矩阵 — 部分覆盖

多分类时可将每个类依次视为“正类”，或使用每类一行一列的更大混淆矩阵（如鸢尾花三分类示例）。

差异：补习资料介绍混淆矩阵概念但仅以二分类为主，未说明多分类时每类依次视为正类或使用每类一行一列的大混淆矩阵及鸢尾花示例。
建议：补充多分类混淆矩阵的处理方式与示例。
置信度（仅供排序）：0.60

**最新学校课件证据**
- 10_decision_tree.pdf · 第 42 页 · `10_decision_tree_d8e30e66_41_0`：Confusion matrix for multi-class classifier
– For multi-class classification, we can treat each class as
“positive” in turn, or use a larger confusion matrix with one
row/column per class. Predicted setosa Predicted versicolor Predicted virginica
Actual setosa 16 0 0
Actual versicolor 0 16 1
Actual virginica 0 0 17
The University of Sydney Page 42
- 10_decision_tree.pdf · 第 42 页 · `10_decision_tree_d8e30e66_41_1`：Confusion matrix for multi-class classifier
– For multi-class classification, we can treat each class as
“positive” in turn, or use a larger confusion matrix with one
row/column per class. Predicted setosa Predicted versicolor Predicted virginica
Actual setosa 16 0 0
Actual versicolor 0 16 1
Actual virginica 0 0 17
The University of Sydney Page 42

**往期补习课件证据**
- 10 讲义.pdf · 第 10 页 · `10_讲义_d344dc1e_9_0`：后剪枝 (Post-pruning)：先让树充分生长，再砍掉多余的分支。 l 方法：REP (错误率降低剪枝)、PEP (悲观错误剪枝)。 l 优点：通常比预剪枝效果更好，但计算成本高。 4. 4 混淆矩阵 confusion matrix
混淆矩阵（Confusion Matrix）是评估分类模型性能的核心工具。 它通过一个表格，清晰地展示模型预测结
果与真实情况的对比，让我们能直观地看到模型“混淆”了哪些类别，从而进行更深入的诊断。 准确率 (Accuracy)
公式：(TP + TN) / (TP + TN + FP + FN)
含义：模型所有预测中，正确的比例是多少？ 注意：在样本类别不平衡时（如99%正常，1%欺诈），准确率会具有欺骗性。 精确率 (Precision)
公式：TP / (TP + FP)
含义：在所有被模型预测为正例的样本中，有多少是真正的正例？ 它关心的是预测

## T021 交叉验证 — 已覆盖

单一训练/测试划分可能运气好或坏；k折交叉验证将训练数据分成k折，训练k个临时模型并平均结果。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.90

**最新学校课件证据**
- 10_decision_tree.pdf · 第 43 页 · `10_decision_tree_d8e30e66_42_0`：Cross - Validation
– A single train/test split may
be lucky or unlucky
– In 𝑘-fold cross-validation:
– split the training data into 𝑘
folds
– train 𝑘 temporary models
– average the results
The University of Sydney Page 43

**往期补习课件证据**
- 10 讲义.pdf · 第 11 页 · `10_讲义_d344dc1e_10_0`：4. 5 交叉验证 cross valiadation
交叉验证 核心思想是通过反复将数据集划分为训练集和验证集，来更可靠、更稳健地衡量模型在未知数
据上的表现，即模型的“泛化能力”。 传统的模型评估方法是将数据一次性划分为训练集和测试集（例如7:3），这种方法简单，但存在两大问
题：
结果不稳定：评估结果高度依赖于单次随机划分。 如果测试集恰好包含异常样本或类别分布不均，结果就
可能产生偏差。 数据浪费：测试集只使用一次，未能充分利用所有数据来评估模型。 K折交叉验证
操作步骤如下：
l 分割：将整个数据集随机划分为 K 个大小相似、互不重叠的子集（称为“折”，Fold）。 K值通常取
5或10。 l 迭代：进行 K 次训练和验证。 每次选择其中1个折作为验证集，剩下的 K-1 个折作为训练集。 l 评估：在 K 次迭代中，每个折都会被用作一次验证集。 记录下每次验证的性能指标（如准确率
- 10 讲义.pdf · 第 11 页 · `10_讲义_d344dc1e_10_1`：优点：
提供更稳健的性能评估
通过多次评估取平均，交叉验证能有效减少因单次随机划分带来的偶然性波动，得到更接近模型真实性能
的估计。 有效防止过拟合
过拟合是指模型在训练数据上表现很好，但在未知数据上表现很差。 交叉验证通过在多个不同的数据子集
上进行验证，能更好地检验模型的泛化能力，帮助发现过拟合问题。 指导模型选择与超参数调优
当需要在不同模型（如决策树 vs. 支持向量机）或不同超参数（如正则化系数）之间做选择时，交叉验证
提供了一个公平的“竞技场”。 我们可以比较它们在相同交叉验证设置下的平均表现，从而选出最优方案。

## T022 用交叉验证选择参数 — 已覆盖

可用交叉验证选择重要模型参数（如决策树的最大树深度和最小叶样本数），使用sklearn的GridSearchCV寻找最佳取值。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.80

**最新学校课件证据**
- 10_decision_tree.pdf · 第 44 页 · `10_decision_tree_d8e30e66_43_0`：Using Cross-Validation to Select Parameters
– We can use cross-validation to
select important model
parameters (tune a tree when
the model is a decision tree)
– If we want to choose the
maximum tree depth and minimal
sample leaf parameter
– We can use from
GridSearchCV
sklearn to find the best value
The University of Sydney Page 44
- 10_decision_tree.pdf · 第 44 页 · `10_decision_tree_d8e30e66_43_1`：Using Cross-Validation to Select Parameters
– We can use cross-validation to
select important model
parameters (tune a tree when
the model is a decision tree)
– If we want to choose the
maximum tree depth and minimal
sample leaf parameter
– We can use from
GridSearchCV
sklearn to find the best value
The University of Sydney Page 44

**往期补习课件证据**
- 10 讲义.pdf · 第 11 页 · `10_讲义_d344dc1e_10_1`：优点：
提供更稳健的性能评估
通过多次评估取平均，交叉验证能有效减少因单次随机划分带来的偶然性波动，得到更接近模型真实性能
的估计。 有效防止过拟合
过拟合是指模型在训练数据上表现很好，但在未知数据上表现很差。 交叉验证通过在多个不同的数据子集
上进行验证，能更好地检验模型的泛化能力，帮助发现过拟合问题。 指导模型选择与超参数调优
当需要在不同模型（如决策树 vs. 支持向量机）或不同超参数（如正则化系数）之间做选择时，交叉验证
提供了一个公平的“竞技场”。 我们可以比较它们在相同交叉验证设置下的平均表现，从而选出最优方案。
- 10 讲义.pdf · 第 12 页 · `10_讲义_d344dc1e_11_0`：4. 6 网格搜索 grid search
网格搜索（Grid Search）是机器学习中一种基础且常用的超参数优化技术。 它通过系统地遍历所有预设的
超参数组合，来寻找能使模型性能达到最优的那一组。 步骤：
定义参数网格：首先，你为想要调整的超参数（如学习率、树的深度）指定一系列候选值。 遍历所有组合：网格搜索会生成这些值的所有可能组合，形成一个“网格”。 训练与评估：对于网格中的每一组超参数，它都会训练一个模型，并评估其性能。 选择最优：最终，它会选出在评估中表现最好的那一组超参数。 优点：
简单直接：原理易于理解，实现方便。 结果稳定：由于是穷举，只要搜索空间设置得当，就不会错过最优解。 缺点：
计算成本高：当超参数数量增多或每个参数的候选值变多时，需要训练的模型数量会呈指数级增长，非常
耗时。 不够智能：它不考虑参数之间的关联，只是机械地尝试所有组合。 交叉验证是网格搜索用来评估每

## T023 最终评估工作流 — 部分覆盖

先做训练/测试划分；在训练数据上尝试多种树设置并用交叉验证比较，选择最佳设置；用全部训练数据训练最终树；在留出测试数据上评估一次。

差异：补习资料涉及训练/测试划分、交叉验证与网格搜索，但未明确给出“用全部训练数据训练最终树、在留出测试集上仅评估一次”的完整工作流步骤。
建议：补充最终评估工作流的完整步骤。
置信度（仅供排序）：0.60

**最新学校课件证据**
- 10_decision_tree.pdf · 第 45 页 · `10_decision_tree_d8e30e66_44_0`：The final evaluation workflow
– Do a train/test split
– For the training data
– Try several tree settings
– Use cross-validation to compare them
– Choose the best setting
– Train final tree on all training data
– Evaluate once on held-out test data
The University of Sydney Page 45
- 10_decision_tree.pdf · 第 45 页 · `10_decision_tree_d8e30e66_44_1`：The final evaluation workflow
– Do a train/test split
– For the training data
– Try several tree settings
– Use cross-validation to compare them
– Choose the best setting
– Train final tree on all training data
– Evaluate once on held-out test data
The University of Sydney Page 45

**往期补习课件证据**
- 10 讲义.pdf · 第 9 页 · `10_讲义_d344dc1e_8_0`：4. 评估设置 EVALUATION SETUP
4. 1 可靠评估的重要性
需防止过拟合，确保模型泛化能力。 常用方法：训练/测试划分、交叉验证。 4. 2 模型复杂度与数据量
l 简单模型（如线性）在数据少时可能更好；复杂模型（如深度树）需要更多数据才能发挥优势。 l 训练误差随模型复杂度降低，测试误差先降后升（过拟合）。 l 数据量小，则复杂度较低的模型 1 更优。 数据量多，模型 2 最终会胜出。 l 即使拥有比现有数据更多的数据，两个模型的性能也不会有显著提升。 4. 3 泛化误差
l 目标是找到测试误差最低的点（欠拟合与过拟合的平衡）。 l 必须使用独立的测试集（或交叉验证）来估计泛化误差。 4. 4 剪枝 Pruning
决策树非常容易过拟合 (Overfitting)，即树长得太深、太复杂，把训练数据中的噪声也学进去了，导致在
新数据上表现很差。 剪枝可以降低模型复杂度。 
- 10 讲义.pdf · 第 11 页 · `10_讲义_d344dc1e_10_2`：支持向量机）或不同超参数（如正则化系数）之间做选择时，交叉验证
提供了一个公平的“竞技场”。 我们可以比较它们在相同交叉验证设置下的平均表现，从而选出最优方案。
- 10 讲义.pdf · 第 12 页 · `10_讲义_d344dc1e_11_1`：不够智能：它不考虑参数之间的关联，只是机械地尝试所有组合。 交叉验证是网格搜索用来评估每一组超参数性能的“标尺”或“裁判”。

## T024 为何考虑树集成 — 已覆盖

单棵决策树易解释但不稳定，训练数据的小变化可能产生不同树；深树常很好地拟合训练数据但泛化差；集成组合多棵树以提升预测性能。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.85

**最新学校课件证据**
- 10_decision_tree.pdf · 第 47 页 · `10_decision_tree_d8e30e66_46_0`：Why consider ensembles of trees
– A single decision tree is easy to
interpret, but can be unstable. Tree 1
– Small changes in the training data
may produce a different tree. Tree 2
– Deep trees often fit the training
Tree 3
data very well, but generalise
poorly. Vote / average
– Ensembles combine many trees to
improve predictive performance. The University of Sydney Page 47
- 10_decision_tree.pdf · 第 47 页 · `10_decision_tree_d8e30e66_46_1`：Vote / average
– Ensembles combine many trees to
improve predictive performance. The University of Sydney Page 47

**往期补习课件证据**
- 10 讲义.pdf · 第 13 页 · `10_讲义_d344dc1e_12_0`：5. 集成树
“决策树就像一位专家，非常专业，但也有自己的偏见和盲区。 如果只请一位专家，万一他判断错了怎么
办？ ”
集成决策树（Ensemble Decision Trees）通过组合多棵决策树，将多个“弱学习器”聚合成一个强大的“强
学习器”，从而显著提升模型的预测能力和稳定性。 根据构建这些树的方式不同，主要衍生出两大核心流
派：Bagging 和 Boosting。 Bagging (Bootstrap Aggregating)
并行地训练多个基学习器，然后通过投票（分类）或平均（回归）的方式整合结果。 其核心是降低方差，
代表作是随机森林。 Boosting
串行地训练基学习器，每一轮都致力于修正前一轮的错误。 其核心是降低偏差，代表算法包括 AdaBoost、
GBDT，以及它们的优化版本 XGBoost 和 LightGBM。
- 10 讲义.pdf · 第 15 页 · `10_讲义_d344dc1e_14_0`：5. 1. 3 为什么随机森林不容易过拟合？ 单一决策树如果很深，几乎可以把训练集完全拟合（准确率 100%），但在测试集上表现差。 但随机森林通过两个手段控制方差：
l Bagging：取平均/投票平滑了各棵树的极端输出。 l 特征随机：打破了最强的特征对每棵树的“垄断”，各棵树犯的错不相关，平均后
就抵消了。 一句话总结：每棵树单独看可能都在过拟合，但它们的错误方向不同，彼此抵消后，整体模
型的泛化能力反而很强。 “100 个偏激的专家，如果偏激的方向各不相同，投票结果反而可能是最公允的。 ”
5. 2 AdaBoost (Adaptive Boosting)
AdaBoost 是 Boosting 家族的开创者，其思想非常直观。 核心原理：调整样本权重
1. 初始化时，所有训练样本的权重相同。 2. 训练第一个弱分类器（通常是决策树桩，即只有一层的决策树）。 3. 根据分类结果，提高

## T025 集成学习基本思想 — 已覆盖

训练多个模型而非一个，组合其预测；群体可能比任何单一模型更可靠；对树而言个体模型通常是决策树；分类用多数投票，回归用平均。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.90

**最新学校课件证据**
- 10_decision_tree.pdf · 第 48 页 · `10_decision_tree_d8e30e66_47_0`：Ensemble learning: the basic idea
– Train multiple models instead
Tree A
of one. – Combine their predictions. Combine
Tree B Final
predictions
– The group can be more
reliable than any single
Tree C
model. – For trees, the individual
Classification: majority vote
models are usually decision
Regression: average
trees. The University of Sydney Page 48
- 10_decision_tree.pdf · 第 48 页 · `10_decision_tree_d8e30e66_47_1`：– For trees, the individual
Classification: majority vote
models are usually decision
Regression: average
trees. The University of Sydney Page 48

**往期补习课件证据**
- 10 讲义.pdf · 第 13 页 · `10_讲义_d344dc1e_12_0`：5. 集成树
“决策树就像一位专家，非常专业，但也有自己的偏见和盲区。 如果只请一位专家，万一他判断错了怎么
办？ ”
集成决策树（Ensemble Decision Trees）通过组合多棵决策树，将多个“弱学习器”聚合成一个强大的“强
学习器”，从而显著提升模型的预测能力和稳定性。 根据构建这些树的方式不同，主要衍生出两大核心流
派：Bagging 和 Boosting。 Bagging (Bootstrap Aggregating)
并行地训练多个基学习器，然后通过投票（分类）或平均（回归）的方式整合结果。 其核心是降低方差，
代表作是随机森林。 Boosting
串行地训练基学习器，每一轮都致力于修正前一轮的错误。 其核心是降低偏差，代表算法包括 AdaBoost、
GBDT，以及它们的优化版本 XGBoost 和 LightGBM。
- 10 讲义.pdf · 第 14 页 · `10_讲义_d344dc1e_13_1`：采样：从原始训练集中进行 N 次 Bootstrap 采样，生成 N 个不同的训练子集。 2. 建树：对每个子集，构建一棵决策树。 l 在生长过程中，每到一个节点，随机选择 m 个特征，从中选出最优分裂点。 l 注意：随机森林的树通常不进行剪枝，让它们充分生长，以保持低偏差。 3. 重复：重复上述步骤，生成由 T 棵树组成的“森林”。 4. 集成：
l 分类问题：采用多数投票 (Majority Voting)，得票最多的类别为最终结果。 l 回归问题：采用平均法 (Averaging)，取所有树预测值的平均数。
- 10 讲义.pdf · 第 14 页 · `10_讲义_d344dc1e_13_2`：集成：
l 分类问题：采用多数投票 (Majority Voting)，得票最多的类别为最终结果。 l 回归问题：采用平均法 (Averaging)，取所有树预测值的平均数。

## T026 随机森林 — 已覆盖

从训练数据抽取多个bootstrap样本，每个样本训练一棵树；每次分裂只考虑随机特征子集；通过投票或平均组合预测；主要效果是相比单棵深树降低方差。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.90

**最新学校课件证据**
- 10_decision_tree.pdf · 第 49 页 · `10_decision_tree_d8e30e66_48_0`：Random Forest: many diverse trees
– Start with many bootstrap samples
of the training data. Data
Tree Vote
sample
– Train one tree on each sample. Sample 1 T1
– At each split, consider only a
random subset of features. Final
Sample 2 T2
– Combine predictions by voting or
averaging. Sample 3 T3
– Main effect: reduce variance
compared with one deep tree. The University of Sydney Page 49
- 10_decision_tree.pdf · 第 49 页 · `10_decision_tree_d8e30e66_48_1`：Sample 3 T3
– Main effect: reduce variance
compared with one deep tree. The University of Sydney Page 49

**往期补习课件证据**
- 10 讲义.pdf · 第 14 页 · `10_讲义_d344dc1e_13_0`：5. 1 随机森林 Random forest
随机森林的“随机”体现在两个方面，这使得森林中的每一棵树都尽可能不同（去相关性），从而让集体
决策更稳健。 5. 1. 1 双重随机性
随机森林的精髓在于引入双重随机性，确保每棵树都不一样。 数据随机：Bootstrap 自助采样
假设你有 1000 个训练样本。 对每一棵树，我们有放回地随机抽取 1000 个样本（所以有些样本会被抽到
多次，有些一次都没抽到）。 l 被抽到的样本称为 袋内样本，用于训练这棵树。 l 没被抽到的样本约占 35. 8%（1/e），称为 袋外样本（OOB），可以当作天然的验证集。 直觉：每棵树看到的训练数据都不一样，就像每个医生见过的病人不完全相同。 特征随机：随机子空间
普通的决策树在每个节点分裂时，会从所有特征中选最佳的那个。 但在随机森林中，每棵树在分裂时只能
从随机选出的部分特征中选最佳的那个。 l 对分
- 10 讲义.pdf · 第 14 页 · `10_讲义_d344dc1e_13_1`：采样：从原始训练集中进行 N 次 Bootstrap 采样，生成 N 个不同的训练子集。 2. 建树：对每个子集，构建一棵决策树。 l 在生长过程中，每到一个节点，随机选择 m 个特征，从中选出最优分裂点。 l 注意：随机森林的树通常不进行剪枝，让它们充分生长，以保持低偏差。 3. 重复：重复上述步骤，生成由 T 棵树组成的“森林”。 4. 集成：
l 分类问题：采用多数投票 (Majority Voting)，得票最多的类别为最终结果。 l 回归问题：采用平均法 (Averaging)，取所有树预测值的平均数。
- 10 讲义.pdf · 第 15 页 · `10_讲义_d344dc1e_14_0`：5. 1. 3 为什么随机森林不容易过拟合？ 单一决策树如果很深，几乎可以把训练集完全拟合（准确率 100%），但在测试集上表现差。 但随机森林通过两个手段控制方差：
l Bagging：取平均/投票平滑了各棵树的极端输出。 l 特征随机：打破了最强的特征对每棵树的“垄断”，各棵树犯的错不相关，平均后
就抵消了。 一句话总结：每棵树单独看可能都在过拟合，但它们的错误方向不同，彼此抵消后，整体模
型的泛化能力反而很强。 “100 个偏激的专家，如果偏激的方向各不相同，投票结果反而可能是最公允的。 ”
5. 2 AdaBoost (Adaptive Boosting)
AdaBoost 是 Boosting 家族的开创者，其思想非常直观。 核心原理：调整样本权重
1. 初始化时，所有训练样本的权重相同。 2. 训练第一个弱分类器（通常是决策树桩，即只有一层的决策树）。 3. 根据分类结果，提高

## T027 梯度提升 — 部分覆盖

顺序而非独立地构建树；每棵新树关注当前集成仍做错的部分；预测逐步相加；每棵树是对当前模型的小修正；通常非常准确，但比随机森林对调参更敏感。

差异：补习资料介绍GBDT拟合残差（负梯度）、串行训练及对超参数敏感，但未明确表述“每棵新树关注当前集成仍做错的部分、预测逐步相加、每棵树是对当前模型的小修正”的梯度提升直觉。
建议：补充梯度提升的逐步修正直觉说明。
置信度（仅供排序）：0.70

**最新学校课件证据**
- 10_decision_tree.pdf · 第 50 页 · `10_decision_tree_d8e30e66_49_0`：Gradient Boosting: trees that correct early erros
– Build trees sequentially, not
independently. Tree 1 Tree 2 Tree 3 Final
– Each new tree focuses on what the
current ensemble still gets wrong. Initial errors Remaining errors
– Predictions are added together
step by step. Key intuition: each tree is a small correction
– Often very accurate, but more to the current model. sensitive to tuning than 
- 10_decision_tree.pdf · 第 50 页 · `10_decision_tree_d8e30e66_49_1`：sensitive to tuning than random
forest. The University of Sydney Page 50

**往期补习课件证据**
- 10 讲义.pdf · 第 17 页 · `10_讲义_d344dc1e_16_1`：Leaf-wise 策略若不加限制（如 max_depth），容易导致过拟合。 算法 所属流派 核心原理 主要优点 主要缺点
随机森林 Bagging 样本与特征双重随机，并行训练， 抗过拟合，鲁棒性 模型复杂，解释性差
投票/平均 强，易于使用
AdaBoost Boosting 迭代调整样本权重，关注错分样本 分类精度高，算法简 对噪声敏感
单
GBDT Boosting 串行训练，每棵树拟合前一轮的残 拟合能力强，精度高 训练慢，难并行，需
差（负梯度） 调参
LightGBM Boosting (优化) 基于GBDT，采用Leaf-wise、GOSS、 速度极快，内存占用 小数据集表现可能
EFB等技术加速 低 不佳，易过拟合

## T028 树模型比较 — 部分覆盖

单树：训练一棵树，优点是可解释性，风险是过拟合，常用参数max_depth、min_samples_leaf；随机森林：训练多棵独立树，优点是稳定、强基线，风险是可解释性较差，常用参数n_estimators、max_features；梯度提升：顺序构建树，优点常是高准确率，风险是对调参敏感，常用参数learning_rate、n_estimators。

差异：补习资料以表格对比随机森林、AdaBoost、GBDT、LightGBM的流派/原理/优缺点，但未按单树/随机森林/梯度提升三列给出训练方式、主要优势、主要风险及max_depth、n_estimators、max_features、learning_rate等参数对照。
建议：补充单树、随机森林、梯度提升的对照表及常用参数。
置信度（仅供排序）：0.60

**最新学校课件证据**
- 10_decision_tree.pdf · 第 52 页 · `10_decision_tree_d8e30e66_51_0`：Comparing tree models
Single Tree Random Forest Gradient Boosting
Training One tree Many independent Trees built sequentially
trees
Main strength Interpretability Stable, strong Often high accuracy
baseline
Main risk Overfitting Less interpretable Sensitive to tuning
Useful params max_depth n_estimators learning_rate
min_samples_leaf max_features n_estimators
The University of Sydney Page 52
- 10_decision_tree.pdf · 第 52 页 · `10_decision_tree_d8e30e66_51_1`：Comparing tree models
Single Tree Random Forest Gradient Boosting
Training One tree Many independent Trees built sequentially
trees
Main strength Interpretability Stable, strong Often high accuracy
baseline
Main risk Overfitting Less interpretable Sensitive to tuning
Useful params max_depth n_estimators learning_rate
min_samples_leaf max_features n_estimators
The University of Sydney Page 52

**往期补习课件证据**
- 10 讲义.pdf · 第 17 页 · `10_讲义_d344dc1e_16_1`：Leaf-wise 策略若不加限制（如 max_depth），容易导致过拟合。 算法 所属流派 核心原理 主要优点 主要缺点
随机森林 Bagging 样本与特征双重随机，并行训练， 抗过拟合，鲁棒性 模型复杂，解释性差
投票/平均 强，易于使用
AdaBoost Boosting 迭代调整样本权重，关注错分样本 分类精度高，算法简 对噪声敏感
单
GBDT Boosting 串行训练，每棵树拟合前一轮的残 拟合能力强，精度高 训练慢，难并行，需
差（负梯度） 调参
LightGBM Boosting (优化) 基于GBDT，采用Leaf-wise、GOSS、 速度极快，内存占用 小数据集表现可能
EFB等技术加速 低 不佳，易过拟合
- 10 讲义.pdf · 第 16 页 · `10_讲义_d344dc1e_15_0`：5. 3 GBDT (Gradient Boosting Decision Tree)
GBDT 将 Boosting 的思想与梯度下降优化算法相结合，使其理论基础更加坚实，应用也更加广泛。 核心原理：拟合残差（负梯度）
与 AdaBoost 调整样本权重不同，GBDT 的每一棵新树都是在拟合前一轮模型的残差（即真实值与当前模
型预测值之间的差距）。 从优化的角度看，这个过程等价于在损失函数空间中进行梯度下降，新树拟合的
是损失函数的负梯度。 主要优点：
拟合能力强，精度高：通过逐步逼近最优解，在很多任务上表现优异。 灵活性高：可以使用多种不同的损失函数（如回归中的均方误差，分类中的对数似然损失）。 局限性：
串行训练，难以并行化，训练速度较慢。 对超参数（如树的数量、学习率、树的深度）比较敏感，需要仔细调参。 5. 4 LightGBM (Light Gradient Boosting 

## T029 W10复习要点 — 部分覆盖

本周目标为学习有监督机器学习技术及Python工具；内容包括决策树、信息增益、评估设置、树集成（随机森林与梯度提升）；阅读Data Science from Scratch第17章；练习sklearn的决策树、随机森林与梯度提升。

差异：补习资料给出本周内容预览（决策树、纯度、ID3、评估设置、集成树、习题），但未提及Data Science from Scratch第17章阅读及sklearn决策树/随机森林/梯度提升练习的具体复习要点。
建议：补充阅读章节与sklearn练习的复习要点。
置信度（仅供排序）：0.60

**最新学校课件证据**
- 10_decision_tree.pdf · 第 54 页 · `10_decision_tree_d8e30e66_53_0`：W10 review: Decision tree
– Objective
Readings
– Learn techniques for supervised
– Data Science from Scratch, Ch. 17
machine learning, with tools in Python. Exercises
– Lecture
– sklearn: decision tree
– Decision tree
– sklearn: random forest
– Information gain
– sklearn: gradient boosting
– Evaluation setup
– Tree ensembles: random forest and
gradient boosting
The University of Sydney Page 54
- 10_decision_tree.pdf · 第 54 页 · `10_decision_tree_d8e30e66_53_1`：17
machine learning, with tools in Python. Exercises
– Lecture
– sklearn: decision tree
– Decision tree
– sklearn: random forest
– Information gain
– sklearn: gradient boosting
– Evaluation setup
– Tree ensembles: random forest and
gradient boosting
The University of Sydney Page 54

**往期补习课件证据**
- 10 讲义.pdf · 第 1 页 · `10_讲义_d344dc1e_0_0`：COMP5310
Week10 Decision Tree
TUTOR：Arya 学姐 时长：2 小时
本 周内容预览：
1 . 决策树
2 . 纯度
3 . ID3 算法
4 . 评估设置
5 . 集成树
6 . 课后习题
- 10 讲义.pdf · 第 9 页 · `10_讲义_d344dc1e_8_0`：4. 评估设置 EVALUATION SETUP
4. 1 可靠评估的重要性
需防止过拟合，确保模型泛化能力。 常用方法：训练/测试划分、交叉验证。 4. 2 模型复杂度与数据量
l 简单模型（如线性）在数据少时可能更好；复杂模型（如深度树）需要更多数据才能发挥优势。 l 训练误差随模型复杂度降低，测试误差先降后升（过拟合）。 l 数据量小，则复杂度较低的模型 1 更优。 数据量多，模型 2 最终会胜出。 l 即使拥有比现有数据更多的数据，两个模型的性能也不会有显著提升。 4. 3 泛化误差
l 目标是找到测试误差最低的点（欠拟合与过拟合的平衡）。 l 必须使用独立的测试集（或交叉验证）来估计泛化误差。 4. 4 剪枝 Pruning
决策树非常容易过拟合 (Overfitting)，即树长得太深、太复杂，把训练数据中的噪声也学进去了，导致在
新数据上表现很差。 剪枝可以降低模型复杂度。 
- 10 讲义.pdf · 第 13 页 · `10_讲义_d344dc1e_12_0`：5. 集成树
“决策树就像一位专家，非常专业，但也有自己的偏见和盲区。 如果只请一位专家，万一他判断错了怎么
办？ ”
集成决策树（Ensemble Decision Trees）通过组合多棵决策树，将多个“弱学习器”聚合成一个强大的“强
学习器”，从而显著提升模型的预测能力和稳定性。 根据构建这些树的方式不同，主要衍生出两大核心流
派：Bagging 和 Boosting。 Bagging (Bootstrap Aggregating)
并行地训练多个基学习器，然后通过投票（分类）或平均（回归）的方式整合结果。 其核心是降低方差，
代表作是随机森林。 Boosting
串行地训练基学习器，每一轮都致力于修正前一轮的错误。 其核心是降低偏差，代表算法包括 AdaBoost、
GBDT，以及它们的优化版本 XGBoost 和 LightGBM。
- 10 讲义.pdf · 第 14 页 · `10_讲义_d344dc1e_13_1`：采样：从原始训练集中进行 N 次 Bootstrap 采样，生成 N 个不同的训练子集。 2. 建树：对每个子集，构建一棵决策树。 l 在生长过程中，每到一个节点，随机选择 m 个特征，从中选出最优分裂点。 l 注意：随机森林的树通常不进行剪枝，让它们充分生长，以保持低偏差。 3. 重复：重复上述步骤，生成由 T 棵树组成的“森林”。 4. 集成：
l 分类问题：采用多数投票 (Majority Voting)，得票最多的类别为最终结果。 l 回归问题：采用平均法 (Averaging)，取所有树预测值的平均数。
