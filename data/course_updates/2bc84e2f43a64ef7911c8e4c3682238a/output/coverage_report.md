# 新旧课件覆盖报告：09_linear_regression_and_logistic_regression.pdf / 9 Linear Regression & Logistic Regression .docx

> 本报告为 AI 辅助审核结果，不构成完全覆盖证明；请逐项检查原文证据。

## T001 监督学习与预测建模概述 — 已覆盖

监督机器学习任务包括简单线性回归、多元线性回归、逻辑回归、决策树和朴素贝叶斯。预测建模从可用数据中预测结果，学习函数 Ŷ=f(X)，X 为输入特征，Y 为实际目标值，Ŷ 为预测目标值；Y 为数值时是回归，Y 为类别时是分类。

差异：补习资料覆盖监督学习定义、y=f(X)映射、回归/分类区分及线性回归、逻辑回归、决策树等算法，但未明确列出朴素贝叶斯。
建议：补充朴素贝叶斯作为监督学习算法的说明。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 3 页 · `09_linear_regression_50c9a546_2_0`：Supervised Learning:
– We’ll now focus on supervised machine learning techniques
– Simple linear regression
– Multiple linear regression
– Logistic regression
– Decision tree
– Naïve Bayes
The University of Sydney Page 3
- 09_linear_regression_and_logistic_regression.pdf · 第 5 页 · `09_linear_regression_50c9a546_4_0`：Predictive Modelling
– Many data science problems
Carbon Purity involve predicting an outcome
Refund Status Income Cheat
level(%) (%)
Yes Single 125K No from available data. 0. 99 90. 01
෠
No Married 100K No 𝑋 → 𝑌
1. 02 86. 05
No Single 70K No
– A predictive model learns a
Yes Married 120K No 1. 15 91. 43
function
No Divorced 95K Yes
1. 29 93. 74 ෠
𝑌 = 𝑓(𝑋)
No Single 85K Yes
1. 46 96. 73
Yes Singl
- 09_linear_regression_and_logistic_regression.pdf · 第 5 页 · `09_linear_regression_50c9a546_4_1`：0. 87 87. 59 • 𝑌 ෠ : predicted target value
• If 𝑌 is numeric, the task is regression
Classification Carbon Purity • If 𝑌 is categoric, the task is
level(%) (%) classification
1. 32 ? The University of Sydney Page 5
Regression

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 表格 2 · `tutoring_8dc0d7188f3c_section39_0_0`：要素 | 说明 | 举例
输入（特征） | 描述每个样本的属性，通常记为 X | 用户的年龄、收入、历史购买次数
输出（标签） | 我们想要预测的目标，通常记为 y | 用户是否会流失（是/否）
训练数据 | 包含已知 (X, y) 对的样本集合 | 过去 10000 个用户的特征和流失情况
模型 | 从 X 到 y 的映射函数 y=f(X) | 逻辑回归模型、决策树
- 9 Linear Regression & Logistic Regression .docx · 3.1 模型形式 · `tutoring_8dc0d7188f3c_section23_0_0`：简单线性回归是一种监督学习（回归）方法，它假设一个自变量 x 和一个因变量 y 之间存在线性关系，目标是找到一条最佳拟合直线，使得预测值 y与真实值的误差最小： α：截距 Intercept（Y轴交点） β：斜率 Slope（X每增加1单位，Y的变化量） ε长误差项 error（真实值与预测值之差） Y:因变量 X自变量
- 9 Linear Regression & Logistic Regression .docx · 表格 1 · `tutoring_8dc0d7188f3c_section38_0_0`：对比维度 | 监督学习 | 无监督学习
数据 | 有标签 (X, y) | 无标签，只有 X
目标 | 预测 | 发现内在结构
典型任务 | 分类、回归 | 聚类、关联规则、降维
评估 | 准确率、F1、MSE 等（有标准答案） | 轮廓系数、SSE、业务可解释性（无标准答案）
- 9 Linear Regression & Logistic Regression .docx · 表格 4 · `tutoring_8dc0d7188f3c_section41_0_0`：算法 | 类型 | 核心思想
线性回归 | 回归 | 拟合一条直线（或超平面）使误差最小
逻辑回归 | 分类 | 用Sigmoid函数将线性输出映射为概率
决策树 | 分类/回归 | 通过一系列 if-else 规则做决策
随机森林 | 分类/回归 | 多棵决策树的投票/平均
支持向量机(SVM) | 分类/回归 | 寻找最大间隔的超平面
K近邻(KNN) | 分类/回归 | 看最近的K个邻居的标签

## T002 预测模型的三个关键组成部分 — 已覆盖

大多数监督预测模型包含三个关键组件：模型形式（f(X) 的形式，如简单线性回归、多元线性回归、逻辑回归）、学习方法（如何找参数，如最小二乘、交叉熵、梯度下降）、评估指标（预测有多好，如 MSE、RMSE、R²、分类指标）。

差异：补习资料给出“模型形式+成本函数+优化算法”三要素及评估指标，但未系统以“模型形式/学习方法/评估指标”三组件框架呈现。
建议：补充三组件框架的明确表述。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 7 页 · `09_linear_regression_50c9a546_6_0`：How Predictive Models are built
– Most supervised predictive models involve three key
components:
Component Key question In this lecture
Model Form What does 𝑓(𝑋) Simple linear regression, multiple
look like? linear regression, logistic regression
Learning method How do we find the cost functions (Least squares, cross-
parameters? entropy), gradient descent
Evaluation metric How good are the MSE, 
- 09_linear_regression_and_logistic_regression.pdf · 第 7 页 · `09_linear_regression_50c9a546_6_1`：entropy), gradient descent
Evaluation metric How good are the MSE, RMSE, 𝑅2 ,classification
predictions? metrics
The University of Sydney Page 7

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 6. Tips · `tutoring_8dc0d7188f3c_section36_0_0`：与简单 baseline 比较 简单模型 + 更多数据往往更好 始终在 held-out 数据上测试 任何预测模型 = 模型形式 Model Form + 成本函数 Cost Function + 优化算法
- 9 Linear Regression & Logistic Regression .docx · 表格 3 · `tutoring_8dc0d7188f3c_section40_0_0`：| 分类 | 回归
预测目标 | 离散的类别标签categoric | 连续的数值numeric
输出示例 | “是垃圾邮件”或“不是垃圾邮件” | 房价 453,200 元
典型算法 | 逻辑回归、决策树、SVM、KNN | 线性回归、决策树回归、SVR
评估指标 | 准确率、精确率、召回率、F1 | MSE、RMSE、R²
- 9 Linear Regression & Logistic Regression .docx · 5.5 损失函数 · `tutoring_8dc0d7188f3c_section35_0_0`：逻辑回归的代价函数使用 对数损失 (Log Loss) 或 交叉熵 (Cross-Entropy)： MSE 的问题：如果逻辑回归使用 MSE，损失函数会是非凸函数（Non-convex），有很多局部最小值，难以找到全局最优解。 Cross-Entropy 的优势：它是凸函数，能保证找到全局最优解。 优化方法：梯度下降

## T003 各回归模型的形式 — 部分覆盖

简单线性回归 ŷ=α+βx 输出数值；多元线性回归 ŷ=θ0+θ1x1+…+θdxd 输出数值；梯度下降是学习参数的优化方法；逻辑回归 p̂=P(Y=1|X) 输出概率/类别标签。

差异：补习资料有简单线性回归、多元线性回归、逻辑回归形式，但未明确将梯度下降列为学习参数的优化方法并给出更新形式。
建议：补充梯度下降作为参数学习优化方法的说明。
置信度（仅供排序）：0.75

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 6 页 · `09_linear_regression_50c9a546_5_0`：From predictive modelling to regression
– In this lecture, we will study different forms of the predictive
function 𝑓(𝑋)
Topic Model Form Output
Simple linear regression 𝑦ො = 𝛼 + 𝛽𝑥 Numeric value
Multiple linear regression 𝑦ො = 𝜃 + 𝜃 𝑥 + 𝜃 𝑥 +. . +𝜃 𝑥 Numeric value
0 1 1 1 1 𝑑 𝑑
Gradient descent Optimisation method for learning Updated model
parameters parameters
Logistic regression 𝑝Ƹ = 𝑃(𝑌 = 1|𝑋
- 09_linear_regression_and_logistic_regression.pdf · 第 6 页 · `09_linear_regression_50c9a546_5_1`：. +𝜃 𝑥 Numeric value
0 1 1 1 1 𝑑 𝑑
Gradient descent Optimisation method for learning Updated model
parameters parameters
Logistic regression 𝑝Ƹ = 𝑃(𝑌 = 1|𝑋) Probability/Class
label
The University of Sydney Page 6

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 表格 4 · `tutoring_8dc0d7188f3c_section41_0_0`：算法 | 类型 | 核心思想
线性回归 | 回归 | 拟合一条直线（或超平面）使误差最小
逻辑回归 | 分类 | 用Sigmoid函数将线性输出映射为概率
决策树 | 分类/回归 | 通过一系列 if-else 规则做决策
随机森林 | 分类/回归 | 多棵决策树的投票/平均
支持向量机(SVM) | 分类/回归 | 寻找最大间隔的超平面
K近邻(KNN) | 分类/回归 | 看最近的K个邻居的标签

## T004 简单线性回归 — 已覆盖

简单线性回归是寻找因变量 Y 与自变量 X 之间最佳拟合直线的方法，只有一个自变量。模型为 ŷi=α̂+β̂xi，α 为截距（直线与 y 轴交点），β 为斜率（方向和陡峭程度）。完整模型为 yi=α+βxi+εi，εi 为误差项。

差异：补习资料覆盖简单线性回归模型形式、截距、斜率、误差项及假设。
建议：无需补充。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 9 页 · `09_linear_regression_50c9a546_8_0`：Simple linear regression
– Method for finding the line
of best fit between the
dependent variable Y and
the independent variable X
– Simple: only one
independent variable
The University of Sydney Page 9
- 09_linear_regression_and_logistic_regression.pdf · 第 10 页 · `09_linear_regression_50c9a546_9_0`：What’s the line that best predicts 𝑌 from 𝑋? Slope
Intercept
መ
𝑦ෝ = 𝛼ො + 𝛽𝑥
𝑖 𝑖
The University of Sydney Page 10
- 09_linear_regression_and_logistic_regression.pdf · 第 11 页 · `09_linear_regression_50c9a546_10_0`：Fitting SLR: learn α and β
– α: Intercept (where the line crosses the y
axis)
– β: Slope (direction and steepness of the line)
𝑦 = 𝛼 + 𝛽𝑥 + 𝜀
– ε : Error (error term describing variation of
𝑖 𝑖 i
data)
– Y is the dependent variable (response). i
– X is the independent variable (predictor). i
The University of Sydney Page 11
- 09_linear_regression_and_logistic_regression.pdf · 第 11 页 · `09_linear_regression_50c9a546_10_1`：i
– X is the independent variable (predictor). i
The University of Sydney Page 11

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 3.1 模型形式 · `tutoring_8dc0d7188f3c_section23_0_0`：简单线性回归是一种监督学习（回归）方法，它假设一个自变量 x 和一个因变量 y 之间存在线性关系，目标是找到一条最佳拟合直线，使得预测值 y与真实值的误差最小： α：截距 Intercept（Y轴交点） β：斜率 Slope（X每增加1单位，Y的变化量） ε长误差项 error（真实值与预测值之差） Y:因变量 X自变量
- 9 Linear Regression & Logistic Regression .docx · 3.4 简单线性回归的假设与局限性 · `tutoring_8dc0d7188f3c_section26_0_0`：假设条件 线性关系：x 和 y 确实是线性关系。 误差项独立同分布，且服从均值为 0 的正态分布。 同方差性：误差的方差是常数，不随 x 变化。 何时不适用？ 数据明显是非线性趋势（可用多项式回归或其它模型） 存在异常值会严重影响拟合线 只有一个自变量，信息量有限（需要多元回归）

## T005 误差、残差与平方误差和 — 已覆盖

误差/残差是观测值与预测值之差 (y_actual−y_predicted)。平方误差和 SSE=Σ(yi−ŷi)²。

差异：补习资料覆盖残差平方和最小化与MSE，但SSE符号未明确出现。
建议：可补充SSE符号定义。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 12 页 · `09_linear_regression_50c9a546_11_0`：Fitting SLR: Minimize sum of squared errors
– Error/residual: difference
between the observed value
and predicted value
(𝑦 − 𝑦 )
𝑎𝑐𝑡𝑢𝑎𝑙 𝑝𝑟𝑒𝑑𝑖𝑐𝑡𝑒𝑑
– Sum of squared errors:
 = SSE =  ( y − yˆ ) 2
i i
Sum Error Square
http://home. ku. edu. tr/yihlamur/public_html/Bitirme%20Projesi%20-
%20Ger%C3%A7ek%20Data%20D%C3%BCzenlenmi%C5%9F/regression/
minitab%20regresion%20hakk%C4%B1nda%20g%C3%BCzel%20bilgil
- 09_linear_regression_and_logistic_regression.pdf · 第 12 页 · `09_linear_regression_50c9a546_11_1`：tr/yihlamur/public_html/Bitirme%20Projesi%20-
%20Ger%C3%A7ek%20Data%20D%C3%BCzenlenmi%C5%9F/regression/
minitab%20regresion%20hakk%C4%B1nda%20g%C3%BCzel%20bilgiler. ht
m
The University of Sydney Page 12

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 3.2 最小二乘法 least square models · `tutoring_8dc0d7188f3c_section24_0_0`：这是最常用的参数估计方法。 它的逻辑是：找到一条直线，使得所有真实数据点到这条直线的垂直距离（残差）的平方和最小。 我们希望这条直线能最好地拟合所有数据点。 最常用的准则是最小化残差平方和（RSS）：
- 9 Linear Regression & Logistic Regression .docx · 2.1.2均方误差MSE · `tutoring_8dc0d7188f3c_section2_0_0`：适用于回归问题（预测连续值，如房价、温度） 均方误差计算的是所有样本的预测值与真实值之差的平方的平均值。 特点：由于使用了平方，它对较大的误差惩罚更重（误差为 2 时，平方后贡献为 4；误差为 10 时，平方后贡献高达 100）。

## T006 最小二乘模型与普通最小二乘(OLS) — 已覆盖

最小二乘模型选择使平方残差尽可能小的参数，即 min Σ(yi−ŷi)²。普通最小二乘(OLS)是线性回归的标准最小二乘方法：模型对参数是线性的，所有观测点被平等对待。

差异：补习资料覆盖最小二乘最小化残差平方和，但OLS术语及“模型对参数线性、观测平等对待”未明确。
建议：补充OLS术语与性质。
置信度（仅供排序）：0.75

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 13 页 · `09_linear_regression_50c9a546_12_0`：Least Squares Models
– Many prediction models make predictions of the form:
– 𝑦ො = 𝑓 𝑥
𝑖 𝑖
– Simple linear regression is a special case of the general form
– A least squares model chooses model parameters to make the
squared residuals (errors) as small as possible
– minσ𝑛 ( 𝑦 − 𝑦ො )2
𝑖=1 𝑖 𝑖
– Ordinary Least Squares (OLS) is the standard least squares
method for linear regression:
– The model is l
- 09_linear_regression_and_logistic_regression.pdf · 第 13 页 · `09_linear_regression_50c9a546_12_1`：Least Squares Models
– Many prediction models make predictions of the form:
– 𝑦ො = 𝑓 𝑥
𝑖 𝑖
– Simple linear regression is a special case of the general form
– A least squares model chooses model parameters to make the
squared residuals (errors) as small as possible
– minσ𝑛 ( 𝑦 − 𝑦ො )2
𝑖=1 𝑖 𝑖
– Ordinary Least Squares (OLS) is the standard least squares
method for linear regression:
– The model is l

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 3.2 最小二乘法 least square models · `tutoring_8dc0d7188f3c_section24_0_0`：这是最常用的参数估计方法。 它的逻辑是：找到一条直线，使得所有真实数据点到这条直线的垂直距离（残差）的平方和最小。 我们希望这条直线能最好地拟合所有数据点。 最常用的准则是最小化残差平方和（RSS）：
- 9 Linear Regression & Logistic Regression .docx · 5.4模型训练 · `tutoring_8dc0d7188f3c_section34_0_0`：在线性回归中我们使用“最小二乘法”(Least Squares)，但在逻辑回归中，由于Sigmoid函数的存在，最小二乘法的损失函数会变成非凸函数（有很多局部最优解），无法通过简单的求导找到全局最优。

## T007 OLS 参数求解公式 — 部分覆盖

目标是找到使 (1/n)Σ(α̂+β̂xi−yi)² 最小的 α̂ 和 β̂（均方误差）。用微积分可得 β̂=Σ(xi−x̄)(yi−ȳ)/Σ(xi−x̄)²=cov(x,y)/Var(x)=r(x,y)*sd(y)/sd(x)，α̂=ȳ−β̂x̄，其中 x̄、ȳ 为均值，sd 为标准差，r 为相关系数。

差异：补习资料有最小二乘概念和MSE/RMSE/R²公式，但未给出β̂=cov(x,y)/Var(x)=r·sd(y)/sd(x)及α̂=ȳ−β̂x̄的闭式求解公式。
建议：补充OLS参数闭式解公式。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 14 页 · `09_linear_regression_50c9a546_13_0`：Ordinary Least Squares (OLS)
መ
– Our goal is to find the optimal value of 𝛼ො and 𝛽 such that
2
1
σ 𝑛 𝛼ො + 𝛽 መ 𝑥 − 𝑦 is the minimum
𝑖=1 𝑖 𝑖
𝑛
– Mean Square Error
– Using calculus
σ （𝑥 − 𝑥ҧ）（𝑦 − 𝑦ത） cov(𝑥, 𝑦) 𝑟(𝑥, 𝑦) ∗ 𝑠𝑑(𝑦)
መ 𝑖 𝑖
𝛽 = = =
σ(𝑥 − 𝑥ҧ)2 Var(𝑥) 𝑠𝑑(𝑥)
𝑖
መ
𝛼ො = 𝑦ത − 𝛽𝑥ҧ
1
𝑥ҧ =
σ𝑛
𝑥 is the average of 𝑥 values
𝑖=1 𝑖 𝑖
𝑛
1
sd is the standard deviation 𝑦ത =
σ𝑛
𝑦 is the average of 𝑦 values
𝑖=1 
- 09_linear_regression_and_logistic_regression.pdf · 第 14 页 · `09_linear_regression_50c9a546_13_1`：Ordinary Least Squares (OLS)
መ
– Our goal is to find the optimal value of 𝛼ො and 𝛽 such that
2
1
σ 𝑛 𝛼ො + 𝛽 መ 𝑥 − 𝑦 is the minimum
𝑖=1 𝑖 𝑖
𝑛
– Mean Square Error
– Using calculus
σ （𝑥 − 𝑥ҧ）（𝑦 − 𝑦ത） cov(𝑥, 𝑦) 𝑟(𝑥, 𝑦) ∗ 𝑠𝑑(𝑦)
መ 𝑖 𝑖
𝛽 = = =
σ(𝑥 − 𝑥ҧ)2 Var(𝑥) 𝑠𝑑(𝑥)
𝑖
መ
𝛼ො = 𝑦ത − 𝛽𝑥ҧ
1
𝑥ҧ =
σ𝑛
𝑥 is the average of 𝑥 values
𝑖=1 𝑖 𝑖
𝑛
1
sd is the standard deviation 𝑦ത =
σ𝑛
𝑦 is the average of 𝑦 values
𝑖=1 

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 3.2 最小二乘法 least square models · `tutoring_8dc0d7188f3c_section24_0_0`：这是最常用的参数估计方法。 它的逻辑是：找到一条直线，使得所有真实数据点到这条直线的垂直距离（残差）的平方和最小。 我们希望这条直线能最好地拟合所有数据点。 最常用的准则是最小化残差平方和（RSS）：
- 9 Linear Regression & Logistic Regression .docx · 表格 5 · `tutoring_8dc0d7188f3c_section42_0_0`：指标 | 公式 | 含义 | 范围
MSE (均方误差) |  | 误差平方的平均，越小越好 | [0, +∞)
RMSE |  | 和 y 同单位，更直观 | [0, +∞)
R² (决定系数) |  | 模型解释的方差比例 | (-∞, 1]，通常 ≥ 0，越近 1 越好

## T008 训练数据与测试数据 — 已覆盖

拟合模型与评估模型是不同的任务。预测建模通常将数据划分为训练集和测试集：训练数据用于学习模型参数，测试数据留出用于检查模型在未见数据上的表现。模型可能在训练数据上拟合很好但在新数据上表现很差。

差异：补习资料覆盖训练/测试集、过拟合泛化差、held-out测试，但未明确“训练数据学习参数、测试数据留出”的表格定义。
建议：补充训练/测试数据用途定义。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 15 页 · `09_linear_regression_50c9a546_14_0`：Training and Testing Data
– Fitting a model and evaluating a model are different tasks
– For predictive modelling, it is typical to split the data into
training/test set
– A model may fit the training data well but perform poorly on
new data
Dataset Purpose
Training data Used to learn the model parameters
Test data Kept aside to check how well the model
performs on unseen data
The University of Sy
- 09_linear_regression_and_logistic_regression.pdf · 第 15 页 · `09_linear_regression_50c9a546_14_1`：Training and Testing Data
– Fitting a model and evaluating a model are different tasks
– For predictive modelling, it is typical to split the data into
training/test set
– A model may fit the training data well but perform poorly on
new data
Dataset Purpose
Training data Used to learn the model parameters
Test data Kept aside to check how well the model
performs on unseen data
The University of Sy

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 2.3.3 恰到好处的拟合 · `tutoring_8dc0d7188f3c_section12_0_0`：这是理想状态。 模型足够复杂以学习数据中的关键模式，但又不会复杂到去学习随机噪声。 它能在训练集和未知的测试集上都表现良好。 表现：在训练集和测试集上的误差都较低，且两者接近。
- 9 Linear Regression & Logistic Regression .docx · 2.3.1 过拟合 overfit · `tutoring_8dc0d7188f3c_section10_0_0`：过拟合 是指模型过于复杂，不仅学习了数据中的真实规律，还"记住"了训练数据中的随机噪声和异常值。 表现：模型在训练数据上表现极好（误差极小），但在新的、未见过的数据上表现急剧下降，泛化能力差。 原因：模型复杂度过高，训练数据量太少。
- 9 Linear Regression & Logistic Regression .docx · 6. Tips · `tutoring_8dc0d7188f3c_section36_0_0`：与简单 baseline 比较 简单模型 + 更多数据往往更好 始终在 held-out 数据上测试 任何预测模型 = 模型形式 Model Form + 成本函数 Cost Function + 优化算法

## T009 MSE 与 RMSE 评估指标 — 已覆盖

MSE 可用于衡量拟合程度，OLS 直接最小化训练数据上的 MSE；但 MSE 以平方单位度量，难以在原问题背景下解释。RMSE 是 MSE 的平方根，与响应变量 y 同单位，更易解释。MSE 和 RMSE 都是尺度相关的，其值依赖 y 的尺度和范围。

差异：补习资料覆盖MSE/RMSE定义与同单位解释，但尺度相关性未明确。
建议：补充尺度相关性说明。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 16 页 · `09_linear_regression_50c9a546_15_0`：Evaluation Metrics
– Can we use Mean Squared Error (MSE) to measure how well the model fits the data? – Yes. OLS directly minimises MSE on the training data. – What is the limitation of MSE? – MSE is measured in squared units. – This makes it difficult to interpret in the original context of the problem. – A more interpretable metric: RMSE
– RMSE stands for Root Mean Squared Error. – RMSE is the s
- 09_linear_regression_and_logistic_regression.pdf · 第 16 页 · `09_linear_regression_50c9a546_15_1`：– RMSE is measured in the same unit as the response variable 𝑦. – However, both MSE and RMSE are scale-dependent
– Their values depend on the scale and range of 𝑦. – For example, predicting exam marks out of 100 and predicting annual income in dollars
may produce very different MSE/RMSE values, even if the models have similar relative
performance. The University of Sydney Page 16
- 09_linear_regression_and_logistic_regression.pdf · 第 16 页 · `09_linear_regression_50c9a546_15_2`：– For example, predicting exam marks out of 100 and predicting annual income in dollars
may produce very different MSE/RMSE values, even if the models have similar relative
performance. The University of Sydney Page 16

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 表格 5 · `tutoring_8dc0d7188f3c_section42_0_0`：指标 | 公式 | 含义 | 范围
MSE (均方误差) |  | 误差平方的平均，越小越好 | [0, +∞)
RMSE |  | 和 y 同单位，更直观 | [0, +∞)
R² (决定系数) |  | 模型解释的方差比例 | (-∞, 1]，通常 ≥ 0，越近 1 越好

## T010 MSE/RMSE 计算示例 — 部分覆盖

以学习时长预测考试分数为例（Mark=50+5*study hours），计算各学生误差与平方误差，MSE=(4+9+16+9)/4=9.5，RMSE=√9.5≈3.08，可解释为预测通常偏差约 3 分。MSE 和 RMSE 衡量预测误差大小但尺度相关，对 0~100 的分数可能可接受，但对 1~5 的满意度评分则很差。

差异：补习资料有MSE/RMSE公式与含义，但无学习时长预测考试分数的具体数值计算示例（MSE=9.5、RMSE≈3.08）。
建议：补充该计算示例。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 17 页 · `09_linear_regression_50c9a546_16_0`：Example: Predicting exam mark from study hours
Mark = 50 + 5 * study hours
y = 50 + 5x
(4 + 9 + 16 + 9)
Study Actual Predicted Squared 𝑀𝑆𝐸 = = 9. 5
Student Error (𝒚−𝒚ෝ)
hours (x) mark (y) mark(𝒚ෝ) error 4
𝑅𝑀𝑆𝐸 = 9. 5 ≈ 3. 08
A 2 58 60 -2 4
B 4 73 70 3 9
Based on RMSE, we can
say that the prediction is
C 6 76 80 -4 16
typically off by 3 points
D 8 93 90 3 9
MSE and RMSE measure the size of predicti
- 09_linear_regression_and_logistic_regression.pdf · 第 17 页 · `09_linear_regression_50c9a546_16_1`：5 ≈ 3. 08
A 2 58 60 -2 4
B 4 73 70 3 9
Based on RMSE, we can
say that the prediction is
C 6 76 80 -4 16
typically off by 3 points
D 8 93 90 3 9
MSE and RMSE measure the size of prediction errors, they are useful but scale dependent
This might be good enough for score between 0~100, but it is very bad if the prediction is for
satisfaction rating between 1~5. The University of Sydney Page 17
- 09_linear_regression_and_logistic_regression.pdf · 第 17 页 · `09_linear_regression_50c9a546_16_2`：08
A 2 58 60 -2 4
B 4 73 70 3 9
Based on RMSE, we can
say that the prediction is
C 6 76 80 -4 16
typically off by 3 points
D 8 93 90 3 9
MSE and RMSE measure the size of prediction errors, they are useful but scale dependent
This might be good enough for score between 0~100, but it is very bad if the prediction is for
satisfaction rating between 1~5. The University of Sydney Page 17

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 表格 5 · `tutoring_8dc0d7188f3c_section42_0_0`：指标 | 公式 | 含义 | 范围
MSE (均方误差) |  | 误差平方的平均，越小越好 | [0, +∞)
RMSE |  | 和 y 同单位，更直观 | [0, +∞)
R² (决定系数) |  | 模型解释的方差比例 | (-∞, 1]，通常 ≥ 0，越近 1 越好
- 9 Linear Regression & Logistic Regression .docx · 2.1.2均方误差MSE · `tutoring_8dc0d7188f3c_section2_0_0`：适用于回归问题（预测连续值，如房价、温度） 均方误差计算的是所有样本的预测值与真实值之差的平方的平均值。 特点：由于使用了平方，它对较大的误差惩罚更重（误差为 2 时，平方后贡献为 4；误差为 10 时，平方后贡献高达 100）。

## T011 决定系数 R² — 已覆盖

R² 是 y 中被解释的变异与总变异之比：R²=Σ(ŷi−ȳ)²/Σ(yi−ȳ)²=1−SSE/SST，SST 为平方总和。取值范围 0 到 1，衡量拟合优度，越高表示线性模型拟合越好。R²=0 表示模型不解释 y 的任何变异；R²=1 表示解释全部变异；R²=0.75 表示解释 75% 的变异。

差异：补习资料覆盖R²定义、范围与解释，但1−SSE/SST公式未明确。
建议：补充R²公式。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 18 页 · `09_linear_regression_50c9a546_17_0`：Coefficient of determination (R2)
– R2: ratio of explained variation in y to total variation in y
σ(𝑦ො − 𝑦ത) 2 σ 𝑦 − 𝑦ො 2 𝑆𝑆𝐸
𝑖 𝑖 𝑖
2
𝑅 = = 1 − = 1 −
σ 𝑦 − 𝑦ത 2 σ 𝑦 − 𝑦ത 2 𝑆𝑆𝑇 Sum of
𝑖 𝑖
squared
– Ranges from 0 to 1, measures goodness of fit, with higher
total
values indicating better fit for the linear model
– 𝑅2 = 0 : the model explains none of the variation in 𝑦
– 𝑅2 = 1 : the model explains al
- 09_linear_regression_and_logistic_regression.pdf · 第 18 页 · `09_linear_regression_50c9a546_17_1`：Coefficient of determination (R2)
– R2: ratio of explained variation in y to total variation in y
σ(𝑦ො − 𝑦ത) 2 σ 𝑦 − 𝑦ො 2 𝑆𝑆𝐸
𝑖 𝑖 𝑖
2
𝑅 = = 1 − = 1 −
σ 𝑦 − 𝑦ത 2 σ 𝑦 − 𝑦ത 2 𝑆𝑆𝑇 Sum of
𝑖 𝑖
squared
– Ranges from 0 to 1, measures goodness of fit, with higher
total
values indicating better fit for the linear model
– 𝑅2 = 0 : the model explains none of the variation in 𝑦
– 𝑅2 = 1 : the model explains al

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 3.3 R²  决定系数 Coefficient of determination · `tutoring_8dc0d7188f3c_section25_0_0`：拟合出直线后，我们需要量化它有多“好”。 R2 取值范围 [0,1]，越接近 1 表示模型拟合越好。 解释：因变量总变异中能被模型解释的比例。 注意：R2 高不代表模型预测准确（可能过拟合），需结合其他指标。 R2 = 0:模型几乎不解释y中的方差 R2 = 1:模型几乎完全解释y中的方差 R2 = 0. 75:模型解释了y中75%的方差
- 9 Linear Regression & Logistic Regression .docx · 表格 5 · `tutoring_8dc0d7188f3c_section42_0_0`：指标 | 公式 | 含义 | 范围
MSE (均方误差) |  | 误差平方的平均，越小越好 | [0, +∞)
RMSE |  | 和 y 同单位，更直观 | [0, +∞)
R² (决定系数) |  | 模型解释的方差比例 | (-∞, 1]，通常 ≥ 0，越近 1 越好

## T012 R² 计算示例 — 部分覆盖

以考试分数为例，SSE=4+9+16+9=38，ȳ=(58+73+76+93)/4=75，SST=(58−75)²+(73−75)²+(76−75)²+(93−75)²=618，R²=1−38/618=0.94。

差异：补习资料有R²概念与0.75示例，但无考试分数SSE=38、SST=618、R²=0.94的具体计算示例。
建议：补充该计算示例。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 19 页 · `09_linear_regression_50c9a546_18_0`：Example: Predicting exam mark from study hours
𝑆𝑆𝐸 = 4 + 9 + 16 + 9 = 38
Study Actual Predicted Squared
Student Error (𝒚−𝒚ෝ)
hours (x) mark (y) mark(𝒚ෝ) error
58 + 73 + 76 + 93
A 2 58 60 -2 4 𝑦ത = = 75
4
B 4 73 70 3 9
𝑆𝑆𝑇 = (58 − 75)2+(73 − 75)2
C 6 76 80 -4 16
+(76 − 75)2+(93 − 75)2= 618
D 8 93 90 3 9
38
𝑅2 = 1 − = 0. 94
618
The University of Sydney Page 19
- 09_linear_regression_and_logistic_regression.pdf · 第 19 页 · `09_linear_regression_50c9a546_18_1`：Example: Predicting exam mark from study hours
𝑆𝑆𝐸 = 4 + 9 + 16 + 9 = 38
Study Actual Predicted Squared
Student Error (𝒚−𝒚ෝ)
hours (x) mark (y) mark(𝒚ෝ) error
58 + 73 + 76 + 93
A 2 58 60 -2 4 𝑦ത = = 75
4
B 4 73 70 3 9
𝑆𝑆𝑇 = (58 − 75)2+(73 − 75)2
C 6 76 80 -4 16
+(76 − 75)2+(93 − 75)2= 618
D 8 93 90 3 9
38
𝑅2 = 1 − = 0. 94
618
The University of Sydney Page 19

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 3.3 R²  决定系数 Coefficient of determination · `tutoring_8dc0d7188f3c_section25_0_0`：拟合出直线后，我们需要量化它有多“好”。 R2 取值范围 [0,1]，越接近 1 表示模型拟合越好。 解释：因变量总变异中能被模型解释的比例。 注意：R2 高不代表模型预测准确（可能过拟合），需结合其他指标。 R2 = 0:模型几乎不解释y中的方差 R2 = 1:模型几乎完全解释y中的方差 R2 = 0. 75:模型解释了y中75%的方差

## T013 指标解释练习 — 部分覆盖

RMSE=4 的合理解释是模型预测通常偏离实际约 4 分；两个模型 RMSE 均为 3 时，RMSE=3 对百分制考试可能可接受但对 1–5 评分很差（尺度相关）；R²=0.72 的最佳解释是模型解释了响应变量约 72% 的变异。

差异：补习资料有R²解释与RMSE同单位，但无RMSE=4解释、RMSE=3尺度对比、R²=0.72解释等练习。
建议：补充指标解释练习题。
置信度（仅供排序）：0.75

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 20 页 · `09_linear_regression_50c9a546_19_0`：Test your understanding
– A model predicting exam marks out of 100 has: 𝑅𝑀𝑆𝐸 = 4
Which interpretation is most appropriate? A. The model explains 4% of the variation in exam marks. B. The model’s predictions are typically about 4 marks away
from the actual marks. C. The model has exactly 4 incorrect predictions. D. The model’s average squared error is 4 marks. The University of Sydney Page 20
- 09_linear_regression_and_logistic_regression.pdf · 第 21 页 · `09_linear_regression_50c9a546_20_0`：Test your understanding
– Two regression models have the same RMSE value of 3. Model A
predicts exam marks out of 100. Model B predicts a satisfaction
rating from 1 to 5. Which statement is most appropriate? A. The two models have equally good predictive performance. B. Model A is definitely worse because exam marks have a larger
range. C. RMSE = 3 may be acceptable for exam marks but very poor fo
- 09_linear_regression_and_logistic_regression.pdf · 第 22 页 · `09_linear_regression_50c9a546_21_0`：Test your understanding
– A regression model has 𝑅 2 = 0. 72, which statement is the best
interpretation? A. The model predicts 72% of the data points exactly. B. The model has an average prediction error of 0. 72. C. The model explains about 72% of the variation in the
response variable. D. The model’s slope is 0. 72. The University of Sydney Page 22

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 3.3 R²  决定系数 Coefficient of determination · `tutoring_8dc0d7188f3c_section25_0_0`：拟合出直线后，我们需要量化它有多“好”。 R2 取值范围 [0,1]，越接近 1 表示模型拟合越好。 解释：因变量总变异中能被模型解释的比例。 注意：R2 高不代表模型预测准确（可能过拟合），需结合其他指标。 R2 = 0:模型几乎不解释y中的方差 R2 = 1:模型几乎完全解释y中的方差 R2 = 0. 75:模型解释了y中75%的方差
- 9 Linear Regression & Logistic Regression .docx · 表格 5 · `tutoring_8dc0d7188f3c_section42_0_0`：指标 | 公式 | 含义 | 范围
MSE (均方误差) |  | 误差平方的平均，越小越好 | [0, +∞)
RMSE |  | 和 y 同单位，更直观 | [0, +∞)
R² (决定系数) |  | 模型解释的方差比例 | (-∞, 1]，通常 ≥ 0，越近 1 越好

## T014 多元线性回归 — 已覆盖

多元线性回归解释两个或多个自变量与一个因变量之间的关系，模型为 Y=α+β1X1+β2X2+…+βdXd。使用线性预测模型，选择 θ 以最小化平方预测误差；对 OLS 线性回归有闭式解。

差异：补习资料覆盖多元线性回归模型形式与超平面，但闭式解未明确。
建议：补充OLS闭式解说明。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 24 页 · `09_linear_regression_50c9a546_23_0`：Multiple linear regression
– Explain the relationship
between:
– two or more independent
Y = α + β X + β X + … + β X variables and
1 1 2 2 d d
– one dependent variable
The University of Sydney Page 24
- 09_linear_regression_and_logistic_regression.pdf · 第 25 页 · `09_linear_regression_50c9a546_24_0`：Learning the Regression Parameters
– We use a linear prediction model:
– We choose θ to minimise the squared prediction errors
Note normal MSE
would have a
denominator of n
– For Ordinary Least Squares linear regression, this has a closed-form
solution. The University of Sydney Page 25
- 09_linear_regression_and_logistic_regression.pdf · 第 25 页 · `09_linear_regression_50c9a546_24_1`：Learning the Regression Parameters
– We use a linear prediction model:
– We choose θ to minimise the squared prediction errors
Note normal MSE
would have a
denominator of n
– For Ordinary Least Squares linear regression, this has a closed-form
solution. The University of Sydney Page 25

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 4.1 模型形式 · `tutoring_8dc0d7188f3c_section28_0_0`：当有多个自变量 X1, X2, ,,, Xd以及一个因变量 时： （其中 X0 = 1 用于截距） 多元线性回归 研究一个因变量 yy 与 多个自变量 x1,x2,…,xp​ 之间的线性关系，目标是找到最优的超平面：
- 9 Linear Regression & Logistic Regression .docx · 3.4 简单线性回归的假设与局限性 · `tutoring_8dc0d7188f3c_section26_0_0`：假设条件 线性关系：x 和 y 确实是线性关系。 误差项独立同分布，且服从均值为 0 的正态分布。 同方差性：误差的方差是常数，不随 x 变化。 何时不适用？ 数据明显是非线性趋势（可用多项式回归或其它模型） 存在异常值会严重影响拟合线 只有一个自变量，信息量有限（需要多元回归）

## T015 scikit-learn 机器学习接口 — 未发现

scikit-learn 中 Fit(X,y) 将模型拟合到训练数据 X、y（X 为特征向量，y 为值）；Predict(T) 对新数据 T 预测值。

差异：补习资料无scikit-learn的Fit(X,y)/Predict(T)接口说明。
建议：补充scikit-learn接口内容。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 26 页 · `09_linear_regression_50c9a546_25_0`：Machine learning in scikit-learn
– Fit(X, y): fits a model to the training data X, y
– X: feature vectors
– y: value
– Predict(T): predict value for new data T
The University of Sydney Page 26

**往期补习课件证据**
- 未检索到可引用证据。

## T016 多项式特征与模型灵活性 — 已覆盖

线性模型可通过多项式变换特征扩展：ŷ=hθ(x)=θ0+θ1x1+θ2x2+…+θdxd。虽然曲线对 x 非线性，但模型对参数 θ0,θ1,…,θd 仍是线性的，因此可用线性回归技术拟合非线性数据集。

差异：补习资料覆盖多项式回归及对参数线性、可拟合非线性趋势。
建议：无需补充。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 28 页 · `09_linear_regression_50c9a546_27_0`：Increasing model flexibility
– A linear model an be extended by Polynomial transformed
features
– 𝑦ො = ℎ (x) = 𝜃 + 𝜃 x1 +𝜃 x2 +. . . +𝜃 xd
𝜽 0 1 2 𝑑
– Although the curve is nonlinear in 𝑥, the model is still linear in
the parameters: 𝜃 , 𝜃 , … , 𝜃
0 1 𝑑
– This allows the use of linear regression
techniques to fit non-linear datasets. The University of Sydney Page 28
- 09_linear_regression_and_logistic_regression.pdf · 第 28 页 · `09_linear_regression_50c9a546_27_1`：+𝜃 xd
𝜽 0 1 2 𝑑
– Although the curve is nonlinear in 𝑥, the model is still linear in
the parameters: 𝜃 , 𝜃 , … , 𝜃
0 1 𝑑
– This allows the use of linear regression
techniques to fit non-linear datasets. The University of Sydney Page 28

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 4.2 多项式回归 · `tutoring_8dc0d7188f3c_section29_0_0`：在简单线性回归中，我们假设 y 和 x 的关系是一条直线，但现实中很多关系是曲线的 项式回归虽然曲线是非线性的，但模型对参数 θ 依然是线性的 多项式回归通过在模型中引入自变量的幂次（x2,x3,…），用一条光滑曲线来拟合非线性趋势：
- 9 Linear Regression & Logistic Regression .docx · 3.4 简单线性回归的假设与局限性 · `tutoring_8dc0d7188f3c_section26_0_0`：假设条件 线性关系：x 和 y 确实是线性关系。 误差项独立同分布，且服从均值为 0 的正态分布。 同方差性：误差的方差是常数，不随 x 变化。 何时不适用？ 数据明显是非线性趋势（可用多项式回归或其它模型） 存在异常值会严重影响拟合线 只有一个自变量，信息量有限（需要多元回归）

## T017 模型复杂度、欠拟合与过拟合 — 已覆盖

更灵活的模型能捕捉更复杂模式，但过度灵活会拟合噪声而非潜在趋势。欠拟合：训练拟合差、测试表现差；良好拟合：训练好、测试好；过拟合：训练非常好、测试常常差（高方差），欠拟合对应高偏差。

差异：补习资料覆盖过拟合、欠拟合、良好拟合及高方差/高偏差。
建议：无需补充。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 29 页 · `09_linear_regression_50c9a546_28_0`：Model Complexity and fit
– A more flexible model can capture more complex patterns. – But too much flexibility can fit noise rather than the underlying
trend. Model Training fit Test performance
Underfitting Poor Poor
Good fit Good Good
Overfitting Very good Often poor
The University of Sydney Page 29
- 09_linear_regression_and_logistic_regression.pdf · 第 29 页 · `09_linear_regression_50c9a546_28_1`：– But too much flexibility can fit noise rather than the underlying
trend. Model Training fit Test performance
Underfitting Poor Poor
Good fit Good Good
Overfitting Very good Often poor
The University of Sydney Page 29
- 09_linear_regression_and_logistic_regression.pdf · 第 30 页 · `09_linear_regression_50c9a546_29_0`：Quality of fit example
e e e
c c c
i i i
r r r
P P P
Size Size Size
Correct fit Overfitting (high variance)
Under-fitting (high bias)
The University of Sydney Page 30

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 2.3.3 恰到好处的拟合 · `tutoring_8dc0d7188f3c_section12_0_0`：这是理想状态。 模型足够复杂以学习数据中的关键模式，但又不会复杂到去学习随机噪声。 它能在训练集和未知的测试集上都表现良好。 表现：在训练集和测试集上的误差都较低，且两者接近。
- 9 Linear Regression & Logistic Regression .docx · 2.3.1 过拟合 overfit · `tutoring_8dc0d7188f3c_section10_0_0`：过拟合 是指模型过于复杂，不仅学习了数据中的真实规律，还"记住"了训练数据中的随机噪声和异常值。 表现：模型在训练数据上表现极好（误差极小），但在新的、未见过的数据上表现急剧下降，泛化能力差。 原因：模型复杂度过高，训练数据量太少。
- 9 Linear Regression & Logistic Regression .docx · 2.3.2欠拟合 underfit · `tutoring_8dc0d7188f3c_section11_0_0`：欠拟合 是指模型过于简单，无法捕捉数据中的基本规律或模式。 就像一个学生只学了加法，却要去解微积分题目。 表现：模型在训练数据上表现就很差（例如，准确率低，误差大）。 原因：模型复杂度太低，特征不足，或训练不充分。
- 9 Linear Regression & Logistic Regression .docx · 2.5.2方差variance · `tutoring_8dc0d7188f3c_section19_0_0`：定义：模型预测值自身的波动范围。 反映了模型对训练数据中随机噪声的敏感程度。 高方差的表现：模型过于复杂，对训练数据中的微小变化（包括噪声）反应过度，导致过拟合。 换一组数据训练，得到的模型可能完全不同。 例子：一个深度神经网络，如果不对其进行任何约束，它可能会为每一套独特的训练数据生成一套完全不同的、极度复杂的预测规则，这就是高方差。

## T018 减少过拟合的方法 — 已覆盖

减少过拟合的方法：使用更简单的模型；使用更少或更相关的特征；尽可能收集更多训练数据；使用训练/测试划分或交叉验证检查泛化；使用正则化抑制过于复杂的模型。

差异：补习资料覆盖更多数据、降复杂度、特征选择、正则化、交叉验证。
建议：无需补充。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 31 页 · `09_linear_regression_50c9a546_30_0`：How can we reduce overfitting? – Use a simpler model
– Use fewer or more relevant features
– Collect more training data, if possible
– Use train/test split or cross-validation to check generalisation. – Use regularization to discourage overly complex models. The University of Sydney Page 31
- 09_linear_regression_and_logistic_regression.pdf · 第 31 页 · `09_linear_regression_50c9a546_30_1`：– Use regularization to discourage overly complex models. The University of Sydney Page 31

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 2.3.4应对策略 · `tutoring_8dc0d7188f3c_section13_0_0`：解决欠拟合（高偏差）： 增加模型复杂度：使用更强大的模型（如从线性模型切换到树模型、神经网络）。 添加更多特征：挖掘或构造更有意义的特征。 减少正则化：如果使用了正则化（如 L1、L2），尝试减弱其强度。 延长训练时间：对于迭代模型（如神经网络），训练更多轮次。 解决过拟合（高方差）： 获取更多训练数据：最有效的方法之一。 降低模型复杂度：选择更简单的模型（如降低多项式阶数、减少树深度、减少神经网络层数）。 特征选择：移除不相关或冗余的特征。 增加正则化： L1 正则化 (Lasso)：倾向于产生稀疏权重，可用于特征选择。
- 9 Linear Regression & Logistic Regression .docx · 2.3.4应对策略 · `tutoring_8dc0d7188f3c_section13_0_1`：增加正则化： L1 正则化 (Lasso)：倾向于产生稀疏权重，可用于特征选择。 L2 正则化 (Ridge)：使权重衰减，倾向于让所有权重都较小。 Dropout（用于神经网络）：在训练中随机"丢弃"一部分神经元。 早停（用于迭代模型）：当验证集误差不再下降时停止训练。
- 9 Linear Regression & Logistic Regression .docx · 2.4 正则化 regularization · `tutoring_8dc0d7188f3c_section14_0_1`：λ很小或为 0 → 几乎不惩罚，容易过拟合 选择方法：使用交叉验证，尝试多个 λ 值，选择使验证集误差最小的那个。

## T019 正则化概念 — 已覆盖

普通训练目标：cost=预测误差；正则化训练目标：cost=预测误差+复杂度惩罚。对线性模型，复杂度常用系数大小衡量，大系数意味着模型更敏感。

差异：补习资料覆盖正则化惩罚项、λ控制强度、大系数更敏感。
建议：无需补充。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 32 页 · `09_linear_regression_50c9a546_31_0`：What is regularization
– Ordinary training objective:
– 𝑐𝑜𝑠𝑡 = 𝑝𝑟𝑒𝑑𝑖𝑐𝑡𝑖𝑜𝑛 𝑒𝑟𝑟𝑜𝑟
– Regularized training objective:
– 𝑐𝑜𝑠𝑡 = 𝑝𝑟𝑒𝑑𝑖𝑐𝑡𝑖𝑜𝑛 𝑒𝑟𝑟𝑜𝑟 + 𝑝𝑒𝑛𝑎𝑙𝑡𝑦 𝑓𝑜𝑟 𝑐𝑜𝑚𝑝𝑙𝑒𝑥𝑖𝑡𝑦
– For linear models, complexity is often measured using
coefficient size
– 𝑙𝑎𝑟𝑔𝑒 𝑐𝑜𝑒𝑓𝑓𝑖𝑐𝑖𝑒𝑛𝑡𝑠 ⇒ 𝑚𝑜𝑟𝑒 𝑠𝑒𝑛𝑠𝑖𝑡𝑖𝑣𝑒 𝑚𝑜𝑑𝑒𝑙
The University of Sydney Page 32
- 09_linear_regression_and_logistic_regression.pdf · 第 32 页 · `09_linear_regression_50c9a546_31_1`：What is regularization
– Ordinary training objective:
– 𝑐𝑜𝑠𝑡 = 𝑝𝑟𝑒𝑑𝑖𝑐𝑡𝑖𝑜𝑛 𝑒𝑟𝑟𝑜𝑟
– Regularized training objective:
– 𝑐𝑜𝑠𝑡 = 𝑝𝑟𝑒𝑑𝑖𝑐𝑡𝑖𝑜𝑛 𝑒𝑟𝑟𝑜𝑟 + 𝑝𝑒𝑛𝑎𝑙𝑡𝑦 𝑓𝑜𝑟 𝑐𝑜𝑚𝑝𝑙𝑒𝑥𝑖𝑡𝑦
– For linear models, complexity is often measured using
coefficient size
– 𝑙𝑎𝑟𝑔𝑒 𝑐𝑜𝑒𝑓𝑓𝑖𝑐𝑖𝑒𝑛𝑡𝑠 ⇒ 𝑚𝑜𝑟𝑒 𝑠𝑒𝑛𝑠𝑖𝑡𝑖𝑣𝑒 𝑚𝑜𝑑𝑒𝑙
The University of Sydney Page 32

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 2.4 正则化 regularization · `tutoring_8dc0d7188f3c_section14_0_0`：正则化 是在代价函数 J(θ)中添加一个惩罚项，限制模型参数的大小，从而抑制模型复杂度，防止过拟合。 λ：正则化参数（超参数），控制惩罚强度 Penalty(θ)：正则化项，常见的L1 正则化和L2 正则化 没有正则化：参数可以任意大，拟合出扭曲的曲线来穿过每个点。 有正则化：参数大的会被“罚款”，模型倾向于选择更小、更平滑的参数，曲线更简单。 λ很大 → 模型过于简单，可能欠拟合。 λ很小或为 0 → 几乎不惩罚，容易过拟合 选择方法：使用交叉验证，尝试多个 λ 值，选择使验证集误差最小的那个。
- 9 Linear Regression & Logistic Regression .docx · 2.5.3 偏差-方差权衡 · `tutoring_8dc0d7188f3c_section20_0_0`：这是一个机器学习中的核心权衡。 我们无法同时最小化偏差和方差。 增加模型复杂度：通常可以降低偏差（模型能力变强），但会增加方差（更容易学到噪声）。 降低模型复杂度：通常可以降低方差（模型更稳定），但会增加偏差（模型能力变弱）。 我们的目标就是找到图中的"最佳点"，使得总误差最小。

## T020 L1/Lasso 与 L2/Ridge 正则化 — 已覆盖

L1/Lasso 惩罚系数绝对值之和 λΣ|θj|，可将某些系数精确收缩为零，起到自动特征选择作用。L2/Ridge 惩罚 λΣθj²，最小化系数、将系数拉向 0。λ 控制正则化强度，λ 大则正则化强；截距 θ0 通常不正则化。

差异：补习资料覆盖L1/Lasso稀疏特征选择、L2/Ridge权重衰减、λ强度、截距不正则化。
建议：无需补充。
置信度（仅供排序）：0.85

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 33 页 · `09_linear_regression_50c9a546_32_0`：Common types of regularization
– L2 and L1 regularization
Method Penalty interpretation
L1/Lasso 𝑑 penalises the sum of absolute coefficient
𝜆 ෍ 𝜃
𝑗 values. It can shrink some coefficients
𝑗=1
exactly to zero, so it can act like automatic
feature selection. L2/Ridge 𝑑 Minimizes coefficients; pulls coefficients
2
𝜆 ෍ 𝜃
𝑗 toward 0
𝑗=1
𝜆 controls regularization strength
Large 𝜆: strong regularization
- 09_linear_regression_and_logistic_regression.pdf · 第 33 页 · `09_linear_regression_50c9a546_32_1`：It can shrink some coefficients
𝑗=1
exactly to zero, so it can act like automatic
feature selection. L2/Ridge 𝑑 Minimizes coefficients; pulls coefficients
2
𝜆 ෍ 𝜃
𝑗 toward 0
𝑗=1
𝜆 controls regularization strength
Large 𝜆: strong regularization
The intercept 𝜃 is often not regularized
0
The University of Sydney Page 33

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 2.4.1 Lasso 回归（L1 正则化） · `tutoring_8dc0d7188f3c_section15_0_0`：惩罚项：所有参数（除截距外）的绝对值之和。 L1 的约束区域是一个菱形，最优解容易落在坐标轴上（βj=0）
- 9 Linear Regression & Logistic Regression .docx · 2.3.4应对策略 · `tutoring_8dc0d7188f3c_section13_0_1`：增加正则化： L1 正则化 (Lasso)：倾向于产生稀疏权重，可用于特征选择。 L2 正则化 (Ridge)：使权重衰减，倾向于让所有权重都较小。 Dropout（用于神经网络）：在训练中随机"丢弃"一部分神经元。 早停（用于迭代模型）：当验证集误差不再下降时停止训练。
- 9 Linear Regression & Logistic Regression .docx · 2.4 正则化 regularization · `tutoring_8dc0d7188f3c_section14_0_0`：正则化 是在代价函数 J(θ)中添加一个惩罚项，限制模型参数的大小，从而抑制模型复杂度，防止过拟合。 λ：正则化参数（超参数），控制惩罚强度 Penalty(θ)：正则化项，常见的L1 正则化和L2 正则化 没有正则化：参数可以任意大，拟合出扭曲的曲线来穿过每个点。 有正则化：参数大的会被“罚款”，模型倾向于选择更小、更平滑的参数，曲线更简单。 λ很大 → 模型过于简单，可能欠拟合。 λ很小或为 0 → 几乎不惩罚，容易过拟合 选择方法：使用交叉验证，尝试多个 λ 值，选择使验证集误差最小的那个。

## T021 梯度下降的动机 — 已覆盖

许多模型/代价函数没有 θ 的闭式解，需要通用搜索过程学习 θ：选择 θ 初值，迭代选择新 θ 以降低 J(θ)（如通过梯度下降），直到达到最小值。OLS 线性回归可直接求解，但许多模型直接求解困难或不可用，梯度下降通过逐步改进找到好的参数。

差异：补习资料覆盖梯度下降用于优化、学习率，但“无闭式解需通用搜索”动机未明确。
建议：补充无闭式解动机说明。
置信度（仅供排序）：0.75

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 35 页 · `09_linear_regression_50c9a546_34_0`：How to learn 𝜃
– For many other models/cost functions, there is no closed-form
solution of 𝜃
– A general search procedure for learning 𝜃
– Choose an initial value for 𝜽
– Iteratively choose a new value for 𝜽 to reduce 𝐽(𝜽) (e. g. , through
gradient descent)
• Until we reach a minimum
The University of Sydney Page 35
- 09_linear_regression_and_logistic_regression.pdf · 第 35 页 · `09_linear_regression_50c9a546_34_1`：g. , through
gradient descent)
• Until we reach a minimum
The University of Sydney Page 35
- 09_linear_regression_and_logistic_regression.pdf · 第 41 页 · `09_linear_regression_50c9a546_40_0`：Why gradient descent
– A model is trained by finding parameters that minimise the cost
– For OLS linear regression, this can be solved directly
– For many models, a direct solution is difficult or unavailable. – Gradient descent finds good parameters by improving them
step by step. The University of Sydney Page 41
- 09_linear_regression_and_logistic_regression.pdf · 第 41 页 · `09_linear_regression_50c9a546_40_1`：– Gradient descent finds good parameters by improving them
step by step. The University of Sydney Page 41

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 5.5 损失函数 · `tutoring_8dc0d7188f3c_section35_0_0`：逻辑回归的代价函数使用 对数损失 (Log Loss) 或 交叉熵 (Cross-Entropy)： MSE 的问题：如果逻辑回归使用 MSE，损失函数会是非凸函数（Non-convex），有很多局部最小值，难以找到全局最优解。 Cross-Entropy 的优势：它是凸函数，能保证找到全局最优解。 优化方法：梯度下降
- 9 Linear Regression & Logistic Regression .docx · 2.2.3 学习率 learning rate · `tutoring_8dc0d7188f3c_section5_0_0`：作用： 控制参数更新的幅度。 当计算出梯度后，学习率决定了参数前进的步长。 学习率过大： 训练震荡，难以收敛，甚至导致损失函数数值爆炸（Loss Nan）。 学习率过小： 收敛速度极慢，需要大量训练时间，容易陷入局部最优解。 常用技巧： 可以从 0. 1, 0. 01, 0. 001 等数量级开始尝试 逐渐缩小学习率（学习率衰减）也是一个好策略

## T022 代价函数直觉示例 — 部分覆盖

用简单线性回归 ŷ=θ0+θ1x 理解代价函数：固定 θ0=0，改变 θ1。θ1=1 时 J=0（完美拟合玩具数据）；θ1=0.5 时 J≈0.58；θ1=0 时 J≈2.33。每个 θ1 值对应不同拟合线和不同代价 J(θ1)，绘制参数与代价得到代价曲线，该例只有一个全局最小值。

差异：补习资料有J(w)=w²−2w+2案例，但无固定θ0=0改变θ1得J=0/0.58/2.33的代价曲线示例。
建议：补充该代价函数直觉示例。
置信度（仅供排序）：0.75

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 36 页 · `09_linear_regression_50c9a546_35_0`：Intuition behind cost function ( 1 of 4 )
We will use the simple linear regression function to help understand
the cost function
Common form: 𝑦ො = 𝛼 + 𝛽𝑥
Generic form: 𝑦ො = ℎ 𝑥 = 𝜃 + 𝜃 𝑥
𝜃 0 1
Cost function:
3. 5
3
𝑥 𝑦
2. 5
Toy example
1 1
2
Y
1. 5
2 2
𝜃 = 0 and 𝜃
= 1
0 1 1
Y = h (X) = X
3 3
𝜃 0. 5
0
0 1 2 3 4
X
The University of Sydney Page 36
- 09_linear_regression_and_logistic_regression.pdf · 第 37 页 · `09_linear_regression_50c9a546_36_0`：Intuition behind cost function (2 of 4)
We are only interested in how 𝜃 change affects the error
1
3. 5
h (x) 3
𝜃
3
2. 5
2
2
Y )
1. 5 𝜃 1
𝜃 = 1 ( J
1
1 1
𝜃 = 0
0. 5 0
0
0 1 2 3 4 0
0 0. 5 1 1. 5 2 2. 5
X
𝜃
1 1
𝐽 0,1 = 1 − 1 2 + 2 − 2 2 + 3 − 3 2 = 0
2 × 3
The University of Sydney Page 37
- 09_linear_regression_and_logistic_regression.pdf · 第 38 页 · `09_linear_regression_50c9a546_37_0`：Intuition behind cost function ( 3 of 4)
the value of 𝜃 is fixed to 0, now we change the value of 𝜃 to 0. 5
0 1
The prediction function becomes 𝑦ො = 0. 5𝑥
3. 5
h (x) 3
𝜃
3
2. 5
2
2
Y )
1. 5 𝜃 1
𝜃 = 0. 5 ( J
1
1 1
𝜃 = 0
0. 5 0
0
0 1 2 3 4 0
0 0. 5 1 1. 5 2 2. 5
X
𝜃
1 1
𝐽 0,0. 5 = 0. 5 − 1 2 + 1 − 2 2 + 1. 5 − 3 2 ≈ 0. 58
The University of Sydney 2 × 3 Page 38
- 09_linear_regression_and_logistic_regression.pdf · 第 39 页 · `09_linear_regression_50c9a546_38_0`：Intuition behind cost function ( 4 of 4 )
the value of 𝜃 is fixed to 0, now we change the value of 𝜃 to 0
0 1
The prediction function becomes 𝑦ො = 0𝑥 = 0
3. 5
h (x) 3
𝜃
3
𝐽 0,0 ≈ 2. 33
2. 5
2
2
Y )
1. 5 𝜃 1
𝜃 = 0 ( J
1
1 1
𝜃 = 0
0. 5 0
0
0 1 2 3 4 0
1 0 0. 5 1 1. 5 2 2. 5
X
𝐽 0,0 = 0 − 1 2 + 0 − 2 2 + 0 − 3 2 ≈ 2. 33 𝜃
1
2 × 3
Has only one global minimum
The University of Sydney Page 39
- 09_linear_regression_and_logistic_regression.pdf · 第 40 页 · `09_linear_regression_50c9a546_39_0`：Learning Means Finding the Lowest Cost
– Each value of θ₁ gives a different fitted line. – Each fitted line gives a different cost J(θ₁). – If we plot many parameter values against their cost, we
get a cost curve. 𝜃 Model Cost Interpretation
1
0 𝑦ො = 0 high Too flat
0. 5 𝑦ො = 0. 5𝑥 medium closer
1 𝑦ො = 𝑥 lowest Perfect for the toy data
The University of Sydney Page 40

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 5.5 损失函数 · `tutoring_8dc0d7188f3c_section35_0_0`：逻辑回归的代价函数使用 对数损失 (Log Loss) 或 交叉熵 (Cross-Entropy)： MSE 的问题：如果逻辑回归使用 MSE，损失函数会是非凸函数（Non-convex），有很多局部最小值，难以找到全局最优解。 Cross-Entropy 的优势：它是凸函数，能保证找到全局最优解。 优化方法：梯度下降

## T023 梯度下降算法与更新规则 — 已覆盖

将代价函数视为参数值上的曲线，斜率指示增加代价的方向，为降低代价应向相反方向移动。算法：初始化 θ，重复直到收敛：θj←θj−α*(∂/∂θj)J(θ)，α 为学习率（取小值，如 0.05），对所有 j=0…d 参数同时更新。对线性回归，∂J/∂θj=(1/n)Σ(hθ(x(i))−y(i))xj(i)。假设 α 足够小，梯度下降总是收敛到全局最小值。

差异：补习资料覆盖梯度下降更新公式、学习率、方向判断，但线性回归偏导公式与同时更新未明确。
建议：补充线性回归梯度公式与同时更新。
置信度（仅供排序）：0.75

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 42 页 · `09_linear_regression_50c9a546_41_0`：Gradient Descent
– Think of the cost function as a
3
curve over parameter values. 2. 5
– A point on the curve represents 2
)
𝜃
the current parameter value. ( 𝐽 1. 5
1
– The slope tells us which
0. 5
direction increases the cost. 0
0 1 𝜃 2 3
– To reduce the cost, move in the
opposite direction. The University of Sydney Page 42
- 09_linear_regression_and_logistic_regression.pdf · 第 43 页 · `09_linear_regression_50c9a546_42_0`：Gradient descent
3
2. 5
– Initialize 𝜃
2
)
𝜃
– Repeat until convergence ( 1. 5
𝐽
1
𝛼 is a learning rate
𝜕
𝜃 ← 𝜃 − 𝛼 ∗ 𝐽(𝜽)
𝑗 𝑗 (taking a small value) 0. 5
𝜕𝜃
𝑗
e. g. 𝛼 = 0.
- 09_linear_regression_and_logistic_regression.pdf · 第 43 页 · `09_linear_regression_50c9a546_42_1`：g. 𝛼 = 0. 05 0
0 1 𝜃 2 3
𝜃 ← 𝜃 − 𝛼 ∗ 1 σ𝑛 ℎ 𝒙(𝑖) − 𝑦(𝑖) 𝑥 (𝑖)
𝑗 𝑗 𝑖=1 𝜽 𝑗
𝑛
simultaneous update for 𝜕 𝐽(𝜽) = 𝜕 1 σ𝑛 ℎ (𝒙(𝑖))−𝑦(𝑖) 2
𝑖=1 𝜽
𝜕𝜃 𝜕𝜃 2𝑛
𝑗 𝑗
2
𝑗 = 0 … 𝑑 parameters/weights = 𝜕 1 σ𝑛 σ𝑑 𝜃 𝑥 (𝑖) −𝑦(𝑖)
𝜕𝜃 2𝑛 𝑖=1 𝑘=0 𝑘 𝑘
𝑗
Gradient descent always converges to the = 1 σ𝑛 σ𝑑 𝜃 𝑥 (𝑖) −𝑦(𝑖) × 𝜕 σ𝑑 𝜃 𝑥 (𝑖) −𝑦(𝑖)
𝑛 𝑖=1 𝑘=0 𝑘 𝑘 𝜕𝜃𝑗 𝑘=0 𝑘 𝑘
global minimum (assuming 𝛼 is small ) = 1 σ𝑛 σ𝑑 𝜃 𝑥 (𝑖) −𝑦(𝑖
- 09_linear_regression_and_logistic_regression.pdf · 第 43 页 · `09_linear_regression_50c9a546_42_2`：𝛼 = 0. 05 0
0 1 𝜃 2 3
𝜃 ← 𝜃 − 𝛼 ∗ 1 σ𝑛 ℎ 𝒙(𝑖) − 𝑦(𝑖) 𝑥 (𝑖)
𝑗 𝑗 𝑖=1 𝜽 𝑗
𝑛
simultaneous update for 𝜕 𝐽(𝜽) = 𝜕 1 σ𝑛 ℎ (𝒙(𝑖))−𝑦(𝑖) 2
𝑖=1 𝜽
𝜕𝜃 𝜕𝜃 2𝑛
𝑗 𝑗
2
𝑗 = 0 … 𝑑 parameters/weights = 𝜕 1 σ𝑛 σ𝑑 𝜃 𝑥 (𝑖) −𝑦(𝑖)
𝜕𝜃 2𝑛 𝑖=1 𝑘=0 𝑘 𝑘
𝑗
Gradient descent always converges to the = 1 σ𝑛 σ𝑑 𝜃 𝑥 (𝑖) −𝑦(𝑖) × 𝜕 σ𝑑 𝜃 𝑥 (𝑖) −𝑦(𝑖)
𝑛 𝑖=1 𝑘=0 𝑘 𝑘 𝜕𝜃𝑗 𝑘=0 𝑘 𝑘
global minimum (assuming 𝛼 is small ) = 1 σ𝑛 σ𝑑 𝜃 𝑥 (𝑖) −𝑦(𝑖) 𝑥

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 2.2.5 案例分析 · `tutoring_8dc0d7188f3c_section9_0_0`：求一维二次函数的最小值： J(w)=w2−2w+2 假设我们随机初始化参数 w的值为 3。 当前猜测： w0=3 代入函数： J(3)=32−2×3+2=5 直观感受：此时我们处于山坡较高的位置（函数值为 5），而我们的目标是走到谷底（函数值最小）。 在 w=3处的梯度：2×3−2=4 方向判断： 梯度值为正数 (4)。 规则：梯度指向函数增长最快的方向。 因此，我们要想让函数值变小（下山），就必须往反方向（负方向）走。 学习率 α=0. 2，根据梯度下降公式进行更新： w1​=3−0. 2×4=2. 2
- 9 Linear Regression & Logistic Regression .docx · 2.2.3 学习率 learning rate · `tutoring_8dc0d7188f3c_section5_0_0`：作用： 控制参数更新的幅度。 当计算出梯度后，学习率决定了参数前进的步长。 学习率过大： 训练震荡，难以收敛，甚至导致损失函数数值爆炸（Loss Nan）。 学习率过小： 收敛速度极慢，需要大量训练时间，容易陷入局部最优解。 常用技巧： 可以从 0. 1, 0. 01, 0. 001 等数量级开始尝试 逐渐缩小学习率（学习率衰减）也是一个好策略
- 9 Linear Regression & Logistic Regression .docx · 5.5 损失函数 · `tutoring_8dc0d7188f3c_section35_0_0`：逻辑回归的代价函数使用 对数损失 (Log Loss) 或 交叉熵 (Cross-Entropy)： MSE 的问题：如果逻辑回归使用 MSE，损失函数会是非凸函数（Non-convex），有很多局部最小值，难以找到全局最优解。 Cross-Entropy 的优势：它是凸函数，能保证找到全局最优解。 优化方法：梯度下降

## T024 梯度下降直觉与学习率选择 — 已覆盖

以 J(w)=w²−2w+2 为例，微积分求导 2w−2=0 得 w=1，但复杂代价函数难以直接求解。梯度下降从随机猜测（如 w=3）开始，计算导数判断方向，用 wi+1=wi−α*dJ(w)/dw 更新（如 α=0.2），逐步逼近最小值。学习率 α 太小则收敛慢，太大可能越过最小值，好的策略是逐渐缩小学习率。

差异：补习资料覆盖J(w)=w²−2w+2、w0=3、α=0.2更新至2.2及学习率过大过小问题。
建议：无需补充。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 44 页 · `09_linear_regression_50c9a546_43_0`：Intuition behind gradient descent
– Given simple cost function
J(𝑤) = 𝑤 2 − 2𝑤 + 2,
find the value of w to minimise J(𝑤)
– From Calculus, by finding the
derivative and set it equal to
zero:
𝑑𝐽(𝑤)
= 2𝑤 − 2 = 0 ⟹ 𝑤 = 1
𝑑𝑤
But this is hard to solve for more complicated cost function! The University of Sydney Page 44
- 09_linear_regression_and_logistic_regression.pdf · 第 45 页 · `09_linear_regression_50c9a546_44_0`：Intuition behind gradient descent
– So, we pick a random number
– Let w= 3, which obviously is wrong
– Step 1: we take the derivative of the function
𝑑𝐽(𝑤)
• = 2𝑤 − 2
𝑑𝑤
– Step 2: we study the derivative at the point we guessed (𝑥 = 3)
𝑑𝐽(𝑤)
• = 2 ∗ 3 − 2 = 4
𝑑𝑤
– Given that the derivative is positive, we know that the value is getting
larger moving to the right (forward)
– Therefore, we need to m
- 09_linear_regression_and_logistic_regression.pdf · 第 46 页 · `09_linear_regression_50c9a546_45_0`：Intuition behind gradient descent
– If we have guessed w = −1 instead, the derivative would have been −4
– then we would know that the function is getting smaller
– By studying the derivative of the current guess, we know if we are getting
closer or further away from the minimum
– So here is the equation
𝑑𝐽(𝑤)
• 𝑤 = 𝑤 − 𝛼 ∗ , 𝛼 is the learning rate, e. g. 𝛼 = 0. 2
𝑖+1 𝑖
𝑑𝑤
– Given our example, we 
- 09_linear_regression_and_logistic_regression.pdf · 第 47 页 · `09_linear_regression_50c9a546_46_0`：Intuition behind gradient descent
– We repeat this process again at 𝑤 = 2. 2
1
𝑑𝐽(𝑤)
• = 2𝑤 − 2
𝑑𝑤
𝑑𝐽(𝑤=2. 2)
• = 2 ∗ 2. 2 − 2 = 2. 4
𝑑𝑤
• 𝑤 = 2. 2 − 0. 2 ∗ 2. 4 = 1. 72 , we moved closer
2
– At 𝑤 = 1. 72
2
𝑑𝐽(𝑤)
• = 2𝑤 − 2
𝑑𝑤
𝑑𝐽(𝑤=1. 72)
• = 2 ∗ 1. 72 − 2 = 1. 44
𝑑𝑤
• 𝑤 = 1. 72 − 0. 2 ∗ 1. 44 = 1. 432 , we moved closer
3
– If we keep repeating this process, we can find the minimum point of the
so
- 09_linear_regression_and_logistic_regression.pdf · 第 48 页 · `09_linear_regression_50c9a546_47_0`：Selecting learning rate
– If 𝛼 is small, gradient
descent can be slow
– If 𝛼 is too large, gradient
descent might overshoot the
minimum
– One good strategy is
gradually shrinking the
learning rate
The University of Sydney Page 48

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 2.2.5 案例分析 · `tutoring_8dc0d7188f3c_section9_0_0`：求一维二次函数的最小值： J(w)=w2−2w+2 假设我们随机初始化参数 w的值为 3。 当前猜测： w0=3 代入函数： J(3)=32−2×3+2=5 直观感受：此时我们处于山坡较高的位置（函数值为 5），而我们的目标是走到谷底（函数值最小）。 在 w=3处的梯度：2×3−2=4 方向判断： 梯度值为正数 (4)。 规则：梯度指向函数增长最快的方向。 因此，我们要想让函数值变小（下山），就必须往反方向（负方向）走。 学习率 α=0. 2，根据梯度下降公式进行更新： w1​=3−0. 2×4=2. 2
- 9 Linear Regression & Logistic Regression .docx · 2.2.3 学习率 learning rate · `tutoring_8dc0d7188f3c_section5_0_0`：作用： 控制参数更新的幅度。 当计算出梯度后，学习率决定了参数前进的步长。 学习率过大： 训练震荡，难以收敛，甚至导致损失函数数值爆炸（Loss Nan）。 学习率过小： 收敛速度极慢，需要大量训练时间，容易陷入局部最优解。 常用技巧： 可以从 0. 1, 0. 01, 0. 001 等数量级开始尝试 逐渐缩小学习率（学习率衰减）也是一个好策略

## T025 批量、随机与小批量梯度下降 — 已覆盖

三者区别在于每次更新使用多少数据：批量使用全部训练数据（稳定但慢），随机使用一个数据点（快但有噪声），小批量使用一小批数据（常见折中）。三者学习同一组共享模型参数，仅在每步梯度估计方式上不同。批量需扫描整个训练集才走一步，n 大时开销高；随机立即开始进展但可能不收敛到最小值。

差异：补习资料覆盖批量、随机、小批量梯度下降的数据使用与优缺点。
建议：无需补充。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 49 页 · `09_linear_regression_50c9a546_48_0`：How Much Data Is Used Per Update? – Gradient descent updates the model parameters repeatedly
– The difference between batch, stochastic and mini-batch
gradient descent is how much data is used to calculate each
update
Method Data used per update Update behaviour
Batch All training data Stable but can be slow
Stochastic One data point Fast but noisy
Mini-batch A small batch of data Common compromis
- 09_linear_regression_and_logistic_regression.pdf · 第 49 页 · `09_linear_regression_50c9a546_48_1`：They
differ only in how the gradient is estimated at each step. The University of Sydney Page 49
- 09_linear_regression_and_logistic_regression.pdf · 第 50 页 · `09_linear_regression_50c9a546_49_0`：Batch vs stochastic gradient descents
– Batch: all n training examples are used to calculate one update
– Repeat until converge 𝜃 ← 𝜃 − 𝛼 1 σ𝑛 ℎ 𝒙(𝑖) − 𝑦(𝑖) 𝑥 (𝑖) for every 𝑗
𝑗 𝑗 𝑖=1 𝜽 𝑗
𝑛
– Accurate but slow:
• has to scan through the entire training set before taking a single step
• costly operation if 𝑛 is large
– Stochastic:
For 𝑖 = 1 to 𝑛
(𝑖)
𝜃 ← 𝜃 − 𝛼 ℎ 𝒙(𝑖) − 𝑦(𝑖) 𝑥 , for every 𝑗
𝑗 𝑗 𝜽 𝑗
– 
- 09_linear_regression_and_logistic_regression.pdf · 第 50 页 · `09_linear_regression_50c9a546_49_1`：Batch vs stochastic gradient descents
– Batch: all n training examples are used to calculate one update
– Repeat until converge 𝜃 ← 𝜃 − 𝛼 1 σ𝑛 ℎ 𝒙(𝑖) − 𝑦(𝑖) 𝑥 (𝑖) for every 𝑗
𝑗 𝑗 𝑖=1 𝜽 𝑗
𝑛
– Accurate but slow:
• has to scan through the entire training set before taking a single step
• costly operation if 𝑛 is large
– Stochastic:
For 𝑖 = 1 to 𝑛
(𝑖)
𝜃 ← 𝜃 − 𝛼 ℎ 𝒙(𝑖) − 𝑦(𝑖) 𝑥 , for every 𝑗
𝑗 𝑗 𝜽 𝑗
– 

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 批量梯度下降 (Batch Gradient Descent): · `tutoring_8dc0d7188f3c_section6_0_0`：做法：每次更新参数时，计算整个训练集的梯度。 优点：方向准确，直奔全局最优。 缺点：当数据量很大时，计算非常慢。
- 9 Linear Regression & Logistic Regression .docx · 随机梯度下降 (Stochastic Gradient Descent, SGD) · `tutoring_8dc0d7188f3c_section7_0_0`：做法：每次只用一个样本来计算梯度并更新参数。 优点：速度极快，可以在线学习。 缺点：路径非常曲折（因为单个样本有噪声），虽然总体是向下的，但会左右摇摆。
- 9 Linear Regression & Logistic Regression .docx · 小批量梯度下降 (Mini-batch Gradient Descent) · `tutoring_8dc0d7188f3c_section8_0_0`：做法：每次使用一小批样本（例如 32、64、128 个）来计算梯度。 优点：结合了前两者的优点，既利用了矩阵运算的加速（效率高），又保持了梯度的相对稳定性。 这是深度学习中最常用的方法。

## T026 回归与分类的区别 — 已覆盖

回归预测数值，输出连续变量（如实值），例如预测房价；分类为每个样本预测类别，输出离散/分类变量，例如预测客户是否违约。

差异：补习资料覆盖回归预测连续值、分类预测离散类别及房价示例。
建议：无需补充。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 53 页 · `09_linear_regression_50c9a546_52_0`：Regression vs classification
– Regression predicts a – Classification predicts a
numerical value class to each example
– Output is a continuous – Output is a discrete /
variable (real value) categorical variable
– E. g. , predict house price – E. g. , predict whether a
customer will default or not
The University of Sydney Page 53
- 09_linear_regression_and_logistic_regression.pdf · 第 53 页 · `09_linear_regression_50c9a546_52_1`：g. , predict whether a
customer will default or not
The University of Sydney Page 53

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 表格 3 · `tutoring_8dc0d7188f3c_section40_0_0`：| 分类 | 回归
预测目标 | 离散的类别标签categoric | 连续的数值numeric
输出示例 | “是垃圾邮件”或“不是垃圾邮件” | 房价 453,200 元
典型算法 | 逻辑回归、决策树、SVM、KNN | 线性回归、决策树回归、SVR
评估指标 | 准确率、精确率、召回率、F1 | MSE、RMSE、R²
- 9 Linear Regression & Logistic Regression .docx · 2.1.2均方误差MSE · `tutoring_8dc0d7188f3c_section2_0_0`：适用于回归问题（预测连续值，如房价、温度） 均方误差计算的是所有样本的预测值与真实值之差的平方的平均值。 特点：由于使用了平方，它对较大的误差惩罚更重（误差为 2 时，平方后贡献为 4；误差为 10 时，平方后贡献高达 100）。

## T027 逻辑回归模型与 sigmoid 函数 — 已覆盖

逻辑回归预测分类标签的概率，例如给定债务金额和逾期次数预测违约概率。二分类中目标 Y∈{0,1}，Y=1 为正类，Y=0 为负类，通常想要 p̂=P(Y=1|X)。步骤1：计算线性得分 z=θ0+θ1x1+…+θdxd；步骤2：转换为概率 p̂=P(Y=1|X)=1/(1+e^(−z))。sigmoid 函数将输出保持在 0 和 1 之间，z→∞ 时趋于 1，z→−∞ 时趋于 0。

差异：补习资料覆盖线性得分z、Sigmoid转概率、输出(0,1)及z→∞/→−∞极限。
建议：无需补充。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 54 页 · `09_linear_regression_50c9a546_53_0`：Logistic regression
– Predict probability of
categorical label
– E. g. , probability of
defaulting on a loan given
– Amount of debt
– Late payment count
http://www. toshistats. net/101-4-logistic-regression/
The University of Sydney Page 54
- 09_linear_regression_and_logistic_regression.pdf · 第 55 页 · `09_linear_regression_50c9a546_54_0`：Logistic regression for classification
– In binary classification, the target is usually: 𝑌 ∈ {0,1}
– Y=1: positive class
– Y=0: negative
– A linear regression model can predict any real number
– 𝑦ො = 𝜃 + 𝜃 𝑥 + 𝜃 𝑥 +. . +𝜃 𝑥
0 1 1 1 1 𝑑 𝑑
– For classification, we often want
– 𝑝Ƹ = 𝑃(𝑌 = 1|𝑋)
The University of Sydney Page 55
- 09_linear_regression_and_logistic_regression.pdf · 第 56 页 · `09_linear_regression_50c9a546_55_0`：Logistic Regression Model
1
– Step 1: calculate a linear score: 𝑙𝑖𝑚 → 1
𝑧→∞ 1+𝑒−𝑧
z = 𝜃 + 𝜃 𝑥 + 𝜃 𝑥 +. . +𝜃 𝑥
0 1 1 1 1 𝑑 𝑑
– Step 2: convert the score into a
probability:
1
𝑝Ƹ = 𝑃(𝑌 = 1|𝑋) =
1 + 𝑒−𝑧
– The sigmoid function keeps the output
between 0 and 1 1
𝑙𝑖𝑚 → 0
𝑧→−∞ 1+𝑒−𝑧
The University of Sydney Page 56
- 09_linear_regression_and_logistic_regression.pdf · 第 56 页 · `09_linear_regression_50c9a546_55_1`：. +𝜃 𝑥
0 1 1 1 1 𝑑 𝑑
– Step 2: convert the score into a
probability:
1
𝑝Ƹ = 𝑃(𝑌 = 1|𝑋) =
1 + 𝑒−𝑧
– The sigmoid function keeps the output
between 0 and 1 1
𝑙𝑖𝑚 → 0
𝑧→−∞ 1+𝑒−𝑧
The University of Sydney Page 56

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 5.1 核心思想 · `tutoring_8dc0d7188f3c_section31_0_0`：第一步：计算线性组合（和线性回归一模一样）： z 可以是任意实数。 第二步：将 z 送入 Sigmoid 函数，压缩到 (0, 1)： 这个 hθ(x) 就是预测为正类的概率 P(y=1∣x;θ)。
- 9 Linear Regression & Logistic Regression .docx · 5.逻辑回归 Logistic regression · `tutoring_8dc0d7188f3c_section30_0_0`：逻辑回归 是一种用于二分类的监督学习算法，它在线性组合的基础上加了一个 Sigmoid 函数，将结果压缩到 (0, 1) 之间，作为样本属于正类的概率。
- 9 Linear Regression & Logistic Regression .docx · 表格 6 · `tutoring_8dc0d7188f3c_section43_0_0`：z 的值 | Sigmoid 输出 | 含义
z=0 | 0. 5 | 模型不确定，正负概率各半
z 很大（如 +5） | ≈ 0. 993 | 几乎确定是正类
z 很小（如 -5） | ≈ 0. 007 | 几乎确定是负类
z→+∞ | → 1 | 
z→−∞ | → 0 |

## T028 从概率到类别标签的阈值 — 已覆盖

逻辑回归预测 p̂=P(Y=1|X)，用阈值将概率转换为类别预测：p̂≥0.5 时 Ŷ=1，p̂<0.5 时 Ŷ=0。阈值可根据问题调整。

差异：补习资料覆盖0.5阈值转类别及可调阈值。
建议：无需补充。
置信度（仅供排序）：0.90

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 57 页 · `09_linear_regression_50c9a546_56_0`：From probability to class label
– Logistic regression predicts:
𝑝Ƹ = 𝑃(𝑌 − 1|𝑋)
– A threshold converts probability into a class prediction:
1, 𝑝ෝ ≥ 0. 5
෠
𝑌 = ቊ
0, 𝑝ෝ < 0. 5
– The threshold can be adjusted depending on the problem
The University of Sydney Page 57
- 09_linear_regression_and_logistic_regression.pdf · 第 57 页 · `09_linear_regression_50c9a546_56_1`：5
෠
𝑌 = ቊ
0, 𝑝ෝ < 0. 5
– The threshold can be adjusted depending on the problem
The University of Sydney Page 57

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 5.3 决策边界 · `tutoring_8dc0d7188f3c_section33_0_0`：有了概率值，我们还需要一个标准来下结论。 逻辑回归通常以 0. 5 为界限： 预测概率 ≥ 0. 5 → 预测为 类别 1（例如：是垃圾邮件）。 预测概率 < 0. 5 → 预测为 类别 0（例如：不是垃圾邮件）。 Tips：可以通过调整阈值（Threshold）来改变决策边界

## T029 逻辑回归训练与交叉熵损失 — 已覆盖

需要奖励正确类别高概率的代价函数。逻辑回归常用对数损失/交叉熵而非最小二乘误差，模型自信地犯错时代价高。公式：J(θ)=−(1/n)Σ[yi log p̂i+(1−yi)log(1−p̂i)]。单例损失为 −[yi log p̂i+(1−yi)log(1−p̂i)]：实际类 1 且 p̂=0.95 时损失 0.05，p̂=0.60 时 0.51，p̂=0.10（自信但错误）时 2.30；实际类 0 时对称。

差异：补习资料覆盖交叉熵/对数损失、自信犯错高惩罚、公式与直观理解，但具体数值示例（0.05/0.51/2.30）未明确。
建议：补充交叉熵数值示例。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 58 页 · `09_linear_regression_50c9a546_57_0`：Training Logistic Regression
– We need a cost function that rewards high probability for the
correct class. – Logistic regression commonly uses log loss / cross-entropy,
instead of Least Square error
– The cost is high when the model is confidently wrong
– The formula is
𝑛
1
𝐽 𝜃 = − ෍ 𝑦 log 𝑝Ƹ + 1 − 𝑦 log(1 − 𝑝Ƹ )
𝑖 𝑖 𝑖 𝑖
𝑛
𝑖=1
The University of Sydney Page 58
- 09_linear_regression_and_logistic_regression.pdf · 第 58 页 · `09_linear_regression_50c9a546_57_1`：Training Logistic Regression
– We need a cost function that rewards high probability for the
correct class. – Logistic regression commonly uses log loss / cross-entropy,
instead of Least Square error
– The cost is high when the model is confidently wrong
– The formula is
𝑛
1
𝐽 𝜃 = − ෍ 𝑦 log 𝑝Ƹ + 1 − 𝑦 log(1 − 𝑝Ƹ )
𝑖 𝑖 𝑖 𝑖
𝑛
𝑖=1
The University of Sydney Page 58
- 09_linear_regression_and_logistic_regression.pdf · 第 59 页 · `09_linear_regression_50c9a546_58_0`：Cross entry loss example
– The individual case loss: − 𝑦 log 𝑝Ƹ + 1 − 𝑦 log(1 − 𝑝Ƹ )
𝑖 𝑖 𝑖 𝑖
Actual class 𝑝Ƹ = 𝑃(𝑌 = 1|𝑋) Interpretation Cross-entropy loss
1 0. 95 Confident and correct −log(0. 95) = 0. 05
1 0. 60 Correct, but less confident −log(0. 60) = 0. 51
1 0. 10 Confident but wrong −log(0. 10) = 2. 30
0 0. 05 Confident and correct −log(0. 95) = 0. 05
0 0. 40 Correct but less confident −log(
- 09_linear_regression_and_logistic_regression.pdf · 第 59 页 · `09_linear_regression_50c9a546_58_1`：10) = 2. 30
The University of Sydney Page 59

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 5.5 损失函数 · `tutoring_8dc0d7188f3c_section35_0_0`：逻辑回归的代价函数使用 对数损失 (Log Loss) 或 交叉熵 (Cross-Entropy)： MSE 的问题：如果逻辑回归使用 MSE，损失函数会是非凸函数（Non-convex），有很多局部最小值，难以找到全局最优解。 Cross-Entropy 的优势：它是凸函数，能保证找到全局最优解。 优化方法：梯度下降
- 9 Linear Regression & Logistic Regression .docx · 2.1.3交叉熵损失 Cross entropy loss · `tutoring_8dc0d7188f3c_section3_0_0`：适用于分类问题（预测类别，如图片是猫还是狗） 交叉熵损失衡量的是模型预测出的概率分布与真实标签的概率分布之间的差异。 目标：让模型对正确答案的预测概率尽可能高（接近1），对其他错误答案的预测概率尽可能低（接近0）。 工作原理：模型预测得越准，交叉熵损失值就越小；预测得越差，损失值就越大。 在模型训练过程中，我们的目标就是通过不断调整模型参数，来最小化这个交叉熵损失。 直观理解：当真实标签为 1 时，我们希望模型预测的概率也接近 1。 如果此时模型预测了一个很低的概率（比如 0. 1），那么 log(0. 1) 会是一个很大的负数，再乘以前面的负号，就会导致损失值变得很大，表示惩罚很重。
- 9 Linear Regression & Logistic Regression .docx · 2.1.3交叉熵损失 Cross entropy loss · `tutoring_8dc0d7188f3c_section3_0_1`：1），那么 log(0. 1) 会是一个很大的负数，再乘以前面的负号，就会导致损失值变得很大，表示惩罚很重。 二分类交叉熵损失 这个公式就是将所有样本（无论是正类还是负类）的预测误差加起来求平均，用来评估模型整体的分类准确度。

## T030 机器学习实践技巧与特征缩放 — 已覆盖

先将 ML 模型与最简单基线比较并迭代；最佳策略常是更简单模型加更多/更好数据；始终在未用于训练的留出数据上测试。确保特征在相似尺度上，重缩放特征使其零均值、单位方差：x̄j=(1/n)Σxj(i)，替换为 xj(i)=(xj(i)−x̄j)/sj，sj 为特征 j 的标准差。缩放后更容易找到对所有参数都适用的学习率；若特征尺度差异大，适合一个权重的学习率可能对另一个权重过大或过小。

差异：补习资料覆盖baseline比较、held-out测试、特征缩放零均值单位方差及学习率，但标准化公式未明确。
建议：补充特征缩放公式。
置信度（仅供排序）：0.80

**最新学校课件证据**
- 09_linear_regression_and_logistic_regression.pdf · 第 61 页 · `09_linear_regression_50c9a546_60_0`：Tips and tricks
– Compare ML models to the simplest baseline first; Iterate
– Best strategy is often a simpler model with more/better data
– Always test on held-out data that hasn’t been used for training
The University of Sydney Page 61
- 09_linear_regression_and_logistic_regression.pdf · 第 62 页 · `09_linear_regression_50c9a546_61_0`：Tips and tricks
– Make sure features are on a similar scale. – Rescale features to have zero mean and unit variance
– Let 𝑥ҧ be the mean of feature 𝑗: 𝑥ҧ =
1 σ𝑛
𝑥
(𝑖)
𝑗 𝑗 𝑖=1 𝑗
𝑛
– Replace each value with:
(𝑖)
𝑥 − 𝑥ത
(𝑖) 𝑗 𝑗
𝑥 =
𝑗 𝑠
𝑗
– 𝑠 is the standard deviation of feature 𝑗
𝑗
– After recalling features, it is easier to find a learning rate that works
well for all weights. – If the features are 
- 09_linear_regression_and_logistic_regression.pdf · 第 62 页 · `09_linear_regression_50c9a546_61_1`：– If the features are on vastly different scales, a learning rate that works well
for updating one weight might be too large or too small to update the other
weight equally well. The University of Sydney Page 62

**往期补习课件证据**
- 9 Linear Regression & Logistic Regression .docx · 6. Tips · `tutoring_8dc0d7188f3c_section36_0_0`：与简单 baseline 比较 简单模型 + 更多数据往往更好 始终在 held-out 数据上测试 任何预测模型 = 模型形式 Model Form + 成本函数 Cost Function + 优化算法
- 9 Linear Regression & Logistic Regression .docx · 2.6 特征缩放 · `tutoring_8dc0d7188f3c_section21_0_1`：通过缩放，让所有特征处于相似的数值范围（如均值为 0，方差为 1），使等高线图变成圆形。 这样梯度下降可以沿着最短路径直接走向全局最小值，极大地提升训练速度。
- 9 Linear Regression & Logistic Regression .docx · 2.2.3 学习率 learning rate · `tutoring_8dc0d7188f3c_section5_0_0`：作用： 控制参数更新的幅度。 当计算出梯度后，学习率决定了参数前进的步长。 学习率过大： 训练震荡，难以收敛，甚至导致损失函数数值爆炸（Loss Nan）。 学习率过小： 收敛速度极慢，需要大量训练时间，容易陷入局部最优解。 常用技巧： 可以从 0. 1, 0. 01, 0. 001 等数量级开始尝试 逐渐缩小学习率（学习率衰减）也是一个好策略
