import spacy
from spacy.lang.en.examples import sentences 

nlp = spacy.load("en_core_web_sm")
#text = sentences[0]
text = '''
Global oil prices have risen as Iran continues to launch strikes across the Middle East in response to ongoing attacks by the US and Israel.

Brent crude, the global benchmark for oil prices, jumped by 10% to touch more than $82 a barrel on Monday after at least three ships were attacked near the Strait of Hormuz at the weekend. Natural gas prices also surged by as much as 25%.

Iran warned vessels not to pass through the crucial waterway in the south of the country, through which about 20% of the world's oil and gas is shipped.

In London, the FTSE 100 stock market index opened nearly 1% down with shares in airlines falling after airspace was closed across the Middle East.

Leading stock markets in Europe sustained bigger drops. In France, the CAC-40 fell by 1.6% while Germany's Dax dropped by 1.7%.

Meanwhile, the price of gold, which is viewed as a safe-haven asset during periods of uncertainty, added 2.3% to $5,395.99 an ounce.

International shipping has almost come to a standstill at the entrance to the Strait of Hormuz, with analysts warning that a prolonged conflict could push energy prices even higher.

The UK Maritime Trade Operations Centre (UKMTO) said that two vessels had been struck, and an "unknown projectile" was reported to have "exploded in very close proximity" to a third.

After its initial surge, Brent crude fell back to $79 a barrel while US-traded oil was up by around 7.6% at $72.20.

"The market isn't panicking", Saul Kavonic, head of energy research at MST Marquee told the BBC. "There is more clarity that so far, oil transport and production infrastructure hasn't been a primary target by any side," he added.

"The market will be watching for signs that traffic through the Strait of Hormuz returns, which would see oil prices subside again."
'''
doc = nlp(text)
print(doc.text)

#for token in doc:
#    print(token.text, token.pos_, token.dep_)

print()
for ent in doc.ents:
    #print(ent.text, ent.start_char, ent.end_char, ent.label_)
    print(ent.text, ent.label_)