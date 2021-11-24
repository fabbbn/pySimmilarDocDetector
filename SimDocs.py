import pandas as pd
import math

from sqlalchemy.engine.base import Engine
from sqlalchemy.sql import text as sql_txt


class SimDocs:
    pass
    def CbrDocsSearch(self, searched_vectors:dict, base_vectors:dict):
        # retrieval => dataframe (doc_part_id, sim_doc_part_id, cos_sim_value) 
        print("SimDocs.CbrDocsSearch() accessed")
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
        # print(retrieved.shape)
        # reuse search result with value greater than 0.2, then revise
        # reuse => array of dataframe (doc_part_id, sim_doc_part_id, cos_sim_value)
        # revised => array of dataframe, => concat => result
        threshold = 0.2
        temp = retrieved
        ids = temp.groupby(['doc_part_id']).nunique().reset_index()['doc_part_id'].array
        grouped = []
        reused = []
        revised = []
        for id in ids:
            grouped.append(
                retrieved[retrieved['doc_part_id']==id].reset_index()
            )
        for grp in grouped:
            # print(type(grp))
            # print(grp.shape)
            max_row = (grp.iloc[grp['cos_sim_value'].idxmax()].to_frame().transpose())
            del max_row['index']
            if ( grp['cos_sim_value'].max() ) >= threshold:
                # print("get max above th")
                reuse_rows = grp.loc[ grp['cos_sim_value'] >= threshold ].reset_index().sort_values(by=['cos_sim_value'], ascending=False)
                reused.append(
                    reuse_rows.iloc[:, 2:]
                )
            else:
                # print("get max below th")
                reused.append(max_row)
            revised.append(max_row)
        print(reused[0])
        for i in reused:
            print(i.shape)
        result = pd.concat(revised, ignore_index=True)
        result['doc_part_id'] = result['doc_part_id'].astype(int)
        result['sim_doc_part_id'] = result['sim_doc_part_id'].astype(int)

        list_retrieved = []
        list_reused = []
        for r in reused:
            list_retrieved.append(retrieved.shape[0])
            list_reused.append(r.shape[0])
        result = pd.DataFrame.from_dict({
            'doc_part_id': result['doc_part_id'],
            'sim_doc_part_id': result['sim_doc_part_id'],
            'cos_sim_value': result['cos_sim_value'],
            'n_of_retrieved': list_retrieved,
            'n_of_reused': list_reused
        })
        # print(result)
        return {
            "retrieved": retrieved,
            "reused": reused,
            "result": result
        }


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