#!/usr/bin/python3

import psycopg2
import re
import string
import sys

_PUNCTUATION = frozenset(string.punctuation)

def _remove_punc(token):
    """Removes punctuation from start/end of token."""
    i = 0
    j = len(token) - 1
    idone = False
    jdone = False
    while i <= j and not (idone and jdone):
        if token[i] in _PUNCTUATION and not idone:
            i += 1
        else:
            idone = True
        if token[j] in _PUNCTUATION and not jdone:
            j -= 1
        else:
            jdone = True
    return "" if i > j else token[i:(j+1)]

def _get_tokens(query):
    rewritten_query = []
    tokens = re.split('[ \n\r]+', query)
    for token in tokens:
        cleaned_token = _remove_punc(token)
        if cleaned_token:
            if "'" in cleaned_token:
                cleaned_token = cleaned_token.replace("'", "''")
            rewritten_query.append(cleaned_token)
    return rewritten_query


def search_initial(query, query_type, start, perpage):   
    rewritten_query = _get_tokens(query)   
    length = len(rewritten_query)
    rewritten_query = str(tuple(rewritten_query)).rstrip(',)') + ')'

    try:
        connection = psycopg2.connect(
            user="cs143", password="cs143",
            host="localhost",
            port="5432",
            database="searchengine")
    
        cursor = connection.cursor()
    except Exception as error:
        print("Error occurred during connection.", error)
        exit()

    and_query = """
        CREATE MATERIALIZED VIEW CACHE AS
            SELECT 
                song_name,
                artist_name,
                song_url 
            FROM (
                SELECT * 
                FROM song_score 
                WHERE token in {}
                )a 
            GROUP BY song_name, song_url, artist_name 
            Having count(token)={} 
            ORDER BY sum(a.tf_idf) DESC;
    """.format(rewritten_query, length) 

    or_query = """
        CREATE MATERIALIZED VIEW CACHE AS
            SELECT 
                song_name,
                artist_name,
                song_url 
            FROM SONG_SCORE 
            WHERE SONG_SCORE.token IN {}  
            ORDER BY tf_idf DESC;
    """.format(rewritten_query)

    extract = """
        SELECT 
            * 
        FROM CACHE
        LIMIT {} OFFSET {};
    """.format(perpage,start)

    try:
        cursor.execute("DROP MATERIALIZED VIEW if exists CACHE;")
    except Exception as error:
        print("Error occurred during executing and_query", error)
        connection.close()
        exit()

    if query_type == "and":
        try:
            cursor.execute(and_query)
        except Exception as error:
            print("Error occurred during executing and_query", error)
            connection.close()
            exit()
    elif query_type == "or":
        try:
            cursor.execute(or_query)
        except Exception as error:
            print("Error occurred during executing or_query", error)
            connection.close()
            exit()
    else:
        print("Error: Wrong method input")
        connection.close()
        exit()

    cursor.execute(extract)

    # Can also use fetchone or fetchmany and iterate
    rows = cursor.fetchall()

    connection.commit()
    connection.close()

    return rows

def search(query, query_type, start, perpage):
    try:
        connection = psycopg2.connect(
            user="cs143", password="cs143",
            host="localhost",
            port="5432",
            database="searchengine")
    
        cursor = connection.cursor()
    except Exception as error:
        print("Error occurred during connection.", error)
        exit()

    extract= """
        SELECT 
            * 
        FROM CACHE
        LIMIT {} OFFSET {};
    """.format(perpage,start)

    try:
        cursor.execute(extract)
    except Exception as error:
        print("Error occurred during executing extract", error)
        connection.close()
        exit()

    if query_type != "or" and query_type != "and":
        print("Error: Wrong method input")
        connection.close()
        exit()

    # Can also use fetchone or fetchmany and iterate
    rows = cursor.fetchall() 
 
    connection.close()

    return rows

def getTotalNum():
    try:
        connection = psycopg2.connect(
            user="cs143", password="cs143",
            host="localhost",
            port="5432",
            database="searchengine")
    
        cursor = connection.cursor()
    except Exception as error:
        print("Error occurred during connection.", error)
        exit()

    getlength = """
        SELECT COUNT(*) FROM CACHE;
    """

    try:
        cursor.execute(getlength)
    except Exception as error:
        print("Error occurred during executing getlength", error)
        connection.close()
        exit()

    # Can also use fetchone or fetchmany and iterate
    rows = cursor.fetchall() 
 
    connection.close()

    return rows


if __name__ == "__main__":
    if len(sys.argv) > 2:
        result = search(' '.join(sys.argv[2:]), sys.argv[1].lower())
        print(result)
    else:
        print("USAGE: python3 search.py [or|and] term1 term2 ...")

