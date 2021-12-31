import sys
import os
from urllib.request import urlopen
import ssl
import tarfile
from utils import log


def download(url, path):
    certificate = ssl._create_unverified_context()

    with urlopen(url, context=certificate) as _url, open(path, 'wb') as file:
        size = float(_url.getheader('Content-Length'))
        print(f'{size/1024/1024:.3f} MB')
        
        down = 0
        perc = 0
        print(f"[{'-'*50}] {perc:0>2d}% {down/1024:\u0020>4.0f} KB", end='\r')
        
        while True:
            chunk = _url.read(1024)
            down += 1024
            perc = int(down/size*100)
            d = str(down//1024).ljust(4,' ') + ' KB' if down < 1024**2 * 8 else str(down/1024/1024)[:5] + ' MB'
            
            print(f"[{'='*(perc//2):-<50s}] {perc:0>2d}% {d}", end='\r')
            
            
            if chunk:
                file.write(chunk)
            else:
                break
        
        print(f"[{'='*50}] {perc:0>2d}% {down/1024:\u0020>4.0f} KB")


def extract(path):
    with tarfile.open(path) as archive:
        archive.extractall(os.path.dirname(path))
        
    os.remove(path)


if __name__ == "__main__":
    url = sys.argv[1]
    save_to = sys.argv[2]
    
    print(f'URL:- {url}')
    print(f'save_to: {save_to}')
    print()
    print('#'*50)
    print('downloading', end=' ')
    
    download(url, save_to)
    
    print('download finished')
    print('#'*50)
    
    print()
    print('extracting file')
    
    try:
        extract(save_to)
    except Exception as e:log(e)
    
    print('extracting file complete')
    print()
    input('press enter to continue')
    