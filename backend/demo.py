"""
    demo演示程序：
    使用Taskflow进行属性级情感分析
    单文本情感分析：针对输入的语句进行单文本情感分析
    批量文本情感分析：读取txt文件内容后进行批量情感分析
"""

# 导入所需依赖
import os
import paddle
from paddlenlp import Taskflow
from utils import write_json_file
from utils import format_results,format_print,load_txt

# 单条文本情感分析预测函数
def predict(input_text,schema):
    """
    Predict based on Taskflow.
    """
    # 单条文本情感分析
    senta = Taskflow("sentiment_analysis", model="uie-senta-base", schema=schema)
    # predict with Taskflow
    results = senta(input_text)
    # 如果语句中没有属性词，只有情感词，则调用语句级情感分析
    if results==[{}]:
        schema2 = ['情感倾向[正向，负向]']
        senta2 = Taskflow("sentiment_analysis", model="uie-senta-base", schema=schema2)
        results = senta2(input_text)
        sentiment = results[0]['情感倾向[正向，负向]'][0]['text']
        results = [{"aspect": 'None', "opinions": input_text, "sentiment": sentiment}]
    else:
        # 将结果输出，并以list形式保存到consequence中
        results = format_results(results)
    # 返回预测结果 
    return results

# 批量情感分析预测函数
def batchPredict(file_path,schema):
    """
    Predict based on Taskflow.
    """
    # read file
    if not os.path.exists(file_path):
        raise ValueError("something with wrong for your file_path, it may be not exists.")
    examples = load_txt(file_path)

    # 批量情感分析
    senta = Taskflow("sentiment_analysis", model="uie-senta-base", schema=schema,
                      batch_size=4, max_seq_len=512)
    # predict with Taskflow
    results = senta(examples)
    # 保存结果
    save_path = os.path.join('./outputs', "sentiment_results.json")
    write_json_file(results, save_path)
    print("The results of sentiment analysis has been saved to: {}".format(save_path))
    # 将结果输出并以list形式保存到consequence中
    results = format_results(results)
    # 返回预测结果 
    return results

if __name__== "__main__" :
    # 定义schema
    schema =  [{"评价维度":["观点词", "情感倾向[正向,负向,未提及]"]}]

    # 单条文本情感分析
    input_text_1 = "环境装修不错，也很干净，前台服务非常好"
    result_text_1 = predict(input_text_1,schema)
    format_print(result_text_1)

    input_text_2 = "蛋糕味道不错，很好吃，店家很耐心，服务也很好，很棒"
    result_text_2 = predict(input_text_2,schema)
    format_print(result_text_2)

    # 读取txt文件内容进行批量情感分析
    file_path = './textresource/test_hotel_small.txt'
    # 批量文本情感分析
    result_batch = batchPredict(file_path,schema)
    format_print(result_batch)






