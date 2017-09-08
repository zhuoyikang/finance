# !/usr/bin/env python
# -*- coding: utf-8 -*-

# 策略代码总共分为三大部分，1)PARAMS变量 2)initialize函数 3)handle_data函数
# 请根据指示阅读。或者直接点击运行回测按钮，进行测试，查看策略效果。

# 策略名称：R-Breaker策略
# 关键词：趋势跟踪、反转。
# 方法：
# 1)根据前一个交易日的收盘价、最高价和最低价数据通过一定方式计算出六个价位；
# 2)同时采取趋势跟踪和反转策略，既抓趋势，也抓反转。

from datetime import datetime

# 阅读1，首次阅读可跳过:
# PARAMS用于设定程序参数，回测的起始时间、结束时间、滑点误差、初始资金和持仓。
# 可以仿照格式修改，基本都能运行。如果想了解详情请参考新手学堂的API文档。
PARAMS = {
    "start_time": "2016-09-01 00:00:00",
    "end_time": "2017-09-07 00:00:00",
    "commission": 0.002,
    "slippage": 0.001,
    "account_initial": {"huobi_cny_cash": 100000,
                      "huobi_cny_ltc": 0},
}


# 阅读2，遇到不明白的变量可以跳过，需要的时候回来查阅:
# initialize函数是两大核心函数之一（另一个是handle_data），用于初始化策略变量。
# 策略变量包含：必填变量，以及非必填（用户自己方便使用）的变量
def initialize(context):
    # 设置回测频率, 可选：'1m', '5m', '15m', '30m', '60m', '1d', '1w', '1M', '1y'
    context.frequency = "4h"
    # 设置回测基准, 比特币：'huobi_cny_ltc', 莱特币：'huobi_cny_ltc', 以太坊：'huobi_cny_eth'
    context.benchmark = "huobi_cny_ltc"
    # 设置回测标的, 比特币：'huobi_cny_ltc', 莱特币：'huobi_cny_ltc', 以太坊：'huobi_cny_eth'
    context.security = "huobi_cny_ltc"


# 阅读3，策略核心逻辑：
# handle_data函数定义了策略的执行逻辑，按照frequency生成的bar依次读取并执行策略逻辑，直至程序结束。
# handle_data和bar的详细说明，请参考新手学堂的解释文档。
def handle_data(context):
    # 获取回看时间窗口内的历史数据
    hist = context.data.get_price(context.security, count=1, frequency='1d')
    if len(hist.index) < 1:
        context.log.warn("bar的数量不足, 等待下一根bar...")
        return

    # 前日最高价
    high_price = hist['high'][-1]
    # 前日最低价
    low_price = hist['low'][-1]
    # 前日收盘价
    close_price = hist['close'][-1]

    # 中心点
    pivot = (high_price + close_price + low_price) / 3

    # R-Breaker的阻力线和支撑线
    # 趋势策略-突破买入价
    buy_break = high_price + 2 * (pivot - low_price)
    # 反转策略-观察卖出价
    sell_setup = pivot + (high_price - low_price)
    # 反转策略-反转卖出价
    sell_enter = 2 * pivot - low_price
    # 反转策略-反转买入价
    buy_enter = 2 * pivot - high_price
    # 反转策略-观察买入价
    buy_setup = pivot - (high_price - low_price)
    # 趋势策略-突破卖出价
    sell_break = low_price - 2 * (high_price - pivot)

    # 获取当前价格
    current_price = context.data.get_current_price(context.security)

    d = context.time.get_current_bar_time().date()
    # 当前bar所在日期的开始时间
    today_start_time = datetime.combine(d, datetime.min.time())
    # 转化为字符串
    today_start_time = today_start_time.strftime("%Y-%m-%d %H:%M:%S")
    # 获取本日历史数据
    today_hist = context.data.get_price(context.security, start_time=today_start_time, frequency=context.frequency)

    # 当日最高价
    today_high = today_hist['high'].max()
    # 当日最低价
    today_low = today_hist['low'].min()

    context.log.info("当前价格=%.2f,日内最高价=%.2f" % (current_price, today_high))
    context.log.info("突破买入价=%.2f，观察卖出价=%.2f，反转卖出价=%.2f，反转买入价=%.2f，观察买入价=%.2f，突破卖出价=%.2f"
                     % (buy_break,sell_setup,sell_enter,buy_enter,buy_setup,sell_break))

    # 突破策略信号
    if current_price > buy_break:
        # 盘中价格超过突破买入价，则采取趋势策略，产生买入信号
        context.log.info("趋势策略买入信号：当前价格超过了突破买入价")
        if context.account.huobi_cny_cash >= HUOBI_CNY_LTC_MIN_ORDER_CASH_AMOUNT:
            # 市价单全仓买入
            context.log.info("正在买入 %s" % context.security)
            context.log.info("下单金额为 %s 元" % context.account.huobi_cny_cash)
            context.order.buy(context.security, cash_amount=str(context.account.huobi_cny_cash))
        else:
            context.log.info('现金不足，无法下单')
    elif current_price < sell_break:
        # 盘中价格跌破突破卖出价，则采取趋势策略，产生卖出信号
        context.log.info("产生趋势策略卖出信号：当前价格跌破了突破卖出价")
        if context.account.huobi_cny_ltc >= HUOBI_CNY_LTC_MIN_ORDER_QUANTITY:
            # 市价单全仓卖出
            context.log.info("正在卖出 %s" % context.security)
            context.log.info("卖出数量为 %s" % context.account.huobi_cny_ltc)
            context.order.sell(context.security, quantity=str(context.account.huobi_cny_ltc))
        else:
            context.log.info("仓位不足，无法卖出")
    # 反转策略信号
    elif today_high > sell_setup and current_price < sell_enter:
        # 当日内最高价超过观察卖出价后，盘中价格出现回落，且进一步跌破反转卖出价构成的支撑线，产生卖出信号
        context.log.info("反转策略卖出信号: 当前价格跌破反转卖出价,且日内最高价超过观察卖出价")
        if context.account.huobi_cny_ltc >= HUOBI_CNY_LTC_MIN_ORDER_QUANTITY:
            # 市价单全仓卖出
            context.log.info("正在卖出 %s" % context.security)
            context.log.info("卖出数量为 %s" % context.account.huobi_cny_ltc)
            context.order.sell(context.security, quantity=str(context.account.huobi_cny_ltc))
        else:
            context.log.info("仓位不足，无法卖出")
    elif today_low < buy_setup and current_price > buy_enter:
        # 当日内最低价低于观察买入价后，盘中价格出现反弹，且进一步超过反转买入价构成的阻力线，产生买入信号
        context.log.info("反转策略买入信号：当前价格突破了反转买入价,且日内最低价低于观察买入价")
        if context.account.huobi_cny_cash >= HUOBI_CNY_LTC_MIN_ORDER_CASH_AMOUNT:
            # 市价单全仓买入
            context.log.info("正在买入 %s" % context.security)
            context.log.info("下单金额为 %s 元" % context.account.huobi_cny_cash)
            context.order.buy(context.security, cash_amount=str(context.account.huobi_cny_cash))
        else:
            context.log.info('现金不足，无法下单')
    else:
        context.log.info("无交易信号，进入下一根bar")
