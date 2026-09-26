import time
from collections import defaultdict
from random import SystemRandom


# 全局真随机生成器
rng = SystemRandom()


class FairRandomPicker:
    def __init__(self, items):
        self.items = items
        self.history = defaultdict(int)  # 记录每个人的被抽中次数
        self.cooldown = {}  # 记录每个人的屏蔽到期时间

    def calculate_weights(self):
        weights = []
        now = time.time()
        for item in self.items:
            # 1. 基础权重 (保证每个人都有初始机会)
            w = 10.0

            # 2. 极端公平：频率惩罚(历史越少,权重越高,指数级拉平)
            # 加上 1 防止除零,乘数越大,公平性干预越强
            w += 100.0 / (self.history[item] + 1)

            # 3. 极端公平：冷却屏蔽(刚抽完立即失去资格,强制拉平)
            if item in self.cooldown and now - self.cooldown[item] < 30:  # 30秒冷却
                w = 0.0  # 权重归零,强制跳过

            weights.append(w)
        return weights

    def pick(self):
        weights = self.calculate_weights()
        # 4. 极端随机：基于上述公平权重,使用系统熵源进行不可复现的选择
        chosen = rng.choices(self.items, weights=weights, k=1)[0]

        # 更新历史记录,形成闭环反馈
        self.history[chosen] += 1
        self.cooldown[chosen] = time.time()
        return chosen
