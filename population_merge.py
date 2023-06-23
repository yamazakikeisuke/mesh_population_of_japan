import glob
import zipfile
import os
import pandas as pd
import geopandas as gpd

##########ファイルの解凍##########
#作業ディレクトリーのパスをセット（統計局からダウンロードしたzipファイルを置いておく）
path = "./4次メッシュ人口統計（2020年_国勢調査）"
#path = "./4次メッシュ_境界データ"

files = os.listdir(path)
for file in files:
    files_name = file.replace(".zip", "")
    #解凍したファイルセット
    zip_f = zipfile.ZipFile(path + "/" + file)
    #解凍を実行。解凍したファイルを保存するディレクトリーの親は「path + _unzip/」
    zip_f.extractall(path + "_unzip/" + files_name)
    zip_f.close()
    
########解凍した地域ごとのメッシュファイルを読み込んで結合する########
path = "./4次メッシュ人口統計（2020年_国勢調査）_unzip"
dirs = os.listdir(path)
df_population = pd.DataFrame(index=[], columns=[])
for dir in dirs:
    files = os.listdir(path + "/" + dir)
    for file in files:
        df = pd.read_csv(path + "/" + dir + "/" + file)
        #１行目が列の日本語名なので削除
        df = df.drop(0, axis=0)
        #結合
        df_population = pd.concat([df_population, df])

#重複している行を削除
df_population.drop_duplicates(subset='KEY_CODE', inplace=True)
df_population.reset_index(inplace=True, drop=True)

########地域毎の境界データを読み込んで結合する########
path = "./4次メッシュ_境界データ_unzip"
dirs = os.listdir(path)
df_all = pd.DataFrame(index=[], columns=[])
for dir in dirs:
    files = os.listdir(path + "/" + dir)
    files = [f for f in files if '.shp' in f]
    for file in files:
        df = gpd.read_file(path + "/" + dir + "/" + file)
        #結合
        df_all = pd.concat([df_all, df])
        
df_all.reset_index(inplace=True, drop=True)

#人口と境界のファイルをマージする
df_all = df_all.astype({'KEY_CODE': int})
df_population = df_population.astype({'KEY_CODE': int})
df_merge = pd.merge(df_all, df_population, how="left", on="KEY_CODE")

#ファイルが大きくなりすぎたので人が住んでいるメッシュのみに絞る
df_merge_limit = df_merge.dropna(subset=['T001101001'])

#人口総数とメッシュに関するデータのみを出力
df_merge_limit[["KEY_CODE","T001101001","geometry"]].to_file(filename="./Japanese_population_mesh_500.geojson", driver="GeoJSON", encoding='utf-8')