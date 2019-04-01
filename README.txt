目前抽取因果对的规则有两种：

1. 基于依存句法的规则（syntactic_rules.py）
准确率相对较高
rule_1: 匹配“...造成...”句式
例：【事故】造成【经济损失】
rule_2: 匹配“...造成的...”句式
例：【事故】造成的【经济损失】
rule_3: 匹配“造成...的...”句式
造成【经济损失】的【事故】

2. 基于正则表达式的规则（lexical_rules.py）
准确率较低，抽取的因果关系中容易带有多余成分；但召回率较高，能抽取到依存句法规则无法发现的因果关系
rule_1: 匹配“因为...导致...”句式
rule_2: 匹配“...未导致...”句式（未使用）
rule_3: 匹配“...导致...”句式
rule_4: 匹配“...是导致...的原因”句式（未使用）

pyltp使用文档：	
在线演示：http://ltp.ai/demo.html

------------------------------
新构建的图谱：

1. index_to_event.pkl
key: event_id
value: event_text

2. cause_effect_hash
key: cause_effect_id
value: {
    'cause': cause_id
    'effect': effect_id
    'short_context': 因果对所在的上下文（短，1个句子）
    'context': 因果对所在的上下文（长）
    'rule_name': 抽取出该因果对的规则名称
}
