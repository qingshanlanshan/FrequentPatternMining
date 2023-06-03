import json
from tqdm import tqdm

def load_wiki(filename:str):
    map = {}
    with open('datasets/'+filename, 'r') as f:
        for line in tqdm(f):
            data = json.loads(line)
            map[data['qid']]=data
    return map

def data2records(data):
    records = {}
    for key, value in tqdm(data.items()):
        record=set()
        for i in value['types']:
            record.add(i)
        for triples in value['head_triples']:
            record.add('h_'+triples[1])
        for triples in value['tail_triples']:
            record.add('t_'+triples[1])
        records[key]=record
    return records

def data2Tid(records:dict):
    dataset={}
    for key,value in tqdm(records.items()):
        for item in value:
            if not item in dataset:
                dataset[item]=set()
            dataset[item].add(key)
    return dataset

def eclat(dataset:dict,support:int,k:int):
    assert(k>=1)
    assert(k.__class__==int)
    
    dataset=filter_support(dataset,support)
    ret=dataset.copy()
    while(k>1):
        ret=merge_items(dataset,ret)
        ret=filter_support(ret,support)
        k-=1
    return ret

def filter_support(dataset:dict,min_support:int):
    copy_dataset=dataset.copy()
    for key,value in tqdm(copy_dataset.items()):
        if len(value)<min_support:
            dataset.pop(key)
    return dataset

def merge_items(dataset:dict,workingset:dict):
    newset={}
    for key1,value1 in tqdm(workingset.items()):
        for key2,value2 in tqdm(dataset.items()):
            if key2[1]=='_':
                continue
            if key1==key2:
                continue
            if key2 in key1:
                continue
            if key1.__class__==frozenset:
                new_key=list(key1)
            else:
                new_key=[key1]
            new_key.append(key2)
            new_key=frozenset(new_key)
            if new_key in newset:
                continue
            newset[new_key]=value1.intersection(value2)
    return newset

def load_alias():
    map={}
    with open("datasets/alias_fudandm2023.jsonl",'r') as f:
        for line in f:
            data = json.loads(line)
            map[data['qid']]=data['alias']
    return map

def load_freqset(filename:str):
    ret={}
    with open("output/"+filename,'r') as f:
        for line in f:
            itemset,recordset=line.strip().split(':')
            itemset=itemset.split(',')
            recordset=recordset.split(',')
            if len(itemset)==1:
                itemset=itemset[0]
            else:
                itemset=frozenset(itemset)
            ret[itemset]=set(recordset)
    return ret

def filter_entity(freqset:list):
    ret=[]
    for itemset in freqset:
        add=True
        for item in itemset:
            if item[0]!='Q':
                add=False
                break
        if add:
            ret.append(itemset)
    return ret
# dump a list of sets to a csv file
def dump(filename:str, data:list, alias_map=None):
    with open("output/"+filename,'w') as f:
        for itemset in data:
            if itemset.__class__==str:
                f.write(itemset)
                f.write("\n")
                continue
            for i in range(len(itemset)):
                item=list(itemset)[i]
                if alias_map!=None:
                    if item[1]=='_':
                        f.write(item[:2])
                        if item[2:] in alias_map:
                            f.write(alias_map[item[2:]])
                        else:
                            f.write(item[2:])
                    else:
                        f.write(alias_map[item])
                else:
                    f.write(item)
                if i!=len(itemset)-1:
                    f.write(',')
            f.write('\n')

def dump_freqset(freqset:dict,filename:str):
    with open("output/"+filename,'w') as f:
        for key,value in tqdm(freqset.items()):
            if key.__class__==str:
                f.write(key)
            else:
                key_list=list(key)
                for i in range(len(key)):
                    f.write(key_list[i])
                    if i!=len(key_list)-1:
                        f.write(',')
            f.write(":")
            value_list=list(value)
            for i in range(len(value)):
                f.write(value_list[i])
                if i!=len(value)-1:
                    f.write(',')
            f.write('\n')

def generate_2_rules(freq2:dict,freq1:dict,min_conf:float):
    ret={}
    for key,value in freq2.items():
        rule_sup=len(value)
        item1,item2=list(key)
        if item1[1]=='_' or item2[1]=='_':
            continue
        if not item1 in freq1:
            item1=frozenset([item1])
        if not item2 in freq1:
            item2=frozenset([item2])
        item1_sup=len(freq1[item1])
        item2_sup=len(freq1[item2])

        conf1=rule_sup/item1_sup
        conf2=rule_sup/item2_sup        
        
        if(conf1>=min_conf):
            if item1 not in ret:
                ret[item1]=set()
            if item2.__class__==str:
                ret[item1].add(item2)
            else:
                for i in item2:
                    ret[item1].add(i)
        if(conf2>=min_conf):
            if item2 not in ret:
                ret[item2]=set()
            if item1.__class__==str:
                ret[item2].add(item1)
            else:
                for i in item1:
                    ret[item2].add(i)
    return ret

def generate_3_rules(freq3:dict,freq2:dict,min_conf:float):
    ret={}
    for key,value in tqdm(freq3.items()):
        rule_sup=len(value)
        item1,item2,item3=list(key)
        item12_sup=len(freq2[frozenset([item1,item2])])
        item13_sup=len(freq2[frozenset([item1,item3])])
        item23_sup=len(freq2[frozenset([item2,item3])])
        
        conf3=rule_sup/item12_sup
        conf2=rule_sup/item13_sup
        conf1=rule_sup/item23_sup
        
        if conf1>min_conf:
            newkey=frozenset([item2,item3])
            if not newkey in ret:
                ret[newkey]=set()
            ret[newkey].add(item1)
        if conf2>min_conf:
            newkey=frozenset([item1,item3])
            if not newkey in ret:
                ret[newkey]=set()
            ret[newkey].add(item2)
        if conf3>min_conf:
            newkey=frozenset([item1,item2])
            if not newkey in ret:
                ret[newkey]=set()
            ret[newkey].add(item3)
    return ret


# rules is a dict where key is an item and value is a set of items
def dump_rules(data:dict,filename:str):
    with open("output/"+filename,'w') as f:
        for key,value in data.items():
            if key.__class__==str:
                f.write(key)
            elif key.__class__==frozenset:
                key_list=list(key)
                for i in range(len(key)):
                    f.write(key_list[i])
                    if i!=len(key_list)-1:
                        f.write(',')
            f.write("->")
            value_list=list(value)
            for i in range(len(value)):
                f.write(value_list[i])
                if not i==len(value_list)-1:
                    f.write(",")
            f.write("\n")
            

        
    

        
    
if __name__ == '__main__':
    data = load_wiki("mini_wiki.jsonl")
    print(data['Q5']['types'])
    records=data2records(data)
    print(records['Q5'])
    dataset=data2Tid(records)

    support=20
    freq1=filter_support(dataset,support)
    dump_freqset(freq1,"test_freq1.csv")
    ret=freq1.copy()    
    ret=merge_items(freq1,ret)
    ret=filter_support(ret,support)
    freq2=ret
    dump_freqset(freq2,"test_freq2.csv")
    ret=merge_items(freq1,ret)
    ret=filter_support(ret,support)
    freq3=ret
    dump_freqset(freq3,"test_freq3.csv")


    support=20
    freq1=load_freqset("test_freq1.csv")
    freq2=load_freqset("test_freq2.csv")
    print(next(iter(freq2.keys())))
    
    rules=generate_2_rules(freq2,freq1,0.5)

    dump_rules(rules,"test_rules.csv")
        
    
