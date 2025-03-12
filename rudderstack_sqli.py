"""
Author: Aleksa Zaztezalo
Date: May 2025
Description: SQLi to RCE in Rudderstack. It get's the flag from /flag.txt.
"""

def gen_sqli(ip, port):
    """
    Takes two strings, ip and port, and generates an sqli payload. The SQLi
    port sends a request to containing tht tontents of /flag.txt to http://ip:port.
    """
    pass

def send_request(url, proxy, ip, port):
    """
    Takes a targert url, url, a proxy url, and the ip and port of a
    reverse shell listener. Sends a SQLi request.
    """
    pass

def start_server(port):
    """
    Opens an http simple server on the specified port.
    """
    pass
    
def main():
    pass

if __name__ == "__main__":
    pass