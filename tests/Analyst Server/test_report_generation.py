from geo_agent.AnalystServer.analyst import format_final_report

markdown_report = '''
---

# Morning Briefing: Trade News (May 5-6, 2026)

## Key Actors & Their Classifications

| Actor Name | Classification | Occurrences |
|------------|----------------|-------------|
| United States | Country | 6 |
| European | Other | 3 |
| Taiwan | Country | 2 |
| China | Country | 2 |
| India | Country | 2 |
| Jamaica | Country | 1 |
| G7 | Government | 1 |
| European Union | Government | 1 |
| European Commission | Government | 1 |
| Enterprise Singapore | Government | 1 |
| Huawei | Company | 1 |
| ZTE | Company | 1 |
| Deutsche Post | Company | 1 |
| DHL | Company | 1 |
| Singapore | Country | 1 |

---

## Events Extracted from Articles

| Event | Source Article |
|-------|----------------|
| US retakes top trading partner position with Taiwan | "AI and chips propel US back to top of Taiwan's trade chart" (Digitimes) |
| Singapore firms pursue US market expansion | "Some Singapore firms eye US expansion despite trade and regulatory challenges" (CNA) |
| Enterprise Singapore aids firms with US regulatory compliance | "Some Singapore firms eye US expansion despite trade and regulatory challenges" (CNA) |
| G7 trade ministers convene in Paris | "G7 trade ministers set to meet but not discuss latest US tariff threat" (Digital Journal) |
| Middle East war repercussions dominate ministers discussion | "G7 trade ministers set to meet but not discuss latest US tariff threat" (Digital Journal) |
| Ministers refuse to address US auto tariff threat | "G7 trade ministers set to meet but not discuss latest US tariff threat" (Digital Journal) |
| Ministers discuss critical minerals supply chain security | "G7 trade ministers set to meet but not discuss latest US tariff threat" (Digital Journal) |
| India and Jamaica strengthen bilateral trade ties | "India, Jamaica agree to boost trade, skilled mobility, healthcare cooperation: Jaishankar" (The Times of India) |
| India and Jamaica agree on skilled worker mobility | "India, Jamaica agree to boost trade, skilled mobility, healthcare cooperation: Jaishankar" (The Times of India) |
| India and Jamaica cooperate on healthcare professionals | "India, Jamaica agree to boost trade, skilled mobility, healthcare cooperation: Jaishankar" (The Times of India) |
| EU recommends banning Huawei, ZTE 5G equipment | "EU advises member states against using Chinese networking equipment" (GSMArena.com) |
| Deutsche Post meets forecast despite tariff turmoil | "Deutsche Post AGM: CEO flags tariff turmoil, lifts dividend to €1.90 and backs 2026 EBIT view" (MarketBeat) |
| Deutsche Post raises dividend to €1.90 | "Deutsche Post AGM: CEO flags tariff turmoil, lifts dividend to €1.90 and backs 2026 EBIT view" (MarketBeat) |
| Deutsche Post maintains 2026 EBIT outlook | "Deutsche Post AGM: CEO flags tariff turmoil, lifts dividend to €1.90 and backs 2026 EBIT view" (MarketBeat) |
| European stock futures fall amid US trade tensions | "European stock futures fall amid US trade tensions and Middle East conflicts" (Crypto Briefing) |

---

## Claims & Article Support

| Claim | Supporting Articles | Disagreeing Articles |
|-------|---------------------|---------------------|
| US-Taiwan trade partnership reflects deepening US strategic reliance on Taiwanese technology | 1 (Digitimes) | 0 |
| The shift in Taiwan's largest trade partner signals a new phase in US-China tech competition | 1 (Digitimes) | 0 |
| Taiwan's advanced chip exports to the US are critical to American technological leadership | 1 (Digitimes) | 0 |
| AI and semiconductor demand has made Taiwan indispensable to US economic security | 1 (Digitimes) | 0 |
| US surpassing China as Taiwan's top trade partner represents a strategic victory against Chinese influence | 1 (Digitimes) | 0 |
| The US offers superior access to capital for Singapore businesses | 1 (CNA) | 0 |
| The US innovation ecosystem provides unique opportunities for foreign firms | 1 (CNA) | 0 |
| US regulatory frameworks create significant barriers for Singapore companies | 1 (CNA) | 0 |
| Enterprise Singapore effectively supports firms navigating US regulatory frameworks | 1 (CNA) | 0 |
| US partnerships provide essential growth opportunities for Singapore firms | 1 (CNA) | 0 |
| G7 trade ministers are avoiding direct discussion of US tariff threats | 1 (Digital Journal) | 0 |
| Middle East war repercussions will dominate the G7 trade meeting agenda | 1 (Digital Journal) | 0 |
| Critical minerals and small packages are important trade issues for G7 | 1 (Digital Journal) | 0 |
| The US threatens additional tariffs on European vehicles | 1 (Digital Journal) | 0 |
| India and Jamaica agreed to strengthen trade linkages | 1 (Times of India) | 0 |
| India and Jamaica agreed to cooperate on recruitment and mobility of skilled professionals | 1 (Times of India) | 0 |
| Cooperation includes healthcare workers and teachers mobility | 1 (Times of India) | 0 |
| Both nations agreed to explore digital innovation cooperation | 1 (Times of India) | 0 |
| Cultural exchange and sports cooperation were discussed | 1 (Times of India) | 0 |
| The European Commission has recommended that EU member states exclude Huawei gear from telecom infrastructure | 1 (GSMArena.com) | 0 |
| The European Commission has recommended that EU member states exclude ZTE gear from telecom infrastructure | 1 (GSMArena.com) | 0 |
| A European Union-wide ban on Chinese 5G networking equipment is being implemented | 1 (GSMArena.com) | 0 |
| Chinese networking equipment poses security risks to EU telecom infrastructure | 1 (GSMArena.com) | 0 |
| Tariff turmoil negatively impacted Deutsche Post's performance | 1 (MarketBeat) | 0 |
| Deutsche Post can maintain its 2026 EBIT outlook despite global trade weakness | 1 (MarketBeat) | 0 |
| Weak global trade poses a significant challenge to Deutsche Post | 1 (MarketBeat) | 0 |
| Dividend increase to €1.90 is justified despite ongoing tariff disruptions | 1 (MarketBeat) | 0 |

---

## Summary

The trade news from May 5-6, 2026 reveals several key themes:

1. **US-Taiwan Tech Trade Surge**: The US has retaken its position as Taiwan's top trading partner, driven by AI and semiconductor demand, signaling a strategic shift in the US-China tech competition.

2. **EU-China 5G Tensions**: The European Commission is recommending EU member states ban Chinese networking equipment from Huawei and ZTE, citing security concerns.

3. **G7 Avoiding US Tariffs**: G7 trade ministers met in Paris but deliberately avoided discussing the latest US tariff threats, with Middle East war repercussions dominating the agenda.

4. **Bilateral Trade Agreements**: India and Jamaica agreed to strengthen trade ties, focusing on skilled worker mobility and healthcare cooperation.

5. **Corporate Impact**: Deutsche Post maintained its 2026 outlook despite tariff turmoil, raising its dividend to €1.90, while European stock futures fell amid US trade tensions.
'''

def main():
    format_final_report(markdown_report)

if __name__ == "__main__":
    main()