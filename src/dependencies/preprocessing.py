import re
import pandas as pd
from pathlib import Path

TEMP_DATA = r'E:\Personal\interview\bigc\tmp_data'
LAZADA_PLATFORM = 'lazada'
SHOPEE_PLATFORM = 'shopee'

def clean_price_laz(x):
  if x.startswith('฿'):
    x = x.replace('฿','')
    x = float(x.replace(',',''))
  return x

def clean_sold_laz(x):
  if isinstance(x, str) and x != None:
    x = x.replace('ชิ้น','').strip()
    x = int(x)
  return x

def clean_sold_shp(x):
  if 'พัน' in x:
    x = x.replace('พัน','')
    x = float(x) * 1000
  
  if x != None and x != 'None':
    return int(float(x))
  return None

def clean_brandname(x):
  if '(' in x:
    x = re.sub(r"[\(\[].*?[\)\]]", "", x)
  return x

def null_value(x):
  if x == 'None' or x == 'NaN':
    x = None
  return x

def main_laz_clean(file: str):
  df = pd.read_csv(f'{TEMP_DATA}\{file}')
  df.drop(['matched'], axis=1, inplace=True)
  df_clean = df.copy()
  df_clean['price'] = df_clean['price'].apply(clean_price_laz)
  df_clean['sold'] = df_clean['sold'].apply(clean_sold_laz)
  return df_clean

def main_shp_clean(file: str):
  df = pd.read_csv(f'{TEMP_DATA}\{file}')
  df.drop(['matched'], axis=1, inplace=True)
  df_clean = df.copy()
  df_clean['price'] = df_clean['price'].astype(float)
  df_clean['sold'] = df_clean['sold'].apply(clean_sold_shp)
  df_clean['brand_name'] = df_clean['brand_name'].apply(clean_brandname)
  return df_clean

def main(search_term):
  
  # import file name start with _
  prefix_filename = search_term.replace(' ','_')
  fileNames = [file.name for file in Path(TEMP_DATA).iterdir() if file.name.startswith(prefix_filename)] 
  print(fileNames)
  
  df1_clean = pd.DataFrame
  df2_clean = pd.DataFrame

  for file in fileNames:
    source = file.replace('.csv','')
    source = source.split('_')[-1]
    print(source)
    if source == LAZADA_PLATFORM:
      df1_clean = main_laz_clean(file)
      
    elif source == SHOPEE_PLATFORM:
      df2_clean = main_shp_clean(file)
    else:
      raise Exception('no support others source')
    
  vertical_concat = pd.concat([df1_clean, df2_clean], axis=0)
  vertical_concat.drop_duplicates(subset=['product_name','store_name','platform'], inplace=True)
  vertical_concat['store_name'] = vertical_concat['store_name'].apply(null_value) 
  vertical_concat['sold'] = vertical_concat['sold'].apply(null_value) 
  vertical_concat['brand_name'] = vertical_concat['brand_name'].apply(null_value) 
  vertical_concat['specification'] = vertical_concat['specification'].apply(null_value)
  vertical_concat['search'] = search_term 
  vertical_concat = vertical_concat[[ 'product_name', 'price', 'sold', 'store_name', 'brand_name',
        'specification',  'platform','alink','search']]


  vertical_concat.to_csv(f'{TEMP_DATA}\prep_{prefix_filename}2.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
  search_term_default = 'keychron k4'
  main(search_term_default)