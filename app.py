### Start solution here
import pandas as pd
import numpy as np
import os
import glob
import json
 
import pprint
from json2html import *

from pathlib import Path
from flask import jsonify, Flask, render_template, request
import os
import stat
from pymongo import MongoClient
from random import randint

app = Flask(__name__)
def get_csv():
    path = os.getcwd()

    df1=[]
    dirs=os.listdir(path)
    index=0
    dict_ref={}
    dict_ref1={}
    final_dg=[]
    df1=[]
    df2=[]
    df=[]
    if os.path.exists("consolidated_output.1.csv"):
        os.remove("consolidated_output.1.csv")
        print("The file has been deleted successfully")
    for d in dirs:
        if os.path.isdir(d):
            for filename in glob.iglob(path+'/'+d +'/'+ '**/**', recursive=True):
                if not filename.endswith(".txt") and Path(filename).is_file():
                    print(filename)            
                    if(os.path.basename(filename)=='sample_data.1.csv'):
                        df1=pd.read_csv(filename).query("worth >= 1.0")
                        df1['source']=filename
                    elif(os.path.basename(filename)=='sample_data.3.dat'):
                        df2 =pd.read_csv(filename)
                        df2['worth'] = df2['worth']*df2['material_id']
                        df2['source']=filename
                    elif(os.path.basename(filename)=='sample_data.2.dat'):
                        df3 =pd.read_csv(filename,sep='|')
                        df=df3.groupby('product_name').agg({'product_name':'first','quality':'first','material_id':'max','worth':'sum'})
                        df['source']=filename
                elif Path(filename).is_file():
                        df4 =pd.read_csv(filename)
                        dict_ref1=pd.Series(df4.material_name.values,index=df4.id).to_dict()
                else:
                    continue      
            target = pd.concat([df1,df2,df], ignore_index=True)
            target['material_name'] = target['material_id'].map(dict_ref1)
            target.to_csv("consolidated_output.1.csv")



@app.route('/')
def index(): 
    filename = "consolidated_output.1.csv" 
    data = pd.read_csv(filename, header=0)
    data.to_html(open('templates/data.html', 'w'))
#Step 1: Connect to MongoDB - Note: Change connection string as needed
    client = MongoClient(port=27017)
    db=client['datadb']   
    coll = db["customerdata"]
    data = pd.read_csv(filename)
    payload = json.loads(data.to_json(orient='records'))
    coll.remove()
    coll.insert(payload)
    data.to_html(open('templates/data.html', 'w'))
    return render_template('data.html')
@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
       
        client = MongoClient(port=27017)
        db=client['datadb']   

        coll = db["customerdata"]
        result = request.form
        query={result.getlist('key')[0]:result.getlist('value')[0]}
        fd=coll.find(query)
        list_cur = list(fd) 
        column_names=[]
      
        for key,value in list_cur[0].items():
            column_names.append(key)
        print(column_names)
        return render_template("result.html",list_data=list_cur,colnames=column_names)
    else:
        return render_template('resultform.html')



@app.route('/product',methods = ['POST', 'GET'])
def query_prod(): 
    produ_list="nice_product,fancy_product"
    if request.method == 'POST':

        client = MongoClient(port=27017)
        db=client['datadb']   
        coll = db["customerdata"]
        result = request.form
        product_worth={}
     
        list_pr = [y for y in (x.strip() for x in request.form['list'].split(',')) if y]
        for product in list_pr:
            myquery = {"product_name": product}
            fd=coll.find_one(myquery)
            product_worth[product]=fd['worth']
     
        return render_template("search.html", data=product_worth)
    else:
        return render_template("product.html",some_list=produ_list)
if __name__ == '__main__':
    app.run()




