import json
import os

from utils import log, tmp_html, file_size
from utils import search as doc_search
from wox import Wox, WoxAPI


class Doc(Wox):
    ### load settings and data ###############################################
    with open('docs.json', 'r', encoding='utf-8') as f, open('settings.json', 'r') as settings:
        data = json.load(f)
        settings = json.load(settings)
        
    for index, path in enumerate(settings["doc_paths"]):
        settings["doc_paths"][index] = os.path.abspath(path)
        
    
    options = ['install', 'uninstall', 'settings']
    
    ## get installed docs ####################################################
    docs = []
    for path in settings["doc_paths"]:
        if os.path.exists(path):
            for i in os.listdir(path):
                if os.path.isdir(os.path.join(path, i)) and i.endswith('.docset'):
                    ico = os.path.join(path, i, 'icon@2x.png')
                    if not os.path.exists(ico):
                        ico = os.path.join(path, i, 'icon.png')
                    
                    docs.append({
                        'name': i[:-7],
                        'path': os.path.join(path, i),
                        'IcoPath': ico
                    })
        
    #########################################################################################
    def query(self, _query):
        _query = _query.split()
        log('query:- ' + ' '.join(_query))
                
        if _query[0] == 'install':
            return self.install_query(_query[1:])
        
        elif _query[0] == 'uninstall':
            return self.uninstall_query(_query[1:])
        
        elif _query[0] == 'settings':
            return self.settings_query(_query[1:])
        
        elif _query[0] in self.settings['alias'].keys():
            return self._doc_search(self.settings['alias'][_query[0]], _query[1:])
        
        for _doc in self.docs:
            if _query[0].lower() == _doc['name'].lower():
                return self._doc_search(_doc['name'], _query[1:])

        return self.main_query(_query)
    
    def context_menu(self, data):
        results = []
        return results

    def install(self, url, name):
        import sys
        path = self.settings['doc_paths'][self.settings['new_download_loc']-1]
        archive_path = os.path.join(path, name) + '.tgz'
        
        python_path = sys.executable.replace('/', '\\')
        file_path = os.path.abspath("./installer.py").replace('/', '\\')
        python_path = python_path if python_path[-5] == "n" else python_path[:-5]+".exe"
        
        WoxAPI.hide_app()
        try:
            import subprocess
            subprocess.Popen([python_path, file_path, url, archive_path])
        except Exception as e:
            log(e)
        
    def open_in_webbrowser(self, url):
        import webbrowser
        webbrowser.open(url)
    
    def copy_url(self, url):
        os.system(f'echo {url} | clip')
        
    def install_select(self, doc_loc, data):
        name = data[doc_loc]['name']
        url = data[doc_loc]['url']
        install = {
            "Title": "download and install",
            "SubTitle": f"size:- {file_size(url)}",
            "IcoPath": "./Images/download-solid.png",
            "JsonRPCAction": {
                    'method': 'install',
                    'parameters': [f"{url}",
                                   f"{name}"],
                    'dontHideAfterAction': False
                }
        }
        open_in_webbrowser = {
            "Title": "open in default web browser",
            "SubTitle": f"{name} :- {url}",
            "IcoPath": "./Images/browser-solid.png",
            "JsonRPCAction": {
                    'method': 'open_in_webbrowser',
                    'parameters': [f"{url}"],
                    'dontHideAfterAction': False
                }
        }
        copy_url = {
            "Title": "copy to clipboard",
            "SubTitle": f"{name} :- {url}",
            "IcoPath": "./Images/clipboard-list-solid.png",
            "JsonRPCAction": {
                    'method': 'copy_url',
                    'parameters': [f"{url}"],
                    'dontHideAfterAction': False
                }
        }
        
        return [install, open_in_webbrowser, copy_url]
         
    def install_query(self, _query):
        ### get installable docs #######
        if self.settings['doc_search_install'] == 3:
            data = self.data['official'] + self.data['user_contrib'] + self.data['cheat_sheets']
        elif self.settings['doc_search_install'] == 2:
            data = self.data['official'] + self.data['user_contrib']
        else:
            data = self.data['official']
        ###################################
            
        names = [i['name'] for i in data]
        if _query[0] in names:      # doc selected
            return self.install_select(names.index(_query[0]), data)
        
        ### select a doc ##################################        
        _query = " ".join(_query).lower()
        
        results = []
        for i in data:
            if i['name'] in [j['name'] for j in self.docs]:
                continue

            if _query in i['name'].lower():
                results.append({
                    "Title": f"{i['name']}",
                    "SubTitle": f"{i['url']} size:-{file_size(i['url'])}",
                    "IcoPath": "./Images/download-solid.png",
                    "JsonRPCAction": {
                        'method': '_set_query',
                        'parameters': [f"install {i['name']}"],
                        'dontHideAfterAction': True
                    }
                })

        results.sort(key = lambda x: 2 if x['Title'].lower().startswith(_query) 
                                else 1 if x['Title'].lower().endswith(_query) else 0, 
                    reverse=True)

        return results[:50]
    
    def uninstall(self, path):
        log('removing:- ' + path)
        from shutil import rmtree
        rmtree(path, onerror=log)
                
    def uninstall_query(self, _query):
        _query = ' '.join(_query)
        
        results = []
        for doc in self.docs:
            if _query in doc['name']:
                results.append({
                    "Title": f"{doc['name']}",
                    "SubTitle": f"{doc['path']}",
                    "IcoPath": f"{doc['IcoPath']}",
                    "JsonRPCAction":{
                        'method': 'uninstall',
                        'parameters': [f"{doc['path']}"],
                        'dontHideAfterAction': False
                    }
                })
                
        results.sort(key = lambda x:2 if x['Title'].lower().startswith(_query) 
                                else 1 if x['Title'].lower().endswith(_query) else 0, 
                    reverse=True)
        
        return results[:50]
    
    def settings_query(self, _query):
        if len(_query):
            if _query[0] == 'doc_path':
                if len(_query[1:]):
                    if _query[1] == 'add':
                        path = ' '.join(_query[2:])
                        return [{
                            "Title": f"{'add path' if os.path.exists(path) else 'path doesn`t exists'}",
                            "SubTitle": f"{path}",
                            "IcoPath": "./Images/cog-solid.png",
                            "JsonRPCAction": {
                                'method': 'add_doc_path' if os.path.exists(path) else '',
                                'parameters': [path],
                                'dontHideAfterAction': False
                            }
                        }]
                    
                    elif _query[1] == 'remove':
                        with open('./settings.json', 'r') as f:
                            settings = json.load(f)
                        result = []
                        for path in settings['doc_paths']:
                            result.append({
                                "Title": f"{path}",
                                "SubTitle": "",
                                "IcoPath": "./Images/cog-solid.png",
                                "JsonRPCAction": {
                                    'method': 'remove_doc_path',
                                    'parameters': [path],
                                    'dontHideAfterAction': False
                            }
                            })
                        return result
                
                return [{
                        "Title": "add docset location",
                        "SubTitle": "ADD",
                        "IcoPath": "./Images/cog-solid.png",
                        "JsonRPCAction": {
                            'method': '_set_query',
                            'parameters': ["settings doc_path add"],
                            'dontHideAfterAction': True
                        }
                    },{
                        "Title": "remove docset locations",
                        "SubTitle": "REMOVE",
                        "IcoPath": "./Images/cog-solid.png",
                        "JsonRPCAction": {
                            'method': '_set_query',
                            'parameters': ["settings doc_path remove"],
                            'dontHideAfterAction': True
                        }
                    }
                ]
            
            elif _query[0] == 'default_install_loc':
                result = []
                cur = self.settings['new_download_loc']
                for index, loc in enumerate(self.settings['doc_paths'], 1):
                    result.append({
                        "Title": f"{loc}",
                        "SubTitle": f"{'current' if cur==index else ''}",
                        "IcoPath": "./Images/cog-solid.png",
                        "JsonRPCAction": {
                            'method': 'change_setting',
                            'parameters': ['new_download_loc', index],
                            'dontHideAfterAction': False
                        }
                    })
                    
                return result
            
            elif _query[0] == 'doc_install_search':
                return [{
                    "Title": f"All",
                    "SubTitle": f"official, user contributed, cheat sheets",
                    "IcoPath": "./Images/cog-solid.png",
                    "JsonRPCAction": {
                        'method': 'change_setting',
                        'parameters': ['doc_search_install', 3],
                        'dontHideAfterAction': False
                    }
                },{
                    "Title": f"official, user contributed",
                    "SubTitle": f"official, user contributed",
                    "IcoPath": "./Images/cog-solid.png",
                    "JsonRPCAction": {
                        'method': 'change_setting',
                        'parameters': ['doc_search_install', 2],
                        'dontHideAfterAction': False
                    }
                },{
                    "Title": f"only official",
                    "SubTitle": f"official",
                    "IcoPath": "./Images/cog-solid.png",
                    "JsonRPCAction": {
                        'method': 'change_setting',
                        'parameters': ['doc_search_install', 1],
                        'dontHideAfterAction': False
                    }
                }
                ]
            
            elif _query[0] == 'default_doc_open':
                return [{
                    "Title": f"default webbrowser",
                    "SubTitle": f"open in default webbrowser",
                    "IcoPath": "./Images/cog-solid.png",
                    "JsonRPCAction": {
                        'method': 'change_setting',
                        'parameters': ['doc_open_method', 'web'],
                        'dontHideAfterAction': False
                    }
                },{
                    "Title": f"zeal or velocity",
                    "SubTitle": f"open in zeal or velocity",
                    "IcoPath": "./Images/cog-solid.png",
                    "JsonRPCAction": {
                        'method': 'change_setting',
                        'parameters': ['doc_open_method', 'dash'],
                        'dontHideAfterAction': False
                    }
                }]
            
            elif _query[0] == 'alias':
                if len(_query[1:]):
                    if _query[1] == 'add':
                        def valid(txt):
                            if len(txt.split(':')) != 2:
                                return False
                            if ' ' in txt or txt[-1] == ':':
                                return False
                            return True
                        
                        txt = ' '.join(_query[2:])
                        a = txt.split(':')
                        return [{
                            "Title": f"{a[0]} = {a[1]}" if valid(txt) else 'invalid format',
                            "SubTitle": f"format:= alias:name",
                            "IcoPath": "./Images/cog-solid.png",
                            "JsonRPCAction": {
                                'method': 'add_alias' if valid(txt) else '',
                                'parameters': [*(txt.split(':'))],
                                'dontHideAfterAction': False
                            }
                        }]
                    
                    elif _query[1] == 'remove':
                        result = []
                        for alias in self.settings['alias']:
                            result.append({
                                "Title": f"{alias}",
                                "SubTitle": f"{self.settings['alias'][alias]}",
                                "IcoPath": "./Images/cog-solid.png",
                                "JsonRPCAction": {
                                    'method': 'remove_alias',
                                    'parameters': [alias],
                                    'dontHideAfterAction': False
                            }
                            })
                        return result
                
                return [{
                        "Title": "add docset location",
                        "SubTitle": "ADD",
                        "IcoPath": "./Images/cog-solid.png",
                        "JsonRPCAction": {
                            'method': '_set_query',
                            'parameters': ["settings alias add"],
                            'dontHideAfterAction': True
                        }
                    },{
                        "Title": "remove docset locations",
                        "SubTitle": "REMOVE",
                        "IcoPath": "./Images/cog-solid.png",
                        "JsonRPCAction": {
                            'method': '_set_query',
                            'parameters': ["settings alias remove"],
                            'dontHideAfterAction': True
                        }
                    }
                ]
        else:
            doc_paths = {
                "Title": "Manage docset locations",
                "SubTitle": "ADD, REMOVE",
                "IcoPath": "./Images/cog-solid.png",
                "JsonRPCAction": {
                    'method': '_set_query',
                    'parameters': ["settings doc_path"],
                    'dontHideAfterAction': True
                }
            }
            default_install_loc = {
                "Title": "set default docset install location",
                "SubTitle": "",
                "IcoPath": "./Images/cog-solid.png",
                "JsonRPCAction": {
                    'method': '_set_query',
                    'parameters': ["settings default_install_loc"],
                    'dontHideAfterAction': True
                }
            }
            doc_install_search = {
                "Title": "Manage what type of docs search when install",
                "SubTitle": "ALL, official & user contributed, official only",
                "IcoPath": "./Images/cog-solid.png",
                "JsonRPCAction": {
                    'method': '_set_query',
                    'parameters': ["settings doc_install_search"],
                    'dontHideAfterAction': True
                }
            }
            default_doc_open = {
                "Title": "Manage default document open method",
                "SubTitle": "Webbrowser, zeal or velocity",
                "IcoPath": "./Images/cog-solid.png",
                "JsonRPCAction": {
                    'method': '_set_query',
                    'parameters': ["settings default_doc_open"],
                    'dontHideAfterAction': True
                }
            }
            alias = {
                "Title": "Manage aliases",
                "SubTitle": "ADD, REMOVE",
                "IcoPath": "./Images/cog-solid.png",
                "JsonRPCAction": {
                    'method': '_set_query',
                    'parameters': ["settings alias"],
                    'dontHideAfterAction': True
                }
            }
            
            return [doc_paths, default_install_loc, doc_install_search, default_doc_open, alias]
    
    def add_doc_path(self, path):
        paths = self.settings['doc_paths']
        paths.append(path)
        self.change_setting("doc_paths", paths)
        
    def remove_doc_path(self, path):
        with open('./settings.json', 'r') as f:
            paths = json.load(f)['doc_paths']
        paths.remove(path)
        log(path, paths)
        self.change_setting("doc_paths", paths)
        
    def add_alias(self, _alias, name):
        alias = self.settings['alias']
        alias.update({_alias: name})
        self.change_setting("alias", alias)
    
    def remove_alias(self, _alias):
        alias = self.settings['alias']
        alias.pop(_alias)
        self.change_setting("alias", alias)
    
    def main_query(self, _query):
        _query = ' '.join(_query).lower(), '_'.join(_query).lower()
        results = []

        for i in self.docs:
            if _query[0] in i['name'].lower() or _query[1] in i['name'].lower():
                results.append({
                    "Title": f"{i['name']}",
                    "SubTitle": "",
                    "IcoPath": f"{i['IcoPath']}",
                    "JsonRPCAction": {
                        'method': '_set_query',
                        'parameters': [f"{i['name']}"],
                        'dontHideAfterAction': True
                    }
                })
        results.sort(key = lambda x: 2 if x['Title'].lower().startswith(_query[0]) or x['Title'].lower().startswith(_query[1])
                                else 1 if x['Title'].lower().endswith(_query[0]) or x['Title'].lower().endswith(_query[1]) 
                                else 0, 
                    reverse=True)
        
        for i in self.options:
            if i.startswith(_query[0]):
                results.insert(0,{
                    "Title": f"{i}",
                    "SubTitle": "option",
                    "IcoPath": f"./Images/cog-solid.png",
                    "ContextData": "ctxData",
                    "JsonRPCAction": {
                        'method': '_set_query',
                        'parameters': [f"{i}"],
                        'dontHideAfterAction': True
                    }
                })
                
        return results[:50]
                    
    def _set_query(self, _query):
        with open('plugin.json', 'r') as f:
            key = json.load(f)['ActionKeyword']
            
        WoxAPI.change_query(f'{key} {_query} ')
        
    def change_setting(self, key, value):
        with open('./settings.json', 'r') as f:
            settings = json.load(f)
            settings[key] = value

        with open('./settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
        
    def _doc_search(self, doc_name, _query):
        for i in self.docs:
            if doc_name == i['name']:
                doc_path = i['path']
                icon_path = i['IcoPath']
                break

        db_path = os.path.join(doc_path, r"Contents\Resources\docSet.dsidx")
        if os.path.exists(db_path):
            return doc_search(db_path, _query, icon_path, doc_name)

    def doc_open(*args):
        ## found a bug :- expected 2 arguments but 3 given
        path = args[-2]
        search = args[-1]

        with open('./settings.json', 'r') as f:
            method = json.load(f)['doc_open_method']

        if method == "web":
            import webbrowser

            #### create a tmp html doc with redirection to target. (because there is no way to open URLs with bookmarks('#'))
            tmp_html(path)
            
            webbrowser.open_new("file:///" + os.path.abspath("./tmp/redirect.html"))

        elif method == "dash":
            os.startfile(f"Dash://{search}")
            
        
if __name__ == "__main__":
    try:
        Doc()
    except Exception as e:
        log('error:- ' + e)
        raise e
    
