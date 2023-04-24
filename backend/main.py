"""
    基于FastAPI的属性级情感分析后端模块
    先加载观点抽取和情感分析模型预热后再启动后端接口服务
"""
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time

import paddle
from paddlenlp import Taskflow
from utils import format_print
from demo import predict,batchPredict
from collections import defaultdict
from utils import load_json_file

schema =  [{"评价维度":["观点词", "情感倾向[正向,负向,未提及]"]}]

# 模型预热，属性级情感分析
input_text = "环境装修不错，也很干净，前台服务非常好"
result_text = predict(input_text,schema)
format_print(result_text)

class SentimentResult:
    """
    load and analyze result of sentiment analysis.
    """
    def __init__(self, file_path, sentiment_name="情感倾向[正向,负向,未提及]", opinion_name="观点词"):
        self.file_path = file_path
        self.sentiment_name = sentiment_name
        self.opinion_name = opinion_name
        self.examples = load_json_file(file_path)
        self.read_and_count_result(self.examples)

    def read_and_count_result(self, examples):
        sentiment_name = self.sentiment_name
        opinion_name = self.opinion_name
        aspect_frequency = defaultdict(int)
        opinion_frequency = defaultdict(int)
        aspect_opinion_positives = defaultdict(int)
        aspect_opinion_negatives = defaultdict(int)

        aspect_sentiment = defaultdict(dict)
        aspect_opinion = defaultdict(dict)
        for example in examples:
            if not example:
                continue
            for aspect in example["评价维度"]:
                aspect_name = aspect["text"]
                if "relations" not in aspect:
                    continue
                if sentiment_name not in aspect["relations"] or opinion_name not in aspect["relations"]:
                    continue
                sentiment = aspect["relations"][sentiment_name][0]
                if sentiment["text"] == "未提及":
                    continue
                aspect_frequency[aspect_name] += 1
                if sentiment["text"] not in aspect_sentiment[aspect_name]:
                    aspect_sentiment[aspect_name][sentiment["text"]] = 1
                else:
                    aspect_sentiment[aspect_name][sentiment["text"]] += 1

                opinions = aspect["relations"][opinion_name]
                for opinion in opinions:
                    opinion_text = opinion["text"]
                    opinion_frequency[opinion_text] += 1
                    if opinion_text not in aspect_opinion[aspect_name]:
                        aspect_opinion[aspect_name][opinion_text] = 1
                    else:
                        aspect_opinion[aspect_name][opinion_text] += 1

                    aspect_opinion_text = aspect_name + opinion_text
                    if sentiment["text"] == "正向":
                        aspect_opinion_positives[aspect_opinion_text] += 1
                    else:
                        aspect_opinion_negatives[aspect_opinion_text] += 1

        aspect_freq_items = sorted(aspect_frequency.items(), key=lambda x: x[1], reverse=True)
        descend_aspects = [item[0] for item in aspect_freq_items]

        self.aspect_frequency = aspect_frequency   # 每个属性出现的频率
        #{'酒店': 1, '手艺': 1, '服务': 4, '房间': 8, '设施': 1, '早餐': 1}
        self.opinion_frequency = opinion_frequency # 每种观点词出现的频率
        #{'非常好': 1, '棒': 1, '好': 2, '干净': 4, '热情': 1, '大': 1, '小': 2}
        self.aspect_sentiment = aspect_sentiment   # 各属性的情感倾向统计
        #{'酒店': {'正向': 1}, '手艺': {'正向': 1}, '服务': {'正向': 3, '负向': 1}}
        self.aspect_opinion = aspect_opinion       # 各属性的观点词统计
        #{'酒店': {'非常好': 1}, '手艺': {'棒': 1}, '服务': {'好': 1, '热情': 1, '差': 1, '服务': 1}, '房间': {'干净': 4, '大': 1, '小': 2, '热': 1, '一般': 1, '漂亮': 1}}
        self.aspect_opinion_positives = aspect_opinion_positives # 正向属性观点词统计
        #{'酒店非常好': 1, '手艺棒': 1, '服务好': 1, '房间干净': 4, '服务热 情': 1}
        self.aspect_opinion_negatives = aspect_opinion_negatives # 负向属性观点词统计
        #{'房间小': 2, '房间热': 1, '服务差': 1, '房间一般': 1}
        self.descend_aspects = descend_aspects   #将各属性出现次数降序排序
        #['房间', '服务', '性价比', '酒店', '手艺', '设施', '早餐', '风格', '环境']

# 创建一个 FastAPI「实例」，名字为app
app = FastAPI()

# 设置允许跨域请求，解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求体数据类型：text  用户输入的要进行属性级情感分析的文本
class Document(BaseModel):
    text: str

# 定义路径操作装饰器：POST方法 + API接口路径
# 单文本情感分析接口
@app.post("/v1/singleEmotionAnalysis/", status_code=200)
# 定义路径操作函数，当接口被访问将调用该函数
async def SingleEmotionAnalysis(document: Document):
    try:
        # 获取用户输入的要进行属性级情感分析的文本内容
        input_text = document.text
        # 调用加载好的模型进行属性级情感分析
        singleAnalysisResult = predict(input_text,schema)
        # 接口结果返回
        results = {"message": "success", "inputText": document.text, "singleAnalysisResult": singleAnalysisResult}
        return results
    # 异常处理
    except Exception as e:
        print("异常信息：", e)
        raise HTTPException(status_code=500, detail=str("请求失败，服务器端发生异常！异常信息提示：" + str(e)))

# 批量情感分析接口
@app.post("/v1/batchEmotionAnalysis/", status_code=200)
# 定义路径操作函数，当接口被访问将调用该函数
async def BatchEmotionAnalysis(file: UploadFile):
    # 读取上传的文件
    fileBytes = file.file.read()
    fileName = file.filename
    # 判断上传文件类型
    fileType = fileName.split(".")[-1]
    if fileType != "txt":
        raise HTTPException(status_code=406, detail=str("请求失败，上传文件格式不正确！请上传txt文件！"))
    try:
        # 将添加时间标记重命名避免重复
        now_time = int(time.mktime(time.localtime(time.time())))
        filePath = "./textresource/" + str(now_time) + "_" + fileName
        # 将用户上传的文件保存到本地
        fout = open(filePath, 'wb')
        fout.write(fileBytes)
        fout.close()
        # 批量文本情感分析
        batchAnalysisResults = batchPredict(filePath,schema)
        sr = SentimentResult('./outputs/sentiment_results.json')
        # 属性频率词云图数据
        aspect_wc_data = []
        for item in sr.aspect_frequency:
            text = {}
            text['name'] = item
            text['value'] = sr.aspect_frequency[item]
            aspect_wc_data.append(text)
        # 属性频率柱状图数据
        content_freq_items = sr.aspect_frequency.items()
        content_freq_items = sorted(content_freq_items, key=lambda x: x[1], reverse=True)
        content_freq_items = content_freq_items[:15]
        aspect_hist_x_data = [item[0] for item in content_freq_items]
        aspect_hist_y_data = [item[1] for item in content_freq_items]
        # 属性+观点数据
        new_aspect_opinion = {}
        for aspect in sr.aspect_opinion:
            for opinion in sr.aspect_opinion[aspect]:
                key = aspect + opinion
                new_aspect_opinion[key] = sr.aspect_opinion[aspect][opinion]
        aspect_opinion_data = new_aspect_opinion
        # 属性+观点词云图数据
        aspect_opinion_wc_data = []
        for item in aspect_opinion_data:
            text = {}
            text['name'] = item
            text['value'] = aspect_opinion_data[item]
            aspect_opinion_wc_data.append(text)
        # 属性+观点柱状图数据
        content_freq_items = aspect_opinion_data.items()
        content_freq_items = sorted(content_freq_items, key=lambda x: x[1], reverse=True)
        content_freq_items = content_freq_items[:15]
        aspect_opinion_hist_x_data = [item[0] for item in content_freq_items]
        aspect_opinion_hist_y_data = [item[1] for item in content_freq_items]
        # 属性+情感词云图数据
        new_aspect_opinion = {}
        for aspect in sr.aspect_sentiment:
            for sentiment in sr.aspect_sentiment[aspect]:
                key = aspect + sentiment
                new_aspect_opinion[key] = sr.aspect_sentiment[aspect][sentiment]
        aspect_sentiment_wc_data = []
        for item in new_aspect_opinion:
            text = {}
            text['name'] = item
            text['value'] = new_aspect_opinion[item]
            aspect_sentiment_wc_data.append(text)
        # 属性+情感柱状图数据
        aspect_sentiment_hist_x_data = []
        aspect_sentiment_positives = []
        aspect_sentiment_negatives = []
        keep_aspects = set(sr.descend_aspects[:15])
        for aspect, sentiment in sr.aspect_sentiment.items():
            if aspect not in keep_aspects:
                continue
            aspect_sentiment_hist_x_data.append(aspect)
            if "正向" in sentiment:
                aspect_sentiment_positives.append(sentiment["正向"])
            else:
                aspect_sentiment_positives.append(0)
            if "负向" in sentiment:
                aspect_sentiment_negatives.append(sentiment["负向"])
            else:
                aspect_sentiment_negatives.append(0)

        # 接口结果返回
        results = {"message": "success", "batchAnalysisResults": batchAnalysisResults,
                  "aspect_wc_data": aspect_wc_data,
                  "aspect_hist_x_data": aspect_hist_x_data,
                  "aspect_hist_y_data": aspect_hist_y_data,
                  "aspect_opinion_wc_data": aspect_opinion_wc_data,
                  "aspect_opinion_hist_x_data": aspect_opinion_hist_x_data,
                  "aspect_opinion_hist_y_data": aspect_opinion_hist_y_data,
                  "aspect_sentiment_wc_data": aspect_sentiment_wc_data,
                  "aspect_sentiment_hist_x_data": aspect_sentiment_hist_x_data,
                  "aspect_sentiment_positives": aspect_sentiment_positives,
                  "aspect_sentiment_negatives": aspect_sentiment_negatives}
        return results
    # 异常处理
    except Exception as e:
        print("异常信息：", e)
        raise HTTPException(status_code=500, detail=str("请求失败，服务器端发生异常！异常信息提示：" + str(e)))

# 启动创建的实例app，设置启动ip和端口号
uvicorn.run(app, host="127.0.0.1", port=8000)
