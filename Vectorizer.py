import math
from os import sep
from databases.core import Database
import pandas as pd
import re
from pandas.core.frame import DataFrame


class Vectorizer:
    # pass
    __bag_of_words = pd.DataFrame()
    __tokens = []
    __idfs = pd.DataFrame()
    __N = 0
    __configuration = ""

    def __init__(self, tokens, bow, n, config):
        self.__bag_of_words = bow
        self.__tokens = tokens
        self.__N = n
        self.__configuration = config
        self.__idfs = self.__idfGenerator()

    # static function => as util function
    @staticmethod
    def tfGenerator(token_paths: list) -> list:
        # return list of dataframe(token, frequency, occur)
        tokens = []
        for i in range(len(token_paths)):
            if re.search(r'.txt', token_paths[i]):
                with open(token_paths[i], 'r') as f:
                    token = str(f.read().strip()).split(", ")
                    df = pd.DataFrame.from_dict({
                        'token': list(i for i in token),
                        'frequency': list(1 for i in range(len(token)))
                    })
                    df = df.groupby(by=['token']).agg(
                        {'frequency': 'sum'}).reset_index()
                    df['occur'] = list(1 for i in range(len(df)))
                    tokens.append(df)
            else:
                df = pd.read_csv(token_paths[i])
                # print(df)
                tokens.append(df)
        return tokens

    def tfIdf(self) -> list:
        tfidfs = []
        # calculate weight as tf*idf
        # iterate parts of documents
        for token in self.__tokens:
            # count tf x idf using configs
            data = self.__termWeighting(token)
            tfidfs.append(data)
        print("Vectorizer.tfIdf() accessed")
        return (tfidfs)

    def __termWeighting(self, tokens) -> pd.DataFrame:
        # result => dataframe: token, frequency, idf, weight
        w = {}
        idf = {}
        for index, row in tokens.iterrows():
            idf[row[0]] = (
                self.__idfs.loc[self.__idfs['token'] == row[0]].idf.item())
            w[row[0]] = (row[1] * idf[row[0]])
            # w[row[0]] = (row[1] * idf_list.loc[idf_list['token']==row[0]]['idf'])
        # print("weighting accessed")
        weighted_tokens = pd.DataFrame.from_dict({
            'token': list(i for i in w.keys()),
            'frequency': tokens['frequency'],
            'idf': list(i for i in idf.values()),
            'weight': list(i for i in w.values())
        })
        return weighted_tokens

    def __idfGenerator(self) -> pd.DataFrame:
        # retrive all bobot dari bag of words dengan konfigurasi
        # return idf_list =
        if self.__configuration == "manning":
            idf_list = self.__manningIdf()
        elif self.__configuration == "jiffriya":
            idf_list = self.__jiffriyaIdf()
        elif self.__configuration == "xu":
            idf_list = self.__xuIdf()
        elif self.__configuration == "saptono":
            idf_list = self.__saptonoIdf()
        return idf_list

    def __manningIdf(self) -> pd.DataFrame:
        print("manning IDF accessed")
        # LOG(N/DF)
        idf = {}
        for index, row in self.__bag_of_words.iterrows():
            idf[row[0]] = math.log10(self.__N/row[1])
            # weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))

        idfs = pd.DataFrame.from_dict({
            'token': list(i for i in idf.keys()),
            'idf': list(i for i in idf.values())
        })
        # return => dataframe(token, idf)
        return idfs

    def __jiffriyaIdf(self) -> pd.DataFrame:
        print("jiffriya IDF accessed")
        # ( 1 + LOG(N/DF) )
        idf = {}
        for index, row in self.__bag_of_words.iterrows():
            idf[row[0]] = 1+(math.log10(self.__N/row[1]))
            # weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))

        idfs = pd.DataFrame.from_dict({
            'token': list(i for i in idf.keys()),
            'idf': list(i for i in idf.values())
        })
        # return => dataframe(token, idf)
        return idfs

    def __xuIdf(self) -> pd.DataFrame:
        print("xu IDF accessed")
        # (LOG(N/(1+DF)))
        idf = {}
        for index, row in self.__bag_of_words.iterrows():
            idf[row[0]] = math.log10(self.__N/(row[1]+1))
            # weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))

        idfs = pd.DataFrame.from_dict({
            'token': list(i for i in idf.keys()),
            'idf': list(i for i in idf.values())
        })
        # return => dataframe(token, idf)
        return idfs

    def __saptonoIdf(self) -> pd.DataFrame:
        print("saptono IDF accessed")
        # (LN(N/DF)+1)
        idf = {}
        for index, row in self.__bag_of_words.iterrows():
            idf[row[0]] = (math.log(self.__N/row[1]))+1
            # weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))

        idfs = pd.DataFrame.from_dict({
            'token': list(i for i in idf.keys()),
            'idf': list(i for i in idf.values())
        })
        # return => dataframe(token, idf)
        return idfs
