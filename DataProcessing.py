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
        return ( cleaned.strip() )

    
    def casefoldingText(self, text):
        return ( text.lower() )

    
    def tokenizeText(self, text):
        return ( text.split(" ") )

    
    def stopwordRemoval(self, tokens):
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()

        # Kalimat
        swremoved = stopword.remove(" ".join(tokens))
        return( swremoved.split(" ") )
            

    def stemmingTokens(self, tokens):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        stemmed = []
        # stemming process
        for token in tokens:
            stemmed.append(stemmer.stem(token))
        return ( stemmed )


    def preprocessingText(self, splitted):
        cleaned = []
        casefold = []
        tokenized = []
        swremoved = []
        stemmed = []
        for part in splitted:
            temp = self.cleaningText(part['text'])
            cleaned.append({
                "title":part['chapter'],
                "content": temp
            })
            temp = self.casefoldingText(temp)
            casefold.append({
                "title":part['chapter'],
                "content": temp
            })
            temp = self.tokenizeText(temp)
            tokenized.append({
                "title":part['chapter'],
                "content": temp
            })
            temp = self.stopwordRemoval(temp)
            swremoved.append({
                "title":part['chapter'],
                "content": temp
            })
            temp = self.stemmingTokens(temp)
            stemmed.append({
                "title":part['chapter'],
                "content": temp
            })

        return({
            "Bagian Dokumen": splitted,
            "Hasil Pra-pengolahan Teks": {
                "Cleaning" : cleaned,
                "Case Folding": casefold,
                "Tokenisasi": tokenized,
                "Stopword Removal": swremoved,
                "Stemming": stemmed
            }
        })