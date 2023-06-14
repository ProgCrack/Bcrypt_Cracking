import bcrypt
import string

def clean_salt(salt):
    printable = set(string.printable)
    cleaned_salt = ''.join(filter(lambda x: x in printable, salt))
    print("Cleaned Salt:", cleaned_salt)
    return cleaned_salt

def crack_bcrypt(target_hash, salt, wordlist, cost_factor):
    # Open the wordlist file and read all the passwords, stripping whitespace
    with open(wordlist, 'r') as f:
        passwords = [line.strip() for line in f if line.strip()]

    print("Passwords:", passwords)
    print("Number of Passwords:", len(passwords))

    # Iterate over each password in the wordlist
    for password in passwords:
        cleaned_salt = clean_salt(salt)
        encoded_password = password.encode('utf-8')
        formatted_salt = f"$2b${cost_factor}${cleaned_salt}"
        encoded_salt = formatted_salt.encode('utf-8')
        print("Encoded Password:", encoded_password)
        print("Encoded Salt:", encoded_salt)
        print("Target Hash (encoded):", target_hash.encode('utf-8'))
        
        # Compute the bcrypt hash of the encoded password using the encoded salt
        candidate_hash = bcrypt.hashpw(encoded_password, encoded_salt)
        print("Candidate Hash:", candidate_hash)
        
        # Check if the last part of the candidate hash matches the last part of the target hash
        if candidate_hash.decode().split('$')[-1] == target_hash.split('$')[-1]:
            return password

    return None

def main():
    # Prompt the user to enter the target file name, wordlist file name, and cost factor
    target_file = input("Enter the file name containing the target hash and salt: ")
    wordlist_file = input("Enter the file name of the wordlist: ")
    cost_factor = int(input("Enter the cost factor (number of rounds): "))

    # Open the target file and extract the target hash and salt
    with open(target_file, 'r') as f:
        target_hash, salt = f.read().split(',')
        salt = salt.strip()

    print("Salt:", salt)
    print("Target Hash:", target_hash)
    
    # Call the crack_bcrypt function with the target hash, salt, wordlist file name, and cost factor
    cracked_password = crack_bcrypt(target_hash, salt, wordlist_file, cost_factor)

    if cracked_password:
        print("Password cracked successfully!")
        print("Cracked password:", cracked_password)
    else:
        print("Password not found in the wordlist.")

if __name__ == "__main__":
    main()
