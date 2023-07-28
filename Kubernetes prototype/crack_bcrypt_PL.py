import bcrypt
import time
import multiprocessing
import os


#print("=" * 70 + "\n")
#print("The running number of processes is:", os.getenv('NUM_PROCESSES'))
# Function to crack bcrypt hashes
def crack_bcrypt_chunk(passwords, target_hash, stop_signal, lock, start_time):
    for line_number, password in enumerate(passwords, start=1):
        if stop_signal.value:
            return

        encoded_password = password.encode('utf-8')
        if bcrypt.checkpw(encoded_password, target_hash.encode('utf-8')):
            with lock:
                stop_signal.value = 1
                #total_time = time.time() - start_time.value
                print("=" * 50 + "\n")
                print("Password cracked successfully!")
                print("Cracked password:", password)
                #print("Line number:", line_number)
                #print("Total processing time:", total_time, "seconds")
                return

# Main function
def main():
    wordlist_file = os.getenv('INPUT_FILE')  # Input file path
    target_hash = os.getenv('TARGET_HASH')
    num_processes = int(os.getenv('NUM_PROCESSES', '1'))  # Read NUM_PROCESSES environment variable

    # Read the wordlist file
    with open(wordlist_file, 'r') as f:
        passwords = [line.strip() for line in f if line.strip()]

    # Split the wordlist into chunks
    chunk_size = len(passwords) // num_processes
    wordlist_chunks = [passwords[i:i+chunk_size] for i in range(0, len(passwords), chunk_size)]

    # Create shared variables
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    stop_signal = manager.Value('i', 0)
    start_time = manager.Value('d', time.time())

    # Create and start processes
    processes = []
    for chunk in wordlist_chunks:
        p = multiprocessing.Process(target=crack_bcrypt_chunk,
                                    args=(chunk, target_hash, stop_signal, lock, start_time))
        processes.append(p)
        p.start()

    # Wait for all processes to finish
    for p in processes:
        p.join()

    # Check if password is found
    if stop_signal.value == 0:
        print("=" * 50 + "\n")
        print("Password not found in the wordlist.")

    # Print total processing time
    total_time = time.time() - start_time.value
    print("Total processing time:", total_time, "seconds" + "\n")
    print("=" * 50)


if __name__ == "__main__":
    main()

