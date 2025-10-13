name = input("What is your name? ")
print("Hello,", name + "!")

name = input("What is your name? ")
if name.lower() == "biondi":
    print("Wow, that’s my teacher’s name too!")
else:
    print("Nice to meet you,", name + "!")

import random

greetings = ["Hello", "Hi", "Hey", "Nice to see you", "What's up", "Howdy", 
             "How's it going", "How do you do"]
name = input("Your name: ")
print(random.choice(greetings), name + "!")

color = input("What's your favorite color? ")
print(f"Really? I like {color} too! Great minds think alike.")

print("Let's play a quick quiz!")
answer = input("What language are we learning today? ").lower()

if answer == "python":
    print("Correct! 🐍 You’re a coding genius!")
else:
    print("Not quite... It's Python! Keep going!")

import random

number = random.randint(1, 10)
guess = int(input("Guess a number between 1 and 10: "))

if guess == number:
    print("Perfect! You guessed it right!")
elif guess > number:
    print("Too high! The number was", number)
else:
    print("Too low! The number was", number)
