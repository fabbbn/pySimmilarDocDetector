# from DataProcessing import splitDocument
from DataProcessing import DataProcessing
import os
import pandas as pd
s = './grouped-tf/haiiii.csv'
print(os.path.basename(s))
text = "\r\n\r\n RANGKUMAN      Remaja cenderung menghabiskan lebih banyak waktu dengan teman sebaya, namun\r\nremaja masih membutuhkan orangtua sebagai dasar rasa aman (secure base) atau sebagai\r\ntempat aman untuk kembali secara periodis dan mendapatkan dukungan emosional (Papalia,\r\n2014). BAB I LATAR BELAKANG Namun terkadang situasi yang tidak diinginkan dapat terjadi, salah satu situasi ini\r\nadalah perceraian orangtua (Hermansyah, 2019). Di Indonesia sendiri perceraian terus\r\nmeningkat hingga 20\%\ sejak tahun 2009-2016 (Astuti, 2017). BAB II KAJIAN TEORI Pada tahun 2015 terdapat\r\n347.256 talak dan cerai yang terjadi di Indonesia, angka ini menunjukkan peningkatan sebesar\r\n3.019 kasus dari tahun sebelumnya (Badan Pusat Statistik, 2019). Ironisnya, dibandingkan\r\nnegara-negara kawasan Asia Pasifik lain, angka perceraian di Indonesia merupakan yang\r\ntertinggi (Astuti, 2017).\r\n\r\n   BAB III METODE PENELITIAN    Tujuan dari penelitian ini adalah mengetahui peran self compassion dan kecerdasan\r\nemosi terhadap rumination pada remaja korban broken home. Penelitian menggunakan\r\npendekatan kuantitatif dengan melibatkan tiga variabel, yaitu satu variabel terikat\r\n(rumination) dan dua variabel bebas (self compassion dan kecerdasan emosi ). Ketiga variabel\r\nakan diukur menggunakan tiga buah alat ukur berbentuk skala Likert. Sebelum digunakan\r\nuntuk pengambilan data, ketiga skala akan diuji coba terlebih dahulu hingga di dapatkan\r\nitem-item yang teruji valid dan reliabel. Uji coba alat ukur diberikan kepada 50 orang anak\r\nkorban broken home. Alat ukur yang terdiri dari item-item yang valid dan reliabel akan\r\ndigunakan pada pengambilan data penelitian. Sampel pada penelitian ini berjumlah 200 orang\r\nanak korban broken home.\r\n\r\n         Luaran dari penelitian ini diharapkan dapat melakukan pembuktian konsep fungsi\r\ndan/atau karakteristik penting secara analitis dan eksperimental. Bentuk luaran yang\r\ndiharapkan adalah prosiding pada seminar internasional bereputasi terindeks Scopus atau\r\npublikasi pada jurnal nasional terakreditasi sinta. Tingkat serapan teknologi untuk penelitian\r\nini yaitu pada tingkat 3: pembuktian konsep fungsi dan/atau karakteristik penting secara\r\nanalitis dan eksperimental.\r\n\r\nKata kunci : Rumination, Self Compassion dan Kecerdasan Emosi, Broken Home\r\n                                                      "
# text = "RANGKUMAN 1231 ..nci dcisdic asj PENDAHULUAN BAB I LATAR BELAKANG BAB II KAJIAN TEORI BAB III METODE PENELITIAN"
dp = DataProcessing()
cleaned = []
casefold = []
tokenized = []
swremoved = []
stemmed = []
splitted = dp.splitDocument(text)

df = pd.DataFrame.from_dict({
    'token': ['siapa', 'aku', 'huhu', 'hehe'],
    'freq' : [2, 5, 1, 7],
    'idf': [0.99, 0.7, 0.1, 0.99],
    'weight': [0.7, 0.3, 0.2, 0.5]
})
for index, row in df.iterrows():
    print(row[3]*df.loc[ df['token']=='siapa' ]['weight'].item())

df['idf'] = df['idf'].astype(int)
print(df.dtypes)
print(df.loc[ df['weight'] >= 0.3 ].reset_index().sort_values(by=['weight'], ascending=False))
# arrays = []
# arrays.append(df.iloc[df['weight'].idxmax()].to_frame().transpose())
# arrays.append(df.iloc[df['weight'].idxmin()].to_frame().transpose())

# for i in arrays:
#     print((i))
# for part in splitted:
#     temp = dp.cleaningText(part['text'])
#     cleaned.append({
#         "title":part['chapter'],
#         "content": temp
#     })
#     temp = dp.casefoldingText(temp['after'])
#     casefold.append({
#         "title":part['chapter'],
#         "content": temp
#     })
#     temp = dp.tokenizeText(temp['after'])
#     tokenized.append({
#         "title":part['chapter'],
#         "content": temp
#     })
#     temp = dp.stopwordRemoval(temp['after'])
#     swremoved.append({
#         "title":part['chapter'],
#         "content": temp
#     })
#     temp = dp.stemmingTokens(temp['after'])
#     stemmed.append({
#         "title":part['chapter'],
#         "content": temp
#     })


# print(cleaned)
# print(casefold)
# print(tokenized)
# print(swremoved)
# print(stemmed)
