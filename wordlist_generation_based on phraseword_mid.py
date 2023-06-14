import itertools
import string

def generate_wordlist_variations(wordphrase):
    '''
    The output formula will be like this:
    {character}{special_char_start}{word_variation[0].upper()}{word_variation[1:].lower()}{i:02d}{special_char_end}
    where
    {character}: Represents a letter from the lowercase or uppercase alphabet.
    {special_char_start}: Represents a special character from the defined set of special characters at the beginning of the variation.
    {word_variation[0].upper()}: Represents the first character of the word_variation in uppercase.
    {word_variation[1:].lower()}: Represents the remaining characters of the word_variation in lowercase.
    {i:02d}: Represents a two-digit number starting from 01 and incrementing up to 99. It is zero-padded to ensure a two-digit format.
    {special_char_end}: Represents a special character from the defined set of special characters at the end of the variation.

    Each variation follows this pattern, combining characters, special characters, and the user-entered wordphrase in different combinations.
    '''
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    special_chars = "!@#$%^&*><,.';:"
    variations = set()

    if wordphrase.islower():
        word_variations = [wordphrase]
    elif wordphrase.isupper():
        word_variations = [wordphrase.lower()]
    else:
        word_variations = [wordphrase, wordphrase.lower()]

    for char in itertools.chain(lowercase, uppercase):
        for special_char_start in special_chars:
            for special_char_end in special_chars:
                for word_variation in word_variations:
                    for i in range(1, 100):
                        variation = f"{char}{special_char_start}{word_variation[0].upper()}{word_variation[1:].lower()}{i:02d}{special_char_end}"
                        variations.add(variation)

    return variations

# Ask the user for the wordphrase
wordphrase = input("Enter a wordphrase: ")

variations = generate_wordlist_variations(wordphrase)

# Include a variation of the wordphrase itself
variations.add(wordphrase)
variations.add(wordphrase.lower())
variations.add(wordphrase.capitalize())

# Add variations with mixed cases for the wordphrase
for word_variation in list(variations):
    variations.add(word_variation.swapcase())

# Save the variations to a text file
output_file = "wordlist_variations.txt"
with open(output_file, "w") as file:
    for variation in variations:
        file.write(variation + "\n")

print("Wordlist variations saved to", output_file)
