from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

application= Flask(__name__) # initializing a flask app
app=application
@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink="https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'

            prod_html = bs(prodRes.text, "html.parser")
            k=prod_html.find("div",{"class":"col JOpGWq"}).find_all("a")[-1]
            m_pg="https://www.flipkart.com" + k["href"]
            prodRes1 = requests.get(m_pg)
            pd_box1 = bs(prodRes1.text, "html.parser")
            pg_link="https://www.flipkart.com" + pd_box1.find("div",{"class":"_2MImiq _1Qnn1K"}).a["href"][:-1]
            all_pg=[]
            for i in range(1,6):
                ll=(pg_link + str(i))
                all_pg.append(ll)
            pd_com = []
            pd_review = []
            pd_head = []  # Initialize as an empty list
            pd_rat = []
            revewer_name = []
            reviews = []  # List to store all the dictionaries

            for j in all_pg:
                prodRes5 = requests.get(j)
                n_pg_html = bs(prodRes5.text, "html.parser")
                pd_box = n_pg_html.find_all("div", {"class": "col _2wzgFH K0kLPL"})

                try:
                    for i in pd_box:
                        pd_review.append(i.p.text)

                except Exception as f:
                    print(f)

            

                try:
                    #commentHead.encode(encoding='utf-8')
                    for i in pd_box:
                        pd_head.append(i.div.div.div.p)
                except:
                    pd_head = 'No Comment Heading'

                try:
                    for i in pd_box:
                        pd_com.append(i.find("div", {"class": "t-ZTKy"}).text)
                except Exception as f:
                    print(f)

                try:
                    for i in pd_box:
                        pd_rat.append(i.div.find("div").text)
                except Exception as f:
                    print(f)

                try:
                    for i in pd_box:
                        revewer_name.append(i.find("p", {"class": "_2sc7ZR _2V5EHH"}).text)
                except Exception as f:
                    print(f)

                # Loop through the lists and create a dictionary for each set of data
                for idx in range(len(pd_review)):
                    mydict = {
                        # You need to define 'searchString' somewhere in your code
                        "Customer Name": revewer_name[idx],
                        "Rating": pd_rat[idx],
                        "Comment": pd_com[idx],
                        "Review": pd_review[idx],
                        'prodact name': searchString
                    
                    }
                    reviews.append(mydict)
            print(reviews)
            

            #client = pymongo.MongoClient("mongodb+srv://sabyasachi:sabyasachi@cluster0.ln0bt5m.mongodb.net/?retryWrites=true&w=majority")
            #db = client['review_scrap']
            #review_col = db['review_scrap_data']
            #review_col.insert_many(reviews)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000)
	#app.run(debug=True)