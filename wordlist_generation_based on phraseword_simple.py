import itertools
import string

def generate_wordlist_variations(wordphrase):
    '''
    The output formula will be like this:
    {character}{special_char_start}{wordphrase}{i:02d}{special_char_end}
    where
    {character}: Represents a letter from the lowercase or uppercase alphabet.
    {special_char_start}: Represents a special character from the defined set of special characters at the beginning of the variation.
    {wordphrase}: Represents the wordphrase entered by the user.
    {i:02d}: Represents a two-digit number starting from 00 and incrementing up to 99. It is zero-padded to ensure a two-digit format.
    {special_char_end}: Represents a special character from the defined set of special characters at the end of the variation.

    Each variation follows this pattern, combining characters, special characters, and the user-entered wordphrase in different combinations.
    '''

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    special_chars = "!@#$%^&*><,.';:"
    variations = []

    for char in itertools.chain(lowercase, uppercase):
        for special_char_start in special_chars:
            for special_char_end in special_chars:
                for i in range(0, 100):
                    variation = f"{char}{special_char_start}{wordphrase}{i:02d}{special_char_end}"
                    variations.append(variation)

    return variations

# Ask the user for the wordphrase
wordphrase = input("Enter a wordphrase: ")

variations = generate_wordlist_variations(wordphrase)

# Remove duplicates and sort variations
variations = list(set(variations))
variations.sort()

# Save the variations to a text file
output_file = "wordlist_variations.txt"
with open(output_file, "w") as file:
    for variation in variations:
        file.write(variation + "\n")

print("Wordlist variations saved to", output_file)
