# 新旧课件覆盖报告：10_decision_tree.pdf / 10 Decision Tree.docx

> 本报告为 AI 辅助审核结果，不构成完全覆盖证明；请逐项检查原文证据。

## T001 决策树分类的基本概念 — 已覆盖

决策树通过一系列问题将观测映射到目标值，可视为if/else语句的层次结构；每个非叶节点标注一个属性并对应属性值测试，每个叶节点标注一个类别；模型直观且可解释，简单树的集成也能表现良好。

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
- 10 Decision Tree.docx · 决策树 · `tutoring_1384af84c831_section0_0_0`：决策树（Decision Tree）是一种常用的机器学习算法，广泛应用于分类和回归问题。 决策树通过树状结构来表示决策过程，每个内部节点代表一个特征或属性的测试，每个分支代表测试的结果，每个叶节点代表一个类别或值。
- 10 Decision Tree.docx · 1.3 决策树的优缺点 · `tutoring_1384af84c831_section5_0_0`：优点 易于理解和解释：决策树的结构直观，易于理解和解释。 处理多种数据类型：可以处理数值型和类别型数据。 不需要数据标准化：决策树不需要对数据进行标准化或归一化处理。 缺点 容易过拟合：决策树容易过拟合，特别是在数据集较小或树深度较大时。 对噪声敏感：决策树对噪声数据较为敏感，可能导致模型性能下降。 不稳定：数据的小变化可能导致生成完全不同的树。

## T002 ID3贪心决策树归纳算法 — 已覆盖

从包含全部训练样本的单一根节点开始；若节点所有样本属于同一类则标记为叶节点；否则对每个候选属性计算启发式或统计度量（如信息增益），选择最佳属性标注当前节点并分裂样本：类别属性每个值一个分支，连续属性选择分裂点a（如A<a、A≥a）；对每个子节点重复；当所有样本同类或无属性剩余（标为多数类）时停止。

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
- 10 Decision Tree.docx · 3.1 算法步骤（贪心、自顶向下递归） · `tutoring_1384af84c831_section11_0_0`：分而治之（Divide-and-conquer:）思想：递归划分数据，直到子集纯净（全属同一类） 1. 从根节点开始，所有训练样本都在根节点。 2. 若当前节点样本全部属于同一类别，则停止，标记为叶节点。 3. 否则，计算每个特征的信息增益，选择信息增益最大的特征作为当前节点的划分特征。 4. 根据该特征的每个取值，将样本划分到子节点。 5. 对每个子节点递归执行上述步骤。 5. 停止条件： - 所有样本属于同一类。 - 没有剩余特征可划分（用多数投票确定叶节点类别）。 - 树深度达到预设值。
- 10 Decision Tree.docx · 1.4 工作原理 · `tutoring_1384af84c831_section6_0_0`：决策树的构建过程通常被称为 “分而治之” (Divide and Conquer)。 最著名的算法有 ID3, C4. 5 和 CART。 决策树通过递归地将数据集分割成更小的子集来构建树结构。 具体步骤如下： 选择最佳特征：根据某种标准（如信息增益、基尼指数等）选择最佳特征进行分割。 分割数据集：根据选定的特征将数据集分成多个子集。 递归构建子树：对每个子集重复上述过程，直到满足停止条件（如所有样本属于同一类别、达到最大深度等）。 生成叶节点：当满足停止条件时，生成叶节点并赋予类别或值。

## T003 决策树的分治构建过程 — 已覆盖

采用分治策略：选择属性将数据划分为子集，检查子集是否纯净（全True或全False），若纯净则停止，否则重复；示例中先选择Level属性进行分裂。

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
- 10 Decision Tree.docx · 1.4 工作原理 · `tutoring_1384af84c831_section6_0_0`：决策树的构建过程通常被称为 “分而治之” (Divide and Conquer)。 最著名的算法有 ID3, C4. 5 和 CART。 决策树通过递归地将数据集分割成更小的子集来构建树结构。 具体步骤如下： 选择最佳特征：根据某种标准（如信息增益、基尼指数等）选择最佳特征进行分割。 分割数据集：根据选定的特征将数据集分成多个子集。 递归构建子树：对每个子集重复上述过程，直到满足停止条件（如所有样本属于同一类别、达到最大深度等）。 生成叶节点：当满足停止条件时，生成叶节点并赋予类别或值。
- 10 Decision Tree.docx · 3.1 算法步骤（贪心、自顶向下递归） · `tutoring_1384af84c831_section11_0_0`：分而治之（Divide-and-conquer:）思想：递归划分数据，直到子集纯净（全属同一类） 1. 从根节点开始，所有训练样本都在根节点。 2. 若当前节点样本全部属于同一类别，则停止，标记为叶节点。 3. 否则，计算每个特征的信息增益，选择信息增益最大的特征作为当前节点的划分特征。 4. 根据该特征的每个取值，将样本划分到子节点。 5. 对每个子节点递归执行上述步骤。 5. 停止条件： - 所有样本属于同一类。 - 没有剩余特征可划分（用多数投票确定叶节点类别）。 - 树深度达到预设值。
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_0`：Level = Mid 划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG： 计算 Junior 子集的熵： PhD 特征： PhD=Yes: 2 个 (0 True, 2 False) → 熵 0 PhD=No: 3 个 (3 True, 0 False) → 熵 0 条件熵 = 0，IG = 0. 97 Tweets 特征：

## T004 决策树构建示例（面试数据） — 已覆盖

以14条面试者训练数据（9 True/5 False）为例，特征为Level、Lang、Tweets、PhD，类标签为Interviewed well；依次按Level、Tweets、PhD等属性分裂，最终得到决策树并对新申请者A15（Senior, R, No, No）预测为False。

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
- 10_decision_tree.pdf · 第 9 页 · `10_decision_tree_d8e30e66_8_1`：A6 Junior R Yes Yes False
Junior
Mid A7 Mid R Yes Yes True
Senior
A8 Senior Python No No False
A9 Senior R Yes No True
A10 Junior Python Yes No True
A11 Senior Python Yes Yes True
A12 Mid Python No Yes True
A13 Mid Java Yes No True
A14 Junior Python No Yes False
New data: A15 Senior R No No ? The University of Sydney Page 9
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
- 10_decision_tree.pdf · 第 10 页 · `10_decision_tree_d8e30e66_9_1`：Decision Tree
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
- 10_decision_tree.pdf · 第 11 页 · `10_decision_tree_d8e30e66_10_1`：Senior Python Yes Yes True
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
True False Junior Python Yes No True
True False
Junior R Yes Yes False
2True 3False 3True 2False
Junior Python No Yes False
The University of Sydney Page 11
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
- 10_decision_tree.pdf · 第 12 页 · `10_decision_tree_d8e30e66_11_1`：Senior Junior A5 Junior R Yes No True
Mid
A6 Junior R Yes Yes False
True A7 Mid R Yes Yes True
Tweets
PhD? A8 Senior Python No No False
A9 Senior R Yes No True
Yes No Yes
No
A10 Junior Python Yes No True
A11 Senior Python Yes Yes True
True False True False A12 Mid Python No Yes True
A13 Mid Java Yes No True
A14 Junior Python No Yes False
A15 Senior R No No False
The University of Sydney Page 12

**往期补习课件证据**
- 10 Decision Tree.docx · 3.3 示例：面试者数据集 · `tutoring_1384af84c831_section13_0_0`：目标：预测新申请人 A15（Senior, R, No, No）是否面试好。
- 10 Decision Tree.docx · 3.3.4 预测 A15 · `tutoring_1384af84c831_section16_0_0`：A15 (Senior, R, No, No) 按照树：Level=Senior 分支，再根据其他特征到达叶节点， 最终预测为 False。
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_2`：95，IG ≈ 0. 02 因此 Junior 节点选择 PhD 划分，得到两个纯节点（PhD=Yes 全 False，PhD=No 全 True）。 Level=Senior Level=Senior 节点（5 个：2 True, 3 False）可继续划分（可能选 Tweets 等），最终得到如 PDF 中的树。

## T005 信息增益与属性选择 — 已覆盖

ID3选择信息增益最高的属性；在每个非叶节点询问哪个属性带来最大不确定性减少；信息增益是分裂前不确定性减去分裂后不确定性，增益越高分裂越好；不确定性用熵度量。

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
- 10 Decision Tree.docx · 2.3 信息增益Information Gain (IG) · `tutoring_1384af84c831_section8_0_0`：信息增益表示划分后信息熵 entropy的程度。 ID3与C4. 5选择信息增益最大的特征进行划分。
- 10 Decision Tree.docx · 3. ID3算法 · `tutoring_1384af84c831_section10_0_0`：ID3（Iterative Dichotomiser 3）采用信息增益（Information Gain）选择划分属性。
- 10 Decision Tree.docx · 3.3.2 依靠信息增益进行划分 · `tutoring_1384af84c831_section14_0_0`：总样本熵 总样本14个，true9个，false5个 条件熵 Level Level 信息增益最大，故根节点按 Level 划分。

## T006 信息增益的形式定义 — 部分覆盖

IG(Y|X)=H(Y)−H(Y|X)，其中Y为类标签，X为属性，H(Y)为分裂前Y的熵，H(Y|X)为给定X后Y的条件熵（分裂后不确定性）。

差异：补习资料仅说明信息增益表示划分后熵降低的程度，未给出 IG(Y|X)=H(Y)−H(Y|X) 的形式化公式及 H(Y|X) 条件熵定义。
建议：补充信息增益的形式化定义公式及条件熵符号说明。
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
- 10 Decision Tree.docx · 2.3 信息增益Information Gain (IG) · `tutoring_1384af84c831_section8_0_0`：信息增益表示划分后信息熵 entropy的程度。 ID3与C4. 5选择信息增益最大的特征进行划分。
- 10 Decision Tree.docx · 2.1 熵Entropy · `tutoring_1384af84c831_section7_0_0`：信息熵是用来衡量“不确定性”或“混乱程度”的指标。

## T007 熵的定义与解释 — 部分覆盖

H(Y)=−Σ p_i log2(p_i)，p_i=p(Y=y_i)，m为类别数；熵越高不确定性越大，熵范围从0（完全纯净）到log2(k)（k为类别数）；二分类最大熵为1。

差异：补习资料仅定性说明熵衡量不确定性，未给出 H(Y)=−Σp_i log2(p_i) 公式、熵范围0到log2(k)及二分类最大熵为1的说明。
建议：补充熵的数学定义、取值范围及二分类最大熵结论。
置信度（仅供排序）：0.65

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
- 10 Decision Tree.docx · 2.1 熵Entropy · `tutoring_1384af84c831_section7_0_0`：信息熵是用来衡量“不确定性”或“混乱程度”的指标。
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_0`：Level = Mid 划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG： 计算 Junior 子集的熵： PhD 特征： PhD=Yes: 2 个 (0 True, 2 False) → 熵 0 PhD=No: 3 个 (3 True, 0 False) → 熵 0 条件熵 = 0，IG = 0. 97 Tweets 特征：

## T008 熵计算示例（二分类） — 未发现

以50% Yes和50% No为例，H(Y)=−(0.5*log2(0.5)+0.5*log2(0.5))=1。

差异：无补习证据展示50% Yes/50% No 时熵计算为1的示例。
建议：补充二分类均衡分布熵=1的计算示例。
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

H(Y|X)=Σ p(X=v_i)*H(Y|X=v_i)，即Y的平均条件熵；示例中p(X=Math)=0.5、p(X=History)=0.25、p(X=CS)=0.25。

差异：补习资料有按权重加权条件熵的计算实例，但未给出 H(Y|X)=Σp(X=v_i)H(Y|X=v_i) 的一般公式及 Math/History/CS 概率示例。
建议：补充条件熵的一般定义公式。
置信度（仅供排序）：0.60

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
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_1`：97 Tweets 特征： Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92 Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1 条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02 Lang 特征： Lang=Python: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92 Lang=R: 2 个 (1 True, 1 False) → 熵 = 1 条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
- 10 Decision Tree.docx · 3.3.2 依靠信息增益进行划分 · `tutoring_1384af84c831_section14_0_0`：总样本熵 总样本14个，true9个，false5个 条件熵 Level Level 信息增益最大，故根节点按 Level 划分。

## T010 特定条件熵H(Y|X=v_i) — 部分覆盖

H(Y|X=v_i)是仅X取值为v_i的记录中Y的熵；示例中H(Y|X=Math)=1，H(Y|X=History)=0，H(Y|X=CS)=0。

差异：补习资料有子集内熵为0或约0.92的计算，但未明确给出 H(Y|X=v_i) 的定义及 Math/History/CS 具体示例。
建议：补充特定条件熵的定义与示例。
置信度（仅供排序）：0.55

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
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_0`：Level = Mid 划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG： 计算 Junior 子集的熵： PhD 特征： PhD=Yes: 2 个 (0 True, 2 False) → 熵 0 PhD=No: 3 个 (3 True, 0 False) → 熵 0 条件熵 = 0，IG = 0. 97 Tweets 特征：
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_1`：97 Tweets 特征： Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92 Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1 条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02 Lang 特征： Lang=Python: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92 Lang=R: 2 个 (1 True, 1 False) → 熵 = 1 条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02

## T011 条件熵计算示例 — 部分覆盖

由p与各条件熵加权求和得H(Y|X)=0.5*1+0.25*0+0.25*0=0.5。

差异：补习资料有加权条件熵计算，但未给出 0.5*1+0.25*0+0.25*0=0.5 这一具体示例。
建议：补充该条件熵数值示例。
置信度（仅供排序）：0.55

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

**往期补习课件证据**
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_1`：97 Tweets 特征： Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92 Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1 条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02 Lang 特征： Lang=Python: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92 Lang=R: 2 个 (1 True, 1 False) → 熵 = 1 条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
- 10 Decision Tree.docx · 3.3.2 依靠信息增益进行划分 · `tutoring_1384af84c831_section14_0_0`：总样本熵 总样本14个，true9个，false5个 条件熵 Level Level 信息增益最大，故根节点按 Level 划分。

## T012 信息增益计算示例 — 未发现

由H(Y)=1、H(Y|X)=0.5得IG(Y|X)=1−0.5=0.5。

差异：无补习证据展示 H(Y)=1、H(Y|X)=0.5 得 IG=0.5 的具体计算示例。
建议：补充信息增益数值计算示例。
置信度（仅供排序）：0.80

**最新学校课件证据**
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

## T013 熵与信息增益的理解练习 — 未发现

包含多道练习：20样本10正10负时熵高（=1）；15样本同类时熵为0；二分类熵在正负均衡时最高；100样本50/50时分裂B（左50正0负、右0正50负）更优；一个子节点纯净的分裂能减少部分不确定性；数值特征不应总在中位数分裂，最佳阈值应最大程度降低类别不确定性；分裂A（左右各25正25负）信息增益为0，分裂B更优。

差异：无补习证据覆盖这些理解练习题（20样本均衡熵、15同类熵0、二分类最大熵、100样本分裂比较、数值特征阈值、分裂A增益为0等）。
建议：补充对应练习题及解析。
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
- 10_decision_tree.pdf · 第 22 页 · `10_decision_tree_d8e30e66_21_1`：5 ∗ 𝑙𝑜𝑔 0. 5 = − 𝑙𝑜𝑔 = − − = 1
2 2 2
2
The University of Sydney Page 22
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
- 10_decision_tree.pdf · 第 24 页 · `10_decision_tree_d8e30e66_23_1`：when positive and negative examples are equally balanced
– D. when there are more positive than negative
The University of Sydney Page 24
- 10_decision_tree.pdf · 第 25 页 · `10_decision_tree_d8e30e66_24_0`：Test your understanding
– A node has 100 examples: 50 positive and 50 negative. Which
split is likely better? – A. Left: 25 positive, 25 negative; Right: 25 positive, 25 negative
– B. Left: 50 positive, 0 negative; Right: 0 positive, 50 negative
– C. Left: 45 positive, 45 negative; Right: 5 positive, 5 negative
– D. Left: 30 positive, 30 negative; Right: 20 positive, 20 negative
The University of 
- 10_decision_tree.pdf · 第 25 页 · `10_decision_tree_d8e30e66_24_1`：Left: 45 positive, 45 negative; Right: 5 positive, 5 negative
– D. Left: 30 positive, 30 negative; Right: 20 positive, 20 negative
The University of Sydney Page 25
- 10_decision_tree.pdf · 第 26 页 · `10_decision_tree_d8e30e66_25_0`：Test your understanding
– A split produces:
– Left child: 10 positive, 0 negative
– Right child: 40 positive, 50 negative
– Which statement is most accurate? – A. The split is useless because it is unbalance
– B. The split reduces some uncertainty because one child is pure
– C. The split must be the best split because one child is pure
– D. The split has zero information gain
The University of Syd
- 10_decision_tree.pdf · 第 26 页 · `10_decision_tree_d8e30e66_25_1`：The split must be the best split because one child is pure
– D. The split has zero information gain
The University of Sydney Page 26
- 10_decision_tree.pdf · 第 27 页 · `10_decision_tree_d8e30e66_26_0`：Test your understanding
– For a numeric feature in a decision tree, should we always split
at the median value? – A. Yes, because it creates equal-sized groups
– B. Yes, because equal-sized groups always maximise information gain
– C. No, because the best threshold is the one that most reduces class
uncertainty
– D. No, because decision trees cannot use numeric features
The University of Sydney Pa
- 10_decision_tree.pdf · 第 27 页 · `10_decision_tree_d8e30e66_26_1`：No, because the best threshold is the one that most reduces class
uncertainty
– D. No, because decision trees cannot use numeric features
The University of Sydney Page 27
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
- 10_decision_tree.pdf · 第 28 页 · `10_decision_tree_d8e30e66_27_1`：Split A, because it is balanced is less than 1
– B. Split B, because it reduces uncertainty more
For split B, there is
– C. They are equally good
some information
– D. Cannot say because the split must be 50/50 gain
The University of Sydney Page 28
- 10_decision_tree.pdf · 第 28 页 · `10_decision_tree_d8e30e66_27_2`：They are equally good
some information
– D. Cannot say because the split must be 50/50 gain
The University of Sydney Page 28

**往期补习课件证据**
- 未检索到可引用证据。

## T014 Level属性的信息增益计算 — 部分覆盖

H(Interviewed well)=H(9,5)=0.94；按Level分裂后条件熵约0.7；IG(Interviewed well|Level)=0.94−0.7=0.24。

差异：补习资料说明Level信息增益最大并按Level划分，但未给出 H(9,5)=0.94、条件熵0.7、IG=0.24 的具体数值计算。
建议：补充Level属性信息增益的完整数值计算。
置信度（仅供排序）：0.60

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

**往期补习课件证据**
- 10 Decision Tree.docx · 3.3.2 依靠信息增益进行划分 · `tutoring_1384af84c831_section14_0_0`：总样本熵 总样本14个，true9个，false5个 条件熵 Level Level 信息增益最大，故根节点按 Level 划分。
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_0`：Level = Mid 划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG： 计算 Junior 子集的熵： PhD 特征： PhD=Yes: 2 个 (0 True, 2 False) → 熵 0 PhD=No: 3 个 (3 True, 0 False) → 熵 0 条件熵 = 0，IG = 0. 97 Tweets 特征：

## T015 各属性信息增益比较 — 部分覆盖

IG(Interviewed well|Tweets)=0.15，IG(Interviewed well|PhD)=0.048，IG(Interviewed well|Lang)=0.029；Level信息增益最高，因此选择该属性是合理的。

差异：补习资料未给出 Tweets=0.15、PhD=0.048、Lang=0.029 的具体数值比较。
建议：补充各属性信息增益数值对比。
置信度（仅供排序）：0.55

**最新学校课件证据**
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
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_2`：95，IG ≈ 0. 02 因此 Junior 节点选择 PhD 划分，得到两个纯节点（PhD=Yes 全 False，PhD=No 全 True）。 Level=Senior Level=Senior 节点（5 个：2 True, 3 False）可继续划分（可能选 Tweets 等），最终得到如 PDF 中的树。
- 10 Decision Tree.docx · 2.3 信息增益Information Gain (IG) · `tutoring_1384af84c831_section8_0_0`：信息增益表示划分后信息熵 entropy的程度。 ID3与C4. 5选择信息增益最大的特征进行划分。

## T016 Junior子集上PhD属性的信息增益 — 已覆盖

Junior层级5条记录中H(Interviewed well)=H(3,2)=0.97；按PhD分裂后条件熵为0；IG(Interviewed well|PhD)=0.97，IG(Tweets)=0.02，IG(Lang)=0.02，PhD信息增益最高，故在Junior层级下一步选择PhD。

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
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_0`：Level = Mid 划分后，Level=Mid 的节点已纯净（全 True），停止。 Level=Junior Level=Junior 节点（5 个样本：3 True, 2 False）需继续划分。 计算 Junior 子集下各特征的 IG： 计算 Junior 子集的熵： PhD 特征： PhD=Yes: 2 个 (0 True, 2 False) → 熵 0 PhD=No: 3 个 (3 True, 0 False) → 熵 0 条件熵 = 0，IG = 0. 97 Tweets 特征：
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_1`：97 Tweets 特征： Tweets=Yes: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92 Tweets=No: 2 个 (1 True, 1 False) → 熵 = 1 条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02 Lang 特征： Lang=Python: 3 个 (2 True, 1 False) → 熵 ≈ 0. 92 Lang=R: 2 个 (1 True, 1 False) → 熵 = 1 条件熵 = 3/5×0. 92 + 2/5×1 = 0. 95，IG ≈ 0. 02
- 10 Decision Tree.docx · 3.3.3 继续划分 · `tutoring_1384af84c831_section15_0_2`：95，IG ≈ 0. 02 因此 Junior 节点选择 PhD 划分，得到两个纯节点（PhD=Yes 全 False，PhD=No 全 True）。 Level=Senior Level=Senior 节点（5 个：2 True, 3 False）可继续划分（可能选 Tweets 等），最终得到如 PDF 中的树。

## T017 scikit-learn决策树分类器参数 — 未发现

重要参数包括：max_depth（树的最大深度）；criterion（gini：选择使误分类最小的分裂；entropy：选择使总不确定性最小的分裂）；splitter（best：为每个特征选择最优阈值；random：为每个特征选择最佳随机阈值）。

差异：无补习证据说明scikit-learn决策树的max_depth、criterion(gini/entropy)、splitter(best/random)参数。
建议：补充sklearn决策树分类器关键参数说明。
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

## T018 四类别分裂的信息增益练习 — 未发现

四类等概率时分裂前熵log2(4)=2，分裂后0.5*1+0.5*1=1，IG=2−1=1；该分裂因每个分支不确定性降低而带来信息增益。

差异：无补习证据覆盖四类别等概率分裂的信息增益计算（log2(4)=2，分裂后1，IG=1）。
建议：补充该多分类信息增益练习及计算。
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
- 10_decision_tree.pdf · 第 36 页 · `10_decision_tree_d8e30e66_35_1`：This gives maximum information gain because the classes are evenly
divided
– D. This must be worse than a 50/50 random split
The University of Sydney Page 36
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

## T019 为何需要评估决策树 — 已覆盖

ID3等决策树算法是贪心的，只选择当前步骤的局部最优分裂，不保证全局最优树；决策树可能过拟合（持续分裂直到训练数据完全分类，可能捕捉噪声而非模式）；模型依赖训练数据，不同样本产生不同树，结果可能无法泛化到新数据；真正目标是在未见数据上表现良好。

差异：无明确差异说明
建议：请教师核对后决定是否补充
置信度（仅供排序）：0.80

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
- 10 Decision Tree.docx · 4.4 剪枝Pruning · `tutoring_1384af84c831_section20_0_0`：决策树非常容易过拟合 (Overfitting)，即树长得太深、太复杂，把训练数据中的噪声也学进去了，导致在新数据上表现很差。 剪枝可以降低模型复杂度。 预剪枝 (Pre-pruning)：在构建树的过程中提前停止。 方法：限制树的最大深度、限制叶节点最少样本数。 缺点：可能具有“短视”问题（贪心算法的局限）。 后剪枝 (Post-pruning)：先让树充分生长，再砍掉多余的分支。 方法：REP (错误率降低剪枝)、PEP (悲观错误剪枝)。 优点：通常比预剪枝效果更好，但计算成本高。
- 10 Decision Tree.docx · 1.3 决策树的优缺点 · `tutoring_1384af84c831_section5_0_0`：优点 易于理解和解释：决策树的结构直观，易于理解和解释。 处理多种数据类型：可以处理数值型和类别型数据。 不需要数据标准化：决策树不需要对数据进行标准化或归一化处理。 缺点 容易过拟合：决策树容易过拟合，特别是在数据集较小或树深度较大时。 对噪声敏感：决策树对噪声数据较为敏感，可能导致模型性能下降。 不稳定：数据的小变化可能导致生成完全不同的树。

## T020 训练准确率与测试准确率及复杂度控制 — 部分覆盖

训练表现不足够；高训练准确率与低测试准确率可能表明过拟合；可通过max_depth、min_samples_leaf（分裂后每个叶节点最少样本数）、min_samples_split（节点允许分裂前的最少样本数）控制树复杂度，并用交叉验证尝试不同参数组合选择最佳组合；示例中很深的树训练1.00/测试0.70，较小的树0.85/0.80。

差异：补习资料涉及过拟合、剪枝、交叉验证调参，但未明确给出训练/测试准确率对比示例（1.00/0.70 vs 0.85/0.80）及min_samples_leaf、min_samples_split参数定义。
建议：补充训练/测试准确率对比示例及复杂度控制参数说明。
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
- 10 Decision Tree.docx · 4.4 剪枝Pruning · `tutoring_1384af84c831_section20_0_0`：决策树非常容易过拟合 (Overfitting)，即树长得太深、太复杂，把训练数据中的噪声也学进去了，导致在新数据上表现很差。 剪枝可以降低模型复杂度。 预剪枝 (Pre-pruning)：在构建树的过程中提前停止。 方法：限制树的最大深度、限制叶节点最少样本数。 缺点：可能具有“短视”问题（贪心算法的局限）。 后剪枝 (Post-pruning)：先让树充分生长，再砍掉多余的分支。 方法：REP (错误率降低剪枝)、PEP (悲观错误剪枝)。 优点：通常比预剪枝效果更好，但计算成本高。
- 10 Decision Tree.docx · 4.5 交叉验证cross valiadation · `tutoring_1384af84c831_section22_0_2`：优点：充分利用了所有数据，每个样本都参与了训练和验证；结果比单次划分更稳定。 优点：
提供更稳健的性能评估 通过多次评估取平均，交叉验证能有效减少因单次随机划分带来的偶然性波动，得到更接近模型真实性能的估计。 有效防止过拟合 过拟合是指模型在训练数据上表现很好，但在未知数据上表现很差。 交叉验证通过在多个不同的数据子集上进行验证，能更好地检验模型的泛化能力，帮助发现过拟合问题。 指导模型选择与超参数调优 当需要在不同模型（如决策树 vs. 支持向量机）或不同超参数（如正则化系数）之间做选择时，交叉验证提供了一个公平的“竞技场”。 我们可以比较它们在相同交叉验证设置下的平均表现，从而选出最优方案。

## T021 二分类混淆矩阵与评估指标 — 已覆盖

混淆矩阵展示分类器犯的错误类型：TP、FN、FP、TN；Accuracy=(TP+TN)/(TP+FN+FP+TN)；Precision=TP/(TP+FP)（预测为好申请者中实际为好的比例）；Recall=TP/(TP+FN)（所有好申请者中被模型找到的比例）；F1=2*Precision*Recall/(Precision+Recall)。

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
- 10 Decision Tree.docx · 4.4 混淆矩阵 confusion matrix · `tutoring_1384af84c831_section21_0_0`：混淆矩阵（Confusion Matrix）是评估分类模型性能的核心工具。 它通过一个表格，清晰地展示模型预测结果与真实情况的对比，让我们能直观地看到模型“混淆”了哪些类别，从而进行更深入的诊断。 准确率 (Accuracy) 公式：(TP + TN) / (TP + TN + FP + FN) 含义：模型所有预测中，正确的比例是多少？ 注意：在样本类别不平衡时（如99%正常，1%欺诈），准确率会具有欺骗性。 精确率 (Precision) 公式：TP / (TP + FP) 含义：在所有被模型预测为正例的样本中，有多少是真正的正例？ 它关心的是预测得“准不准”。
- 10 Decision Tree.docx · 4.4 混淆矩阵 confusion matrix · `tutoring_1384af84c831_section21_0_1`：含义：在所有被模型预测为正例的样本中，有多少是真正的正例？ 它关心的是预测得“准不准”。 召回率 (Recall) 公式：TP / (TP + FN) 含义：在所有真实的正例中，模型成功找出了多少？ 它关心的是找得“全不全”。 F1分数 (F1-Score) 公式：2 * (Precision * Recall) / (Precision + Recall) 含义：精确率和召回率的调和平均数。 当需要同时兼顾精确率和召回率时，这是一个很好的综合指标。 只看单一的准确率指标，可能会掩盖模型的真实问题。

## T022 多分类混淆矩阵 — 部分覆盖

多分类时可将每个类别依次视为“正类”，或使用每类一行一列的更大混淆矩阵。

差异：补习资料仅讨论二分类混淆矩阵，未说明多分类时每类依次视为正类或使用每类一行一列的更大混淆矩阵。
建议：补充多分类混淆矩阵的处理方式。
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
- 10 Decision Tree.docx · 4.4 混淆矩阵 confusion matrix · `tutoring_1384af84c831_section21_0_2`：当需要同时兼顾精确率和召回率时，这是一个很好的综合指标。 只看单一的准确率指标，可能会掩盖模型的真实问题。 混淆矩阵的价值在于： 揭示类别不平衡下的真相 一个模型在欺诈检测任务中，即使总是预测“无欺诈”，也能获得99%的准确率（如果只有1%的欺诈样本）。 但它的混淆矩阵会显示，它一个欺诈行为都没抓到（TP=0, FN=全部欺诈样本）。 指导不同场景下的决策权衡 不同类型的错误，其代价天差地别。 混淆矩阵帮助我们根据业务需求做出权衡。

## T023 交叉验证 — 已覆盖

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
- 10 Decision Tree.docx · 4.5 交叉验证cross valiadation · `tutoring_1384af84c831_section22_0_0`：交叉验证 核心思想是通过反复将数据集划分为训练集和验证集，来更可靠、更稳健地衡量模型在未知数据上的表现，即模型的“泛化能力”。 传统的模型评估方法是将数据一次性划分为训练集和测试集（例如7:3），这种方法简单，但存在两大问题： 结果不稳定：评估结果高度依赖于单次随机划分。 如果测试集恰好包含异常样本或类别分布不均，结果就可能产生偏差。 数据浪费：测试集只使用一次，未能充分利用所有数据来评估模型。 K折交叉验证 操作步骤如下： 分割：将整个数据集随机划分为 K 个大小相似、互不重叠的子集（称为“折”，Fold）。 K值通常取5或10。
- 10 Decision Tree.docx · 4.5 交叉验证cross valiadation · `tutoring_1384af84c831_section22_0_1`：分割：将整个数据集随机划分为 K 个大小相似、互不重叠的子集（称为“折”，Fold）。 K值通常取5或10。 迭代：进行 K 次训练和验证。 每次选择其中1个折作为验证集，剩下的 K-1 个折作为训练集。 评估：在 K 次迭代中，每个折都会被用作一次验证集。 记录下每次验证的性能指标（如准确率）。 平均：最后，计算 K 次验证结果的平均值，作为模型最终的 performance 评估。 优点：充分利用了所有数据，每个样本都参与了训练和验证；结果比单次划分更稳定。 优点：
提供更稳健的性能评估

## T024 用交叉验证选择参数 — 部分覆盖

可用交叉验证选择重要模型参数（如决策树的最大树深度和最小叶样本数），使用sklearn的GridSearchCV寻找最佳值。

差异：补习资料提到交叉验证用于超参数调优及网格搜索，但未明确提及用GridSearchCV选择最大树深度和最小叶样本数。
建议：补充GridSearchCV调参的具体用法。
置信度（仅供排序）：0.60

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
- 10 Decision Tree.docx · 4.5 交叉验证cross valiadation · `tutoring_1384af84c831_section22_0_3`：支持向量机）或不同超参数（如正则化系数）之间做选择时，交叉验证提供了一个公平的“竞技场”。 我们可以比较它们在相同交叉验证设置下的平均表现，从而选出最优方案。
- 10 Decision Tree.docx · 4.6 网格搜索grid search · `tutoring_1384af84c831_section23_0_1`：简单直接：原理易于理解，实现方便。 结果稳定：由于是穷举，只要搜索空间设置得当，就不会错过最优解。 缺点： 计算成本高：当超参数数量增多或每个参数的候选值变多时，需要训练的模型数量会呈指数级增长，非常耗时。 不够智能：它不考虑参数之间的关联，只是机械地尝试所有组合。 交叉验证是网格搜索用来评估每一组超参数性能的“标尺”或“裁判”。

## T025 最终评估工作流 — 部分覆盖

先做训练/测试划分；在训练数据上尝试多种树设置并用交叉验证比较，选择最佳设置；在全部训练数据上训练最终树；在留出测试数据上评估一次。

差异：补习资料涉及训练/测试划分与交叉验证，但未完整给出“训练/测试划分→交叉验证选参→全训练集训练→留出测试集评估一次”的完整工作流。
建议：补充最终评估工作流的完整步骤。
置信度（仅供排序）：0.55

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
- 10 Decision Tree.docx · 4.1 可靠评估的重要性 · `tutoring_1384af84c831_section17_0_0`：需防止过拟合，确保模型泛化能力。 常用方法：训练/测试划分、交叉验证。
- 10 Decision Tree.docx · 4.5 交叉验证cross valiadation · `tutoring_1384af84c831_section22_0_0`：交叉验证 核心思想是通过反复将数据集划分为训练集和验证集，来更可靠、更稳健地衡量模型在未知数据上的表现，即模型的“泛化能力”。 传统的模型评估方法是将数据一次性划分为训练集和测试集（例如7:3），这种方法简单，但存在两大问题： 结果不稳定：评估结果高度依赖于单次随机划分。 如果测试集恰好包含异常样本或类别分布不均，结果就可能产生偏差。 数据浪费：测试集只使用一次，未能充分利用所有数据来评估模型。 K折交叉验证 操作步骤如下： 分割：将整个数据集随机划分为 K 个大小相似、互不重叠的子集（称为“折”，Fold）。 K值通常取5或10。
- 10 Decision Tree.docx · 案例三：交叉验证与模型选择（计算题） · `tutoring_1384af84c831_section33_0_0`：背景： 你训练了两种不同的决策树模型（Tree A 和 Tree B），并采用 5 折交叉验证评估其性能。 以下是它们在每一折上的准确率： 计算 Tree A 和 Tree B 的平均准确率和标准差。 哪个模型的平均性能更好？ 哪个模型更稳定（即波动更小）？ 如果你需要部署一个对性能波动敏感的模型，你会选择哪个？ 为什么？ 假设你使用留出法（单次训练/测试划分，比例 80/20）得到的结果是 Tree A 更好，但交叉验证显示 Tree B 的平均性能更优。 你认为哪个评估结果更可信？ 解释原因。

## T026 为何考虑树集成 — 已覆盖

单棵决策树易解释但不稳定，训练数据的小变化可能产生不同树；深树常很好地拟合训练数据但泛化差；集成结合多棵树以提升预测性能。

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
- 10 Decision Tree.docx · 1.3 决策树的优缺点 · `tutoring_1384af84c831_section5_0_0`：优点 易于理解和解释：决策树的结构直观，易于理解和解释。 处理多种数据类型：可以处理数值型和类别型数据。 不需要数据标准化：决策树不需要对数据进行标准化或归一化处理。 缺点 容易过拟合：决策树容易过拟合，特别是在数据集较小或树深度较大时。 对噪声敏感：决策树对噪声数据较为敏感，可能导致模型性能下降。 不稳定：数据的小变化可能导致生成完全不同的树。
- 10 Decision Tree.docx · 5.集成树 · `tutoring_1384af84c831_section24_0_0`：“决策树就像一位专家，非常专业，但也有自己的偏见和盲区。 如果只请一位专家，万一他判断错了怎么办？ ” 集成决策树（Ensemble Decision Trees）通过组合多棵决策树，将多个“弱学习器”聚合成一个强大的“强学习器”，从而显著提升模型的预测能力和稳定性。 根据构建这些树的方式不同，主要衍生出两大核心流派：Bagging 和 Boosting。 Bagging (Bootstrap Aggregating) 并行地训练多个基学习器，然后通过投票（分类）或平均（回归）的方式整合结果。 其核心是降低方差，代表作是随机森林。
- 10 Decision Tree.docx · 5.1.3 为什么随机森林不容易过拟合？ · `tutoring_1384af84c831_section27_0_0`：单一决策树如果很深，几乎可以把训练集完全拟合（准确率 100%），但在测试集上表现差。 但随机森林通过两个手段控制方差： Bagging：取平均/投票平滑了各棵树的极端输出。 特征随机：打破了最强的特征对每棵树的“垄断”，各棵树犯的错不相关，平均后就抵消了。 一句话总结：每棵树单独看可能都在过拟合，但它们的错误方向不同，彼此抵消后，整体模型的泛化能力反而很强。 “100 个偏激的专家，如果偏激的方向各不相同，投票结果反而可能是最公允的。 ”

## T027 集成学习基本思想 — 已覆盖

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
- 10 Decision Tree.docx · 5.集成树 · `tutoring_1384af84c831_section24_0_0`：“决策树就像一位专家，非常专业，但也有自己的偏见和盲区。 如果只请一位专家，万一他判断错了怎么办？ ” 集成决策树（Ensemble Decision Trees）通过组合多棵决策树，将多个“弱学习器”聚合成一个强大的“强学习器”，从而显著提升模型的预测能力和稳定性。 根据构建这些树的方式不同，主要衍生出两大核心流派：Bagging 和 Boosting。 Bagging (Bootstrap Aggregating) 并行地训练多个基学习器，然后通过投票（分类）或平均（回归）的方式整合结果。 其核心是降低方差，代表作是随机森林。
- 10 Decision Tree.docx · 5.1.2 算法流程 · `tutoring_1384af84c831_section26_0_1`：分类问题：采用多数投票 (Majority Voting)，得票最多的类别为最终结果。 回归问题：采用平均法 (Averaging)，取所有树预测值的平均数。

## T028 随机森林 — 已覆盖

从训练数据的多个bootstrap样本开始，每个样本训练一棵树；每次分裂只考虑随机特征子集；通过投票或平均组合预测；主要效果是相比单棵深树降低方差。

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
- 10 Decision Tree.docx · 5.1.2 算法流程 · `tutoring_1384af84c831_section26_0_0`：构建随机森林的过程可以概括为以下四步： 采样：从原始训练集中进行 N 次 Bootstrap 采样，生成 N 个不同的训练子集。 建树：对每个子集，构建一棵决策树。 在生长过程中，每到一个节点，随机选择 m 个特征，从中选出最优分裂点。 注意：随机森林的树通常不进行剪枝，让它们充分生长，以保持低偏差。 重复：重复上述步骤，生成由 T 棵树组成的“森林”。 集成： 分类问题：采用多数投票 (Majority Voting)，得票最多的类别为最终结果。 回归问题：采用平均法 (Averaging)，取所有树预测值的平均数。
- 10 Decision Tree.docx · 5.1.1双重随机性 · `tutoring_1384af84c831_section25_0_0`：随机森林的精髓在于引入双重随机性，确保每棵树都不一样。 数据随机：Bootstrap 自助采样 假设你有 1000 个训练样本。 对每一棵树，我们有放回地随机抽取 1000 个样本（所以有些样本会被抽到多次，有些一次都没抽到）。 被抽到的样本称为 袋内样本，用于训练这棵树。 没被抽到的样本约占 35. 8%（1/e），称为 袋外样本（OOB），可以当作天然的验证集。 直觉：每棵树看到的训练数据都不一样，就像每个医生见过的病人不完全相同。 特征随机：随机子空间 普通的决策树在每个节点分裂时，会从所有特征中选最佳的那个。 但在随机森林中，每棵树在分裂时只能从随机选出的部分特征中选最佳的那个。
- 10 Decision Tree.docx · 5.1.3 为什么随机森林不容易过拟合？ · `tutoring_1384af84c831_section27_0_0`：单一决策树如果很深，几乎可以把训练集完全拟合（准确率 100%），但在测试集上表现差。 但随机森林通过两个手段控制方差： Bagging：取平均/投票平滑了各棵树的极端输出。 特征随机：打破了最强的特征对每棵树的“垄断”，各棵树犯的错不相关，平均后就抵消了。 一句话总结：每棵树单独看可能都在过拟合，但它们的错误方向不同，彼此抵消后，整体模型的泛化能力反而很强。 “100 个偏激的专家，如果偏激的方向各不相同，投票结果反而可能是最公允的。 ”

## T029 梯度提升 — 部分覆盖

顺序而非独立地构建树；每棵新树关注当前集成仍做错的部分；预测逐步相加；通常非常准确，但比随机森林对调参更敏感。

差异：补习资料说明GBDT串行训练、拟合残差、对超参数敏感，但未明确表述“每棵新树关注当前集成仍做错的部分、预测逐步相加”的梯度提升直觉。
建议：补充梯度提升逐步修正错误的直觉说明。
置信度（仅供排序）：0.65

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
- 10 Decision Tree.docx · 表格 1 · `tutoring_1384af84c831_section34_0_0`：算法 | 所属流派 | 核心原理 | 主要优点 | 主要缺点
随机森林 | Bagging | 样本与特征双重随机，并行训练，投票/平均 | 抗过拟合，鲁棒性强，易于使用 | 模型复杂，解释性差
AdaBoost | Boosting | 迭代调整样本权重，关注错分样本 | 分类精度高，算法简单 | 对噪声敏感
GBDT | Boosting | 串行训练，每棵树拟合前一轮的残差（负梯度） | 拟合能力强，精度高 | 训练慢，难并行，需调参
LightGBM | Boosting (优化) | 基于GBDT，采用Leaf-wise、GOSS、EFB等技术加速 | 速度极快，内存占用低 | 小数据集表现可能不佳，易过拟合

## T030 树模型比较 — 部分覆盖

单树：训练一棵树，优点是可解释性，风险是过拟合，常用参数max_depth、min_samples_leaf；随机森林：训练多棵独立树，优点是稳定、强基线，风险是可解释性较差，常用参数n_estimators、max_features；梯度提升：顺序构建树，优点常是高准确率，风险是对调参敏感，常用参数learning_rate、n_estimators。

差异：补习资料有随机森林与GBDT优缺点对比，但未给出单树/随机森林/梯度提升在训练方式、主要优势、风险、常用参数（max_depth、min_samples_leaf、n_estimators、max_features、learning_rate）上的完整对照表。
建议：补充三类树模型的完整对比表。
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
- 10 Decision Tree.docx · 表格 1 · `tutoring_1384af84c831_section34_0_0`：算法 | 所属流派 | 核心原理 | 主要优点 | 主要缺点
随机森林 | Bagging | 样本与特征双重随机，并行训练，投票/平均 | 抗过拟合，鲁棒性强，易于使用 | 模型复杂，解释性差
AdaBoost | Boosting | 迭代调整样本权重，关注错分样本 | 分类精度高，算法简单 | 对噪声敏感
GBDT | Boosting | 串行训练，每棵树拟合前一轮的残差（负梯度） | 拟合能力强，精度高 | 训练慢，难并行，需调参
LightGBM | Boosting (优化) | 基于GBDT，采用Leaf-wise、GOSS、EFB等技术加速 | 速度极快，内存占用低 | 小数据集表现可能不佳，易过拟合
- 10 Decision Tree.docx · 5.3 GBDT (Gradient Boosting Decision Tree) · `tutoring_1384af84c831_section29_0_1`：拟合能力强，精度高：通过逐步逼近最优解，在很多任务上表现优异。 灵活性高：可以使用多种不同的损失函数（如回归中的均方误差，分类中的对数似然损失）。 局限性： 串行训练，难以并行化，训练速度较慢。 对超参数（如树的数量、学习率、树的深度）比较敏感，需要仔细调参。
- 10 Decision Tree.docx · 5.1.3 为什么随机森林不容易过拟合？ · `tutoring_1384af84c831_section27_0_0`：单一决策树如果很深，几乎可以把训练集完全拟合（准确率 100%），但在测试集上表现差。 但随机森林通过两个手段控制方差： Bagging：取平均/投票平滑了各棵树的极端输出。 特征随机：打破了最强的特征对每棵树的“垄断”，各棵树犯的错不相关，平均后就抵消了。 一句话总结：每棵树单独看可能都在过拟合，但它们的错误方向不同，彼此抵消后，整体模型的泛化能力反而很强。 “100 个偏激的专家，如果偏激的方向各不相同，投票结果反而可能是最公允的。 ”
