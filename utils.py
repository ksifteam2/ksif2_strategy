"""
    Utility gathered file
"""

import itertools
from collections import OrderedDict
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def make_year_esg_column(from_year=2011, to_year=2018, esg=('E', 'S', 'G')):
    return list(itertools.chain.from_iterable([list(zip([x] * len(esg), esg)) \
                                               for x in list(range(from_year, to_year))] \
                                              ))


def backtesting(back_obj, price_file, save_file=None, method='eq'):
    """
    :param back_obj:
    :param price_file: Price File (Might be changed)
    :param save_file:
    :return:
    """
    # TODO : date index based on price file
    back_obj = OrderedDict(sorted(back_obj.items(), key=lambda v: v))
    price_df = pd.read_csv(price_file, header=[0, 1], encoding='euc-kr', parse_dates=[0], index_col=0)

    price_val = []
    date_axis = []

    for period, firms in back_obj.items():
        try:
            price_val.extend(price_df[period[0]:period[1]][firms].fillna(0).apply(np.average, axis=1))
            date_axis.extend(price_df[period[0]:period[1]].index.values)
        except Exception as e:
            pass
            # print(key, firms)
            # print(e)

    plt.plot(date_axis, price_val)

    if save_file:
        plt.savefig(save_file)

    plt.show()


if __name__ == "__main__":
    test_obj = {
        (datetime(2017, 10, 1), datetime(2018, 1, 1)): ['A000020', 'A000030'],
        (datetime(2018, 1, 1), datetime(2018, 6, 20)): ['A000020', 'A000030']
    }
    backtesting(test_obj, './data/Adjusted Price.csv', save_file="test.png")
