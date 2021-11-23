import pandas as pd
import math

from sqlalchemy.engine.base import Engine
from sqlalchemy.sql import text as sql_txt



class SimDocs:
    pass
    def CbrDocsSearch(self, searched_vectors:dict, base_vectors:dict):
# retrieval
        doc_ids = []
        base_ids = []
        cos_sim = []
        for doc_id, search in searched_vectors.items():
            for base_id, base in base_vectors.items():
                doc_ids.append(doc_id)
                base_ids.append(base_id)
                cos_sim.append(
                    (self.__vectorsDotProduct(search, base))/((self.__vectorMagnitude(search['weight'].array))*(self.__vectorMagnitude(base['weight'].array)))
                )
        retrieved = pd.DataFrame.from_dict({
            'doc_part_id': doc_ids,
            'sim_doc_part_id': base_ids,
            'cos_sim_value': cos_sim
        })
# reuse search result with value greater than 0.2, then revise
        threshold = 0.2
        temp = retrieved
        parts = temp.groupby(['doc_part_id']).nunique().reset_index()['doc_part_id'].array
        grouped = []
        reused = []
        revised = []
        for id in parts:
            grouped.append(
                retrieved[retrieved['doc_part_id']==id]
            )
        for grp in grouped:
            if grp['cos_sim_value'].max()<threshold:
                print("get max below th")
                print(grp.iloc[[grp['cos_sim_value'].idxmax()]])
            #     reused.append(grp.iloc[grp['cos_sim_value'].idxmax()])
            else:
                print("get max above th")
            #     reused.append(grp[grp['cos_sim_value']>=0.2])
            print(grp.iloc[[grp['cos_sim_value'].idxmax()], :])
            # revised.append(grp.iloc[grp['cos_sim_value'].idxmax()])
        # list_retrieved = list(retrieved.shape[0] for i in parts)
        # list_reused = list(
        #     df.shape[0] for df in reused
        #     )
        # result = pd.DataFrame.from_dict({
        #     'doc_part_id': parts,
        #     'sim_doc_part_id': revised['sim_doc_part_id'],
        #     'cosine_sim_value': revised['cosine_sim_value'],
        #     'n_of_retrieved': list_retrieved,
        #     'n_of_reused': list_reused
        # })
        # print(result)
        # return result


    def __retrieval(self, searched_vectors:dict, base_vectors:dict):
        # retrieval, cosine similarity count
        # cos_sim = (a.b)/(|a|.|b|)
        doc_ids = []
        base_ids = []
        cos_sim = []
        for doc_id, search in searched_vectors.items():
            for base_id, base in base_vectors.items():
                doc_ids.append(doc_id)
                base_ids.append(base_id)
                cos_sim.append(
                    (self.__vectorsDotProduct(search, base))/((self.__vectorMagnitude(search['weight'].array))*(self.__vectorMagnitude(base['weight'].array)))
                )
        result = pd.DataFrame.from_dict({
            'doc_part_id': doc_ids,
            'sim_doc_part_id': base_ids,
            'cos_sim_value': cos_sim
        })
        return result


    def __reuse(self, datas:pd.DataFrame):
        threshold = 0.2
        temp = datas
        parts = temp.groupby(['doc_part_id']).nunique().reset_index()['doc_part_id'].array
        grouped = []
        filtered = []
        for id in parts:
            grouped.append(
                datas[datas['doc_part_id']==id]
            )
        for grp in grouped:
            if grp['cos_sim_value'].max()<threshold:
                filtered.append(grp.iloc[grp['cos_sim_value'].idxmax()])
            else:
                filtered.append(grp[grp['cos_sim_value']>=0.2])
        
        return filtered

    
    def __revise(self, datas:pd.DataFrame):
        result={}
        return result


    # async def __retain(self, datas:pd.DataFrame):
    #     result={}
    #     async with engine.connect() as con:
    #         query = '''SELECT * FROM proposals
    #         '''
    #     statement = sql_txt(query)
    #     result = await con.execute(statement)
    #     print(result.fetchall())
    #     return result

    
    def __vectorMagnitude(self, weights):
        # |a| = sqrt(sum(ai^2))
        result = 0
        for weight in weights:
            result = result + math.pow(weight, 2)
        return math.sqrt(result)

    def __vectorsDotProduct(self, df_weights1:pd.DataFrame, df_weights2:pd.DataFrame):
        # params: 2 dataframes (token, freq, idf, weight)
        # a.b = (a1*b1)+(a2*b2)+...+(an*bn)
        result = 0
        if (df_weights1.shape[0]) < (df_weights2.shape[0]):
            a = df_weights1
            b = df_weights2
        else:
            a = df_weights2
            b = df_weights1

        for idx, row in a.iterrows():
            # if both token exist, result = result + (ai*bi), 
            # if one of them is not exist, then the value is automatically be 0 (zero)
            if b.loc[b['token']==row[0]]['weight'].any():
                result = result + (row[3] * (b.loc[b['token']==row[0]]['weight'].item()))
        return result