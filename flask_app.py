import ast
import os

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bS
from urllib.request import urlopen as uReq
import json

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/products', methods=['POST', 'GET'])  # route to display the product page
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ", "%20")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring
            uclient = uReq(flipkart_url)
            flipkartpage = uclient.read()
            uclient.close()
            flipkart_html = bS(flipkartpage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})

            del bigboxes[0:3]
            del bigboxes[-5:]
            alldata = {}

            for boxes in bigboxes:

                productname = boxes.find("div", {"class": "_3wU53n"})
                productLinks = "https://www.flipkart.com" + boxes.div.div.div.a['href']
                alldata[productname.text] = productLinks
            with open('url.txt', 'w') as file:               #dumping the url dict in a txt file
                file.write(json.dumps(alldata))

            return render_template("links.html", alldata = alldata)
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
        return render_template("links.html")
    else:
        return render_template("index.html")



@app.route('/review/<product>', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def review(product):
        try:
            file = open("url.txt", "r")
            contents = file.read()
            dictionary = ast.literal_eval(contents)
            productlink = dictionary[product]
            prodRes = requests.get(productlink)
            prodRes.encoding = 'utf-8'
            prod_html = bS(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})
            reviews = []
            for commentbox in commentboxes:
                try:
                    # name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                except:
                    name = 'No Name'
                try:
                    # rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'
                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text

                except Exception as e:
                    print("Exception while creating dictionary: ", e)
                mydict = {"Product": product, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
        return render_template('results.html')


#port = int(os.getenv("PORT"))
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    #app.run(host='0.0.0.0', port=port)
    app.run(host='127.0.0.1', port=8001, debug=True)
