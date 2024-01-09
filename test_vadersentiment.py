from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

"""
score compound
-----------
Le score compound est celui le plus couramment utilisé pour l'analyse des sentiments par la plupart des chercheurs,
y compris les auteurs.
sentiment positif : si compound score >= 0,05
sentiment neutre : si ( compound score > -0,05) et ( compoundscore < 0,05)
sentiment négatif : si compound score <= -0,05

pos: score composite normalisé et pondéré
-----------
Les scores 'pos', 'neu' et 'neg' sont des ratios pour les proportions de texte qui entrent dans chaque catégorie
(ils devraient donc tous totaliser 1... ou s'en rapprocher avec l'opération float).
Ce sont les mesures les plus utiles si vous souhaitez analyser le contexte et la présentation de la façon dont
le sentiment est véhiculé ou intégré dans la rhétorique pour une phrase donnée.
"""

sentences = [
    "Personne ne sait où est Soro Guillaume. C'est un génie #guineenne224 #abidjan225 #burkinatiktok"
    "#mali #camerountiktok #senegalaise_tik_tok"
    "#ouagadougou #ouagadougou #cotedivoire #france #niger #COCAN #paris #josey "
]

analyzer = SentimentIntensityAnalyzer()
for sentence in sentences:
    apc = analyzer.polarity_scores(sentence)
    print("analyzer polarity scores --> ", apc)
    print("{:-<65} {}".format(sentence, str(apc)))

    avc = analyzer.score_valence(sentiments=apc.get('compound'), text=sentence)
    print("analyzer score valence --> ", avc)
