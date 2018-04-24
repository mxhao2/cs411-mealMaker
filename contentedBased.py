def simpath(id):
    import pandas as pd
    ibs = pd.read_csv('ibs.csv')
    
    idToIndexMap = {}
    for i in range(1,len(ibs.columns)):
        idToIndexMap.update({ibs.columns[i]: i})     
    idx = []
    for i in id:
        idx.append(idToIndexMap.get(str(i)))
        
    m=pd.read_csv('MG.csv')
    
    com=[]
    for j in idx:
        x=m.iloc[j-1].values        
        for i in range(len(m)):
                       y=m.iloc[i].values
                       pxy=sum([a*b for a,b in zip(x,y)])
                       pxx=sum([a*b for a,b in zip(x,x)])
                       pyy=sum([a*b for a,b in zip(y,y)])
                       s=2*pxy/(pxx+pyy)
                       com.append([i+1,s])
    com.sort(key=lambda x: x[1],reverse=True) 
    com=[i[0] for i in com if i[0] not in idx][:5]
    ret = []
    for c in com:
        ret.append(ibs.columns[c])
    
    
    return(ret)