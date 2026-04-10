"""
Generate a sample dataset for testing purposes.
This creates a small CSV that mimics the structure of the Kaggle Fake Reviews Dataset.
For production, replace with the full dataset from:
https://www.kaggle.com/datasets/mexwell/fake-reviews-dataset

Run: python data/generate_sample_data.py
"""
import csv
import os

# Sample genuine reviews (OR = Original/Real)
genuine_reviews = [
    ("Home_and_Kitchen_5", 4, "OR", "I bought this coffee maker about 3 months ago. It works fine for making basic drip coffee. The brew time is about 5 minutes for a full pot. My only complaint is the carafe handle feels a bit cheap. Overall decent value for the price."),
    ("Home_and_Kitchen_5", 3, "OR", "This blender is okay but not great. It struggles with ice and frozen fruit. The motor seems a bit underpowered. However, for smoothies with fresh fruit and liquid, it works just fine. Cleaning is easy."),
    ("Home_and_Kitchen_5", 5, "OR", "After researching several options, I went with this knife set. The chef's knife is very sharp out of the box. I've used them daily for two months now and they still hold their edge well. The wooden block looks nice on the counter."),
    ("Home_and_Kitchen_5", 2, "OR", "Disappointed with this toaster. The slots are too narrow for thick bread, and the browning is uneven. The left side always toasts darker than the right. For the price, I expected better quality control."),
    ("Home_and_Kitchen_5", 4, "OR", "We've had this cookware set for six months now. The nonstick coating is holding up well with regular use. We hand wash them as recommended. The handles stay cool on the stovetop which is a nice feature."),
    ("Electronics_5", 4, "OR", "Good wireless earbuds for the price. Sound quality is decent with clear mids and highs, though the bass could be stronger. Battery life is about 5 hours on a single charge, which matches the specs. Comfortable for wearing during workouts."),
    ("Electronics_5", 3, "OR", "This keyboard works fine for basic typing. The keys have a decent feel but are a bit mushy compared to mechanical keyboards. The wireless connection is stable. Not great for gaming but perfectly fine for office work."),
    ("Electronics_5", 5, "OR", "I use this monitor for graphic design work. The color accuracy is impressive right out of the box. IPS panel provides wide viewing angles. My only wish is that it had more USB ports. Build quality is solid."),
    ("Electronics_5", 2, "OR", "The mouse started double-clicking after just three weeks of use. The scroll wheel also feels loose. I contacted customer support and they were helpful, but I shouldn't have issues this early with a product."),
    ("Electronics_5", 4, "OR", "Solid webcam for video calls. The 1080p quality is clear enough for meetings. Auto-focus works well but takes a second to adjust when you move. The built-in microphone is decent but I prefer using a separate mic."),
    ("Books_5", 5, "OR", "The author does an excellent job explaining complex topics in an approachable way. Each chapter builds on the previous one logically. I particularly enjoyed the case studies in chapters 5 through 8. Would recommend for intermediate learners."),
    ("Books_5", 3, "OR", "Started reading this with high expectations based on the recommendations. The first half was engaging but the second half felt rushed. Some of the character development was lacking. Not bad, but not as good as the author's previous work."),
    ("Books_5", 4, "OR", "Great reference book for Python programming. The code examples are practical and well-explained. I keep it on my desk at work. Some sections could use updating for the latest Python version, but the fundamentals are solid."),
    ("Books_5", 1, "OR", "I found this book extremely repetitive. The author makes the same points over and over in different words. Could have been a 50 page pamphlet instead of a 300 page book. Save your money."),
    ("Books_5", 4, "OR", "My daughter loves this book series. She's read each one multiple times. The stories are age-appropriate and encourage imagination. Good quality print and binding. We've bought the whole set."),
    ("Clothing_5", 4, "OR", "These running shoes fit well right out of the box with no break-in period. Good arch support for my flat feet. I've run about 50 miles in them so far and they're holding up well. True to size, I ordered my normal 10.5."),
    ("Clothing_5", 3, "OR", "The jacket looks nice and is warm enough for fall weather. However, the zipper feels flimsy and I'm concerned about long-term durability. The pockets are a good size. Color matches the photo accurately."),
    ("Clothing_5", 5, "OR", "These are now my favorite work pants. Comfortable enough to wear all day, professional enough for meetings. The stretch material is great for sitting at a desk. I've washed them a dozen times with no fading."),
    ("Clothing_5", 2, "OR", "Ordered a medium based on the size chart and it fits more like a large. The material feels thin and cheap compared to the photos. Returning this and will look elsewhere."),
    ("Clothing_5", 4, "OR", "Comfortable everyday t-shirt. The cotton is soft and breathable. After several washes, it hasn't shrunk or lost its shape. The color is slightly different from the website photo, but still looks good."),
    ("Home_and_Kitchen_5", 5, "OR", "This vacuum cleaner has been a game changer for our home with two dogs. The suction power is strong even on high pile carpet. The dustbin is easy to empty. Battery lasts about 40 minutes which is enough for our apartment."),
    ("Electronics_5", 3, "OR", "Decent tablet for the price. Screen is bright and colorful. Performance is fine for web browsing and streaming but it struggles with heavier apps and games. Battery life is about 6 to 7 hours with moderate use."),
    ("Home_and_Kitchen_5", 4, "OR", "These storage containers seal well and keep food fresh. We've been using them for about two months without any leaks. The lids snap on securely. They stack neatly in the fridge which saves space."),
    ("Electronics_5", 4, "OR", "The router was easy to set up using the companion app. Wi-Fi coverage improved significantly in our two-story house. Speed test shows consistent results near the advertised speeds. The parental controls are a nice bonus."),
    ("Books_5", 5, "OR", "This cookbook has become my go-to for weeknight dinners. Most recipes take 30 minutes or less and use ingredients I already have. The photos are beautiful and the instructions are clear."),
    ("Home_and_Kitchen_5", 3, "OR", "The air fryer works well but is smaller than I expected. It can fit about two chicken breasts at a time. The cooking presets are helpful but the timer dial is hard to read. Easy to clean."),
    ("Clothing_5", 3, "OR", "Good quality socks with decent cushioning. They stay up well throughout the day. The material feels durable. Only giving three stars because they run slightly large."),
    ("Electronics_5", 5, "OR", "I upgraded to this SSD and the difference in boot time is incredible. Went from over a minute to about 15 seconds. File transfers are also noticeably faster. Easy installation with the included instructions."),
    ("Home_and_Kitchen_5", 4, "OR", "This cast iron skillet is heavy but cooks beautifully. Great heat distribution for searing steaks. It came pre-seasoned and ready to use. After a month of use and proper care, the seasoning has only improved."),
    ("Books_5", 4, "OR", "An informative read about the history of space exploration. Well-researched with plenty of footnotes for further reading. Some of the technical sections are dense but overall very accessible for a general audience."),
]

# Sample fake reviews (CG = Computer Generated/Fake)
fake_reviews = [
    ("Home_and_Kitchen_5", 5, "CG", "Amazing product! Absolutely the best purchase I have ever made! This is incredible and everyone needs to buy this immediately! You will not regret it! Five stars! Best ever! Must buy!"),
    ("Home_and_Kitchen_5", 5, "CG", "PERFECT!!! I love this product so much!!! It changed my life!!! Everyone should buy this AMAZING product!!! HIGHLY RECOMMEND!!! INCREDIBLE!!!"),
    ("Home_and_Kitchen_5", 5, "CG", "Love it love it love it! Great product great quality great price! So happy with this purchase! Best thing ever! Would recommend to everyone!"),
    ("Home_and_Kitchen_5", 5, "CG", "This is the most wonderful thing I have ever bought. It is absolutely fantastic and incredible. I cannot say enough good things about this amazing product. It is superb and outstanding in every way."),
    ("Home_and_Kitchen_5", 1, "CG", "WORST PRODUCT EVER!!! DO NOT BUY THIS GARBAGE!!! TERRIBLE AWFUL HORRIBLE!!! COMPLETE WASTE OF MONEY!!! THIS IS A SCAM!!! PATHETIC USELESS JUNK!!!"),
    ("Electronics_5", 5, "CG", "Unbelievable! This is miraculous! I have tried many products but this one is by far the best! It is perfect in every way! Must buy must buy must buy! Life changing!"),
    ("Electronics_5", 5, "CG", "Five stars! Great! Excellent! Wonderful! I love this product so much. It is amazing. It is perfect. Best product. Highly recommend. Must buy. Great quality."),
    ("Electronics_5", 1, "CG", "Terrible terrible terrible. Do not buy this horrible product. It is the worst thing I have ever purchased. Disgusting quality. Complete ripoff. Waste of money. Awful awful awful."),
    ("Electronics_5", 5, "CG", "This product is AMAZING! I bought one for myself and then bought ten more for my family! Everyone LOVES it! BEST PURCHASE EVER! You NEED this in your life!"),
    ("Electronics_5", 5, "CG", "Incredible product. Outstanding quality. Superb design. Perfect functionality. Excellent value. Wonderful experience. Amazing results. Highly recommended. Must have item."),
    ("Books_5", 5, "CG", "BEST BOOK EVER WRITTEN!!! MUST READ!!! LIFE CHANGING!!! I have read thousands of books and this is by far the GREATEST ONE!!! BUY IT NOW!!!"),
    ("Books_5", 1, "CG", "This book is complete garbage. The worst thing ever published. Do not waste your time or money. Horrible writing. Terrible plot. Pathetic characters. A complete scam."),
    ("Books_5", 5, "CG", "Amazing book! Perfect! I love it! Great writing! Fantastic story! Best author ever! Highly recommend! Five stars! Must read! Incredible! Wonderful!"),
    ("Clothing_5", 5, "CG", "OMG this is the BEST clothing item I have EVER purchased!!! AMAZING quality!!! INCREDIBLE fit!!! PERFECT in every way!!! Must buy must buy!!! LIFE CHANGING!!!"),
    ("Clothing_5", 5, "CG", "Love this! Love it! So perfect! So amazing! Best quality! Best fit! Best color! Best everything! Everyone needs this! Buy it now! Five stars! Highly recommend!"),
    ("Clothing_5", 1, "CG", "DO NOT BUY!!! TERRIBLE QUALITY!!! WORST PRODUCT EVER!!! SCAM SCAM SCAM!!! DISGUSTING!!! HORRIBLE!!! I want my money back!!! TRASH!!!"),
    ("Home_and_Kitchen_5", 5, "CG", "This is absolutely the best kitchen product you can buy. It is perfect and amazing and wonderful. I use it every single day and it never disappoints. Best investment ever."),
    ("Home_and_Kitchen_5", 5, "CG", "WOW! Just WOW! I cannot believe how AMAZING this product is! It is PERFECT! INCREDIBLE! FANTASTIC! Everyone I know wants one after seeing mine! MUST BUY!!!"),
    ("Electronics_5", 5, "CG", "Perfect product perfect quality perfect price. I love everything about it. It is amazing and wonderful and fantastic. Best electronics purchase I have made. Highly highly highly recommend."),
    ("Electronics_5", 1, "CG", "Worst. Product. Ever. Do not waste your hard earned money on this garbage. It broke after one day. Terrible quality. Horrible customer service. Complete and total ripoff. Avoid at all costs."),
    ("Home_and_Kitchen_5", 5, "CG", "As advertised. Great product. I love it. My family loves it. My friends love it. Everyone loves it. Best product. Great quality. Great price. Highly recommend to everyone."),
    ("Home_and_Kitchen_5", 5, "CG", "Outstanding! Magnificent! Extraordinary! This product exceeded all my expectations in every possible way! I am completely amazed and thrilled! Best purchase of my entire life!"),
    ("Electronics_5", 5, "CG", "Simply the best! No other product even comes close! This is the gold standard! A must have for every household! Life changing technology! Revolutionary! Game changer!"),
    ("Clothing_5", 5, "CG", "Just as described! Perfect fit! Amazing material! Great color! Love the style! Best clothing purchase ever! Will buy more! Highly recommend! Five stars definitely!"),
    ("Books_5", 5, "CG", "Absolutely phenomenal! Greatest book of all time! Every page is pure gold! The author is a genius! Cannot put it down! Must read for everyone on the planet!"),
    ("Home_and_Kitchen_5", 5, "CG", "I love this product! It is great! It is amazing! It works perfectly! Best product I have ever bought! Everyone should get one! Five stars all the way! Highly recommend!"),
    ("Electronics_5", 5, "CG", "AMAZING AMAZING AMAZING!!! I bought 5 of these because they are SO GOOD!!! BEST ELECTRONICS EVER!!! LIFE CHANGING TECHNOLOGY!!! MUST HAVE!!!"),
    ("Home_and_Kitchen_5", 1, "CG", "Save your money. This product is absolute junk. The worst purchase I have ever made. Terrible quality. Falls apart immediately. A disgusting waste of money. Avoid avoid avoid."),
    ("Clothing_5", 5, "CG", "Best clothing EVER! Perfect quality! Perfect fit! Perfect style! I have never been so happy with a purchase in my entire life! Buy it now you will not regret it!"),
    ("Books_5", 1, "CG", "Horrible horrible horrible. Do not buy this book. Worst writing I have ever seen. The author clearly does not know what they are doing. Complete waste of paper. Terrible terrible terrible."),
]

def main():
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_reviews_dataset.csv")
    
    all_reviews = genuine_reviews + fake_reviews
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["category", "rating", "label", "text_"])
        for review in all_reviews:
            writer.writerow(review)
    
    print(f"Sample dataset generated: {output_path}")
    print(f"Total reviews: {len(all_reviews)}")
    print(f"  Genuine (OR): {len(genuine_reviews)}")
    print(f"  Fake (CG):    {len(fake_reviews)}")
    print()
    print("NOTE: This is a small sample dataset for testing.")
    print("For better accuracy, download the full dataset from:")
    print("https://www.kaggle.com/datasets/mexwell/fake-reviews-dataset")


if __name__ == "__main__":
    main()
