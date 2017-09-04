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


# 阅读 1，首次阅读可跳过:
# PARAMS 用于设定程序参数，回测的起始时间、结束时间、滑点误差、初始资金和持仓。
# 可以仿照格式修改，基本都能运行。如果想了解详情请参考新手学堂的 API 文档。
PARAMS  = {
    "start_time": "2017-09-2 22:00:00",  # 回测起始时间
    "end_time": "2017-09-04 20:00:00",  # 回测结束时间
    "commission": 0.002,  # 此处设置交易佣金
    "slippage": 0.001,  # 此处设置交易滑点
    "account_initial": {"huobi_cny_cash": 100000,
                        "huobi_cny_ltc": 0},  # 设置账户初始状态
}


# 阅读 2，遇到不明白的变量可以跳过，需要的时候回来查阅:
# initialize 函数是两大核心函数之一（另一个是 handle_data），用于初始化策略变量。
# 策略变量包含：必填变量，以及非必填（用户自己方便使用）的变量
def initialize(context):
    context.frequency = "15m"
    context.benchmark = "huobi_cny_ltc"
    context.security = "huobi_cny_ltc"

    # 买入参数
    context.user_data.buy_ma5_cp = 5  # 数据比较位
    context.user_data.buy_ma10_cp = 3  # 数据比较位
    context.user_data.buy_ma30_cp = 2  # 数据比较位
    context.user_data.buy_ma60_cp = 1  # 数据比较位

    context.user_data.sell_ma5_cp = 3  # 数据比较位
    context.user_data.sell_ma10_cp = 1  # 数据比较位
    context.user_data.sell_ma30_cp = 1  # 数据比较位
    context.user_data.sell_ma60_cp = 1  # 数据比较位

    context.user_data.buy_long_window = 60 + context.user_data.buy_ma60_cp
    # context.user_data.buy_frenquency = "30m"
    context.user_data.buy_frenquency = context.frequency
    context.user_data.status = "buy"

    #context.user_data.buy_threshold = 0.01
    context.user_data.price_threshold = 0.00
    context.user_data.sell_threshold = 0.03
    context.user_data.buy_price = 0.0



# 是否在上升
def ma_is_upping(context, array, cp_nice, ma):
    move_god = 0
    while cp_nice > 0 :
        cp_nice -=1
        if move_god == 0 :
            c1 = np.mean(array[-1*ma - move_god:])
        else:
            c1 = np.mean(array[-1*ma - move_god: -move_god])

        c2 = np.mean(array[-1*ma - move_god -1:-move_god -1])
        #context.log.info("c2 %s c1 %s"%(c2, c1))
        move_god +=1
        if c1 < c2:
            return False

    #context.log.info("ma %s is upping ---------------> "%(ma))
    return True



# 是否在下降
def ma_is_downing(context, array, cp_nice, ma):
    move_god = 0

    while cp_nice > 0 :
        cp_nice -=1
        if move_god == 0 :
            c1 = np.mean(array[-1*ma - move_god:])
        else:
            c1 = np.mean(array[-1*ma - move_god: -move_god])

        c2 = np.mean(array[-1*ma - move_god -1: -move_god -1])
        #context.log.info("c2 %s c1 %s"%(c2, c1))
        move_god +=1
        if c1 > c2:
            return False

    #context.log.info("ma %s is downing ---------------->"%(ma))
    return True



# 石佛那个在整体上升
def is_uping(context, hist_close):

    ma5 = np.mean(hist_close[-1 * 5:])
    ma10 = np.mean(hist_close[-1 * 10:])
    ma30 = np.mean(hist_close[-1 * 30:])
    ma60 = np.mean(hist_close[-1 * 60:])

    # 当前ma5穿越ma10再进入一步判断
    # if ma5 < ma10:
    #     return False

    if ma10 < ma30:
        return False

    # if ma_is_upping(context, hist_close, context.user_data.buy_ma5_cp, 5) == False:
    #     return False

    if ma_is_upping(context, hist_close, context.user_data.buy_ma10_cp, 10) == False:
        return False

    if ma_is_upping(context, hist_close, context.user_data.buy_ma30_cp, 30) == False:
        return False

    if ma_is_upping(context, hist_close, context.user_data.buy_ma60_cp, 60) == False:
        return False

    context.log.info("uping buy time occur ma5 %s ma10 %s ma30 %s ma60 %s" %(ma5, ma10,ma30, ma60))
    return True


# 判断是不是一个好的买入时机
# ma5超越ma10，并且ma5,ma10,ma30共同处于上升期，则为买入时机.
def handle_buy(context, hist):
    # 买入时机只抓一次
    # if context.user_data.status != "buy":
    #     return

    hist_close = hist["close"]
    if is_uping(context, hist_close) == False:
        return

    if context.account.huobi_cny_cash <= HUOBI_CNY_LTC_MIN_ORDER_CASH_AMOUNT:
        #context.log.info("想买，但是没钱")
        return

    # 有买入信号，且持有现金，则市价单全仓买入
    buy_quantity = context.account.huobi_cny_cash/hist_close[-1]*0.98

    if buy_quantity < HUOBI_CNY_LTC_MIN_ORDER_QUANTITY:
        # context.user_data.status = "sell"
        # context.log.info("想买，但是已经满仓 %s" % context.security)
        return


    # 只买一次，能买多少是多少
    context.log.info("正在买入 %s" % context.security)
    context.log.info("下单金额为 %s 元" % context.account.huobi_cny_cash)

    context.user_data.status = "sell"

    if context.user_data.buy_price < hist_close[-1]*1.01:
        context.user_data.buy_price = hist_close[-1]*1.01
    context.order.buy_limit(context.security, quantity=str(buy_quantity),
                            price=str(hist_close[-1]*1.01))



def is_downing(context, hist_close):
    ma5 = np.mean(hist_close[-1 * 5:])
    ma10 = np.mean(hist_close[-1 * 10:])
    ma30 = np.mean(hist_close[-1 * 30:])
    ma60 = np.mean(hist_close[-1 * 60:])

    # 当前ma5低于ma10再进入一步判断
    # if ma5 > ma10:
    #     return False

    if ma_is_downing(context, hist_close, context.user_data.sell_ma5_cp, 5) == False:
        return False

    if ma_is_downing(context, hist_close, context.user_data.sell_ma10_cp, 10) == False:
        return False

    if ma_is_downing(context, hist_close, context.user_data.sell_ma30_cp, 30) == False:
        return False

    context.log.info("downing sell time occur ma5 %s ma10 %s ma30 %s ma60 %s" %(ma5, ma10,ma30, ma60))
    return True


# 判断是不是一个好的卖出时机，要清仓.
def handle_sell(context, hist):
    # if context.user_data.status != "sell":
    #     return

    hist_close = hist["close"]
    if is_downing(context, hist_close) == False:
        return

    if context.account.huobi_cny_ltc >= HUOBI_CNY_LTC_MIN_ORDER_QUANTITY:
        sell_price = hist_close[-1]*0.99

        # 计算亏损，如果亏损太大则不卖
        # if ((sell_price - context.user_data.buy_price) / context.user_data.buy_price) < context.user_data.price_threshold:
        #     return

        context.log.warn("正在卖出 %s" % context.security)
        context.log.warn("卖出数量为 %s" % context.account.huobi_cny_ltc)
        context.order.sell_limit(context.security, quantity=str(context.account.huobi_cny_ltc),
                                 price=str(hist_close[-1]*0.99))
    else:
        # 等待下一次买入
        context.user_data.status = "buy"


# 阅读 3，策略核心逻辑：
# handle_data 函数定义了策略的执行逻辑，按照 frequency 生成的 bar 依次读取并执行策略逻辑，直至程序结束。
# handle_data 和 bar 的详细说明，请参考新手学堂的解释文档。
def handle_data(context):
    hist = context.data.get_price(context.security, count=context.user_data.buy_long_window,
                                  frequency=context.user_data.buy_frenquency)
    if len(hist.index) < context.user_data.buy_long_window:
        context.log.info("bar 的数量不足, 等待下一根 bar...")
        return

    handle_buy(context, hist)
    handle_sell(context, hist)
