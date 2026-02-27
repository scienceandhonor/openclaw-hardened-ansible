#!/usr/bin/env python3
"""Daily stoic quote at 7:45 Berlin time."""

import json
import os
import sys
from datetime import datetime

QUOTES = [
    "The happiness of your life depends upon the quality of your thoughts. — MARCUS AURELIUS",
    "We suffer more often in imagination than in reality. — SENECA",
    "It's not what happens to you, but how you react to it that matters. — EPICTETUS",
    "The best revenge is to be unlike him who performed the injury. — MARCUS AURELIUS",
    "Waste no more time arguing about what a good man should be. Be one. — MARCUS AURELIUS",
    "He who fears death will never do anything worthy of a man who is alive. — SENECA",
    "No man is free who is not master of himself. — EPICTETUS",
    "Very little is needed to make a happy life; it is all within yourself, in your way of thinking. — MARCUS AURELIUS",
    "Difficulties strengthen the mind, as labor does the body. — SENECA",
    "Make the best use of what is in your power, and take the rest as it happens. — EPICTETUS",
    "The soul becomes dyed with the color of its thoughts. — MARCUS AURELIUS",
    "As is a tale, so is life: not how long it is, but how good it is, is what matters. — SENECA",
    "First say to yourself what you would be; and then do what you have to do. — EPICTETUS",
    "When you arise in the morning think of what a privilege it is to be alive. — MARCUS AURELIUS",
    "Luck is what happens when preparation meets opportunity. — SENECA",
    "If it is not right, do not do it; if it is not true, do not say it. — MARCUS AURELIUS",
    "He suffers more than he who is in want, who complains. — SENECA",
    "Man is not worried by real problems so much as by his imagined anxieties. — EPICTETUS",
    "You have power over your mind — not outside events. Realize this, and you will find strength. — MARCUS AURELIUS",
    "It is not that we have a short time to live, but that we waste a lot of it. — SENECA",
    "Wealth consists not in having great possessions, but in having few wants. — EPICTETUS",
    "Never let the future disturb you. You will meet it, if you have to, with the same weapons of reason. — MARCUS AURELIUS",
    "Hang on to your youthful enthusiasms — you'll be able to use them better when you're older. — SENECA",
    "Freedom is the only worthy goal in life. — EPICTETUS",
    "Look well into thyself; there is a source of strength which will always spring up if thou wilt always look. — MARCUS AURELIUS",
    "A gem cannot be polished without friction, nor a man perfected without trials. — SENECA",
    "Any person capable of angering you becomes your master. — EPICTETUS",
    "The object of life is not to be on the side of the majority, but to escape finding oneself in the ranks of the insane. — MARCUS AURELIUS",
    "True happiness is to enjoy the present, without anxious dependence upon the future. — SENECA",
    "Begin at once to live, and count each separate day as a separate life. — SENECA",
    "He is a wise man who does not grieve for the things which he has not, but rejoices for those which he has. — EPICTETUS",
    "Accept the things to which fate binds you, and love the people with whom fate brings you together. — MARCUS AURELIUS",
    "While we are postponing, life speeds by. — SENECA",
    "No one can hurt you without your consent. — GANDHI (influenced by Stoicism)",
    "If you are distressed by anything external, the pain is not due to the thing itself, but to your estimate of it. — EPICTETUS",
    "How much time he saves who does not look to see what his neighbor says or does or thinks. — MARCUS AURELIUS",
    "Religion is regarded by the common people as true, by the wise as false, and by rulers as useful. — SENECA",
    "Demand not that events should happen as you wish; but wish them to happen as they do happen. — EPICTETUS",
    "Everything we hear is an opinion, not a fact. Everything we see is a perspective, not the truth. — MARCUS AURELIUS",
    "Throw me to the wolves and I will return leading the pack. — SENECA",
    "We are more often frightened than hurt; and we suffer more from imagination than from reality. — SENECA",
    "Caretake this moment. Immerse yourself in its particulars. — EPICTETUS",
    "Reject your sense of injury and the injury itself disappears. — MARCUS AURELIUS",
    "I have often wondered how it is that every man loves himself more than all the rest of men. — MARCUS AURELIUS",
    "It is not the man who has too little, but the man who craves more, that is poor. — SENECA",
    "Circumstances don't make the man, they only reveal him to himself. — EPICTETUS",
    "When you wake up, think: What a privilege! What a gift! — MARCUS AURELIUS",
    "Difficulties come when you don't pay attention to life's whisper. — EPICTETUS",
    "He suffers twice who thinks beforehand of his pain. — SENECA",
    "How ridiculous and how strange to be surprised at anything which happens in life. — MARCUS AURELIUS",
    "Associate with people who are likely to improve you. — SENECA",
    "First learn the meaning of what you say, and then speak. — EPICTETUS",
    "The key is to keep company only with people who uplift you. — MARCUS AURELIUS",
    "No person has the power to have everything they want, but it is in their power not to want what they don't have. — SENECA",
    "Be tolerant with others and strict with yourself. — MARCUS AURELIUS",
    "Think of the life you have lived until now as over and done with. — MARCUS AURELIUS",
    "Our anxiety does not come from thinking about the future, but from wanting to control it. — SENECA",
    "Nature does not hurry, yet everything is accomplished. — LAO TZU (Stoic influence)",
    "Keep your attention focused entirely on what is truly your own concern. — MARCUS AURELIUS",
    "You could leave life right now. Let that determine what you do and say and think. — MARCUS AURELIUS",
    "If you aren't willing to have a bad day, you'll never have a good life. — SENECA",
    "It's not what happens to you, but how you handle it. — EPICTETUS",
    "The best answer to anger is silence. — MARCUS AURELIUS",
    "He who is brave is free. — SENECA",
    "What we do now echoes in eternity. — MARCUS AURELIUS",
    "Don't explain your philosophy. Embody it. — EPICTETUS",
    "We are time's subjects, and time bids be gone. — MARCUS AURELIUS",
    "To be free of passion and yet full of love. — MARCUS AURELIUS",
    "The impediment to action advances action. What stands in the way becomes the way. — MARCUS AURELIUS",
    "Do not act as if you were going to live ten thousand years. — MARCUS AURELIUS",
    "The man who has done his best shall not be injured by the results. — MARCUS AURELIUS",
    "Loss is nothing else but change, and change is Nature's delight. — MARCUS AURELIUS",
    "A man's worth is no greater than his ambitions. — MARCUS AURELIUS",
    "Never be afraid to raise your voice for honesty and truth and compassion. — MARCUS AURELIUS",
    "Here is a rule to remember in future, when anything tempts you to feel bitter. — MARCUS AURELIUS",
    "If it is not right do not do it; if it is not true do not say it. — MARCUS AURELIUS",
    "The universe is change; our life is what our thoughts make it. — MARCUS AURELIUS",
    "That which is really beautiful has no need of anything. — MARCUS AURELIUS",
    "Be strict with yourself and lenient with others. — MARCUS AURELIUS",
    "When you are offended at any man's fault, turn to yourself and study your own failings. — MARCUS AURELIUS",
    "The art of living is more like wrestling than dancing. — MARCUS AURELIUS",
    "How much more grievous are the consequences of anger than the causes of it. — MARCUS AURELIUS",
    "The opinion of ten thousand men is of no value if none of them know anything about the subject. — MARCUS AURELIUS",
    "Accept whatever comes to you woven in the pattern of your destiny. — MARCUS AURELIUS",
    "The best revenge is not to be like your enemy. — MARCUS AURELIUS",
    "What we do now echoes in eternity. — MARCUS AURELIUS",
    "We must take a higher view of all things. — MARCUS AURELIUS",
    "Do every act of your life as though it were your very last. — MARCUS AURELIUS",
    "No man is happy who does not think himself so. — MARCUS AURELIUS",
    "The things you think about determine the quality of your mind. — MARCUS AURELIUS",
    "Very little is necessary to live a happy life. — MARCUS AURELIUS",
]

OPENCLAW_HOME = os.environ.get('OPENCLAW_HOME', os.path.expanduser('~/.openclaw'))

def get_quote():
    day_of_year = datetime.now().timetuple().tm_yday
    return QUOTES[(day_of_year - 1) % len(QUOTES)]

def main():
    quote = get_quote()
    msg = f"☀️ *Daily Stoic*\n\n_{quote}_\n\n— via The Daily Stoic"
    
    # Write to a file for the cron job to pick up
    output_path = os.path.join(OPENCLAW_HOME, 'stoic-quote.json')
    with open(output_path, 'w') as f:
        json.dump({'message': msg}, f)
    
    print(msg)

if __name__ == '__main__':
    main()
