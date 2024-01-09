from textblob import TextBlob

text = '''
Personne ne sait où est Soro Guillaume. C'est un génie.
'''

blob = TextBlob(text)
blob_tags = blob.tags
# print("blob tags --> ", blob_tags)

blob_noun_phrases = blob.noun_phrases
# print("blob noun phrases --> ", blob_noun_phrases)

# print("sentiment polarity --> ", blob.sentiment.polarity)
# print("sentiment subjectivity --> ", blob.sentiment.subjectivity)

# diviser les TextBlobs en phrases.
for s in blob.sentences:
    print("sentiment polarity --> ", s.sentiment.polarity)
    print("sentiment subjectivity --> ", s.sentiment.subjectivity)

# diviser les TextBlobs en mots.
print("sentence words --> ", blob.words)

# correct phrases
print("correct phrase --> ", blob.correct())
