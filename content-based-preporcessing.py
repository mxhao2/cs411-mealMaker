def preprocessing(meals=pd.read_csv('meals.csv'))
    #meals=pd.read_csv('meals.csv')
    meals['main']=[i.replace('|',', ') for i in meals['meal_desc'].values]
    g=[i.replace('|',', ') for i in meals['meal_desc'].values]
    import re
    import operator
    h=[re.sub('[^a-zA-Z]+', ' ', s) for s in g]
    g=[[i for i in j.split(' ') if i not in stopwords.words('english')] for j in h]
    g=[[i for i in j if i!=''] for j in g]
    wordlist=np.unique([i for sub in g for i in sub])
    dictlst={}
    for i in range(len(wordlist)):
        if wordlist[i] not in dictlst:
            dictlst[wordlist[i]]=i
    encodelist=[[dictlst[i] for i in j] for j in g] 
    MG = []
    Dict_ID = {}
    Dict_Name = {}
    num_topics = len(wordlist)  
    for line in encodelist:
        topic_array = line
        topic_array = [int(x) for x in topic_array[:len(topic_array)-1]]

        count_dict = {}
        for topic in topic_array:
            if topic == 27:
                continue
            if topic not in count_dict:
                count_dict[topic] = 1
            else:
                count_dict[topic] += 1
        count_sorted = sorted(count_dict.items(), key=operator.itemgetter(1), reverse=True)
        try:
            rank = [(count_sorted[0][0],1)]
        except IndexError:
            rand=[1]
        for i in range(len(count_sorted)-1):
            if count_sorted[i+1][1] == count_sorted[i][1]:
                rank.append((count_sorted[i+1][0],rank[i][1]))
            else:
                rank.append((count_sorted[i+1][0],rank[i][1]+1))

        vector = [0.0] * num_topics
        for x in rank:
            vector[x[0]] = 1.0/x[1]

        MG.append(vector)
        with open('MG.csv', 'a') as f:
            pd.DataFrame(MG).to_csv(f,header=True,index=True)