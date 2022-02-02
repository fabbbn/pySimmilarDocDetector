import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sqlalchemy.sql.sqltypes import Boolean


class DataProcessing:
    # pass
    __text = ""
    __title = ""
    __parts = []  # array of dictionary "text" and "chapter"

    def __init__(self, text, title) -> None:
        self.__text = text
        self.__title = title
        valid, parts = self.__splitDocument()
        if valid:
            self.__parts = parts
        else:
            self.__parts = []

    def preprocessingText(self):
        print("DataProcessing.preprocessingText() accessed")
        if len(self.__parts) != 0:
            cleaned = []
            casefold = []
            tokenized = []
            swremoved = []
            stemmed = []
            for part in self.__parts:
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

            return(
                True, {
                    "doc_parts": self.__parts,
                    "doc_pre_process": [
                        {"title": "Text Cleaning",  "result": cleaned},
                        {"title": "Case Folding",  "result": casefold},
                        {"title": "Tokenisasi",  "result": tokenized},
                        {"title": "Stopword Removal",  "result": swremoved},
                        {"title": "Stemming",  "result": stemmed}
                    ]
                })

        else:
            return(False, {})

    def __splitDocument(self):
        try:
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
                idx = re.search(exp, self.__text).start()
                idxs.append(idx)
            idxs.append(len(self.__text))

            # splitting text and construct Part object
            for i in range(len(idxs)-1):
                result.append({
                    "chapter": parts[i],
                    "text": re.sub(exps[i], '', self.__text[idxs[i]:idxs[i+1]])
                })
            result.insert(0, {
                "chapter": "JUDUL",
                "text": self.__title
            })
            return (True, result)

        except Exception:
            return (False, [])

    def __cleaningText(self, text: str) -> str:
        # cleaned = re.sub(r'[^\w\s]', ' ', text)
        cleaned = re.sub(r'[^A-Za-z0-9_\s]', ' ', text)
        cleaned = re.sub(r'\b\d+\b', ' ', cleaned)
        cleaned = re.sub(r'\s{1,}', ' ', cleaned)
        return (cleaned.strip())

    def __casefoldingText(self, text: str) -> str:
        return (text.lower())

    def __tokenizeText(self, text: str) -> str:
        temp = text.split(" ")
        return (", ".join(temp))

    def __stopwordRemoval(self, tokens: str) -> str:
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

    def __stemmingTokens(self, tokens: str) -> str:
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
