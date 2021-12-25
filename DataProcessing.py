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
            r'BAB\s*.*\s*LATAR\s*BELAKANG',
            r'BAB\s*.*\s*KAJIAN\s*TEORI',
            r'BAB\s*.*\s*METODE\s*PENELITIAN'
        ]
        parts = [
            "RANGKUMAN",
            "LATAR BELAKANG",
            "KAJIAN TEORI",
            "METODE PENELITIAN"
        ]
        # // looks for index of each part of document (for slicing)
        print(idxs)
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

    def preprocessingText(self, splitted):
        print("DataProcessing.preprocessingText() accessed")
        cleaned = []
        casefold = []
        tokenized = []
        swremoved = []
        stemmed = []
        for part in splitted:
            temp = self.__cleaningText(part['text'])
            cleaned.append({
                "title": part['chapter'],
                "content": temp
            })
            temp = self.__casefoldingText(temp)
            casefold.append({
                "title": part['chapter'],
                "content": temp
            })
            temp = self.__tokenizeText(temp)
            tokenized.append({
                "title": part['chapter'],
                "content": temp
            })
            temp = self.__stopwordRemoval(temp)
            swremoved.append({
                "title": part['chapter'],
                "content": temp
            })
            temp = self.__stemmingTokens(temp)
            stemmed.append({
                "title": part['chapter'],
                "content": temp
            })

        return({
            "doc_parts": splitted,
            "doc_pre_process": [
                {"title": "Text Cleaning",  "result": cleaned},
                {"title": "Case Folding",  "result": casefold},
                {"title": "Tokenisasi",  "result": tokenized},
                {"title": "Stopword Removal",  "result": swremoved},
                {"title": "Stemming",  "result": stemmed}
            ]
        })
# [^A-Za-z0-9_\s]

    def __cleaningText(self, text):
        # cleaned = re.sub(r'[^\w\s]', ' ', text)
        cleaned = re.sub(r'[^A-Za-z0-9_\s]', ' ', text)
        cleaned = re.sub(r'\b\d+\b', ' ', cleaned)
        cleaned = re.sub(r'\s{1,}', ' ', cleaned)
        return (cleaned.strip())

    def __casefoldingText(self, text):
        return (text.lower())

    def __tokenizeText(self, text):
        temp = text.split(" ")
        return (", ".join(temp))

    def __stopwordRemoval(self, tokens):
        token = tokens.split(", ")
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        # karakter minimal
        min_length = 2
        defined_sw_list = [
            "et", "al", "ibid", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"
        ]

        # Kalimat
        removed = stopword.remove(" ".join(token))
        swremoved = list(word for word in removed.split(" ") if len(
            word) > min_length and word not in defined_sw_list)
        return(", ".join(swremoved))

    def __stemmingTokens(self, tokens):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        stemmed = []
        result = []
        # stemming process
        for token in tokens.split(", "):
            stemmed.append(stemmer.stem(token))
        for stem in stemmed:
            if stem:
                result.append(stem)
        return (", ".join(result))
