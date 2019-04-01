# -*- coding: utf-8 -*-
import pickle
import syntactic_rules
import os
LTP_DATA_DIR = 'ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
from pyltp import Segmentor,Postagger
segmentor = Segmentor()  # 初始化实例
postagger=Postagger()
postagger.load(pos_model_path)
segmentor.load(cws_model_path)  # 加载模型
words = ['元芳', '你', '怎么', '看']
postags = postagger.postag(words)
print('\t'.join(postags))
postagger.release()
words = segmentor.segment('元芳你怎么看')  # 分词
print ('\t'.join(words))
segmentor.release()  # 释放模型