"""
    Utility gathered file
"""

import itertools

def make_year_esg_column(from_year=2011, to_year=2018, esg=('E', 'S', 'G')):
    return list(itertools.chain.from_iterable([list(zip([x] * len(esg), esg))\
                                                for x in list(range(from_year, to_year))]               \
                                ))