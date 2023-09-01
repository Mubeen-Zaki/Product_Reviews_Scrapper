from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup as bs
import logging
from flask_cors import cross_origin,CORS
import csv
import pymongo

app = Flask(__name__)

logging.basicConfig(filename="logging.log",level=logging.INFO)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/review",methods=["POST"])
def search():
    if request.method == "POST":
        name = request.form["content"]
        prod_search_link = "https://www.flipkart.com/search?q=" + name.replace(" ","")
        try:
            flipkart_html = bs(requests.get(prod_search_link).text,'html.parser')
            big_boxes = flipkart_html.find_all("div",{"class":"_2kHMtA"})
            prod_link = "https://www.flipkart.com" + big_boxes[0].a["href"]
            prod_html = bs(requests.get(prod_link).text,'html.parser')
            comment_boxes = prod_html.find_all("div",{"class":"col _2wzgFH"})
            reviews = []
            #Creating a csv file
            f = open('./data_files/' + name + '.csv','w')
            writer = csv.writer(f)
            writer.writerow(["Product","Name","Rating","CommentHead","Comment"])
            for comment_box in comment_boxes:
                try:
                    rating = comment_box.div.div.text
                    heading = comment_box.div.p.text
                    comment = comment_box.find_all("div",{"class":"t-ZTKy"})[0].text.replace("READ MORE","")
                    user = comment_box.find_all("div",{"class":"row _3n8db9"})[0].div.p.text
                except Exception as e:
                    logging.INFO(e)
                my_dict = {"Product":name,"Name":user,"Rating":rating,"CommentHead":heading,"Comment":comment}
                reviews.append(my_dict)
                writer.writerow([name,user,rating,heading,comment])
            f.close()
        except Exception as e:
            logging.INFO(e)
        #Storing the data in MongoDB
        try:
            uri = "mongodb+srv://linux3760:linux3760@cluster0.urxsqur.mongodb.net/?retryWrites=true&w=majority"
            connection = pymongo.MongoClient(uri)
            db = connection["webscrap_db"]
            collec = db["reviews"]
            collec.insert_many(reviews)
        except Exception as e:
            logging.INFO(e)
        return render_template('result.html',reviews = reviews)
    else:
        return render_template('index.html')                    

if __name__ == "__main__":
    app.run(host="0.0.0.0")