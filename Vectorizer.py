import math
import pandas as pd
import re
class Vectorizer:
    pass


    def tfGenerator(self, paths):
        # return array of dataframe(token, freq, occur)
        tokens = []
        for path in paths:
            with open(path, 'r') as f:
                token = str(f.read().strip()).split(" ")
                df = pd.DataFrame.from_dict({
                    'token': list(i for i in token),
                    'freq': list(1 for i in range(len(token)))
                })
                df = df.groupby(by=['token']).agg({'freq':'sum'}).reset_index()
                df['occur'] = list(1 for i in range(len(df)))
                tokens.append(df)

                # saving token into csv for faster computation
                filepath = re.sub(r'.txt', '.csv', path)
                filepath = re.sub(r'/chapter/', '/grouped-tf/', filepath)
                df.to_csv(filepath, index=None)
        
        return tokens


    def TfIdf(self, tfs, bow, N, config='manning'):
        tfidfs = []
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
        # calculate weight as tf*idf
        # iterate parts of documents
        for token in tfs:
            # count tf x idf using configs
            data = self.__termWeighting(token, idf_list)
            tfidfs.append(data)
        return tfidfs


    def __termWeighting(self, tokens, idf_list):
        # result => dataframe: token, frequency, idf, weight
        w = {}
        idf = {}
        for index, row in tokens.iterrows():
            idf[row[0]] = (idf_list.loc[idf_list['token']==row[0]].idf.item())
            w[row[0]] = (row[1] * idf[row[0]])
            # w[row[0]] = (row[1] * idf_list.loc[idf_list['token']==row[0]]['idf'])
        print("weighting accessed")
        weighted_tokens = pd.DataFrame.from_dict({
            'token': list(i for i in w.keys()),
            'freq': tokens['freq'],
            'idf': list(i for i in idf.values()),
            'weight': list(i for i in w.values())
        })
        return weighted_tokens


    def __manningIdf(self, idf_list, N):
        print("manning weighting accessed")
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
        print("jiffriya weighting accessed")
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
        print("xu weighting accessed")
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
        print("saptono weighting accessed")
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
