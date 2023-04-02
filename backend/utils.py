import json

def format_results(results):
    result = []
    for res in results:
        for dimension in res['评价维度']:
            aspect = dimension['text']
            if('观点词' in dimension['relations']):
                opinions = [opinion['text'] for opinion in dimension['relations']['观点词']]
            else:
                opinions = None
            sentiment = dimension['relations']['情感倾向[正向,负向,未提及]'][0]['text']
            con = {"aspect": aspect, "opinions": str(opinions), "sentiment": sentiment}
            result.append(con)
    return result

def format_print(results):
    for res in results:
        print(f"aspect: {res['aspect']}, opinions: {res['opinions']}, sentiment: {res['sentiment']}")
    print()

def load_txt(file_path):
    texts = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            texts.append(line.strip())
    return texts

def write_json_file(examples, save_path):
    with open(save_path, "w", encoding="utf-8") as f:
        for example in examples:
            line = json.dumps(example, ensure_ascii=False)
            f.write(line + "\n")

def load_json_file(path):
    exmaples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            example = json.loads(line)
            exmaples.append(example)
    return exmaples
