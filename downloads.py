import json
from opencc import OpenCC

def convert_simplified_to_traditional(jsonl_file, output_file):
    # 初始化OpenCC转换器(S2T表示简体到繁体)
    cc = OpenCC('s2t')
    
    with open(jsonl_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            if not line.strip():
                continue
                
            try:
                data = json.loads(line)
                
                # 递归转换所有字符串字段
                def convert_obj(obj):
                    if isinstance(obj, dict):
                        return {k: convert_obj(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_obj(item) for item in obj]
                    elif isinstance(obj, str):
                        return cc.convert(obj)
                    return obj
                
                converted_data = convert_obj(data)
                outfile.write(json.dumps(converted_data, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue

# 使用示例
convert_simplified_to_traditional('data/pretrain.jsonl', 'pretrain_tradi.jsonl')