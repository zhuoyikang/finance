# coding: utf-8
# 注：该策略仅供参考和学习，不保证收益。

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 策略代码总共分为三大部分，1)PARAMS 变量 2)initialize 函数 3)handle_data 函数
# 请根据指示阅读。或者直接点击运行回测按钮，进行测试，查看策略效果。

# 策略名称：简单双均线策略
# 策略详细介绍：https://wequant.io/study/strategy.simple_moving_average.html
# 关键词：价格突破、趋势跟踪。
# 方法：
# 1)计算一长一短两个时间窗口的价格均线
# 2)利用均线的突破来决定买卖

import numpy as np
from logging import DEBUG, INFO, WARN, ERROR


# 阅读 1，首次阅读可跳过:
# PARAMS 用于设定程序参数，回测的起始时间、结束时间、滑点误差、初始资金和持仓。
# 可以仿照格式修改，基本都能运行。如果想了解详情请参考新手学堂的 API 文档。
PARAMS = {
    "start_time": "2017-08-15 00:00:00",  # 回测起始时间
    "end_time": "2017-09-03 12:00:00",  # 回测结束时间
    "commission": 0.002,  # 此处设置交易佣金
    "slippage": 0.001,  # 此处设置交易滑点
    "account_initial": {"huobi_cny_cash": 100000,
                        "huobi_cny_ltc": 0},  # 设置账户初始状态
}


# 阅读 2，遇到不明白的变量可以跳过，需要的时候回来查阅:
# initialize 函数是两大核心函数之一（另一个是 handle_data），用于初始化策略变量。
# 策略变量包含：必填变量，以及非必填（用户自己方便使用）的变量
def initialize(context):
    # 设置回测频率, 可选："1m", "5m", "15m", "30m", "60m", "4h", "1d", "1w"
    context.frequency = "1m"
    # 设置回测基准, 比特币："huobi_cny_ltc", 莱特币："huobi_cny_ltc", 以太坊："huobi_cny_ltc"
    context.benchmark = "huobi_cny_ltc"
    # 设置回测标的, 比特币："huobi_cny_ltc", 莱特币："huobi_cny_ltc", 以太坊："huobi_cny_ltc"
    context.security = "huobi_cny_ltc"

    context.user_data.long_period = "5m"
    context.user_data.short_period = "5m"
    # 计算短线所需的历史 bar 数目，用户自定义的变量，可以被 handle_data 使用
    context.user_data.window_short = 5
    # 计算长线所需的历史 bar 数目，用户自定义的变量，可以被 handle_data 使用
    context.user_data.window_long = 20
    # 入场线, 用户自定义的变量，可以被 handle_data 使用
    context.user_data.enter_threshold = 0.03
    # 出场线, 用户自定义的变量，可以被 handle_data 使用
    context.user_data.exit_threshold = 0.05

    context.log.set_level(DEBUG)


# 阅读 3，策略核心逻辑：
# handle_data 函数定义了策略的执行逻辑，按照 frequency 生成的 bar 依次读取并执行策略逻辑，直至程序结束。
# handle_data 和 bar 的详细说明，请参考新手学堂的解释文档。
def handle_data(context):


    # 获取历史数据, 取后 window_long 根 bar
    hist = context.data.get_price(context.security, count=context.user_data.window_long,
                                  frequency=context.user_data.long_period)
    if len(hist.index) < context.user_data.window_long:
        context.log.warn("bar 的数量不足, 等待下一根 bar...")
        return

    # 计算短均线值
    close = np.array(hist["close"])
    short_mean = np.mean(hist["close"][-1 * context.user_data.window_short:])
    # 计算长均线值
    long_mean = np.mean(hist["close"][-1 * context.user_data.window_long:])

    # 价格上轨
    upper = long_mean + context.user_data.enter_threshold * long_mean
    # 价格下轨
    lower = long_mean - context.user_data.exit_threshold * long_mean


    # 短期线突破长期线一定比例，产生买入信号
    if short_mean > upper:
        context.log.warn("买入信号: 当前 短期均线 = %s, 长期均线 = %s, 上轨 = %s, 下轨 = %s" % (
                short_mean, long_mean, upper, lower))

        if context.account.huobi_cny_cash >= HUOBI_CNY_LTC_MIN_ORDER_CASH_AMOUNT:
            # 有买入信号，且持有现金，则市价单全仓买入
            buy_quantity = context.account.huobi_cny_cash/close[-1]*0.98
            if buy_quantity < HUOBI_CNY_LTC_MIN_ORDER_QUANTITY:
                context.log.warn("想买，但是已经满仓 %s" % context.security)
                return

            context.log.warn("正在买入 %s" % context.security)
            context.log.warn("下单金额为 %s 元" % context.account.huobi_cny_cash)
            context.order.buy_limit(context.security, quantity=str(buy_quantity),
                                    price=str(close[-1]*1.01))
            return
        else:
            context.log.info("资金不足，无法买入")
    else:
        context.log.debug("5m无交易信号，进入下一根 bar")



    # 获取历史数据, 取后 window_long 根 bar
    hist = context.data.get_price(context.security, count=context.user_data.window_long,
                                  frequency=context.user_data.short_period)
    if len(hist.index) < context.user_data.window_long:
        context.log.warn("bar 的数量不足, 等待下一根 bar...")
        return

    # 计算短均线值
    close = np.array(hist["close"])
    short_mean = np.mean(hist["close"][-1 * context.user_data.window_short:])
    # 计算长均线值
    long_mean = np.mean(hist["close"][-1 * context.user_data.window_long:])

    # 价格上轨
    upper = long_mean + context.user_data.enter_threshold * long_mean
    # 价格下轨
    lower = long_mean - context.user_data.exit_threshold * long_mean


    if short_mean < lower:
        context.log.warn("卖出信号: 当前 短期均线 = %s, 长期均线 = %s, 上轨 = %s, 下轨 = %s" % (
            short_mean, long_mean, upper, lower))

        if context.account.huobi_cny_ltc >= HUOBI_CNY_LTC_MIN_ORDER_QUANTITY:

            # 有卖出信号，且持有仓位，则市价单全仓卖出
            context.log.warn("正在卖出 %s" % context.security)
            context.log.warn("卖出数量为 %s" % context.account.huobi_cny_ltc)
            context.order.sell_limit(context.security, quantity=str(context.account.huobi_cny_ltc),
                                     price=str(close[-1]*0.99))
            return
        else:
            context.log.info("仓位不足，无法卖出")
    else:
        context.log.debug("1m无交易信号，进入下一根 bar")
