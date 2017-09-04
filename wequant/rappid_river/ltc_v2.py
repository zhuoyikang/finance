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
    "end_time": "2017-09-04 20:00:00",
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
    context.frequency = "15m"
    # 设置回测基准, 比特币："huobi_cny_ltc", 莱特币："huobi_cny_ltc", 以太坊："huobi_cny_eth"
    context.benchmark = "huobi_cny_ltc"
    # 设置回测标的, 比特币："huobi_cny_ltc", 莱特币："huobi_cny_ltc", 以太坊："huobi_cny_eth"
    context.security = "huobi_cny_ltc"

    # 设置ATR值回看窗口
    context.user_data.T = 20

    # 买入参数
    context.user_data.ma5_cp = 5  # 数据比较位
    context.user_data.ma10_cp = 3  # 数据比较位
    context.user_data.ma30_cp = 2  # 数据比较位
    context.user_data.ma60_cp = 1  # 数据比较位
    context.user_data.buy_long_window = 60 + context.user_data.ma60_cp

    # 自定义的初始化函数
    init_local_context(context)

    # 至此initialize函数定义完毕。


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
def is_uping(context, hist):
    hist_close = hist["close"]

    ma5 = np.mean(hist_close[-1 * 5:])
    ma10 = np.mean(hist_close[-1 * 10:])
    ma30 = np.mean(hist_close[-1 * 30:])
    ma60 = np.mean(hist_close[-1 * 60:])

    # 当前ma5穿越ma10再进入一步判断
    # if ma5 < ma10:
    #     return False

    if ma10 < ma30:
        return False

    # if ma_is_upping(context, hist_close, context.user_data.ma5_cp, 5) == False:
    #     return False

    if  ma_is_upping(context, hist_close, context.user_data.ma10_cp, 10) == False:
        return False

    if  ma_is_upping(context, hist_close, context.user_data.ma30_cp, 30) == False:
        return False

    # if ma_is_upping(context, hist_close, context.user_data.ma60_cp, 60) == False:
    #     return False

    return True



def is_downing(context, hist, no):
    hist_close = hist["close"]

    ma5 = np.mean(hist_close[-1 * 5:])
    ma10 = np.mean(hist_close[-1 * 10:])
    ma30 = np.mean(hist_close[-1 * 30:])
    ma60 = np.mean(hist_close[-1 * 60:])

    # 当前ma5低于ma10再进入一步判断
    if ma5 > ma10:
        return False

    # if (ma10 - ma5) / ma10 < context.user_data.sell_threshold:
    #     return False

    if no >= 5 and ma_is_downing(context, hist_close, context.user_data.ma5_cp, 5) == False:
        return False

    if no >= 10 and  ma_is_downing(context, hist_close, context.user_data.ma10_cp, 10) == False:
        return False

    if no >= 30 and ma_is_downing(context, hist_close, context.user_data.ma30_cp, 30) == False:
        return False

    return True


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

    # 2 判断加仓或止损
    if context.user_data.hold_flag is True and context.account.huobi_cny_ltc > 0:  # 先判断是否持仓
        temp = add_or_stop(price, context.user_data.last_buy_price, atr, context, hist.iloc[:len(hist) - 1])
        if temp == 1:  # 判断加仓
            if context.user_data.add_time < context.user_data.limit_unit:  # 判断加仓次数是否超过上限
                context.log.info("产生加仓信号")
                cash_amount = min(context.account.huobi_cny_cash, context.user_data.unit * price)  # 不够1 unit时买入剩下全部
                context.user_data.last_buy_price = price
                if cash_amount >= HUOBI_CNY_LTC_MIN_ORDER_CASH_AMOUNT:
                    context.user_data.add_time += 1
                    context.log.info("正在买入 %s" % context.security)
                    context.log.info("下单金额为 %s 元" % cash_amount)
                    context.order.buy(context.security, cash_amount=str(cash_amount))
                else:
                    context.log.info("订单无效，下单金额小于交易所最小交易金额")
            else:
                context.log.info("加仓次数已经达到上限，不会加仓")
        elif temp == -1:  # 判断止损
            # 重新初始化参数！重新初始化参数！重新初始化参数！非常重要！
            init_local_context(context)
            # 卖出止损
            context.log.info("产生止损信号")
            context.log.info("正在卖出 %s" % context.security)
            context.log.info("卖出数量为 %s" % context.account.huobi_cny_ltc)
            context.order.sell(context.security, quantity=str(context.account.huobi_cny_ltc))
            # 3 判断入场离场
    else:
        out = in_or_out(context, hist.iloc[:len(hist) - 1], price, context.user_data.T)
        if out == 1:  # 入场
            if context.user_data.hold_flag is False:
                value = context.account.huobi_cny_net * 0.01
                context.user_data.unit = calc_unit(value, atr)
                context.user_data.add_time = 1
                context.user_data.hold_flag = True
                context.user_data.last_buy_price = price
                cash_amount = min(context.account.huobi_cny_cash, context.user_data.unit * price)
                # 有买入信号，执行买入
                context.log.info("产生入场信号 %s"%(value))
                context.log.info("正在买入 %s" % context.security)
                context.log.info("下单金额为 %s 元" % cash_amount)
                context.order.buy(context.security, cash_amount=str(cash_amount))
            else:
                context.log.info("已经入场，不产生入场信号")

        elif out == -1:  # 离场
            if context.user_data.hold_flag is True:
                if context.account.huobi_cny_ltc >= HUOBI_CNY_LTC_MIN_ORDER_QUANTITY:
                    context.log.info("产生止盈离场信号")
                    # 重新初始化参数！重新初始化参数！重新初始化参数！非常重要！
                    init_local_context(context)
                    # 有卖出信号，且持有仓位，则市价单全仓卖出
                    context.log.info("正在卖出 %s" % context.security)
                    context.log.info("卖出数量为 %s" % context.account.huobi_cny_ltc)
                    context.order.sell(context.security, quantity=str(context.account.huobi_cny_ltc))
            else:
                context.log.info("尚未入场或已经离场，不产生离场信号")


# 用户自定义的函数，可以被handle_data调用:用于初始化一些用户数据
def init_local_context(context):
    # 上一次买入价
    context.user_data.last_buy_price = 0
    # 是否持有头寸标志
    context.user_data.hold_flag = False
    # 限制最多买入的单元数
    context.user_data.limit_unit = 4
    # 现在买入1单元的security数目
    context.user_data.unit = 0
    # 买入次数
    context.user_data.add_time = 0


# 用户自定义的函数，可以被handle_data调用: 唐奇安通道计算及判断入场离场
# data是日线级别的历史数据，price是当前分钟线数据（用来获取当前行情），T代表需要多少根日线
def in_or_out(context, data, price, T):
    up = np.max(data["high"].iloc[-T:])
    # 这里是T/2唐奇安下沿，在向下突破T/2唐奇安下沿卖出而不是在向下突破T唐奇安下沿卖出，这是为了及时止损
    down = np.min(data["low"].iloc[-int(T / 2):])
    context.log.info("当前价格为: %s, 唐奇安上轨为: %s, 唐奇安下轨为: %s" % (price, up, down))

    hist = context.data.get_price(context.security, count=context.user_data.buy_long_window,
                                  frequency=context.frequency)

    if len(hist.index) < context.user_data.buy_long_window:
        return 0

    if price < down and  is_downing(context, hist, 10):
        return -1


    if is_uping(context, hist) == True and context.account.huobi_cny_cash > HUOBI_CNY_LTC_MIN_ORDER_CASH_AMOUNT:
        return 1

    return 0

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


# 用户自定义的函数，可以被handle_data调用
# 计算unit
def calc_unit(per_value, atr):
    return per_value / atr


# 用户自定义的函数，可以被handle_data调用
def add_or_stop(price, lastprice, atr, context, data):
    T = context.user_data.T
    # 这里是T/2唐奇安下沿，在向下突破T/2唐奇安下沿卖出而不是在向下突破T唐奇安下沿卖出，这是为了及时止损
    up = np.max(data["high"].iloc[-T:])
    down = np.min(data["low"].iloc[-int(T / 2):])

    context.log.info("当前价格为: %s, 唐奇安上轨为: %s, 唐奇安下轨为: %s" % (price, up, down))
    hist = context.data.get_price(context.security, count=context.user_data.buy_long_window,
                                  frequency=context.frequency)
    if len(hist.index) < context.user_data.buy_long_window:
        return 0

    if price < down and is_downing(context, hist, 10):
        return -1

    # 当趋势线向上则买入
    if is_uping(context, hist) == True and context.account.huobi_cny_cash > HUOBI_CNY_LTC_MIN_ORDER_CASH_AMOUNT:
        return 1

    return 0
