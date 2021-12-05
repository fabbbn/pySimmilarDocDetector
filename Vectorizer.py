import math
from os import sep
import pandas as pd
import re
class Vectorizer:
    pass

    def IdfGenerator(self, bow, N, config):
        # retrive all bobot dari bag of words dengan konfigurasi
        # return idf_list = 
        if config == "manning":
            idf_list = self.__manningIdf(bow, N)
        elif config == "jiffriya":
            idf_list = self.__jiffriyaIdf(bow, N)
        elif config == "xu":
            idf_list = self.__xuIdf(bow, N)
        elif config == "saptono":
            idf_list = self.__saptonoIdf(bow, N)
        return idf_list
        

    def tfGenerator(self, paths):
        # return array of dataframe(token, frequency, occur)
        tokens = []
        for i in range (len(paths)):
            if re.search(r'.txt', paths[i]):
                with open(paths[i], 'r') as f:
                    token = str(f.read().strip()).split(", ")
                    df = pd.DataFrame.from_dict({
                        'token': list(i for i in token),
                        'frequency': list(1 for i in range(len(token)))
                    })
                    df = df.groupby(by=['token']).agg({'frequency':'sum'}).reset_index()
                    df['occur'] = list(1 for i in range(len(df)))
                    tokens.append(df)
            else:
                df = pd.read_csv(paths[i])
                # print(df)
                tokens.append(df)
        
        return tokens


    def tfIdf(self, tfs, idf_list):
        tfidfs = []
        # calculate weight as tf*idf
        # iterate parts of documents
        for token in tfs:
            # count tf x idf using configs
            data = self.__termWeighting(token, idf_list)
            tfidfs.append(data)
        print("Vectorizer.tfIdf() accessed")
        return tfidfs


    def __termWeighting(self, tokens, idf_list):
        # result => dataframe: token, frequency, idf, weight
        w = {}
        idf = {}
        for index, row in tokens.iterrows():
            idf[row[0]] = (idf_list.loc[idf_list['token']==row[0]].idf.item())
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


    def __manningIdf(self, idf_list, N):
        print("manning IDF accessed")
        # LOG(N/DF)
        idf = {}
        for index, row in idf_list.iterrows():
            idf[row[0]] = math.log10(N/row[1])
            # weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))
        
        idfs = pd.DataFrame.from_dict({
            'token': list(i for i in idf.keys()),
            'idf': list(i for i in idf.values())
        })
        # return => dataframe(token, idf)
        return idfs 


    def __jiffriyaIdf(self, idf_list, N):
        print("jiffriya IDF accessed")
        # ( 1 + LOG(N/DF) )
        idf = {}
        for index, row in idf_list.iterrows():
            idf[row[0]] = 1+(math.log10(N/row[1]))
            # weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))
        
        idfs = pd.DataFrame.from_dict({
            'token': list(i for i in idf.keys()),
            'idf': list(i for i in idf.values())
        })
        # return => dataframe(token, idf)
        return idfs 


    def __xuIdf(self, idf_list, N):
        print("xu IDF accessed")
        # (LOG(N/(1+DF)))
        idf = {}
        for index, row in idf_list.iterrows():
            idf[row[0]] = math.log10(N/(row[1]+1))
            # weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))
        
        idfs = pd.DataFrame.from_dict({
            'token': list(i for i in idf.keys()),
            'idf': list(i for i in idf.values())
        })
        # return => dataframe(token, idf)
        return idfs 


    def __saptonoIdf(self, idf_list, N):
        print("saptono IDF accessed")
        # (LN(N/DF)+1)
        idf = {}
        for index, row in idf_list.iterrows():
            idf[row[0]] = (math.log(N/row[1]))+1
            # weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))
        
        idfs = pd.DataFrame.from_dict({
            'token': list(i for i in idf.keys()),
            'idf': list(i for i in idf.values())
        })
        # return => dataframe(token, idf)
        return idfs 
