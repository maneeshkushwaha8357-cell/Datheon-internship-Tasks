"""Console Hangman game for the Datheon Python Programming Internship."""

import random

MAX_MISSES = 6

WORDS = [
    "python", "analytics", "dataset", "algorithm", "variable",
    "function", "database", "notebook", "science", "developer",
    "computer", "programming", "statistics", "visualization",
]

HANGMAN_STAGES = [
    r"""
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    /    |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    / \  |
         |
    =========""",
]


def masked_word(word: str, guessed_letters: set[str]) -> str:
    """Return guessed letters and underscores separated by spaces."""
    return " ".join(letter if letter in guessed_letters else "_" for letter in word)


def get_letter() -> str:
    """Read and validate one letter from the player."""
    while True:
        guess = input("Guess one letter: ").strip().lower()
        if len(guess) == 1 and guess.isalpha() and guess.isascii():
            return guess
        print("Please enter one English letter (a-z).")


def play_round(word: str | None = None) -> bool:
    """Play one round. Return True when the player wins."""
    secret = (word or random.choice(WORDS)).lower()
    guessed: set[str] = set()
    misses = 0

    print("\n=== HANGMAN ===")
    print(f"The word has {len(secret)} letters. You have {MAX_MISSES} incorrect guesses.")

    while misses < MAX_MISSES:
        print(HANGMAN_STAGES[misses])
        print(f"\nWord: {masked_word(secret, guessed)}")
        print(f"Incorrect guesses remaining: {MAX_MISSES - misses}")
        if guessed:
            print("Guessed letters:", ", ".join(sorted(guessed)))

        guess = get_letter()
        if guess in guessed:
            print(f"You already guessed '{guess}'. Try a different letter.")
            continue

        guessed.add(guess)
        if guess in secret:
            print("Correct!")
            if all(letter in guessed for letter in secret):
                print(f"\nYou won! The word was '{secret}'.")
                return True
        else:
            misses += 1
            print("That letter is not in the word.")

    print(HANGMAN_STAGES[MAX_MISSES])
    print(f"\nGame over. The word was '{secret}'.")
    return False


def main() -> None:
    """Run rounds until the player chooses to stop."""
    wins = rounds = 0
    while True:
        won = play_round()
        rounds += 1
        wins += int(won)
        print(f"Session score: {wins}/{rounds} wins.")
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again not in {"y", "yes"}:
            print("Thanks for playing. Goodbye!")
            break


if __name__ == "__main__":
    main()
