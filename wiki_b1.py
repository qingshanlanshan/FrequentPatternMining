from wiki_helper import *

alias_map=load_alias()



with open("output/2-rules-10000supp-0_5conf.csv",'r') as f1:
    with open("output/b1.csv",'w') as f2:
        for line in f1:
            key,value=line.strip().split('->')
            key=key.split(',')
            value=value.split(',')
            for i in range(len(key)):
                item=key[i]
                if item[1]=='_' and item[2:] in alias_map:
                    f2.write(alias_map[item[2:]])
                elif item[0]=='Q':
                    f2.write(alias_map[item])
                else:
                    f2.write(item)
                if not i==len(key)-1:
                    f2.write(',')
            f2.write("->")
            for i in range(len(value)):
                item=value[i]
                if item[1]=='_' and item[2:] in alias_map:
                    f2.write(alias_map[item[2:]])
                elif item[0]=='Q':
                    f2.write(alias_map[item])
                else:
                    f2.write(item)
                if i!=len(value)-1:
                    f2.write(',')
            f2.write('\n')
            