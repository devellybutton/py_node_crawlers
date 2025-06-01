import os
import pandas as pd
import json

def excel_to_json(excel_path, json_path):
    df = pd.read_excel(excel_path, header=2, engine='openpyxl')
    df = df[['구분', '이메일(아이디)', '패스워드']]
    df.columns = ['no', 'email', 'password']
    df = df.dropna(subset=['no', 'email', 'password'])
    df['no'] = df['no'].astype(int)
    result = df.to_dict(orient='records')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"JSON 변환 완료: {json_path}")

def load_accounts(json_path, excel_path=None):
    # json 파일이 없고, excel_path가 주어졌을 경우 변환 먼저 수행
    if not os.path.exists(json_path):
        if excel_path:
            excel_to_json(excel_path, json_path)
        else:
            raise FileNotFoundError(f"{json_path} 가 존재하지 않으며 excel_path도 제공되지 않았습니다.")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)