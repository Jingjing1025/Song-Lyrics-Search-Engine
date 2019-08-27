#!/usr/bin/python3

from flask import Flask, render_template, request

import search

application = app = Flask(__name__)
app.debug = True

@app.route('/search', methods=["GET"])
def dosearch():
    query_withDup = request.args['query']
    query = list(set(query_withDup))
    qtype = request.args['query_type']

    page_num = 0
    action_type = request.args['action']
    search_results = 0

    if action_type == "Search":
        page_num = 1
    elif action_type == "Previous" or action_type == "Next":
        page_num = int(request.args['page'])
    else:
        print("Error: Wrong Action Type.")

    start = (page_num-1)*20
    perpage = 20

    if action_type == "Search":
        search_results = search.search_initial(query, qtype, 0, perpage)
    else:
        search_results = search.search(query, qtype, start, perpage)

    length = search.getTotalNum()[0][0]

    if length/perpage > int(length/perpage):
        lastpage = int(length/perpage)+1
    else:
        lastpage = length/perpage

    return render_template('results.html',
            query=query,
            results=length,
            search_results=search_results,
            query_type=qtype,
            page=page_num,
            lastpage=lastpage)


@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        pass
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')