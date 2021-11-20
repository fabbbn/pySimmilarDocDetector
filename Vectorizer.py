import math
# import sqilte3
# DB_NAME = "d.db"
class Vectorizer:
    pass

    def tfCounter(self, iterable_parts):
        # count term frequency for every chapters = dictionary
        tfs = []
        bag_of_words = {}
        # doc_occurence = {}
        for part in iterable_parts:
            tf = {}
            for token in part:
                if token in tf:
                    tf[token]+=1
                else:
                    tf[token]=1
                    doc_occurence[token]

                if token in bag_of_words:
                    bag_of_words[token]+=1
                else:
                    bag_of_words[token]=1
                    # if token in doc_occurence:
                    #     doc_occurence[token]

                
            tfs.append(tf)
            print(len(tf))

        # save each dictionary
        # for dictionary in tfs:
            # saving process (query)
        #     for term, freq in dictionary.items():
        #         print("\"{0}\" = {1} word".format(term, freq))
        # return result
        return {
            "tf_per_part": tfs,
            "bow": bag_of_words
        }


    def TfIdf(self, iterable_parts, config='manning'):
        tfidfs = []
        # query all bag of words => bow
        # SELECT Term as term, Frequency as N, DocOccurence as df from BagOfWords
        # take result from tfs
        tfs = self.tfCounter(iterable_parts)

        # iterate parts of documents
        for token in tfs:
            # count tf x idf using configs
            switcher = {
                'manning': self.manningWeighting(token, bow),
                'jiffriya': self.jiffriyaWeighting(token, bow),
                'xu': self.xuWeighting(token, bow),
                'saptono': self.saptonoWeighting(token, bow)
            }
            func = switcher.get(config)
            tfidfs.append(func())
    
    def manningWeighting(self, token, bow):
        # TF X LOG(N/DF)
        weights = {}
        for term in token:
            weights[term] = token[term] * (math.log10(bow[term]['N']/bow[term]['df']))
        
        return weights


    def jiffriyaWeighting(self, token, bow):
        # TF X ( 1 + LOG(N/DF) )
        weights = {}
        for term in token:
            weights[term] = token[term] * (1+(math.log10(bow[term]['N']/bow[term]['df'])))
        
        return weights


    def xuWeighting(self, token, bow):
        # TF X (LOG(N/(1+DF)))
        weights = {}
        for term in token:
            weights[term] = token[term] * ( math.log10(bow[term]['N']/ (bow[term]['df']+1) ) )
        
        return weights


    def saptonoWeighting(self, token, bow):
        # TF X (LN(N/DF)+1)
        weights = {}
        for term in token:
            weights[term] = token[term] * ( 1 + (math.log(bow[term]['N']/bow[term]['df'])) )
        
        return weights