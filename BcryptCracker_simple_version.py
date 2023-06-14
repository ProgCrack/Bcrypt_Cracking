import bcrypt
import string

def crack_bcrypt(target_hash, wordlist):
    # Extract the cost factor and salt from the target hash
    cost_factor = target_hash[4:6]
    salt = target_hash[7:29]  # Assuming the salt length is fixed at 22 characters

    print("Cost Factor:", cost_factor)
    print("Salt:", salt)
    print("Target Hash:", target_hash)

    # Open the wordlist file and read all the passwords, stripping whitespace
    with open(wordlist, 'r') as f:
        passwords = [line.strip() for line in f if line.strip()]
    print("Number of Password Candidates:", len(passwords))
    # Use the following line for troubleshooting
    #print("Passwords:", passwords)
    

    # Iterate over each password in the wordlist
    for password in passwords:
        encoded_password = password.encode('utf-8')
        full_salt = "$2b$" + cost_factor + "$" + salt
        encoded_salt = full_salt.encode('utf-8')
        
        # Use the following lines for troubleshooting
        #print("Encoded Password:", encoded_password)
        #print("Encoded Salt:", encoded_salt)
        #print("Target Hash (encoded):", target_hash.encode('utf-8'))

        # Compute the bcrypt hash of the encoded password using the encoded salt
        candidate_hash = bcrypt.hashpw(encoded_password, encoded_salt)
        
        # Use the following line for troubleshooting
        #print("Candidate Hash:", candidate_hash) 

        # Check if the candidate hash matches the target hash
        if candidate_hash.decode() == target_hash:
            return password

    return None

def main():
    # Prompt the user to enter the victim's hash and wordlist file name
    target_hash = input("Enter victim's hash: ")
    wordlist_file = input("Enter the file name of the wordlist: ")

    # Call the crack_bcrypt function with the target hash and wordlist file name
    cracked_password = crack_bcrypt(target_hash, wordlist_file)

    if cracked_password:
        print("Password cracked successfully!")
        print("Cracked password:", cracked_password)
    else:
        print("Password not found in the wordlist.")

if __name__ == "__main__":
    main()
