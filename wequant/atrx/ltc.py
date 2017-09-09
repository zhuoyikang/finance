# 注：该策略仅供参考和学习，不保证收益。

# !/usr/bin/env python
# -*- coding: utf-8 -*-

# 策略代码总共分为三大部分，1)PARAMS变量 2)initialize函数 3)handle_data函数
# 请根据指示阅读。或者直接点击运行回测按钮，进行测试，查看策略效果。

# 策略名称：海龟交易策略
# 策略详细介绍：https://wequant.io/study/strategy.turtle_trading.html
# 关键词：趋势跟随、资金管理、分批建仓、动态止损。
# 方法：
# 1)利用唐安奇通道来跟踪趋势产生买卖信号；
# 2)利用ATR（真实波幅均值）分批加仓或者减仓；
# 3)并且动态进行止盈和止损。


import numpy as np

# 阅读1，首次阅读可跳过:
# PARAMS用于设定程序参数，回测的起始时间、结束时间、滑点误差、初始资金和持仓。
# 可以仿照格式修改，基本都能运行。如果想了解详情请参考新手学堂的API文档。
PARAMS = {
    "start_time": "2017-09-1 00:00:00",
    "end_time": "2017-09-08 12:00:00",
    "commission": 0.002,  # 此处设置交易佣金
    "slippage": 0.001,  # 此处设置交易滑点
    "account_initial": {"huobi_cny_cash": 100000,
                        "huobi_cny_ltc": 0},
}


# 阅读2，遇到不明白的变量可以跳过，需要的时候回来查阅:
# initialize函数是两大核心函数之一（另一个是handle_data），用于初始化策略变量。
# 策略变量包含：必填变量，以及非必填（用户自己方便使用）的变量
def initialize(context):
    # 设置回测频率, 可选："1m", "5m", "15m", "30m", "60m", "4h", "1d", "1w"
    context.frequency = "30m"
    # 设置回测基准, 比特币："huobi_cny_ltc", 莱特币："huobi_cny_ltc", 以太坊："huobi_cny_eth"
    context.benchmark = "huobi_cny_ltc"
    # 设置回测标的, 比特币："huobi_cny_ltc", 莱特币："huobi_cny_ltc", 以太坊："huobi_cny_eth"
    context.security = "huobi_cny_ltc"

    # 设置ATR值回看窗口
    context.user_data.T = 14
    # 至此initialize函数定义完毕。


# 阅读3，策略核心逻辑：
# handle_data函数定义了策略的执行逻辑，按照frequency生成的bar依次读取并执行策略逻辑，直至程序结束。
# handle_data和bar的详细说明，请参考新手学堂的解释文档。
def handle_data(context):
    # 获取历史数 据
    hist = context.data.get_price(context.security, count=context.user_data.T + 1, frequency=context.frequency)
    if len(hist.index) < (context.user_data.T + 1):
        context.log.warn("bar的数量不足, 等待下一根bar...")
        return

    # 获取当前行情数据
    price = context.data.get_current_price(context.security)

    # 1 计算ATR
    atr = calc_atr(hist)
    context.log.info("%s"%(atr))



# 用户自定义的函数，可以被handle_data调用：ATR值计算
def calc_atr(data):  # data是日线级别的历史数据
    tr_list = []

    i = 1
    while i < len(data):
        tr = max(data["high"].iloc[i] - data["low"].iloc[i], data["high"].iloc[i] - data["close"].iloc[i - 1],
                 data["close"].iloc[i - 1] - data["low"].iloc[i])
        tr_list.append(tr)
        atr = np.array(tr_list).mean()
        i+=1
    return atr
