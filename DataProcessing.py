import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory


class DataProcessing:
    pass

    def splitDocument(self, text):
        print("DataProcessing.splitDocument() accessed")
        result = []
        idxs = []
        exps = [
            r'RANGKUMAN',
            r'BAB\s*\w*\s*LATAR\s*BELAKANG',
            r'BAB\s*\w*\s*KAJIAN\s*TEORI',
            r'BAB\s*\w*\s*METODE\s*PENELITIAN'
        ]
        parts = [
            "RANGKUMAN",
            "LATAR BELAKANG",
            "KAJIAN TEORI",
            "METODE PENELITIAN"
        ]
        # // looks for index of each part of document (for slicing)
        for exp in exps:
            idx = re.search(exp, text).start()
            idxs.append(idx)
        idxs.append(len(text))
        # splitting text and construct Part object
        for i in range(len(idxs)-1):
            result.append({
                "chapter": parts[i],
                "text": re.sub(exps[i], '', text[idxs[i]:idxs[i+1]])
            })
        return result

    
    def cleaningText(self, text):
        print("DataProcessing.cleanText() accessed")
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        cleaned = re.sub(r'\d+\s', ' ', cleaned)
        cleaned = re.sub(r'\s{1,}', ' ', cleaned)
        return ({
            "before": text,
            "after" : cleaned.strip()
        })

    
    def casefoldingText(self, text):
        return ({
            "before": text,
            "after": text.lower()
        })

    
    def tokenizeText(self, text):
        return ({
            "before": text,
            "after": text.split(" ")
        })

    
    def stopwordRemoval(self, tokens):
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()

        # Kalimat
        swremoved = stopword.remove(" ".join(tokens))
        return({
            "before": tokens,
            "after": swremoved.split(" ")
        })
            

    def stemmingTokens(self, tokens):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        stemmed = []
        # stemming process
        for token in tokens:
            stemmed.append(stemmer.stem(token))
        return ({
            "before": tokens,
            "after" : stemmed
        })
