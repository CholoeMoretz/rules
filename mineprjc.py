# import pickle
# # import syntactic_rules
# # from pyltp import Segmentor, Postagger, Parser
# #
# # f=open('cause_effect_hash.pkl','rb')
# # cause_effect_has=pickle.load(f)
# # f.close()
# # f=open('index_to_event.pkl','rb')
# # index_to_event=pickle.load(f)
# # f.close()
# # segmentor = Segmentor()
# # postagger = Postagger()
# # parser = Parser()
# # segmentor.load("ltp_data_v3.4.0")
# # postagger.load("ltp_data_v3.4.0")
# # parser.load("ltp_data_v3.4.0")
# # phrase='我最最喜欢我家煜嫣'
# # syntactic_rules.build_dependency_tree(phrase, segmentor, postagger, parser)
# -*- coding: utf-8 -*-
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
