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
    return list(itertools.chain.from_iterable([list(zip([x] * len(esg), esg))\
                                                for x in list(range(from_year, to_year))]               \
                                ))

def backtesting(back_obj, price_file, save_file=None, method='eq'):
    """
    :param back_obj:
    :param price_file: Price File (Might be changed)
    :param save_file:
    :return:
    """
    back_obj = OrderedDict(sorted(back_obj.items(), key=lambda v:v))
    price_df = pd.read_csv(price_file, header=[0, 1], encoding='euc-kr', parse_dates=[0], index_col=0)

    price_val = []

    for key, val in back_obj.items():
        price_val.extend(price_df[key[0]:key[1]][val].fillna(0).apply(np.average, axis=1))

    start_date = list(back_obj.keys())[0][0]
    end_date = list(back_obj.keys())[-1][1]

    date_axis = pd.date_range(start_date, end_date, periods=len(price_val))
    plt.plot(date_axis, price_val)

    if save_file:
        plt.savefig(save_file)

    plt.show()


if __name__ == "__main__":
    test_obj = {
        (datetime(2011, 1, 1), datetime(2012, 1, 1)):['A000010', 'A000120', 'A000200'],
        (datetime(2012, 1, 1), datetime(2013, 1, 1)):['A000110', 'A000220', 'A000300']
    }
    backtesting(test_obj, './data/Adjusted Price.csv', save_file="test.png")

