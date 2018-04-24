

def getScore(history, similarities):
   return sum(history*similarities)/sum(similarities)

def get_recs(likes):
    import pandas as pd
    ibs = pd.read_csv('ibs.csv')
    data_neighbors = pd.read_csv('neighbors.csv')
    
    idToIndexMap = {}
    for i in range(1,len(ibs.columns)):
        idToIndexMap.update({ibs.columns[i]: i})    
    user_vector = [0]*(len(ibs.columns) -1)

    for like in likes:
        user_vector[idToIndexMap.get(str(like)) - 1] = 1

    recs = [0]*(len(ibs.columns) - 1)


    for j in range(1,len(ibs.columns)):
        # Get product ID
        productId = ibs.columns[j]
        # get product Index (ibs has extra column for meal_id)
        productIndex = j - 1
        # If user already likes product, ignore
        if user_vector[productIndex] == 1:
            recs[productIndex] = 0
        else:
            # Get top 10 most similar products
            product_top_names = data_neighbors.iloc[productIndex][1:10]
            product_top_sims = ibs.iloc[productIndex].sort_values(ascending=False)[1:10]       
            # Convert to indices
            l = []
            for prod in product_top_names:
                l.append(idToIndexMap.get(str(prod)))
            userVectorTop10Sims = [0]*9
            for k in range(9):
                userVectorTop10Sims[k] = user_vector[l[k]-1]
            x = getScore(userVectorTop10Sims,product_top_sims)
            recs[productIndex] = x
    # Sort by rec Factor
    idToRec = {}
    for j in range(0,len(recs)):
        idToRec[ibs.columns[j+1]] = recs[j]
    s = sorted(idToRec, key=idToRec.get,reverse=True)
    return s[:5]


