# 基于正则表达式的规则
import re
from pyltp import Segmentor, Postagger, Parser


REMOVE_WORD_LIST = ["将", "会", "认为", "正是", "受", "直接", "避免", "是否", "在于", "原因", "可是", "相应", "需要", "没有", "没", "肯定", "来自", "喜欢", "理解", "好像", "是", "有", "了解", "说", "无", "离", "还有", "准备", "还是", "就是", "感受", "知道", "感觉", "看到"]
PROB_WORD_LIST=['可能','暂缓','目前' ,'将会']
PROPER_POSTAG_LIST = ["a", "e", "g", "h", "i", "j", "k", "m", "n", "nh", "nd", "ni", "nl", "ns", "nz", "o", "q", "r", "v", "ws", "x"]
MAIN_POSTAG_LIST = ["a", "n", "nh", "ni", "nl", "ns", "nz", "v", "i", "j"]


def _have_at_least_noun_or_verb(postag_list):
    for postag in MAIN_POSTAG_LIST:
        if postag in postag_list:
            return True
    return False

def _ltp_post_process(s, segmentor, postagger):
    # s = s.encode("utf-8")
    result = ""
    words = segmentor.segment(s)
    postags = postagger.postag(words)
    cause_postag_list = []
    min_index = 500
    max_index = -500
    for index, i in enumerate(zip(words, postags)):
        if i[1] in PROPER_POSTAG_LIST and i[0] not in REMOVE_WORD_LIST:
            min_index = min(min_index, index)
            max_index = max(max_index, index)
    for index, i in enumerate(zip(words, postags)):
        if index >= min_index and index <= max_index:
            result += i[0]
            cause_postag_list.append(i[1])
    if not _have_at_least_noun_or_verb(cause_postag_list):
        return ""
    return result

def dict2list(dict):
    phrase_list=[]
    phrase_list.append(dict['cause'])
    phrase_list.append(dict['connective'])
    phrase_list.append(dict['effect'])
    return phrase_list
# 输出格式：抽取规则\t\t\t时间戳\t\t\t原因短语 触发词 结果短语\t\t\t上下文
def format_output(rule, time, context, phrase_list,prob):
    processed_list = []
    for phrase in phrase_list:
        processed_list.append(_ltp_post_process(phrase,segmentor, postagger))
    return rule + "\t\t\t" + time + "\t\t\t" + (" ".join(processed_list)) + "\t\t\t" + context + "\t\t\t" +prob


# 因A导致B
def rule_1(sentence, remove_word_dict):
    is_done = False
    cause = None
    effect = None
    connective = None
    prob='Unknown'
    rule='none'
    pattern_prob=re.compile(r'可能|也许|也许会|目前|暂缓|尚且|不确定|是否')
    match_prob=pattern_prob.search(sentence)
    if match_prob == None:
        pattern = re.compile(r"(因|因为|由|由于|通过)(.+)(导致|引起|使得|造成|引发|招致|致使)(.+)$")
        match = pattern.search(sentence)
        if match and match.lastindex >= 3:
            cause = match.group(2)
            connective = match.group(3)
            effect = match.group(4)
            cause = _ltp_post_process(cause,segmentor, postagger)
            effect = _ltp_post_process(effect,segmentor, postagger)
            if (cause in remove_word_dict) or (effect in remove_word_dict) or (cause == "") or (effect == "") or ("记者" in cause):
                cause = None
                effect = None
                connective = None
            else:
                prob = 'explicit'
                is_done = True
                rule='rule1'
    if match_prob != None:
        pattern = re.compile(r"(因|因为|由|由于|通过)(.+)(导致|引起|使得|造成|引发|招致|致使)(.+)$")
        match = pattern.search(sentence)
        if match and match.lastindex >= 3:
            cause = match.group(2)
            connective = match.group(3)
            effect = match.group(4)
            cause = _ltp_post_process(cause, segmentor, postagger)
            effect = _ltp_post_process(effect, segmentor, postagger)
            if (cause in remove_word_dict) or (effect in remove_word_dict) or (cause == "") or (effect == "") or (
                    "记者" in cause):
                cause = None
                effect = None
                connective = None
            else:
                prob = 'vague'
                is_done = True
                rule = 'rule1'
    return rule,is_done, cause, effect, connective,prob
# A未导致B
def rule_2(sentence, remove_word_dict):
    is_done = False
    cause = None
    effect = None
    connective = None
    prob = 'Unknown'
    rule='Unknown'
    pattern_prob=re.compile(r'可能|也许|也许会|目前|暂缓|尚且|不确定|是否')
    match_prob=pattern_prob.search(sentence)
    if match_prob == None:
        pattern = re.compile(r"(.+)(未|没有|不足以)(导致|引起|使得|造成|引发|招致|致使)(.+)$")
        match = pattern.search(sentence)
        if match and match.lastindex >= 3:
            cause = match.group(1)
            connective = match.group(2) + match.group(3)
            effect = match.group(4)
            cause = _ltp_post_process(cause, segmentor, postagger)
            effect = _ltp_post_process(effect, segmentor, postagger)
            if (cause in remove_word_dict) or (effect in remove_word_dict) or (cause == "") or (effect == "") or ("记者" in cause):
                cause = None
                effect = None
                connective = None
            else:
                prob = 'explicit'
                rule='rule2'
                is_done = True
    if match_prob != None:
        pattern = re.compile(r"(.+)(未|没有)(导致|引起|使得|造成|引发|招致|致使)(.+)$")
        match = pattern.search(sentence)
        if match and match.lastindex >= 3:
            cause = match.group(1)
            connective = match.group(2) + match.group(3)
            effect = match.group(4)
            cause = _ltp_post_process(cause, segmentor, postagger)
            effect = _ltp_post_process(effect, segmentor, postagger)
            if (cause in remove_word_dict) or (effect in remove_word_dict) or (cause == "") or (effect == "") or (
                    "记者" in cause):
                cause = None
                effect = None
                connective = None
            else:
                prob = 'vague'
                rule='rule2'
                is_done = True
    return rule,is_done, cause, effect, connective,prob


# A导致B
def rule_3(sentence, remove_word_dict):
    is_done = False
    cause = None
    effect = None
    connective = None
    prob = 'Unknown'
    rule='Unkown'
    pattern_prob=re.compile(r'可能|也许|也许会|目前|暂缓|尚且|不确定|是否')
    match_prob=pattern_prob.search(sentence)
    if match_prob == None:
        pattern = re.compile(r"(.+)(导致|引起|使得|(?<!制|改|打|塑)造成|引发|招致|致使)(.+)$")
        match = pattern.search(sentence)
        if match and match.lastindex >= 3:
            cause = match.group(1)
            connective = match.group(2)
            effect = match.group(3)
            cause = _ltp_post_process(cause,segmentor, postagger)
            effect = _ltp_post_process(effect,segmentor, postagger)
            if (cause in remove_word_dict) or (effect in remove_word_dict) or (cause == "") or (effect == "") or ("记者" in cause):
                cause = None
                effect = None
                connective = None
            else:
                prob = 'explicit'
                rule='rule3'
                is_done = True
    if match_prob != None:
        pattern = re.compile(r"(.+)(导致|引起|使得|(?<!制|改|打|塑)造成|引发|招致|致使)(.+)$")
        match = pattern.search(sentence)
        if match and match.lastindex >= 3:
            cause = match.group(1)
            connective = match.group(2)
            effect = match.group(3)
            cause = _ltp_post_process(cause, segmentor, postagger)
            effect = _ltp_post_process(effect, segmentor, postagger)
            if (cause in remove_word_dict) or (effect in remove_word_dict) or (cause == "") or (effect == "") or (
                    "记者" in cause):
                cause = None
                effect = None
                connective = None
            else:
                is_done = True
                rule='rule3'
                prob = 'vague'
    return rule,is_done, cause, effect, connective,prob

# A是导致B的原因
def rule_4(sentence, remove_word_dict):
    is_done = False
    cause = None
    effect = None
    connective = None
    prob = 'Unknown'
    rule='Unknown'
    pattern_prob=re.compile(r'可能|也许|也许会|目前|暂缓|尚且|不确定|是否')
    match_prob=pattern_prob.search(sentence)
    if match_prob ==None:
        pattern = re.compile(r"(.+)是(导致|引起|使得|造成|引发|招致|致使)(.+)的(.*)(原因|因素)$")
        match = pattern.search(sentence)
        if match and match.lastindex >= 3:
            cause = match.group(1)
            connective = match.group(2)
            effect = match.group(3)
            cause = _ltp_post_process(cause,segmentor, postagger)
            effect = _ltp_post_process(effect,segmentor, postagger)
            if (cause in remove_word_dict) or (effect in remove_word_dict) or (cause == "") or (effect == "") or ("记者" in cause):
                cause = None
                effect = None
                connective = None
            else:
                prob='explicit'
                rule='rule4'
                is_done = True
    if match_prob !=None:
        pattern = re.compile(r"(.+)是(导致|引起|使得|造成|引发|招致|致使)(.+)的(.*)(原因|因素)$")
        match = pattern.search(sentence)
        if match and match.lastindex >= 3:
            cause = match.group(1)
            connective = match.group(2)
            effect = match.group(3)
            cause = _ltp_post_process(cause, segmentor, postagger)
            effect = _ltp_post_process(effect, segmentor, postagger)
            if (cause in remove_word_dict) or (effect in remove_word_dict) or (cause == "") or (effect == "") or (
                    "记者" in cause):
                cause = None
                effect = None
                connective = None
            else:
                prob = 'vague'
                rule='rule4'
                is_done = True
    return rule,is_done, cause, effect, connective,prob
segmentor=Segmentor()
postagger=Postagger()
parser=Parser()