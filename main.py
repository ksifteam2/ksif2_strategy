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
# 4. Financial Statistics
# 5. Add Momentum

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import utils
# import configparser

# config = configparser.ConfigParser()
# config.read('./conf.ini')
esg_weight = {'S': 150, 'A+': 120, 'A':100, 'B':90, 'B+':95, 'C':80, 'D':70, 'B이하':80}
year_weight = {2011 : 1, 2012 : 2, 2013 : 3, 2014: 4, 2015 : 5, 2016: 6, 2017 : 7}
sector_weight = {'경기소비재' : 3, '소재' : 3, '산업재' : 3, 'IT' : 3, '금융' : 3, '의료' : 3, '유틸리티' : 4, '통신서비스' : 4, '필수소비재' : 3, '에너지' : 3}
# sector_weight
ESG_SCORE = './data/ESG_Grade.csv'
df = pd.read_csv(ESG_SCORE)

sector_code = './data/firm_sector_code.csv'
code_df = pd.read_csv(sector_code)
ESG = {'지배구조' : 'G', '사회' : 'S', '환경': 'E', 'ESG등급':'ESG'}

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
    df = df.join(code_df.set_index('Firm Num'), on="기업코드")
    
    df.sort_values('산업명-대분류', inplace=True)
    df['산업명-대분류'].fillna('Not Classified', inplace=True)
    df = df.set_index(['산업명-대분류', '기업명'])
    
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

def normalize_score(df, group_by="산업명-대분류"):
    """ Normalize ESG score with Min Max scoring
    Args:
        param1 : dataframe
    Return:
        normalized DataFrame
    """
    grouped = df.groupby(group_by)
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

def get_firm_benchmark(df, sector, _from=2011, _to=2017, limit=3):
    """ Get benchmark firm list from dataframe based upon ESG score
    """
    period = list(range(_from, _to))
    period = list(map(lambda x: str(x) + '_score', period))
    return df[period].loc[sector].sum(axis=1).sort_values(ascending=False)[:limit]

def get_firm_momentum_one_period(df, year):
    """ Helper function of ESG Momentum
    """
    return df[df[str(year) + '_score'] <= df[str(year + 1) + '_score']]

def get_firm_momentum(df, sector, _from=2011, _to=2017):
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

if __name__ == "__main__":
    maindf = init(df)
    maindf = normalize_score(maindf)
    maindf = summary_normal_esg(maindf)
    # for sector in maindf.index.levels[0]:
    #     print('{} : \n{}'.format(
    #         sector,
    #         get_firm_benchmark(maindf, sector, 2012, 2014))
    #     )
    for sector in maindf.index.levels[0]:
        print('{} : \n {}'.format(
            sector, 
            get_firm_momentum(maindf, sector, 2014, 2015)
        ))

    # print(set(maindf['산업명-대분류']))
    # print(scoring(maindf))