<template>
  <div class="app-container">
    <el-card class="box-card">
      <div class="tip">
        请上传要进行批量分析的txt文件
      </div>
      <el-upload
        class="upload-demo"
        drag
        action=""
        :limit="1"
        :http-request="uploadFile"
        accept=".txt"
        style="text-align: center; padding-top:10px;padding-bottom:10px;"
      >
        <i class="el-icon-upload" />
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      </el-upload>
      <el-row style="text-align: center; padding-top:20px;padding-bottom:10px;">
        <el-button type="info" round @click="clear()">清空内容</el-button>
        <el-button type="primary" round @click="batchEmotionAnalysis()">情感分析</el-button>
        <el-button type="success" round @click="saveResult()">保存结果</el-button>
      </el-row>
    </el-card>
    <el-row style="text-align: center; padding-top:10px;padding-bottom:10px;"></el-row>
    <el-card v-show="visible" class="box-card">
      <div v-show="visible" class="tip">
        批量情感分析结果：
      </div>
      <el-table
        id="excel"
        :data="analysisResults"
        height="290"
        border
        style="width: 100%"
      >
        <el-table-column
          prop="aspect"
          label="属性"
          width="180"
        />
        <el-table-column
          prop="opinions"
          label="观点"
        />
        <el-table-column
          prop="sentiment"
          label="情感倾向"
          width="180"
        />
      </el-table>
      <el-row style="text-align: center; padding-top:20px;padding-bottom:20px;">
        <el-button type="primary" round @click="aspect_wc_visual()">属性频率词云图</el-button>
        <el-button type="primary" round @click="aspect_hist_visual()">属性频率柱状图</el-button>
        <el-button type="primary" round @click="aspect_opinion_wc_visual()">属性+观点词云图</el-button>
        <el-button type="primary" round @click="aspect_opinion_hist_visual()">属性+观点柱状图</el-button>
        <el-button type="primary" round @click="aspect_sentiment_wc_visual()">属性+情感词云图</el-button>
        <el-button type="primary" round @click="aspect_sentiment_hist_visual()">属性+情感柱状图</el-button>
      </el-row>
    </el-card>
    <el-row style="text-align: center; padding-top:10px;padding-bottom:10px;"></el-row>
    <!--分析结果可视化-->
    <el-card v-show="aw_visible" class="box-card">
      <div ref="aspect_wc" class="chart-container"/>
    </el-card>
    <el-card v-show="ah_visible" class="box-card" >
      <div ref="aspect_hist" class="chart-container"/>
    </el-card>
    <el-card v-show="aow_visible" class="box-card">
      <div ref="aspect_opinion_wc" class="chart-container"/>
    </el-card>
    <el-card v-show="aoh_visible" class="box-card">
      <div ref="aspect_opinion_hist" class="chart-container" />
    </el-card>
    <el-card v-show="asw_visible" class="box-card">
      <div ref="aspect_sentiment_wc" class="chart-container" />
    </el-card>
    <el-card v-show="ash_visible" class="box-card">
      <div ref="aspect_sentiment_hist" class="chart-container" />
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
export default {
  data() {
    return {
      fileData: '',
      analysisResults: '',
      aspect_wc_data: '',
      aspect_hist_x_data: '',
      aspect_hist_y_data: '',
      aspect_opinion_wc_data: '',
      aspect_opinion_hist_x_data: '',
      aspect_opinion_hist_y_data: '',
      aspect_sentiment_wc_data: '',
      aspect_sentiment_hist_x_data: '',
      aspect_sentiment_positives: '',
      aspect_sentiment_negatives: '',
      visible: false,
      aw_visible: false,
      ah_visible: false,
      aow_visible: false,
      aoh_visible: false,
      asw_visible: false,
      ash_visible: false
    }
  },
  // 上传文件，获取上传文件内容并弹窗提示
  methods: {
    clear() {
      var that = this
      that.analysisResults = ''
      that.aspect_wc_data = ''
      that.aspect_hist_x_data = ''
      that.aspect_hist_y_data = ''
      that.aspect_opinion_wc_data = ''
      that.aspect_opinion_hist_x_data = ''
      that.aspect_opinion_hist_y_data = ''
      that.aspect_sentiment_wc_data = ''
      that.aspect_sentiment_hist_x_data = ''
      that.aspect_sentiment_positives = ''
      that.aspect_sentiment_negatives = ''
      that.visible = false
      that.aw_visible = false
      that.ah_visible = false
      that.aow_visible = false
      that.aoh_visible = false
      that.asw_visible = false
      that.ash_visible = false
      that.$message({
        showClose: true,
        message: '内容已清空！请手动删除文件！',
        type: 'success'
      })
    },
    uploadFile(file) {
      this.fileData = file.file
      console.log(file.file)
      this.$message({
        showClose: true,
        message: '文件上传成功！',
        type: 'success'
      })
    },
    // 保存结果
    saveResult() {
      var tempData = this.analysisResults
      if (tempData === '') {
        this.$message({
          showClose: true,
          message: '情感分析结果内容为空！',
          type: 'warning'
        })
      } else {
        this.Excels.exportExcel('批量情感分析结果.xlsx', '#excel')
        this.$message({
          showClose: true,
          message: '情感分析结果保存成功！',
          type: 'success'
        })
      }
    },
    // 批量情感分析
    batchEmotionAnalysis() {
      var that = this
      // 判断用户是否已经选择要上传的文件
      if (that.fileData === '') {
        this.$message({
          showClose: true,
          message: '请先选择要进行批量情感分析的txt文件！',
          type: 'warning'
        })
        that.analysisResults = ''
        that.visible = false
        return
      }
      that.visible = true
      that.$message({
        showClose: true,
        message: '批量情感分析开始！请稍等！',
        type: 'success'
      })
      // 请求后端批量情感分析接口，请求方法为POST，请求体格式为form-data，字段为file，类型也为file
      var config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
      var form = new FormData()
      form.append('file', that.fileData)
      axios.post('http://127.0.0.1:8000/v1/batchEmotionAnalysis', form, config).then((response) => {
        // 获取接口返回的情感分析预测结果并更新界面数据
        that.analysisResults = response.data.batchAnalysisResults
        that.aspect_wc_data = response.data.aspect_wc_data
        that.aspect_hist_x_data = response.data.aspect_hist_x_data
        that.aspect_hist_y_data = response.data.aspect_hist_y_data
        that.aspect_opinion_wc_data = response.data.aspect_opinion_wc_data
        that.aspect_opinion_hist_x_data = response.data.aspect_opinion_hist_x_data
        that.aspect_opinion_hist_y_data = response.data.aspect_opinion_hist_y_data
        that.aspect_sentiment_wc_data = response.data.aspect_sentiment_wc_data
        that.aspect_sentiment_hist_x_data = response.data.aspect_sentiment_hist_x_data
        that.aspect_sentiment_positives = response.data.aspect_sentiment_positives
        that.aspect_sentiment_negatives = response.data.aspect_sentiment_negatives
        that.visible = true
        that.$message({
          showClose: true,
          message: '批量情感分析完成！',
          type: 'success'
        })
      }).catch((error) => {
        console.log(error)
        that.analysisResults = ''
        that.visible = false
        that.$message({
          showClose: true,
          message: '请求异常，请检查后端服务模块！',
          type: 'error'
        })
      })
    },
    // 批量分析结果可视化
    // 图1
    aspect_wc_visual() {
      var that = this
      that.aw_visible = true;  that.ah_visible = false;   that.aow_visible = false;
      that.aoh_visible = false; that.asw_visible = false; that.ash_visible = false;
      var aspect_wc_chart = echarts.init(this.$refs.aspect_wc);
      var aspect_wc_option = {
        series: [{
          type: 'wordCloud',
          rotationRange: [-90, 90],
          rotationStep: 45,
          textStyle: {
            color: function () {
              return (
                "rgb(" +
                [
                  Math.round(Math.random() * 160),
                  Math.round(Math.random() * 160),
                  Math.round(Math.random() * 160),
                ].join(",") +
                ")"
              );
            },
          },
          data: this.aspect_wc_data
        }]
      };
      aspect_wc_chart.setOption(aspect_wc_option);
    },
    // 图2
    aspect_hist_visual() {
      var that = this
      that.aw_visible = false;  that.ah_visible = true;   that.aow_visible = false;
      that.aoh_visible = false; that.asw_visible = false; that.ash_visible = false;
      var aspect_hist_chart = echarts.init(this.$refs.aspect_hist);
      var aspect_hist_option = {
        title: {
          text: 'The histogram of aspect/frequency', // 设置图表标题
          left: 'center', // 居中对齐
          textStyle: {
            fontFamily: 'Arial', // 设置字体
            fontSize: 15 // 设置字体大小
          },
          top: 25 // 设置距离顶部的距离
        },
        xAxis: {
          name: 'aspect',
          nameLocation: 'middle', // 设置标题位置
          nameGap: 50, // 设置标题与轴线之间的距离
          type: 'category',
          data: this.aspect_hist_x_data,
          boundaryGap: ['10%','10%'],   //两边留白
          axisLabel: {  //x轴文字的配置
            show: true,
            interval: 0,//使x轴文字显示全
            rotate: 45
          }
        },
        yAxis: [{
          name: 'frequency',
          nameRotate: 90, // 设置标题旋转角度
          nameLocation: 'middle', // 设置标题位置
          nameGap: 20, // 设置标题与轴线之间的距离
          type: 'value',
          axisLine:{show:true},
          axisTick:{show:true}
        },
        {
          type: 'value',
          axisLine:{show:true},
          axisTick:{show:true}
        }],
        series: [{
          data: this.aspect_hist_y_data,
          type: 'bar'
        },
        {
          data: this.aspect_hist_y_data,
          type: 'line'
        }]
      };
      aspect_hist_chart.setOption(aspect_hist_option);
    },
    // 图3
    aspect_opinion_wc_visual() {
      var that = this
      that.aw_visible = false;  that.ah_visible = false;  that.aow_visible = true;
      that.aoh_visible = false; that.asw_visible = false; that.ash_visible = false;
      var aspect_opinion_wc_chart = echarts.init(this.$refs.aspect_opinion_wc);
      var aspect_opinion_wc_option = {
        series: [{
          type: 'wordCloud',
          rotationRange: [-90, 90],
          rotationStep: 45,
          textStyle: {
            color: function () {
              return (
                "rgb(" +
                [
                  Math.round(Math.random() * 160),
                  Math.round(Math.random() * 160),
                  Math.round(Math.random() * 160),
                ].join(",") +
                ")"
              );
            },
          },
          data: this.aspect_opinion_wc_data
        }]
      };
      aspect_opinion_wc_chart.setOption(aspect_opinion_wc_option);
    },
    // 图4
    aspect_opinion_hist_visual() {
      var that = this
      that.aw_visible = false; that.ah_visible = false;  that.aow_visible = false;
      that.aoh_visible = true; that.asw_visible = false; that.ash_visible = false;
      var aspect_opinion_hist_chart = echarts.init(this.$refs.aspect_opinion_hist);
      var aspect_opinion_hist_option = {
        title: {
          text: 'The histogram of aspect with opinion/frequency', // 设置图表标题
          left: 'center', // 居中对齐
          textStyle: {
            fontFamily: 'Arial', // 设置字体
            fontSize: 15 // 设置字体大小
          },
          top: 25 // 设置距离顶部的距离
        },
        xAxis: {
          name: 'aspect with opinion',
          nameLocation: 'middle', // 设置标题位置
          nameGap: 50, // 设置标题与轴线之间的距离
          type: 'category',
          data: this.aspect_opinion_hist_x_data,
          boundaryGap: ['10%','10%'],   //两边留白
          axisLabel: {  //x轴文字的配置
            show: true,
            interval: 0,//使x轴文字显示全
            rotate: 45
          }
        },
        yAxis: [{
          name: 'frequency',
          nameRotate: 90, // 设置标题旋转角度
          nameLocation: 'middle', // 设置标题位置
          nameGap: 20, // 设置标题与轴线之间的距离
          type: 'value',
          axisLine:{show:true},
          axisTick:{show:true}
        },
        {
          type: 'value',
          axisLine:{show:true},
          axisTick:{show:true},
        }],
        series: [{
          data: this.aspect_opinion_hist_y_data,
          type: 'bar'
        },
        {
          data: this.aspect_opinion_hist_y_data,
          type: 'line'
        }]
      };
      aspect_opinion_hist_chart.setOption(aspect_opinion_hist_option);
    },
    // 图5
    aspect_sentiment_wc_visual() {
      var that = this
      that.aw_visible = false;  that.ah_visible = false;  that.aow_visible = false;
      that.aoh_visible = false; that.asw_visible = true; that.ash_visible = false;
      var aspect_sentiment_wc_chart = echarts.init(this.$refs.aspect_sentiment_wc);
      var aspect_sentiment_wc_option = {
        series: [{
          type: 'wordCloud',
          rotationRange: [-90, 90],
          rotationStep: 45,
          textStyle: {
            color: function () {
              return (
                "rgb(" +
                [
                  Math.round(Math.random() * 160),
                  Math.round(Math.random() * 160),
                  Math.round(Math.random() * 160),
                ].join(",") +
                ")"
              );
            },
          },
          data: this.aspect_sentiment_wc_data
        }]
      };
      aspect_sentiment_wc_chart.setOption(aspect_sentiment_wc_option);
    },
    // 图6
    aspect_sentiment_hist_visual() {
      var that = this
      that.aw_visible = false;  that.ah_visible = false;  that.aow_visible = false;
      that.aoh_visible = false; that.asw_visible = false; that.ash_visible = true;
      var aspect_sentiment_hist_chart = echarts.init(this.$refs.aspect_sentiment_hist);
      var aspect_sentiment_hist_option = {
        title: {
          text: 'The histogram of aspect/sentiment', // 设置图表标题
          left: 'center', // 居中对齐
          textStyle: {
            fontFamily: 'Arial', // 设置字体
            fontSize: 15 // 设置字体大小
          },
          top: 25 // 设置距离顶部的距离
        },
        legend: {
          data: ['positives', 'negatives']
        },
        xAxis: {
          name: 'aspect',
          nameLocation: 'middle', // 设置标题位置
          nameGap: 50, // 设置标题与轴线之间的距离
          type: 'category',
          data: this.aspect_sentiment_hist_x_data,
          boundaryGap: ['10%','10%'],   //两边留白
          axisLabel: {  //x轴文字的配置
            show: true,
            interval: 0,//使x轴文字显示全
            rotate: 45
          }
        },
        yAxis: [{
          name: 'sentiment frequency',
          nameRotate: 90, // 设置标题旋转角度
          nameLocation: 'middle', // 设置标题位置
          nameGap: 20, // 设置标题与轴线之间的距离
          type: 'value',
          axisLine:{show:true},
          axisTick:{show:true}
        },
        {
          type: 'value',
          axisLine:{show:true},
          axisTick:{show:true},
        }],
        series: [{
          name: 'positives',
          data: this.aspect_sentiment_positives,
          type: 'bar'
        },
        {
          name: 'negatives',
          data: this.aspect_sentiment_negatives,
          type: 'bar'
        }]
      };
      aspect_sentiment_hist_chart.setOption(aspect_sentiment_hist_option);
    }
  }
}
</script>

<style scoped>
  .tip {
    font-family: 宋体;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 20px;
    margin-bottom: 10px;
    text-align: left;
  }
  .chart-container {
    width: 500%; 
    height: 400px;
    margin-left: 400px;
  }
</style>
