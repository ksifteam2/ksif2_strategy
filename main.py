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
    df = df.set_index(['산업명-대분류', '기업명'])
    multi_level_column = list(itertools.chain.from_iterable([list(zip([x] * 3, ('E', 'S', 'G')))\
                                                for x in list(range(2011, 2018))]               \
                                ))
    
    multi_level_column = pd.MultiIndex.from_tuples(multi_level_column)
    grouped_df = pd.DataFrame(index=df.index, columns=multi_level_column)
    
    for col in grouped_df:
        grouped_df[col] = df.loc[df['평가년도'] == col[0]]['score_' + col[1]]
        
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

if __name__ == "__main__":
    maindf = init(df)
    print(maindf)
    # print(set(maindf['산업명-대분류']))
    # print(scoring(maindf))