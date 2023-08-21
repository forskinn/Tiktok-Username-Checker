import os
import threading
import requests


USERNAME_FILE = 'usernames.txt' # auto sets as the user list - to check from
PROXY_TIMEOUT = 10000 # change the timeout if you have better proxies or when you start checking, it may cause it to stop and not load 100%
WORKING_FILE = 'working.txt' # outputs possible available users to txt (if shows working and doesn't actually work then that @ is banned)
lock = threading.Lock()  # Lock for thread-safe writing

def check_username_availability(username, proxy, found_usernames):
    url = f'https://www.tiktok.com/@{username}'
    proxies = {'http': proxy, 'https': proxy} # change 'proxytype' if using socks
    
    try:
        response = requests.get(url, proxies=proxies, timeout=PROXY_TIMEOUT)
        if response.status_code == 404:
            print(f"Username '{username}' is available.")
            with lock:
                found_usernames.add(username)
                with open(WORKING_FILE, 'a') as f:
                    f.write(username + '\n')
        else:
            print(f"Username '{username}' is not available.")
    except requests.exceptions.RequestException:
        print(f"Error checking '{username}' with proxy '{proxy}'.")

def process_usernames(usernames, proxy_list):
    found_usernames = set()
    
    threads = []
    for username in usernames:
        for proxy in proxy_list:
            thread = threading.Thread(target=check_username_availability, args=(username, proxy.strip(), found_usernames))
            threads.append(thread)
            thread.start()
    
    for thread in threads:
        thread.join()

def main():
    if not os.path.isfile(USERNAME_FILE):
        print(f"Username file '{USERNAME_FILE}' not found.")
        return
    
    with open(USERNAME_FILE, 'r') as f:
        usernames = f.read().splitlines()
    
    proxy_file_path = input("Enter the path to the proxy list file on your desktop: ") # make sure the proxy list and *.py are on desktop
    if not os.path.isfile(proxy_file_path):
        print(f"Proxy list file '{proxy_file_path}' not found.")
        return
    
    with open(proxy_file_path, 'r') as proxy_file:
        proxy_list = proxy_file.read().splitlines()
    
    num_threads = int(input("Enter the number of threads to use: ")) # use 1-50 threads, its decently fast regardless. If you have good proxies.
    
    usernames_per_thread = len(usernames) // num_threads
    threads = []
    
    for i in range(num_threads):
        start_idx = i * usernames_per_thread
        end_idx = start_idx + usernames_per_thread if i < num_threads - 1 else len(usernames)
        thread_usernames = usernames[start_idx:end_idx]
        thread = threading.Thread(target=process_usernames, args=(thread_usernames, proxy_list))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print("Username availability check completed.")

if __name__ == '__main__':
    main()
