import os
from json import load
from sqlite3 import OperationalError, connect


def search(db_path, query, icon, lang):
    #### get results from db  ###################################
    with connect(db_path) as db:
        cursor = db.cursor()
        try:
            cursor.execute(
                f"SELECT name,path,fragment FROM searchIndex WHERE name LIKE '%{' '.join(query)}%' ORDER BY length(name) LIMIT 50")
        except OperationalError:
            cursor.execute(
                f"SELECT name,path FROM searchIndex WHERE name LIKE '%{' '.join(query)}%' ORDER BY length(name) LIMIT 50")

        results = cursor.fetchall()

    #### parse results ########################################
    for index, result in enumerate(results):
        if len(result) == 3:
            results[index] = (result[0], result[1].split(
                '>')[-1] + '#' + ('' if result[2] is None else result[2]))
        else:
            results[index] = (result[0], result[1].split('>')[-1])

    ###########################################################
    doc_dir = os.path.join(os.path.dirname(db_path), "Documents")

    if os.path.exists(doc_dir):
        dis_results = []

        for result in results:
            dis_results.append({
                "Title": f"{result[0]}",
                "SubTitle": f"{lang}",
                "IcoPath": f"{icon}",
                "JsonRPCAction": {
                    'method': 'doc_open',
                    'parameters': [f"{os.path.join(doc_dir, result[1])}",
                                   f"{''.join(lang.split('_'))}:{result[0]}"],
                    'dontHideAfterAction': False
                }
            })

        return dis_results


def tmp_html(redirect):
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>redirect</title>
            <meta http-equiv="refresh" content="0; url =
                file:///{}" />
        </head>
        <body>
        </body>
        </html>
        """
    with open("./tmp/redirect.html", "w") as f:
        f.write(html.format(redirect))


def log(*content):
    try:
        with open('./tmp/log.txt', 'r+') as f:
            con = f.read().split('\n')
            con = '\n'.join(con[:1000])    # max log history size
            f.seek(0)
            f.truncate()
            f.write('\n'.join(map(str, content))+'\n' + con)
            
    except IOError:
        with open('./tmp/log.txt', 'w') as f:
            f.write('\n'.join(map(str, content))+'\n')
        

def file_size(url):
    with open('./tmp/file_size.json', 'r') as f:
        size = float(load(f)[url])
    size = f"{(size/1024/1024):.3f} MB"
    
    return size
    
    