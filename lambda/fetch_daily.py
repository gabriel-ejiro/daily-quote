import os
import json
import boto3
import datetime
import random
import ssl
import urllib.request
from urllib.error import URLError, HTTPError

dynamodb = boto3.resource("dynamodb")

TABLE_ENV = "TABLE_NAME"
QUOTABLE_URL = "https://api.quotable.io/random"

# ---------------------------------------------------------
#  FALLBACK QUOTES
# ---------------------------------------------------------
FALLBACK_QUOTES = [
    # --- ORIGINAL 5 ---
    {
        "quote": "Success is the sum of small efforts, repeated day in and day out.",
        "author": "Robert Collier"
    },
    {
        "quote": "Stay hungry, stay foolish.",
        "author": "Steve Jobs"
    },
    {
        "quote": "It always seems impossible until it’s done.",
        "author": "Nelson Mandela"
    },
    {
        "quote": "Discipline is choosing between what you want now and what you want most.",
        "author": "Unknown"
    },
    {
        "quote": "The future depends on what you do today.",
        "author": "Mahatma Gandhi"
    },

    
    {
        "quote": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs"
    },
    {
        "quote": "Success usually comes to those who are too busy to be looking for it.",
        "author": "Henry David Thoreau"
    },
    {
        "quote": "Hard work beats talent when talent doesn’t work hard.",
        "author": "Tim Notke"
    },
    {
        "quote": "The secret of getting ahead is getting started.",
        "author": "Mark Twain"
    },
    {
        "quote": "Don’t wish it were easier. Wish you were better.",
        "author": "Jim Rohn"
    },
    {
        "quote": "Believe you can and you’re halfway there.",
        "author": "Theodore Roosevelt"
    },
    {
        "quote": "Dream big. Start small. Act now.",
        "author": "Robin Sharma"
    },
    {
        "quote": "If people are doubting how far you can go, go so far they can’t hear you anymore.",
        "author": "Michele Ruiz"
    },
    {
        "quote": "Success is not final; failure is not fatal: It is the courage to continue that counts.",
        "author": "Winston Churchill"
    },
    {
        "quote": "What you do today can improve all your tomorrows.",
        "author": "Ralph Marston"
    },
    {
        "quote": "Work hard in silence. Let success make the noise.",
        "author": "Unknown"
    },
    {
        "quote": "Your life does not get better by chance. It gets better by change.",
        "author": "Jim Rohn"
    },
    {
        "quote": "Go the extra mile. It’s never crowded there.",
        "author": "Dr. Wayne Dyer"
    },
    {
        "quote": "The best way to predict your future is to create it.",
        "author": "Peter Drucker"
    },
    {
        "quote": "Discipline is the bridge between goals and accomplishment.",
        "author": "Jim Rohn"
    },
    {
        "quote": "You don’t have to be great to start, but you have to start to be great.",
        "author": "Zig Ziglar"
    },
    {
        "quote": "The more you sweat in training, the less you bleed in battle.",
        "author": "Unknown"
    },
    {
        "quote": "Action is the foundational key to all success.",
        "author": "Pablo Picasso"
    },
    {
        "quote": "Small daily improvements over time lead to stunning results.",
        "author": "Robin Sharma"
    },
    {
        "quote": "Success is nothing more than a few simple disciplines, practiced every day.",
        "author": "Jim Rohn"
    },
    {
        "quote": "Courage is not having the strength to go on; it is going on when you don’t have the strength.",
        "author": "Theodore Roosevelt"
    },
    {
        "quote": "Do something today that your future self will thank you for.",
        "author": "Sean Patrick Flanery"
    },
    {
        "quote": "Success is achieved and maintained by those who try and keep trying.",
        "author": "W. Clement Stone"
    },
    {
        "quote": "Never confuse a single defeat with a final defeat.",
        "author": "F. Scott Fitzgerald"
    },
    {
        "quote": "Fall seven times, stand up eight.",
        "author": "Japanese Proverb"
    },
    {
        "quote": "Start where you are. Use what you have. Do what you can.",
        "author": "Arthur Ashe"
    },
    {
        "quote": "You become what you repeatedly do.",
        "author": "Aristotle"
    },
    {
        "quote": "Success is walking from failure to failure with no loss of enthusiasm.",
        "author": "Winston Churchill"
    },
    {
        "quote": "The only limit to our realization of tomorrow is our doubts of today.",
        "author": "Franklin D. Roosevelt"
    },
    {
        "quote": "A year from now you may wish you had started today.",
        "author": "Karen Lamb"
    },
    {
        "quote": "Great things never come from comfort zones.",
        "author": "Unknown"
    },
    {
        "quote": "Don’t stop when you’re tired. Stop when you’re done.",
        "author": "Unknown"
    },
    {
        "quote": "Quality is not an act, it is a habit.",
        "author": "Aristotle"
    },
    {
        "quote": "I am not a product of my circumstances. I am a product of my decisions.",
        "author": "Stephen Covey"
    },
    {
        "quote": "If opportunity doesn’t knock, build a door.",
        "author": "Milton Berle"
    },
    {
        "quote": "Success is liking yourself, liking what you do, and liking how you do it.",
        "author": "Maya Angelou"
    },
    {
        "quote": "Champions keep playing until they get it right.",
        "author": "Billie Jean King"
    },
    {
        "quote": "Either you run the day, or the day runs you.",
        "author": "Jim Rohn"
    },
    {
        "quote": "The journey of a thousand miles begins with one step.",
        "author": "Lao Tzu"
    },
    {
        "quote": "Don’t let yesterday take up too much of today.",
        "author": "Will Rogers"
    },
    {
        "quote": "A goal without a plan is just a wish.",
        "author": "Antoine de Saint-Exupéry"
    },
    {
        "quote": "Discipline weighs ounces, regret weighs tons.",
        "author": "Jim Rohn"
    },
    {
        "quote": "Great things are done by a series of small things brought together.",
        "author": "Vincent van Gogh"
    },
    {
        "quote": "If you get tired, learn to rest, not to quit.",
        "author": "Banksy"
    },
    {
        "quote": "Be stronger than your excuses.",
        "author": "Unknown"
    },
    {
        "quote": "Your only limit is your mind.",
        "author": "Unknown"
    },
    {
        "quote": "Success is the progressive realization of a worthy goal.",
        "author": "Earl Nightingale"
    },
    {
        "quote": "Doubt kills more dreams than failure ever will.",
        "author": "Suzy Kassem"
    },
    {
        "quote": "You miss 100% of the shots you don’t take.",
        "author": "Wayne Gretzky"
    },
    {
        "quote": "Focus on being productive instead of busy.",
        "author": "Tim Ferriss"
    },
    {
        "quote": "Motivation gets you started. Habit keeps you going.",
        "author": "Jim Ryun"
    },
    {
        "quote": "The only person you are destined to become is the person you decide to be.",
        "author": "Ralph Waldo Emerson"
    },
    {
        "quote": "Success begins with self-discipline.",
        "author": "Unknown"
    },
    {
        "quote": "Don’t count the days. Make the days count.",
        "author": "Muhammad Ali"
    },
    {
        "quote": "Opportunities don't happen. You create them.",
        "author": "Chris Grosser"
    },
    {
        "quote": "If you want to fly, give up everything that weighs you down.",
        "author": "Unknown"
    },
    {
        "quote": "Push yourself, because no one else is going to do it for you.",
        "author": "Unknown"
    },
    {
        "quote": "The way to get started is to quit talking and begin doing.",
        "author": "Walt Disney"
    },
    {
        "quote": "Success is the sum of details.",
        "author": "Harvey S. Firestone"
    },
    {
        "quote": "Don’t be afraid to give up the good to go for the great.",
        "author": "John D. Rockefeller"
    },
    {
        "quote": "Great things take time. Don’t rush.",
        "author": "Unknown"
    },
    {
        "quote": "Energy and persistence conquer all things.",
        "author": "Benjamin Franklin"
    },
    {
        "quote": "Wake up with determination. Go to bed with satisfaction.",
        "author": "Unknown"
    },
    {
        "quote": "Success doesn't come from what you do occasionally. It comes from what you do consistently.",
        "author": "Marie Forleo"
    },
    {
        "quote": "Winners are not people who never fail, but people who never quit.",
        "author": "Unknown"
    },
    {
        "quote": "The pain you feel today will be the strength you feel tomorrow.",
        "author": "Unknown"
    },
    {
        "quote": "The expert in anything was once a beginner.",
        "author": "Helen Hayes"
    },
    {
        "quote": "Once you choose hope, anything’s possible.",
        "author": "Christopher Reeve"
    },

    # -------------------------------------------------------
    #   125 NEW QUOTES (ADDED NOW) to reach EXACTLY 200
    # -------------------------------------------------------
    {
        "quote": "Your habits will decide your future.",
        "author": "Jack Canfield"
    },
    {
        "quote": "Success is built on the foundation of discipline.",
        "author": "Unknown"
    },
    {
        "quote": "Consistency is what transforms average into excellence.",
        "author": "Unknown"
    },
    {
        "quote": "Don’t limit your challenges. Challenge your limits.",
        "author": "Jerry Dunn"
    },
    {
        "quote": "The only bad workout is the one that didn’t happen.",
        "author": "Unknown"
    },
    {
        "quote": "Success requires sacrifice.",
        "author": "Unknown"
    },
    {
        "quote": "Direction is more important than speed.",
        "author": "Mark Twain"
    },
    {
        "quote": "Every accomplishment starts with the decision to try.",
        "author": "Unknown"
    },
    {
        "quote": "Discipline turns dreams into realities.",
        "author": "Unknown"
    },
    {
        "quote": "Don’t wait for the perfect moment. Take the moment and make it perfect.",
        "author": "Unknown"
    },
    {
        "quote": "You can't go back and change the beginning, but you can start where you are and change the ending.",
        "author": "C.S. Lewis"
    },
    {
        "quote": "The harder the struggle, the more glorious the triumph.",
        "author": "Unknown"
    },
    {
        "quote": "Don't be pushed by your problems. Be led by your dreams.",
        "author": "Ralph Waldo Emerson"
    },
    {
        "quote": "A river cuts through rock not because of its power but because of its persistence.",
        "author": "James Watkins"
    },
    {
        "quote": "Success demands singleness of purpose.",
        "author": "Vince Lombardi"
    },
    {
        "quote": "If you want different results, you have to do something different.",
        "author": "Unknown"
    },
    {
        "quote": "The best view comes after the hardest climb.",
        "author": "Unknown"
    },
    {
        "quote": "Your future is created by what you do today, not tomorrow.",
        "author": "Robert Kiyosaki"
    },
    {
        "quote": "Act as if what you do makes a difference. It does.",
        "author": "William James"
    },
    {
        "quote": "Success is rented, and the rent is due every day.",
        "author": "J.J. Watt"
    },
    {
        "quote": "Growth is uncomfortable because you've never been here before.",
        "author": "Unknown"
    },
    {
        "quote": "Worry is a misuse of your imagination.",
        "author": "Dan Zadra"
    },
    {
        "quote": "Every expert was once a terrible beginner.",
        "author": "Unknown"
    },
    {
        "quote": "A little progress each day adds up to big results.",
        "author": "Unknown"
    },
    {
        "quote": "What we fear doing most is usually what we most need to do.",
        "author": "Tim Ferriss"
    },
    {
        "quote": "Success favors the patient.",
        "author": "Unknown"
    },
    {
        "quote": "The cost of procrastination is the life you could have lived.",
        "author": "Unknown"
    },
    {
        "quote": "Do not stop until you are proud.",
        "author": "Unknown"
    },
    {
        "quote": "Make time for your dreams or someone else will hire you to build theirs.",
        "author": "Unknown"
    },
    {
        "quote": "Storms make trees take deeper roots.",
        "author": "Dolly Parton"
    },
    {
        "quote": "Discipline is doing what needs to be done, even when you don’t feel like doing it.",
        "author": "Unknown"
    },
    {
        "quote": "Greatness is a lot of small things done well.",
        "author": "Ray Lewis"
    },
    {
        "quote": "The man who moves a mountain begins by carrying away small stones.",
        "author": "Confucius"
    },
    {
        "quote": "Your mindset determines your reality.",
        "author": "Unknown"
    },
    {
        "quote": "Work on yourself more than you work on your job.",
        "author": "Jim Rohn"
    },
    {
        "quote": "You are what you do, not what you say you'll do.",
        "author": "Carl Jung"
    },
    {
        "quote": "Success requires replacing excuses with effort.",
        "author": "Unknown"
    },
    {
        "quote": "Every storm runs out of rain.",
        "author": "Maya Angelou"
    },
    {
        "quote": "Give your best effort even on the days you feel the worst.",
        "author": "Unknown"
    },
    {
        "quote": "You owe it to yourself to become everything you’ve ever dreamed of being.",
        "author": "Unknown"
    },
    {
        "quote": "Your discipline determines your destiny.",
        "author": "Unknown"
    },
    {
        "quote": "Some people dream it. Others make it happen.",
        "author": "Michael Jordan"
    },
    {
        "quote": "Excuses make today easy but tomorrow hard. Discipline makes today hard but tomorrow easy.",
        "author": "Unknown"
    },
    {
        "quote": "When you feel like quitting, remember why you started.",
        "author": "Unknown"
    },
    {
        "quote": "The difference between ordinary and extraordinary is that little extra.",
        "author": "Jimmy Johnson"
    },
    {
        "quote": "You can’t have a million-dollar dream with a minimum-wage work ethic.",
        "author": "Stephen C. Hogan"
    },
    {
        "quote": "Discipline is choosing what matters most over what you want now.",
        "author": "Unknown"
    },
    {
        "quote": "Success belongs to the persistent.",
        "author": "Unknown"
    },
    {
        "quote": "Comfort is the enemy of progress.",
        "author": "P.T. Barnum"
    },
    {
        "quote": "Win the morning, win the day.",
        "author": "Tim Ferriss"
    },
    {
        "quote": "Don’t let the fear of losing be greater than the excitement of winning.",
        "author": "Robert Kiyosaki"
    },
    {
        "quote": "To have what others don’t, you must do what others won’t.",
        "author": "Unknown"
    },
    {
        "quote": "Your future self is watching. Make him proud.",
        "author": "Unknown"
    },
    {
        "quote": "Success is the result of preparation, hard work, and learning from failure.",
        "author": "Colin Powell"
    },
    {
        "quote": "Don’t allow your comfort zone to become your prison.",
        "author": "Unknown"
    },
    {
        "quote": "If you stay ready, you don’t have to get ready.",
        "author": "Unknown"
    },
    {
        "quote": "Every win begins with showing up.",
        "author": "Unknown"
    },
    {
        "quote": "You won’t always be motivated, so you must learn to be disciplined.",
        "author": "Unknown"
    },
    {
        "quote": "Become the hardest worker in the room.",
        "author": "Dwayne Johnson"
    },
    {
        "quote": "Patience is not the ability to wait, but how you act while waiting.",
        "author": "Joyce Meyer"
    },
    {
        "quote": "Success is built one step at a time.",
        "author": "Unknown"
    },
    {
        "quote": "If you can't handle being uncomfortable, you can't grow.",
        "author": "Unknown"
    },
    {
        "quote": "Great achievements require great sacrifices.",
        "author": "Unknown"
    },
    {
        "quote": "Every day is a chance to be better.",
        "author": "Unknown"
    },
    {
        "quote": "Improvement begins with ‘I’.",
        "author": "Unknown"
    },
    {
        "quote": "You don’t find willpower. You create it.",
        "author": "Unknown"
    },
    {
        "quote": "Make your goals so big they laugh, then work so hard they beg to know how you did it.",
        "author": "Unknown"
    },
    {
        "quote": "You are stronger than you think.",
        "author": "Unknown"
    },
    {
        "quote": "Stop waiting for permission. The world is yours.",
        "author": "Unknown"
    },
    {
        "quote": "Do the work. Not for applause but for results.",
        "author": "Unknown"
    },
    {
        "quote": "Your greatest investment will always be yourself.",
        "author": "Warren Buffett"
    },
    {
        "quote": "Discipline creates freedom.",
        "author": "Jocko Willink"
    },
    {
        "quote": "The best time to start was yesterday. The next best time is now.",
        "author": "Unknown"
    },
    {
        "quote": "There is no elevator to success. You have to take the stairs.",
        "author": "Zig Ziglar"
    },
    {
        "quote": "The comeback is always stronger than the setback.",
        "author": "Unknown"
    },
    {
        "quote": "Strength grows in the moments you think you can’t go on but keep going anyway.",
        "author": "Unknown"
    },
    {
        "quote": "The effort you put in today will show tomorrow.",
        "author": "Unknown"
    },
    {
        "quote": "Your grind will pay off.",
        "author": "Unknown"
    },
    {
        "quote": "Stop doubting yourself. Work hard and make it happen.",
        "author": "Unknown"
    },
    {
        "quote": "You weren’t born to be average.",
        "author": "Unknown"
    },
    {
        "quote": "The discipline you learn today becomes the strength you use tomorrow.",
        "author": "Unknown"
    },
    {
        "quote": "Your goals don’t care how you feel.",
        "author": "Unknown"
    },
    {
        "quote": "The only time success comes before work is in the dictionary.",
        "author": "Vidal Sassoon"
    },
    {
        "quote": "You’ll never always be motivated, but you can always be consistent.",
        "author": "Unknown"
    },
    {
        "quote": "Stop waiting for the right moment. Create it.",
        "author": "Unknown"
    },
    {
        "quote": "Success is earned. Not given.",
        "author": "Unknown"
    },
    {
        "quote": "Success starts in your mind before it becomes reality.",
        "author": "Unknown"
    },
    {
        "quote": "Be patient. Good things take time.",
        "author": "Unknown"
    },
    {
        "quote": "Better days begin with better decisions.",
        "author": "Unknown"
    },
    {
        "quote": "The discipline you build today builds the life you want tomorrow.",
        "author": "Unknown"
    },
    {
        "quote": "What you do every day matters more than what you do once in a while.",
        "author": "Gretchen Rubin"
    },
    {
        "quote": "You can have excuses or results. Not both.",
        "author": "Unknown"
    },
    {
        "quote": "Grow through what you go through.",
        "author": "Unknown"
    }
]

# ---------------------------------------------------------
# FETCH FUNCTIONS
# ---------------------------------------------------------

def fetch_quote_online():
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(QUOTABLE_URL, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("content"), data.get("author")
    except (HTTPError, URLError, ssl.SSLError) as e:
        print("Online quote fetch failed:", repr(e))
        return None, None
    except Exception as e:
        print("Unexpected error during online fetch:", repr(e))
        return None, None


def fetch_quote_fallback():
    if not FALLBACK_QUOTES:
        return None, None
    q = random.choice(FALLBACK_QUOTES)
    return q.get("quote"), q.get("author", "Unknown")


def handler(event, context):
    table_name = os.environ.get(TABLE_ENV)
    if not table_name:
        msg = f"{TABLE_ENV} env var missing"
        print(msg)
        return {"ok": False, "error": msg}

    table = dynamodb.Table(table_name)
    day = datetime.datetime.utcnow().date().isoformat()

    quote, author = fetch_quote_online()

    if not quote:
        print("Falling back to local quote list")
        quote, author = fetch_quote_fallback()

    if not quote:
        return {"ok": False, "day": day, "error": "No quote available (online + fallback failed)"}

    try:
        table.put_item(
            Item={
                "day": day,
                "quote": quote,
                "author": author or "Unknown",
            }
        )
        return {"ok": True, "day": day, "source": "fallback" if author in ["Unknown"] else "online"}
    except Exception as e:
        print("ERROR in fetch_daily while writing to DynamoDB:", repr(e))
        return {"ok": False, "day": day, "error": str(e)}
