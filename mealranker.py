def rank_meals(dataTuple, calorieWeight, carbsWeight, fatWeight, proteinWeight, priceWeight, numMeals):

    # n = numMeals
    n = len(dataTuple)
    
    best = []
    data = list(list(x) for x in dataTuple)
    
    top20 = 15
    high20 = 5
    mid20 = 0
    low20 = -5
    bottom20 = -10
    
    #Create score for each row
    for i in range(0,n):
        data[i].append(0)
        
    #Data is [[id, desc, calories, carbs, fat, protein, price, score]
    #         [id, desc, calories, carbs, fat, protein, price, score]...]
    
    #Sort by calories
    data.sort(key= lambda x: x[2], reverse=True)
    for i in range(0,n//5):
        data[i][7] += top20 * calorieWeight
    for i in range(n//5,n//5 *2):
        data[i][7] += high20 * calorieWeight
    for i in range(n//5 * 2,n//5 * 3):
        data[i][7] += mid20 * calorieWeight
    for i in range(n//5*3,n//5 * 4):
        data[i][7] += low20 * calorieWeight
    for i in range(n//5*4,n//5 * 5):
        data[i][7] += bottom20 * calorieWeight
        
    #Sort by carbs
    data.sort(key= lambda x: x[3], reverse=True)
    for i in range(0,n//5):
        data[i][7] += top20 * carbsWeight
    for i in range(n//5,n//5 * 2):
        data[i][7] += high20 * carbsWeight
    for i in range(n//5 * 2,n//5 * 3):
        data[i][7] += mid20 * carbsWeight
    for i in range(n//5 * 3,n//5 * 4):
        data[i][7] += low20 * carbsWeight
    for i in range(n//5 * 4,n//5 * 5):
        data[i][7] += bottom20 * carbsWeight
        
    #Sort by fat
    data.sort(key= lambda x: x[4], reverse=True)
    for i in range(0,n//5):
        data[i][7] += top20 * fatWeight
    for i in range(n//5,n//5 * 2):
        data[i][7] += high20 * fatWeight
    for i in range(n//5 * 2,n//5 * 3):
        data[i][7] += mid20 * fatWeight
    for i in range(n//5 * 3,n//5 * 4):
        data[i][7] += low20 * fatWeight
    for i in range(n//5 * 4,n//5 * 5):
        data[i][7] += bottom20 * fatWeight
        
    #Sort by protein
    data.sort(key= lambda x: x[5], reverse=True)
    for i in range(0,n//5):
        data[i][7] += top20 * proteinWeight
    for i in range(n//5,n//5 * 2):
        data[i][7] += high20 * proteinWeight
    for i in range(n//5 * 2,n//5 * 3):
        data[i][7] += mid20 * proteinWeight
    for i in range(n//5 * 3,n//5 * 4):
        data[i][7] += low20 * proteinWeight
    for i in range(n//5 * 4,n//5 * 5):
        data[i][7] += bottom20 * proteinWeight
        
    #Sort by price
    data.sort(key= lambda x: x[6], reverse=True)
    for i in range(0,n//5):
        data[i][7] += top20 * priceWeight
    for i in range(n//5,n//5 * 2):
        data[i][7] += high20 * priceWeight
    for i in range(n//5 * 2,n//5 * 3):
        data[i][7] += mid20 * priceWeight
    for i in range(n//5 * 3,n//5 * 4):
        data[i][7] += low20 * priceWeight
    for i in range(n//5 * 4,n//5 * 5):
        data[i][7] += bottom20 * priceWeight
     
    # Sort by score
    data.sort(key= lambda x: x[7], reverse=True)
    for i in range(0,n):
        best.append(data[i])
    
    return best