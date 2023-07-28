

import bcrypt
import time
import os
from threading import Thread
import queue


#print("=" * 70 + "\n")
#print("The running number of threads created is:", os.getenv('NUM_PROCESSES'))
def crack_bcrypt_chunk(q, target_hash, password_found):
    while not q.empty():
        if password_found[0]:
            return

        password = q.get()
        encoded_password = password.encode('utf-8')
        candidate_hash = bcrypt.hashpw(encoded_password, target_hash.encode('utf-8'))
        if candidate_hash.decode() == target_hash:
            password_found[0] = True
            print("=" * 50 + "\n")
            print("Password cracked successfully!")
            print("Cracked password:", password)
            return

def main():
    wordlist_chunk = os.getenv('INPUT_FILE')  # Input file path
    target_hash = os.getenv('TARGET_HASH')
    num_threads = int(os.getenv('NUM_PROCESSES', '1'))  # Read NUM_PROCESSES environment variable

    # Initialize the queue
    q = queue.Queue()

    # Read the wordlist chunk
    with open(wordlist_chunk, 'r') as f:
        passwords = [line.strip() for line in f if line.strip()]

    # Put passwords into the queue
    for password in passwords:
        q.put(password)
    #num_passwords = len(passwords)
    #print("Number of passwords loaded into the queue:", num_passwords)

    # Create shared variable for password found flag
    password_found = [False]

    # Create and start threads
    threads = []
    for _ in range(num_threads):
        thread = Thread(target=crack_bcrypt_chunk, args=(q, target_hash, password_found))
        thread.start()
        threads.append(thread)

    # Measure total execution time
    start_time = time.time()

    # Wait for all threads to finish or password found
    for thread in threads:
        thread.join()
    # Check if password was found
    if not password_found[0]:
        print("=" * 50 + "\n")
        print("Password not found in the wordlist.")
    end_time = time.time()
    total_time = end_time - start_time
    print("Total execution time:", total_time, "seconds" + "\n")
    print("=" * 50)



if __name__ == "__main__":
    main()


