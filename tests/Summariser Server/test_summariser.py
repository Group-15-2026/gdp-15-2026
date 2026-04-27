from geo_agent.Entities.Article import Article, _Source
from geo_agent.SummariserServer.summariser import extract_act_eve

from utils import setup

import asyncio
from datetime import datetime
#import pytest

# XX TODO: add unit tests. Currently just seeing if the code runs

async def main():
    setup()

    article1 = Article(
        article_id = "",
        article_title = "",
        publication_time = datetime.now(),
        source = _Source(
            source_id = "",
            source_name = "Bob's Newsagents"
        ),

        #text_body = "Today my friend Bob started a new job at Apple! He's also moving from the United Kingdom to the UK"
        text_body = '''
The chief Foreign Office official ousted over the decision to grant Peter Mandelson a security clearance despite vetting concerns is expected to face questions from MPs on Tuesday.
Sir Olly Robbins will be grilled by the Foreign Affairs Committee over why the ex-US ambassador received the clearance, and whether No 10 was told about red flags.
It adds to the potential jeopardy Sir Keir Starmer faces next week, with the planned appearance coming a day after he is due to appear in the Commons to answer questions about the row.
Sir Olly's predecessor Lord Simon McDonald has defended the senior official, telling BBC Radio 4's Today programme that "No 10 wanted a scalp and wanted it quickly".
He continued: "I cannot see that there was any process, any fairness, any giving [Sir Olly] the chance to set out his case, and that feels, to me, wrong."
Lord McDonald, who was permanent secretary between 2015 and 2020, said details from the "confidential" vetting process would "never be shared with No 10 or the prime minister".
An outright failure of the vetting process "would have to be conveyed to the political level", Lord McDonald added - and the fact it appears not to have been indicates "the picture was more complicated than Number 10 wished to present".
But multiple Whitehall sources have told BBC News security officials did outrightly recommend against Mandelson's security clearance.
On Friday the government published the UK Security Vetting's decision template, the type of document they would have been presented with in Mandelson's case.
It shows security officials typically indicate a low, moderate or high level of concern followed by an explicit recommendation that clearance be approved, approved with risk management, or denied. Both sets of options are reflected by green, yellow, or red boxes.

A screenshot of a risk assessment document published by Downing Street
Image source,Downing Street
Image caption,
No 10 released the report template the Foreign Office would have been presented with following Mandelson's vetting

The BBC has been told that in Mandelson's vetting, officials ticked the red boxes in both instances, indicating the highest level of concern, and explicitly recommending his security clearance be denied.
Sir Keir has come under intense scrutiny from opposition MPs, who have sought to cast doubt on his insistence that he first learned Mandelson had failed the vetting process earlier this week.
The prime minister had previously told the Commons that "due process" was followed over Mandelson's appointment, prompting accusations from opposition MPs that he misled Parliament.
On Friday evening, Downing Street took the unusual step of releasing an official account of the meeting on 15 April during which the prime minister has said he was informed about Mandelson's vetting for the first time.
He has labelled the decision not to inform him sooner as "staggering", adding: "That I wasn't told that he had failed security vetting when I was telling Parliament that due process had been followed is unforgivable."
Dame Emily Thornberry wrote to Sir Olly on Friday requesting that he appears before the Foreign Affairs Committee she chairs to answers questions.
She said developments this week had "called into question" evidence Sir Olly previously gave to the committee.

Chris Mason: Mandelson nightmare haunts Starmer again
Published
1 day ago
What we know about Mandelson's vetting and security clearance
Published
21 hours ago

It has also emerged that Cabinet Secretary Antonia Romeo found out about Mandelson's vetting failure in late March, but had to investigate the circumstances and legal implications before informing the prime minister.
Mandelson was announced as the government's choice to be US ambassador in December 2024, with developed vetting beginning the same day.
He formally took up the post in February 2025, before being removed last September when further details about his past ties with convicted sex offender Jeffrey Epstein came to light.
Sir Olly had been the most senior civil servant at the Foreign Office for two weeks when it was announced Mandelson had been picked for the Washington role.
Dame Emily Thornberry wrote to Sir Olly on Friday requesting that he appears before the Foreign Affairs Committee she chairs to answers questions.
She said developments this week had "called into question" evidence Sir Olly previously gave to the committee.

Sir Olly Robbins wears a navy suit as he walks down Whitehall at dusk
Image source,PA Media
Image caption,
Sir Olly Robbins, pictured in 2019, was effectively sacked from his role at the Foreign Office on Thursday night

BBC News understands he has not formally accepted the committee's invitation, but friends of his said he was preparing to appear on Tuesday.
They also cast doubt on whether Sir Olly ever actually saw the recommendation to the Foreign Office not to approve Lord Mandelson's vetting.
Allies said it was unlikely he was given the full report and may only have seen more specific risks thrown up during the process.
BBC News understands the vetting report returned a "no" verdict on whether a security clearance granting access to sensitive government material should be given to Mandelson.
Vetting of government employees and appointees is carried out by a government agency overseen by the Cabinet Office, which reports back to hiring departments with recommendations.
Following Sir Olly's departure, Conservative leader Kemi Badenoch said the prime minister had "no one left to sack" and described his position as untenable.
Liberal Democrat leader Sir Ed Davey called for an investigation by the Privileges Committee into whether the prime minister intentionally misled Parliament.
The SNP, Green Party and Reform UK have also called for Sir Keir to resign.
'''
    )

    articles = [article1]

    article, actors, events = await extract_act_eve(articles)

    for actor in actors:
        print(actor.name, actor.actor_type)

    print()

    for event in events:
        print(event.event)

if __name__ == "__main__":
    asyncio.run(main())