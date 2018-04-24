import MySQLdb

def connection():
    try:
        conn = MySQLdb.connect(host="localhost", user="mealmaker_asishtb2", passwd="mealmaker", db="mealmaker_db")
        
        c = conn.cursor()
    
    except Exception as e:
        return(str(e))
     
    return c, conn