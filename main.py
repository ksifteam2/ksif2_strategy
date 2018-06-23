"""
    Title   : Project ESGing
    Author  : Jiwoo Park, Misun Gong
    Date    : 2018.6.11
"""
# TODO 
# 0. Configs
# 1. Classification
# 2. Weight
# 3. Score ( Upper 75% )
# 4. Financial Filter
# - 레버리지: 자기자본 대비 부채 비율(총부채/자기자본) < 2
# - 유동성: 당좌비율((유동자산-재고자산)/유동부채 > 1)
# - PER: 주가이익비율(주가/주당순이익) > 1
# - PBR: 주가순자산비율(주가/주당순자산) > 1
# 5. Add Momentum

from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import utils

esg_weight = {'S': 150, 'A+': 120, 'A':100, 'B':90, 'B+':95, 'C':80, 'D':70, 'B이하':80}
year_weight = {2011 : 1, 2012 : 2, 2013 : 3, 2014: 4, 2015 : 5, 2016: 6, 2017 : 7}
sector_weight = {'경기소비재' : 3, '소재' : 3, '산업재' : 3, 'IT' : 3, '금융' : 3, '의료' : 3, '유틸리티' : 4, '통신서비스' : 4, '필수소비재' : 3, '에너지' : 3}
# sector_weight
ESG_SCORE = './data/ESG_Grade.csv'
df = pd.read_csv(ESG_SCORE)

sector_code = './data/firm_sector_code.csv'
code_df = pd.read_csv(sector_code)
ESG = {'지배구조' : 'G', '사회' : 'S', '환경': 'E', 'ESG등급':'ESG'}

price_file = './data/price.csv'
price_df = pd.read_csv(price_file)
price_df['Date'] = pd.to_datetime(price_df['Date'], format='%m/%d/%Y')
price_df = price_df.set_index('Date').sort_index()
def init(df):
    """ Arrange DataFrame
    Args:
        param1 : dataframe to arrange
    Rets:
        No return
    """
    for col in df[['ESG등급', '지배구조', '사회', '환경']]:
        df['score_' + ESG[col]] = df[col].dropna().map(lambda x: esg_weight[x])
    del df['비고']
    
    df["기업코드"] = list(map(lambda x: "A" + ("000000" + str(x))[-6:] , df["기업코드"]))
    df = df.join(code_df.set_index('Firm'), on="기업코드")
    
    df.sort_values('산업명-대분류', inplace=True)
    df['산업명-대분류'].fillna('Not Classified', inplace=True)
    df = df.set_index(['산업명-대분류', '기업명', '기업코드'])
    
    multi_level_column = utils.make_year_esg_column()
    multi_level_column = pd.MultiIndex.from_tuples(multi_level_column)
    
    grouped_df = pd.DataFrame(index=df.index, columns=multi_level_column)
    for col in grouped_df:
        grouped_df[col] = df.loc[df['평가년도'] == col[0]]['score_' + col[1]]
    grouped_df = grouped_df[~grouped_df.index.duplicated(keep='first')]
    
    return grouped_df

def scoring(df, group_with='기업명', score_with="평가년도", scoring_dict=year_weight):
    """ Score item given weight
    Args:
        param1: df (DataFrame to calculate)
        param2: group_with (column name to group)
        param3: score_with (scoring criteria)
        param4: score_dict (scoring dictionary)
    Return:
        Series that is scored with standard.
    """
    score = df.groupby(group_with)              \
              .apply(lambda x:                  \
                        sum(x[score_with]       \
                            .apply(             \
                                lambda y: scoring_dict[y]
                    )))
    return score

def normalize_score(df):
    """ Normalize ESG score with Min Max scoring
    Args:
        param1 : dataframe
    Return:
        normalized DataFrame
    """
    grouped = df.groupby(df.index.get_level_values(0))
    return (df - grouped.min()) / (grouped.max() - grouped.min())

def summary_normal_esg(df, _from=2011, _to=2017):
    """ Calculate normal esg score with given period, sector, and dataframe
    Args:
        param1 : dataframe (DataFrame)
        param2 : sector (string)
        param3 : from period (int)
        param4 : to period (int)
    """
    period = list(range(_from, _to))
    for year in period:
        df[str(year) + '_score'] = df[year].sum(axis=1)
    return df

def get_firm_benchmark_by_sector(df, sector, year, limit=3):
    """ Get benchmark firm list from dataframe based upon ESG score with sector
    """
    
    ret = df[year].loc[sector].sum(axis=1).sort_values(ascending=False)[:limit]
    return ret

def get_firm_benchmark(df, year, limit=3):
    """ Get benchmark firm list from dataframe based upon ESG score with all
    """
    sector_all = df.index.levels[0]
    ret = []
    for sector in sector_all:
        ret.append(get_firm_benchmark_by_sector(df, sector, year, limit))
    return pd.concat(ret)

def get_firm_momentum_one_period(df, year):
    """ Helper function of ESG Momentum
    """
    return df[df[str(year) + '_score'] <= df[str(year + 1) + '_score']]

def get_firm_momentum_by_sector(df, sector, _from=2011, _to=2017):
    """ Get firm list from dataframe based upon ESG momentum
    Args:
        param1 : dataframe (dataframe)
        param2 : sector (string)
        param3 : from year (int)
        param4 : to year (to)
    Return
        filtered and arranged dataframe only have momentum
    """
    columns = list(map(lambda x: str(x) + '_score', 
                list(range(_from, _to + 1))
                ))
    df = df.loc[sector]
    for year in list(range(_from, _to)):
        df = get_firm_momentum_one_period(df, year)
    return df[columns]

def get_firm_momentum(df, _from, _to):
    """ Get firm based upon firm ESG momentum
    """
    sector_all = df.index.levels[0]
    ret = []
    for sector in sector_all:
        ret.append(get_firm_momentum_by_sector(df, sector, _from, _to))
    return pd.concat(ret)

def get_return_series(firm_list, period):
    """ Return return series of eq-weight portfolio in given period. This period
    is yearly base starts from July 1st.
    Args:
        param1 : list of firm (List)
        param2 : period tuple (int, int)    
    Return:
        Equal weighted portfolio's return
    """
    s = datetime(period[0], 7, 1)
    e = datetime(period[1], 7, 1)
    price_bm = price_df[firm_list][1:]
    price_bm = price_bm.rolling(window=2).apply(lambda x: (x[-1] - x[0]) / x[0])
    
    return price_bm.mean(axis=1)[s:e]

def get_firm_name_with_code(code):
    # df[('A' + ("000000" + df['기업코드'])[-6:]) == code]

    return df.loc[code.values]

if __name__ == "__main__":
    maindf = init(df)
    maindf = normalize_score(maindf)
    maindf = summary_normal_esg(maindf)

    period_list = list(zip(range(2011, 2017), range(2012, 2018)))
    bm_return = pd.Series([1], index=[datetime(2011, 6, 30)])
    
    init_seed = 1
    for period in period_list:
        bm_list = get_firm_benchmark(maindf, period[0]).index
        print("{}: \n {}".format(period,", ".join(bm_list.get_level_values('기업코드').values)))
        return_series = get_return_series(bm_list.get_level_values('기업코드'), (period[0], period[1])) + 1
        bm_return = bm_return.append(return_series * init_seed)
        init_seed = return_series.cumprod().iloc[-1]
        print("**{}**".format(init_seed))
        # print(init_seed)
    # print(bm_return)
    # plt.plot(bm_return)
    # plt.show()
    # bm_list = get_firm_benchmark(maindf).index.get_level_values('기업코드')
    # bm_return = get_return_series(temp, (2012, 2013))
    # plt.plot(bm_return)
    # plt.show()
