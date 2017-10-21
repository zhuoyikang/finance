#!/usr/bin/env python
# coding=utf-8

import os, sys

def usage():
    print "usage: updown.py 买入价格 本金"




if __name__=="__main__":
    if len(sys.argv) != 3:
        usage()
        exit()


    price = float(sys.argv[1])
    principal = float(sys.argv[2])
    # diff = 1000
    # rate = diff / principal
    rate = 0.04

    down = price -  (price * rate)
    up =  price +  (price * rate )

    print "rate:", rate
    print "up price:", up
    print "down price:", down

