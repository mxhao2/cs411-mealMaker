from flask import Flask, render_template, redirect, url_for, request, flash, session
from wtforms import Form, TextField, PasswordField, IntegerField, validators, SelectField
from wtforms.validators import Required


#Import passlib to encrypt password
from passlib.hash import sha256_crypt

#Import escape string to prevent people from injecting bad SQL stuff into forms
from MySQLdb import escape_string as thwart

#This script is used to connect to the database. To change DB configuration, modify the script
from dbconnect import connection

# This script is used for generating meals based on nutrient and price preferences
from mealranker import rank_meals
from recommender import get_recs
from contentedBased import simpath

import random

#This is for garbage collection
import gc

app = Flask(__name__)

app.secret_key = "SECRET_KEY"


@app.route('/')
def home():
    return redirect(url_for('login'))
    
    
    
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm', message="Passwords must match!")])
    confirm = PasswordField('Repeat Password')
    
class InsertAndDeleteForm(Form):
    id = IntegerField('Meal ID')
    
class UpdatePasswordForm(Form):
    current_password = PasswordField('Current Password', [validators.Required()])
    password = PasswordField('New Password', [validators.Required(), validators.EqualTo('confirm', message="Passwords must match!")])
    confirm = PasswordField('Repeat Password')

class UpdateMealDescription(Form):
    id = IntegerField('Meal ID', [validators.Required()])
    desc = TextField('New Description')

class SearchMeal(Form):
    query = TextField('Query')

class MealFinder(Form):
    calories = IntegerField('Calories (1=Very Low, 2=Low, 3=Indifferent, 4=High, 5=Very High)', [validators.Required(), validators.NumberRange(min=1, max=5, message='Must be [1-5]')])
    carbs = IntegerField('Carbs (1=Very Low, 2=Low, 3=Indifferent, 4=High, 5=Very High)', [validators.Required(), validators.NumberRange(min=1, max=5, message='Must be [1-5]')])
    fat = IntegerField('Fat (1=Very Low, 2=Low, 3=Indifferent, 4=High, 5=Very High)', [validators.Required(), validators.NumberRange(min=1, max=5, message='Must be [1-5]')])
    protein = IntegerField('Protein (1=Very Low, 2=Low, 3=Indifferent, 4=High, 5=Very High)', [validators.Required(), validators.NumberRange(min=1, max=5, message='Must be [1-5]')])
    price = IntegerField('Price (1=Very Low, 2=Low, 3=Indifferent, 4=High, 5=Very High)', [validators.Required(), validators.NumberRange(min=1, max=5, message='Must be [1-5]')])



    
# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #Check if username and password are correct.
        c, conn = connection()
        #Check if username exists.
        command = 'SELECT * FROM User WHERE username = "'+ request.form['username']+'" AND password = "' + request.form['password'] + '";'
            
        
        x = c.execute(command)
        if int(x) > 0:
            session['username'] = request.form['username']
            return redirect(url_for('mymeals'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)
    
# Route for handling the login page logic
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            
            username = str(form.username.data)
            password = str(form.password.data)
            
            c, conn = connection()
            #Check if username exists.
            command = 'SELECT * FROM User WHERE username = "'+ thwart(username)+'";'
            
            
            x = c.execute(command)
            
            if int(x) > 0:
                flash("That username is already taken!")
                return render_template('register.html', form=form)
            
            else:
                command = 'INSERT INTO User(username,password) VALUES ("'+thwart(username)+'","'+thwart(password)+'");'
                
                c.execute(command)
                conn.commit()
                flash("Thanks for registering")
                
                c.close()
                conn.close()
                gc.collect()
                
                session['logged_in'] = True
                session['username'] = username
                
                return redirect(url_for('login'))
        
        return render_template('register.html', form=form)    
    except Exception as e:
        return(str(e))
        
        
# Route for handling the mymeals page logic
@app.route('/mymeals', methods=['GET', 'POST'])
def mymeals():
    error = None
    c, conn = connection()

    #Display all the meals of this person.
    command = 'SELECT meals.meal_id, meals.meal_desc, meals.meal_cals, meals.meal_carbs, meals.meal_fat, meals.meal_protein, cast((meals.meal_price) as  decimal(16,2)) FROM favorites, meals WHERE username = "'+ session['username']+'" AND favorites.meal_id = meals.meal_id;'
    
    x = c.execute(command)
    
    data = c.fetchall()
    return render_template('mymeals.html', data=data, username=session['username'], form=InsertAndDeleteForm(), form2=InsertAndDeleteForm(), form3=UpdateMealDescription(), form4=SearchMeal())
    
# Route for handling adding meals    
@app.route('/mymealsadd', methods=['GET', 'POST'])
def mymealsadd():
    error = None
    c, conn = connection()
    insertForm = InsertAndDeleteForm(request.form)
    try:
        if request.method == "POST" and insertForm.validate():
            
            meal_id = str(insertForm.id.data)
            
            command = 'INSERT INTO favorites(username, meal_id) VALUES ("'+session['username']+'",'+str(meal_id)+');'
            
            
            x = c.execute(command)
            conn.commit()
            
            
    except Exception as e:
        if('Duplicate entry' not in str(e)):
            return(str(e))

    #Display all the meals of this person.
    command = 'SELECT meals.meal_id, meals.meal_desc, meals.meal_cals, meals.meal_carbs, meals.meal_fat, meals.meal_protein, cast((meals.meal_price) as  decimal(16,2)) FROM favorites, meals WHERE username = "'+ session['username']+'" AND favorites.meal_id = meals.meal_id;'
    
    x = c.execute(command)
    
    data = c.fetchall()
    return render_template('mymeals.html', data=data, username=session['username'], form=InsertAndDeleteForm(), form2=InsertAndDeleteForm(), form3=UpdateMealDescription(), form4=SearchMeal())

# Route for handling deleting meals
@app.route('/mymealsdelete', methods=['GET', 'POST'])
def mymealsdelete():
    error = None
    c, conn = connection()
    deleteForm = InsertAndDeleteForm(request.form)
    try:
        if request.method == "POST" and deleteForm.validate():
            
            meal_id = str(deleteForm.id.data)
            
            command = 'DELETE FROM favorites WHERE username = "'+session['username']+'" AND meal_id = '+str(meal_id)+';'
            
            
            
            x = c.execute(command)
            conn.commit()
            
            
    except Exception as e:
        return(str(e))

    #Display all the meals of this person.
    command = 'SELECT meals.meal_id, meals.meal_desc, meals.meal_cals, meals.meal_carbs, meals.meal_fat, meals.meal_protein, cast((meals.meal_price) as  decimal(16,2)) FROM favorites, meals WHERE username = "'+ session['username']+'" AND favorites.meal_id = meals.meal_id;'
    
    x = c.execute(command)
    
    data = c.fetchall()
    return render_template('mymeals.html', data=data, username=session['username'], form=InsertAndDeleteForm(), form2=InsertAndDeleteForm(), form3=UpdateMealDescription(), form4=SearchMeal())
# Route for handling updating meal description    
@app.route('/mymealsupdatedesc', methods=['GET', 'POST'])
def mymealsupdatedesc():
    error = None
    c, conn = connection()
    updateForm = UpdateMealDescription(request.form)
    try:
        if request.method == "POST" and updateForm.validate():
            
            meal_id = str(updateForm.id.data)
            description = str(updateForm.desc.data)
            
            command = 'UPDATE meals SET meals.meal_desc = "' + description + '"  WHERE meals.meal_id = '+str(meal_id)+';'
            
            
            
            x = c.execute(command)
            conn.commit()
            
            
    except Exception as e:
        return(str(e))

    #Display all the meals of this person.
    command = 'SELECT meals.meal_id, meals.meal_desc, meals.meal_cals, meals.meal_carbs, meals.meal_fat, meals.meal_protein, cast((meals.meal_price) as  decimal(16,2)) FROM favorites, meals WHERE username = "'+ session['username']+'" AND favorites.meal_id = meals.meal_id;'
    
    x = c.execute(command)
    
    data = c.fetchall()
    return render_template('mymeals.html', data=data, username=session['username'], form=InsertAndDeleteForm(), form2=InsertAndDeleteForm(), form3=UpdateMealDescription(), form4=SearchMeal())    
# Route for handling updating passwords    
@app.route('/updatepassword', methods=['GET', 'POST'])
def updatepassword():
    error = None
    try:
        updatePasswordForm = UpdatePasswordForm(request.form)
        if request.method == "POST" and updatePasswordForm.validate():
                
                current_password = str(updatePasswordForm.current_password.data)
                password = str(updatePasswordForm.password.data)
                
                c, conn = connection()
                #Check if password is correct for this username.
                command = 'SELECT * FROM User WHERE username = "'+ session['username']+'" AND password = "' + current_password + '";'

                
                x = c.execute(command)
                
                if int(x) == 0:
                    flash("Current password is wrong!")
                    return render_template('updatepassword.html', form=updatePasswordForm)
                
                else:
                    command = 'UPDATE User SET password = "'+password+'" WHERE username = "' + session['username'] + '";'
                    
                    
                    c.execute(command)
                    conn.commit()
                    
                    c.close()
                    conn.close()
                    gc.collect()
                    
                    session['logged_in'] = False
                    session['username'] = None
                    
                    return redirect(url_for('login'))
    except Exception as e:
        return(str(e))
                
    return render_template('updatepassword.html', form=updatePasswordForm)    
    
@app.route('/searchMealByDesc', methods=['GET', 'POST'])
def searchMealByDesc():
    error = None
    c,conn = connection()
    searchQuery = ""
    searchForm = SearchMeal(request.form)
    try:
        if request.method == 'POST' and searchForm.validate():
            searchQuery = str(searchForm.query.data)
            command = "select meals.meal_id, meals.meal_desc, meals.meal_cals, meals.meal_carbs, meals.meal_fat, meals.meal_protein, cast((meals.meal_price) as  decimal(16,2)) from meals where meals.meal_desc like '%"  + searchQuery + "%';" 
            x = c.execute(command)
            data = c.fetchall()
    except Exception as e:
        return(str(e))
        
    return render_template('searchResults.html', data=data)
    
@app.route('/mealfinder', methods=['GET', 'POST'])
def mealfinder():
    error = None
    c,conn = connection()
    best = []
    try:
        searchForm = MealFinder(request.form)
        if request.method == 'POST' and searchForm.validate():
            #Choose NUM_MEALS different random meals and put into comma separated list.
            # Ex. '45,65,3,4,56
            
            NUM_MEALS = 299
            mealIDs = random.sample(range(1,300), NUM_MEALS)
            mealIDstring = ','.join([str(v) for v in mealIDs])
            
            #Extract attribute weights
            calorieWeight = int(searchForm.calories.data) - 3
            carbsWeight = int(searchForm.carbs.data) - 3
            fatWeight = int(searchForm.fat.data) - 3
            proteinWeight = int(searchForm.protein.data) - 3
            priceWeight = int(searchForm.price.data) - 3
            
            #Select them from database
            # command = "select meals.meal_id, meals.meal_desc, meals.meal_cals, meals.meal_carbs, meals.meal_fat, meals.meal_protein, cast((meals.meal_price) as  decimal(16,2)) from meals where meals.meal_id IN ("  + mealIDstring + ");"
            command = "select meals.meal_id, meals.meal_desc, meals.meal_cals, meals.meal_carbs, meals.meal_fat, meals.meal_protein, cast((meals.meal_price) as  decimal(16,2)) from meals;"
            x = c.execute(command)
            data = c.fetchall()
            
            # Send data to the algorithm, which will return the best 20 meals
            best = rank_meals(data, calorieWeight, carbsWeight, fatWeight, proteinWeight, priceWeight, NUM_MEALS)
            
            
            
    except Exception as e:
        return(str(e))
        
    return render_template('mealfinder.html', data=best, form=searchForm)
@app.route('/getRecommendations', methods=['GET', 'POST'])
def getRecommendations():
    
    c,conn = connection()
    
    command  = 'SELECT meal_id FROM favorites WHERE username = "'+session['username'] + '";'
    x = c.execute(command)
    data = c.fetchall()
    likes = []
    import re
    for row in data:
        result = re.sub('[^0-9]','', str(row))
        likes.append(int(result))
    recs = get_recs(likes)
    totalList = []
    for rec in recs:
        totalList.append(int(rec))
    recs2 = simpath(likes)
    for rec in recs2:
        totalList.append(int(rec))
        
    command = 'SELECT meals.meal_id, meals.meal_desc, meals.meal_cals, meals.meal_carbs, meals.meal_fat, meals.meal_protein, cast((meals.meal_price) as  decimal(16,2)) from meals where '
    for i in range(len(totalList)):
        command += 'meal_id = ' + str(totalList[i]) 
        if i != len(totalList) - 1:
            command += ' OR '
    c.execute(command) 
    data = c.fetchall()

    return render_template('recs.html', data=data)

if __name__ == '__main__':
    app.run(debug=True) # Debug true for development purpose.
