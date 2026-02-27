#!/usr/bin/env python3
"""Daily stoic quote with multi-paragraph reflection, delivered at 7:45 Berlin time."""

import json
import os
import sys
from datetime import datetime

QUOTES = [
    {
        "quote": "The happiness of your life depends upon the quality of your thoughts. — MARCUS AURELIUS",
        "reflection": (
            "Marcus wrote this near the end of Book V of the Meditations, during a period when "
            "his administrative duties and the northern frontier campaigns gave him every reason "
            "to let bitterness colour his inner life. Rather than catalogue his problems, he "
            "returned again and again to the only lever he actually controlled: the character of "
            "his own thinking.\n\n"
            "This is not a call to 'think positive' in the shallow sense. Marcus is pointing at "
            "something structural — your thoughts are not just commentary on your life, they are "
            "the medium in which your life is experienced. Two people can face the same hardship "
            "and inhabit completely different realities, because reality is filtered through "
            "interpretation before it ever reaches you.\n\n"
            "Today, pay attention to the thought that arises before your emotional reaction. "
            "That thought is not a fact — it is a draft you can revise. The revision is the practice."
        ),
    },
    {
        "quote": "We suffer more often in imagination than in reality. — SENECA",
        "reflection": (
            "Seneca wrote this to Lucilius, a friend anxious about an upcoming legal trial. "
            "Rather than offering reassurance about the verdict, Seneca pointed out that Lucilius "
            "had already suffered the trial a hundred times in his mind — and the real event could "
            "only happen once.\n\n"
            "Modern psychology calls this 'anticipatory anxiety,' and the research backs Seneca up: "
            "people consistently overestimate both the likelihood and the intensity of negative "
            "outcomes. The mental rehearsal of disaster is almost always worse than the disaster "
            "itself, partly because imagination has no time limit and no counterbalancing details.\n\n"
            "Next time you catch yourself running a worst-case scenario on repeat, notice the loop. "
            "You are not preparing — you are suffering in advance for something that may never arrive. "
            "Put the energy into what you can do right now, and let the future audition for your "
            "attention when it actually shows up."
        ),
    },
    {
        "quote": "It's not what happens to you, but how you react to it that matters. — EPICTETUS",
        "reflection": (
            "Epictetus knew this from experience that most philosophers never had. Born into "
            "slavery, he endured a broken leg — some accounts say his master deliberately "
            "crippled him — and yet he went on to teach in Rome and later founded a school in "
            "Nicopolis that attracted students from across the empire. His philosophy was not "
            "armchair theory; it was forged in circumstances where reaction was the only freedom "
            "available.\n\n"
            "The principle is deceptively simple but operationally demanding. It does not say "
            "events don't matter. It says your response is where your agency lives. A job loss, "
            "a harsh word, a plan that falls apart — these are real. But between the event and "
            "your response is a gap, and in that gap lives everything that defines your character.\n\n"
            "Practice today by noticing one moment where your automatic reaction kicks in before "
            "you've chosen it. Just noticing the gap is the first step to widening it."
        ),
    },
    {
        "quote": "The best revenge is to be unlike him who performed the injury. — MARCUS AURELIUS",
        "reflection": (
            "Marcus wrote this while dealing with Avidius Cassius, a general who declared himself "
            "emperor in a failed revolt. The political pressure to retaliate harshly was immense, "
            "yet Marcus chose restraint — reportedly he wanted Cassius captured alive so he could "
            "pardon him. Cassius was killed by his own soldiers before that could happen, but "
            "Marcus's intention tells us everything about how he understood revenge.\n\n"
            "Retaliation feels like strength, but it binds you to the person who wronged you. You "
            "become a mirror of their worst qualities. Marcus saw that the truly powerful response "
            "is to refuse the invitation to become like them — to answer cruelty with integrity, "
            "not because it's naive, but because it's the only move that actually frees you.\n\n"
            "When someone wrongs you today, ask: what kind of person do I want to be in this "
            "moment? The answer to that question matters more than whatever they did."
        ),
    },
    {
        "quote": "Waste no more time arguing about what a good man should be. Be one. — MARCUS AURELIUS",
        "reflection": (
            "This line from Meditations X.16 is Marcus at his most impatient — with himself. He "
            "had access to the finest philosophical education in the ancient world, years of "
            "Stoic training under Rusticus and Apollonius, and yet he still caught himself "
            "theorising about virtue instead of practising it. The note is a self-correction "
            "written in the middle of a military campaign.\n\n"
            "We all know this trap. Reading one more book about productivity instead of starting "
            "the work. Debating the best exercise routine instead of going for a walk. The "
            "discussion about goodness can itself become the obstacle to goodness, because it "
            "lets you feel like you're making progress while standing still.\n\n"
            "Today, pick one thing you've been thinking about doing — something kind, useful, "
            "or difficult — and do it without further debate. The doing is the argument."
        ),
    },
    {
        "quote": "He who fears death will never do anything worthy of a man who is alive. — SENECA",
        "reflection": (
            "Seneca spent years under the threat of execution by Nero, who would eventually "
            "order his death. He lived knowing that any day could be his last — not as a "
            "metaphor, but as a political reality. This context gives the line an urgency that "
            "a comfortable reading strips away.\n\n"
            "Fear of death is really fear of loss — loss of time, of experience, of the people "
            "you love. But Seneca's insight is that this fear, left unchecked, produces the very "
            "loss it dreads. The person paralysed by mortality doesn't live more carefully; they "
            "live less fully. They avoid risk, defer joy, and hoard time they never actually spend.\n\n"
            "You don't have to be fearless. You have to act despite the fear. Ask yourself what "
            "you would do today if the timeline didn't stretch to infinity. Then do that."
        ),
    },
    {
        "quote": "No man is free who is not master of himself. — EPICTETUS",
        "reflection": (
            "Coming from a man who was literally enslaved for much of his early life, this "
            "redefines freedom in a way that no one born free could do as convincingly. Epictetus "
            "had seen external freedom granted and revoked by others. The only freedom that could "
            "not be taken from him was self-governance — the ability to choose his responses, "
            "direct his attention, and maintain his principles regardless of circumstance.\n\n"
            "Self-mastery does not mean suppression. It means you are not at the mercy of every "
            "passing impulse, craving, or emotional weather pattern. The person who snaps at "
            "everyone when hungry is not free; they are controlled by their blood sugar. The person "
            "who cannot sit with boredom without reaching for a screen is not free; they are "
            "managed by their discomfort.\n\n"
            "Freedom starts with small acts of sovereignty: pausing before you react, choosing "
            "what deserves your attention, doing what you decided to do even when you no longer "
            "feel like it."
        ),
    },
    {
        "quote": "Very little is needed to make a happy life; it is all within yourself, in your way of thinking. — MARCUS AURELIUS",
        "reflection": (
            "This was written by the most powerful man in the known world — someone who had "
            "access to every luxury the Roman Empire could provide. And yet his personal "
            "notebooks repeatedly return to the theme that none of it is the source of "
            "contentment. Not the palaces, not the authority, not the wealth. Happiness, "
            "he found, was an inside job.\n\n"
            "This is not asceticism for its own sake. Marcus is not saying you should want "
            "nothing. He is saying that when you understand how little is truly needed, you "
            "stop being held hostage by what you don't have. The gap between 'enough' and "
            "'more' is where most unhappiness lives — and it is a gap that external achievement "
            "can never close, because it moves with you.\n\n"
            "Consider what you already have that you once desperately wanted. That feeling of "
            "arrival faded, didn't it? The Stoics would say: the feeling faded because it was "
            "never about the thing. Train your thinking, and the sense of enough follows you "
            "everywhere."
        ),
    },
    {
        "quote": "Difficulties strengthen the mind, as labor does the body. — SENECA",
        "reflection": (
            "Seneca drew this analogy deliberately. Every Roman understood physical training — "
            "the gymnasium was a daily institution. You would never expect to get stronger by "
            "avoiding exertion. And yet, Seneca observed, that is exactly what people expect of "
            "their minds: comfort without growth, resilience without resistance.\n\n"
            "The comparison holds up under modern research. Psychologists call it 'stress "
            "inoculation' — controlled exposure to difficulty builds the mental architecture "
            "needed to handle larger challenges. People who have navigated moderate adversity "
            "show better coping skills than those who have faced either no adversity or "
            "overwhelming trauma. The difficulty is the training.\n\n"
            "When you face something hard today, try reframing it: this is a rep, not a "
            "punishment. You are not being broken down — you are being built up. The discomfort "
            "is the proof that growth is happening."
        ),
    },
    {
        "quote": "Make the best use of what is in your power, and take the rest as it happens. — EPICTETUS",
        "reflection": (
            "This is the entire Stoic programme compressed into a single sentence. Epictetus "
            "taught what he called the 'dichotomy of control' — the sharp distinction between "
            "what is up to you (your choices, your effort, your character) and what is not (other "
            "people's behaviour, external outcomes, the past). Misery, he argued, comes almost "
            "entirely from confusing the two categories.\n\n"
            "The practical application is immediate. You can prepare for the interview; you "
            "cannot control whether they hire you. You can be a good partner; you cannot "
            "guarantee how the other person feels. You can write the best code you know how; "
            "you cannot control whether the project gets cancelled. Pour your full effort into "
            "the part that is yours, and then release your grip on the rest.\n\n"
            "This is not passivity — it is the most efficient allocation of your finite energy. "
            "Everything you spend worrying about what you cannot influence is energy stolen from "
            "what you can."
        ),
    },
    {
        "quote": "The soul becomes dyed with the color of its thoughts. — MARCUS AURELIUS",
        "reflection": (
            "Marcus uses the metaphor of a dyer's vat — once fabric is submerged, the colour "
            "becomes part of its structure, not just its surface. He means that thoughts are not "
            "passing visitors; they are the dye in which your character soaks. Think cynical "
            "thoughts long enough and you become a cynic. Think generous thoughts and generosity "
            "becomes your default.\n\n"
            "This is not mysticism — it is pattern recognition. Neuroscience now confirms that "
            "repeated thought patterns physically reshape neural pathways. The things you "
            "habitually think become easier to think, and eventually become the lens through "
            "which everything is filtered. Your mind does not just reflect your thoughts; "
            "it is constructed by them.\n\n"
            "Pay attention today to the colour of your mental background noise. Is it anxious? "
            "Resentful? Grateful? Curious? That colour is not just describing your mood — it is "
            "shaping the person you are becoming."
        ),
    },
    {
        "quote": "As is a tale, so is life: not how long it is, but how good it is, is what matters. — SENECA",
        "reflection": (
            "Seneca used this analogy in his essay 'On the Shortness of Life,' written to "
            "Paulinus, a man consumed by administrative duties who kept postponing the life he "
            "actually wanted to live. Seneca's point was sharp: a long, unfocused life is not "
            "a triumph — it is a long waste. A short life lived with intention and presence is "
            "the complete work.\n\n"
            "Nobody finishes a great novel and wishes it had been three hundred pages longer for "
            "the sake of length. What makes a story satisfying is density of meaning — every "
            "scene matters, every choice reveals character. Seneca saw life the same way. The "
            "person who lives deliberately for forty years has lived more than the person who "
            "drifts for eighty.\n\n"
            "Ask yourself today: am I adding pages, or am I adding meaning? The answer changes "
            "what you do with the afternoon."
        ),
    },
    {
        "quote": "First say to yourself what you would be; and then do what you have to do. — EPICTETUS",
        "reflection": (
            "Epictetus taught this as a two-step discipline, and the order matters. Most people "
            "start with action — grinding through tasks, optimising routines, chasing goals — "
            "without first settling the question of identity. Who are you trying to become? "
            "Without that answer, effort is just motion.\n\n"
            "The Stoics called this 'prohairesis' — your fundamental orientation, the person you "
            "have decided to be. Once that is clear, decisions simplify dramatically. A person "
            "who has decided to be courageous does not need to debate whether to speak up. A "
            "person who has decided to be disciplined does not renegotiate with themselves every "
            "morning about whether to do the work.\n\n"
            "Try it today: before your first task, state clearly to yourself who you intend to "
            "be. Not what you intend to accomplish — who you intend to be while accomplishing it. "
            "The tasks will follow from that."
        ),
    },
    {
        "quote": "When you arise in the morning think of what a privilege it is to be alive. — MARCUS AURELIUS",
        "reflection": (
            "Marcus did not write this from comfort. His mornings often began with reports of "
            "plague casualties, military setbacks, or political treachery. The instruction to "
            "feel gratitude upon waking is not a denial of those realities — it is a deliberate "
            "act of perspective-setting before the day's difficulties have a chance to frame "
            "everything for you.\n\n"
            "Gratitude as a morning practice works because it primes the filter through which "
            "you will interpret the rest of the day. If you start by noticing what you have, "
            "the day's inconveniences register as minor against that backdrop. If you start by "
            "worrying about what's ahead, even small setbacks confirm the narrative that things "
            "are going wrong.\n\n"
            "This does not require a journal or a ritual. Just one conscious thought before your "
            "feet hit the floor: I am here. That is not guaranteed. What will I do with it?"
        ),
    },
    {
        "quote": "Luck is what happens when preparation meets opportunity. — SENECA",
        "reflection": (
            "This line is often quoted in business contexts, stripped of its Stoic roots. Seneca's "
            "original point was philosophical: what the world calls 'luck' is not random — it is "
            "the visible result of invisible preparation meeting a moment that others were not "
            "ready for. The lucky person is almost always the person who was practising when no "
            "one was watching.\n\n"
            "The Stoics were not fatalists. They believed in Providence — a rational order to the "
            "universe — but they also believed your job was to be ready for whatever that order "
            "presented. You cannot control when opportunity arrives. You can control whether you "
            "are prepared when it does. The musician who gets a lucky break has ten thousand hours "
            "of practice behind them. The break is just the moment when the world finally notices.\n\n"
            "Ask yourself: what am I preparing for, even when nothing seems to be happening? "
            "That preparation is not wasted time — it is the foundation for every future 'lucky' "
            "break."
        ),
    },
    {
        "quote": "If it is not right, do not do it; if it is not true, do not say it. — MARCUS AURELIUS",
        "reflection": (
            "This is Marcus at his most binary — no grey area, no situational ethics. He wrote it "
            "as a personal rule, not a law for others. The simplicity is the point: when you strip "
            "away rationalisation, most ethical dilemmas are not actually dilemmas. You know what "
            "is right. The hard part is doing it when it costs you something.\n\n"
            "Truth-telling is the sharper edge of the two. Lying is almost always easier in the "
            "short term. But Seneca observed that the liar must remember every lie, maintain every "
            "fiction, and live in fear of exposure. The truth-teller carries no such burden. "
            "Honesty is not just moral — it is operationally lighter.\n\n"
            "Today, notice the moments where you're tempted to shade the truth or cut a small "
            "ethical corner. The stakes may be tiny. But Marcus understood that character is built "
            "in the tiny moments, not the dramatic ones."
        ),
    },
    {
        "quote": "He suffers more than he who is in want, who complains. — SENECA",
        "reflection": (
            "Seneca makes a counterintuitive claim: the person who complains about their situation "
            "suffers more than the person who simply endures the same situation in silence. This is "
            "not a call to suppress feelings. It is an observation about what complaint does to the "
            "mind — it amplifies suffering by rehearsing it, narrating it, and turning a temporary "
            "state into an identity.\n\n"
            "Watch what happens when you complain. The act of verbalising a grievance recruits your "
            "attention, your memory, and your social environment into the service of the problem. "
            "You replay it, refine it, and invite others to validate it. The problem grows not "
            "because the circumstances changed, but because you fed it.\n\n"
            "This does not mean you should never voice difficulty. It means there is a difference "
            "between stating a problem to solve it and narrating a problem to inhabit it. Notice "
            "which one you are doing."
        ),
    },
    {
        "quote": "Man is not worried by real problems so much as by his imagined anxieties. — EPICTETUS",
        "reflection": (
            "Epictetus taught in Nicopolis to students who came from privilege — young Romans "
            "anxious about their careers, their reputations, their inheritances. He noticed that "
            "their suffering was almost entirely anticipatory. The real problems, when they "
            "actually arrived, were handled. It was the imagined ones that paralysed them.\n\n"
            "This pattern has only intensified. We now have 24-hour news, social media feeds, and "
            "infinite information streams designed to present potential threats. The result is a "
            "generation that worries more and faces less actual danger than any in history. The "
            "gap between imagined and real problems has never been wider.\n\n"
            "Try a simple exercise: write down what you're anxious about right now. Next week, "
            "check the list. Most of it will not have happened. The few things that did happen "
            "were probably manageable. The list is the evidence."
        ),
    },
    {
        "quote": "You have power over your mind — not outside events. Realize this, and you will find strength. — MARCUS AURELIUS",
        "reflection": (
            "This is the thesis statement of the Meditations. Marcus returns to it in different "
            "forms across all twelve books because, as emperor, he was constantly surrounded by "
            "things he could not control — plagues, wars, betrayals, natural disasters. His only "
            "refuge was the one territory that remained fully his: his own mind.\n\n"
            "The strength he describes is not emotional numbness. It is the strength that comes "
            "from ceasing to fight battles you cannot win. Every ounce of energy spent trying to "
            "control other people, outcomes, or the past is energy wasted. When you redirect that "
            "energy to the one thing you actually control — your own responses — you suddenly have "
            "more of it than you knew.\n\n"
            "Today, when something frustrates you, ask one question: is this within my control? "
            "If yes, act. If no, redirect. That single sorting mechanism will save you more energy "
            "than any productivity system ever invented."
        ),
    },
    {
        "quote": "It is not that we have a short time to live, but that we waste a lot of it. — SENECA",
        "reflection": (
            "This is the opening argument of Seneca's 'On the Shortness of Life,' and it reframes "
            "the entire human complaint about mortality. We don't have too little time, he argues. "
            "We have plenty. The problem is that we spend it on things that don't matter — endless "
            "busywork, petty feuds, mindless entertainment, and the maintenance of appearances.\n\n"
            "Seneca calculated that a person who lives to seventy but spends the majority of those "
            "years on trivia has lived less than someone who dies at forty but inhabits every year "
            "with purpose. Length of life is measured in attention, not heartbeats.\n\n"
            "Audit your last week honestly. How much of it was spent on things that actually "
            "mattered to you? The gap between that number and the total is not time that was "
            "stolen from you — it is time you gave away. The good news is that you can stop "
            "giving it away at any moment."
        ),
    },
    {
        "quote": "Wealth consists not in having great possessions, but in having few wants. — EPICTETUS",
        "reflection": (
            "Epictetus owned almost nothing. His home was a simple hut with a straw mat and an "
            "iron lamp — and when the lamp was stolen, he replaced it with an earthenware one "
            "and remarked that the thief had lost more than he had. This was not performance. "
            "Epictetus genuinely believed that desire, not deprivation, was the source of poverty.\n\n"
            "The mathematics are elegant. If wealth is the ratio of what you have to what you "
            "want, there are two ways to increase it. Most people focus exclusively on the "
            "numerator — acquiring more. Epictetus focused on the denominator — wanting less. "
            "The second strategy has no ceiling and no competition.\n\n"
            "This does not mean you should not pursue material goals. It means you should examine "
            "whether your wants are genuinely yours or inherited from advertising, social "
            "comparison, and cultural default settings. A want you chose is worth pursuing. A "
            "want you absorbed without examination is just noise."
        ),
    },
    {
        "quote": "Never let the future disturb you. You will meet it, if you have to, with the same weapons of reason. — MARCUS AURELIUS",
        "reflection": (
            "Marcus wrote this as a reminder that the person you will be when the future arrives "
            "is the same person you are now — equipped with the same faculties of reason, "
            "judgement, and resilience. The future feels threatening because you imagine facing it "
            "with your present emotional state, but that is never how it works. When the crisis "
            "actually comes, you rise to meet it.\n\n"
            "There is a useful asymmetry here. You cannot prepare for the future by worrying about "
            "it, because worry degrades the very faculties you will need. But you can prepare by "
            "strengthening your reason and character now — those travel with you into whatever "
            "comes.\n\n"
            "The next time you feel anxious about what lies ahead, remember: you are not sending "
            "your current anxious self into that future moment. You are sending whoever you will "
            "be then — someone who has, by definition, survived everything between now and then."
        ),
    },
    {
        "quote": "Hang on to your youthful enthusiasms — you'll be able to use them better when you're older. — SENECA",
        "reflection": (
            "Seneca was in his sixties when he wrote most of his letters to Lucilius, and age had "
            "given him a perspective that youth cannot: enthusiasm without naivety. He had watched "
            "peers lose their fire as they aged, settling into routine cynicism, and he recognised "
            "that this was not wisdom — it was surrender.\n\n"
            "The enthusiasms of youth — curiosity, ambition, the belief that things can change — "
            "are not mistakes to outgrow. They are fuel. What changes with age is the engine that "
            "burns them. A young person's enthusiasm is scattered; an older person's enthusiasm, "
            "properly maintained, is focused. The combination of fire and precision is unstoppable.\n\n"
            "If you notice your excitement about something fading — a project, a skill, a cause — "
            "ask whether the thing actually stopped mattering or whether you just got tired. "
            "Tiredness is fixable. Loss of meaning is not. Know the difference."
        ),
    },
    {
        "quote": "Freedom is the only worthy goal in life. — EPICTETUS",
        "reflection": (
            "For Epictetus, freedom was not political liberty or financial independence — it was "
            "the state of not being enslaved by your own desires, fears, and false beliefs. He "
            "had experienced literal slavery and found that even after manumission, most people "
            "remained enslaved to things far subtler than chains: social approval, comfort, the "
            "opinions of others.\n\n"
            "This is a radical claim. He is not saying freedom is one good among many. He is "
            "saying it is the precondition for all other goods. Without inner freedom, wealth is "
            "just gilded captivity, relationships are codependency, and achievement is compulsion "
            "wearing the mask of ambition.\n\n"
            "Consider where you feel unfree today. Not externally — internally. What are you "
            "doing out of obligation that you never actually chose? What are you avoiding out of "
            "fear that you never actually examined? Each honest answer is a key."
        ),
    },
    {
        "quote": "Look well into thyself; there is a source of strength which will always spring up if thou wilt always look. — MARCUS AURELIUS",
        "reflection": (
            "Marcus wrote this during a period of illness, when external strength — the body, "
            "political power, military command — was failing him. He turned inward not as an "
            "escape but as a reconnaissance mission: what resources do I actually have that "
            "cannot be taken from me?\n\n"
            "What he found was what the Stoics called the 'ruling reason' — the part of the mind "
            "that can observe, evaluate, and choose regardless of external circumstances. This is "
            "not willpower in the popular sense. It is something quieter: the ability to return "
            "to your own centre when everything around you is in motion.\n\n"
            "The instruction to 'look well' is important. A glance won't do. Self-knowledge "
            "requires honest, sustained attention — the kind most people avoid because what they "
            "find is uncomfortable. But Marcus promises that if you keep looking, the strength "
            "is there. Not strength to control the world, but strength to meet it."
        ),
    },
    {
        "quote": "A gem cannot be polished without friction, nor a man perfected without trials. — SENECA",
        "reflection": (
            "Seneca loved craft metaphors because they made abstract philosophy tangible. Everyone "
            "understood that a raw gemstone looks like an ordinary rock. The beauty is already "
            "inside — but it only becomes visible through a process that is, from the gem's "
            "perspective, entirely violent. Cutting, grinding, polishing. The gem does not become "
            "something new; it becomes what it always was, minus the rough exterior.\n\n"
            "Trials work the same way on character. They do not add something foreign to you. "
            "They remove what is unnecessary — the illusions, the complacency, the untested "
            "assumptions about who you are. What remains after a genuine trial is more you, not "
            "less.\n\n"
            "The next time you face friction — a difficult conversation, a project that keeps "
            "failing, a period of discomfort — ask what it might be polishing away. The answer "
            "is usually something you didn't need but were reluctant to let go of."
        ),
    },
    {
        "quote": "Any person capable of angering you becomes your master. — EPICTETUS",
        "reflection": (
            "Epictetus is describing a power transfer that happens without anyone signing a "
            "contract. The moment someone can reliably trigger your anger, they control your "
            "emotional state, your attention, and often your behaviour. You become a puppet "
            "operated by their actions — and they may not even know they're pulling the strings.\n\n"
            "This does not mean anger is always wrong. Aristotle argued that anger at the right "
            "thing, in the right measure, at the right time, is virtuous. But Epictetus is "
            "talking about reactive anger — the kind that is triggered automatically, before "
            "any judgement has been applied. That kind of anger is not a tool you're using; it "
            "is a reflex someone else is exploiting.\n\n"
            "The practice is not to suppress anger but to insert a pause between the trigger and "
            "the response. In that pause, ask: do I want to give this person authority over my "
            "inner state? Usually the answer is no — and the anger dissolves on its own."
        ),
    },
    {
        "quote": "The object of life is not to be on the side of the majority, but to escape finding oneself in the ranks of the insane. — MARCUS AURELIUS",
        "reflection": (
            "Marcus observed that crowds, including Roman political crowds, often adopted "
            "positions that no individual member would defend on their own. Mob psychology, "
            "groupthink, social contagion — he saw all of these two thousand years before they "
            "had names. His response was not contrarianism for its own sake. It was a commitment "
            "to thinking for himself even when consensus pulled in the other direction.\n\n"
            "The majority is not always wrong. But the majority is always the majority, which "
            "means its conclusions are shaped by social pressure, not just evidence. The person "
            "who defaults to the popular position without examining it is not agreeing — they are "
            "outsourcing their judgement.\n\n"
            "Today, notice one opinion you hold mainly because everyone around you holds it. "
            "Examine it on its own merits. You may end up keeping it — but now it's yours."
        ),
    },
    {
        "quote": "True happiness is to enjoy the present, without anxious dependence upon the future. — SENECA",
        "reflection": (
            "Seneca noticed that most people live in a state of permanent anticipation — waiting "
            "for the promotion, the move, the relationship, the retirement. The present moment "
            "is treated as a lobby, not a destination. Happiness is always scheduled for later.\n\n"
            "The trap is that 'later' never arrives in the form you expected. Each achievement "
            "reveals a new horizon, and the habit of deferral transfers seamlessly from one goal "
            "to the next. The person who cannot enjoy the present will not enjoy the future either, "
            "because when the future arrives it will be the present, and they will still be looking "
            "ahead.\n\n"
            "This is not an argument against planning. It is an argument against making your "
            "wellbeing conditional on outcomes you do not yet have. The test is simple: can you "
            "experience satisfaction right now, with things exactly as they are? If not, no "
            "external change will fix that."
        ),
    },
    {
        "quote": "Begin at once to live, and count each separate day as a separate life. — SENECA",
        "reflection": (
            "Seneca prescribed this as a practical exercise, not a poetic sentiment. Treat today "
            "as a complete unit — not a chapter in a longer story, but a story unto itself. It has "
            "a beginning (you woke up), a middle (the hours ahead), and an end (you will sleep). "
            "What kind of story will it be?\n\n"
            "The power of this reframe is that it eliminates the two greatest sources of wasted "
            "time: regret about yesterday and anxiety about tomorrow. If today is its own life, "
            "yesterday's mistakes belong to a different life, and tomorrow is someone else's "
            "problem. You are left with only what you can actually do: live this day well.\n\n"
            "Try it as an experiment. At the end of today, ask: if this had been my only day, "
            "would I be satisfied with how I spent it? The question is clarifying in a way that "
            "no long-term planning can match."
        ),
    },
    {
        "quote": "He is a wise man who does not grieve for the things which he has not, but rejoices for those which he has. — EPICTETUS",
        "reflection": (
            "Epictetus observed that most suffering is comparative. You are not unhappy because "
            "of what you lack — you are unhappy because you are focused on the gap between what "
            "you have and what you believe you should have. Shift the focus to what is present, "
            "and the emotional landscape changes without any external circumstance moving.\n\n"
            "This is not about lowering standards. It is about recognising that gratitude and "
            "ambition are not opposites. You can want more while appreciating what exists. The "
            "person who only sees what's missing is running on a deficit that no achievement can "
            "fill, because each new acquisition reveals a new absence.\n\n"
            "Try this: name three things you have right now that you once wanted desperately. "
            "You got them — and then stopped noticing. The act of re-noticing is the practice."
        ),
    },
    {
        "quote": "Accept the things to which fate binds you, and love the people with whom fate brings you together. — MARCUS AURELIUS",
        "reflection": (
            "Marcus did not choose his co-emperor (his adopted brother Lucius Verus was imposed "
            "on him), his wars (the Marcomanni invaded, not the other way around), or his plague "
            "(the Antonine plague killed millions). He chose how he related to all of it. This "
            "line is not passive acceptance — it is active embrace of the hand you were dealt.\n\n"
            "The instruction to 'love' the people fate brings you is harder than accepting "
            "circumstances. You can tolerate a difficult colleague or endure a challenging family "
            "member. Loving them requires seeing them as part of the same fabric you are woven "
            "into — not obstacles to your life, but the actual material of your life.\n\n"
            "Today, consider someone in your life who is difficult. They are there. That is the "
            "fact. The question is not how to remove them but how to respond to them in a way "
            "that reflects who you want to be."
        ),
    },
    {
        "quote": "While we are postponing, life speeds by. — SENECA",
        "reflection": (
            "Seneca wrote this in his mid-sixties, acutely aware that the time he had postponed "
            "things into was now the time he was living in. The future he had been saving things "
            "for had arrived, and it looked exactly like the present — busy, imperfect, and "
            "finite. There was no magical later when conditions would be ideal.\n\n"
            "Postponement is seductive because it feels like a decision without a cost. But the "
            "cost is invisible and compounding: each day you defer is a day you will never get "
            "back, spent on something other than what matters most to you. The tragedy is not "
            "that life is short — it is that we keep acting as if it is long.\n\n"
            "What have you been putting off? Not the trivial errands — the meaningful thing. "
            "The conversation, the project, the change. There will never be a better time than "
            "now, because 'now' is the only time that actually exists."
        ),
    },
    {
        "quote": "No one can hurt you without your consent. — GANDHI (influenced by Stoicism)",
        "reflection": (
            "Gandhi attributed this insight to his reading of the Stoics, particularly Epictetus, "
            "whose Discourses he studied while imprisoned in South Africa. The idea is radical: "
            "external actions — insults, injustice, even physical violence — can cause pain, but "
            "they cannot damage your inner self unless you allow them to define you.\n\n"
            "This is not victim-blaming. Gandhi was beaten, imprisoned, and eventually murdered. "
            "He did not claim those experiences were painless. He claimed that his response to "
            "them remained his own. The distinction matters enormously: pain is inevitable; "
            "suffering as identity is a choice.\n\n"
            "The practical application is in the small moments. Someone dismisses your work. "
            "Someone speaks rudely. Your first reaction is automatic. But the second reaction — "
            "whether you carry the wound forward or set it down — that is yours. And that is "
            "where consent lives."
        ),
    },
    {
        "quote": "If you are distressed by anything external, the pain is not due to the thing itself, but to your estimate of it. — EPICTETUS",
        "reflection": (
            "This is the core mechanism of Stoic psychology: between event and emotion sits "
            "judgement. A traffic jam is not stressful — your judgement that it should not exist "
            "is stressful. A cancelled flight is not infuriating — your expectation that plans "
            "should proceed without disruption is infuriating. Remove the judgement and the "
            "emotion loses its fuel.\n\n"
            "Cognitive behavioural therapy, developed two thousand years later, is built on "
            "exactly this principle. The therapist's job is to help you identify the 'estimate' — "
            "the automatic thought between event and emotion — and evaluate whether it is accurate "
            "or distorted. Epictetus was doing this in a toga.\n\n"
            "The next time you feel distressed, try separating the event from your interpretation. "
            "State the facts without adjectives. 'The meeting was moved' is a fact. 'The meeting "
            "was ruined' is an estimate. The gap between the two is where your freedom lives."
        ),
    },
    {
        "quote": "How much time he saves who does not look to see what his neighbor says or does or thinks. — MARCUS AURELIUS",
        "reflection": (
            "Marcus was surrounded by courtiers, advisors, and senators whose entire careers "
            "depended on monitoring what everyone else was doing. He saw how much mental energy "
            "the imperial court consumed in gossip, comparison, and political positioning — and "
            "how little of it produced anything of value.\n\n"
            "The modern equivalent is obvious. Social media is a machine for showing you what "
            "your neighbours say, do, and think. Every scroll is a choice to invest your "
            "attention in someone else's life instead of your own. The time cost is real but "
            "invisible, because it accumulates in minutes, not hours.\n\n"
            "Marcus's advice is not antisocial — it is attentional hygiene. Care about people. "
            "Help people. But stop monitoring people. The difference is the difference between "
            "engagement and surveillance. One builds relationships; the other just burns time."
        ),
    },
    {
        "quote": "Religion is regarded by the common people as true, by the wise as false, and by rulers as useful. — SENECA",
        "reflection": (
            "Seneca served as advisor to Nero and saw firsthand how power uses belief as a tool. "
            "His observation is not an attack on faith — it is a taxonomy of how the same "
            "institution is experienced differently depending on one's position. The common "
            "person seeks comfort, the philosopher seeks truth, and the ruler seeks leverage. "
            "All three are looking at the same thing and seeing entirely different objects.\n\n"
            "The broader Stoic point is about intellectual independence. Any system of belief — "
            "religious, political, cultural — should be evaluated on its merits, not adopted "
            "because it is convenient, comforting, or expected. The Stoics were not atheists; "
            "they believed in a rational Providence. But they insisted on arriving at that belief "
            "through reason, not social pressure.\n\n"
            "Examine one belief you hold today. Ask: do I hold this because I've thought it "
            "through, or because everyone around me holds it? The answer may surprise you."
        ),
    },
    {
        "quote": "Demand not that events should happen as you wish; but wish them to happen as they do happen. — EPICTETUS",
        "reflection": (
            "This is from the Enchiridion, Epictetus's handbook, and it is perhaps the most "
            "counterintuitive instruction in all of Stoicism. It sounds like surrender — but it "
            "is actually the most radical form of engagement. By aligning your will with reality, "
            "you stop wasting energy on resistance and redirect it to response.\n\n"
            "The distinction is between preference and demand. You can prefer that things go well "
            "without demanding it. Preference motivates effort; demand creates suffering when "
            "effort fails. The person who prefers a good outcome works hard and adapts when "
            "things change. The person who demands a good outcome works hard and breaks when "
            "things change.\n\n"
            "Try holding your plans today as preferences rather than demands. 'I'd like this to "
            "go well' rather than 'this must go well.' The difference in grip strength changes "
            "everything about how the day unfolds."
        ),
    },
    {
        "quote": "Everything we hear is an opinion, not a fact. Everything we see is a perspective, not the truth. — MARCUS AURELIUS",
        "reflection": (
            "Marcus wrote this not as a postmodern relativist but as a practical epistemologist. "
            "He dealt daily with conflicting reports from generals, advisors, and spies — each "
            "one claiming to describe reality, each one filtered through the describer's biases, "
            "incentives, and limitations. He learned that the map is never the territory.\n\n"
            "This does not mean truth doesn't exist. It means your first interpretation of any "
            "event is provisional — a draft, not a final copy. The confident certainty with which "
            "you assess a situation on first impression is almost always overconfidence. More "
            "information, more perspectives, and more time will reveal layers you missed.\n\n"
            "Today, hold one of your firm opinions lightly. Not loosely — lightly. The difference "
            "is that you still act on it, but you remain open to the possibility that you are "
            "seeing a perspective, not the whole picture."
        ),
    },
    {
        "quote": "Throw me to the wolves and I will return leading the pack. — SENECA",
        "reflection": (
            "Seneca wrote with the swagger of someone who had been exiled to Corsica for eight "
            "years and came back to become the most powerful advisor in Rome. The line is not "
            "bravado — it is autobiographical. He was thrown to the wolves, and he did return "
            "leading the pack. The exile that was meant to destroy him became the period in "
            "which he wrote some of his finest philosophical work.\n\n"
            "The deeper point is about the relationship between adversity and leadership. The "
            "person who has survived being thrown to the wolves understands the wolves. They "
            "have knowledge that cannot be acquired any other way — not through study, not "
            "through observation, only through direct experience of the worst case.\n\n"
            "When you find yourself in a situation that feels like exile — isolated, stripped "
            "of status, starting over — remember that this is not the end of your story. It "
            "may be the chapter that gives you the authority to lead."
        ),
    },
    {
        "quote": "We are more often frightened than hurt; and we suffer more from imagination than from reality. — SENECA",
        "reflection": (
            "Seneca returns to this theme repeatedly because he considered it one of the most "
            "practically useful insights in all of philosophy. The arithmetic is clear: for every "
            "feared event that actually occurs, dozens of feared events dissolve on their own. "
            "The suffering from the fear itself dwarfs the suffering from the actual events.\n\n"
            "He prescribed a specific exercise: 'premeditatio malorum' — the premeditation of "
            "evils. Not anxious rumination, but calm, deliberate consideration of worst cases. "
            "What is the worst that could happen? Could I survive it? What would I do? This "
            "transforms vague dread into a concrete plan, and concrete plans are far less "
            "frightening than shapeless anxiety.\n\n"
            "The next time fear grips you, write down specifically what you are afraid of. "
            "Specificity is the antidote to anxiety. Vague threats are infinite; specific "
            "scenarios are finite and usually manageable."
        ),
    },
    {
        "quote": "Caretake this moment. Immerse yourself in its particulars. — EPICTETUS",
        "reflection": (
            "Epictetus taught that presence is not a luxury — it is a discipline. Most people "
            "move through moments without ever inhabiting them, their attention split between "
            "memory and anticipation. The moment itself — with its textures, details, and "
            "unrepeatable specifics — passes unnoticed.\n\n"
            "The word 'caretake' is deliberate. It implies responsibility. This moment has been "
            "given to you, and it will not come again. To sleepwalk through it is not neutral — "
            "it is a small act of waste. To attend to it fully is not mystical — it is the most "
            "basic form of respect for your own life.\n\n"
            "Pick one ordinary moment today — a meal, a walk, a conversation — and attend to "
            "its particulars. The temperature, the sounds, the quality of light. You are not "
            "trying to feel something special. You are trying to actually experience what is "
            "already happening."
        ),
    },
    {
        "quote": "Reject your sense of injury and the injury itself disappears. — MARCUS AURELIUS",
        "reflection": (
            "Marcus is making a precise psychological claim: the injury you feel from an insult, "
            "a slight, or an injustice is not caused by the event itself but by your judgement "
            "that you have been wronged. Change the judgement and the emotional wound closes. "
            "This does not mean the event didn't happen — it means the suffering is optional.\n\n"
            "This is difficult to accept when the injury feels real. But consider: the same event "
            "can injure one person deeply and leave another untouched. The difference is not in "
            "the event but in the interpretation. The person who does not perceive themselves as "
            "injured is, functionally, not injured.\n\n"
            "The practice is not to deny pain but to examine the story you are telling about it. "
            "'They disrespected me' is a story. 'They said X' is a fact. The gap between the "
            "fact and the story is where the injury lives — and where it can be released."
        ),
    },
    {
        "quote": "I have often wondered how it is that every man loves himself more than all the rest of men. — MARCUS AURELIUS",
        "reflection": (
            "The full passage continues: '...but yet sets less value on his own opinion of "
            "himself than on the opinion of others.' Marcus found this contradiction baffling. "
            "We claim to value ourselves above all, but we hand the verdict on our worth to "
            "strangers, acquaintances, and social media algorithms without a second thought.\n\n"
            "The inconsistency reveals something important: self-love, for most people, is not "
            "genuine self-knowledge. It is self-preference — wanting good things for yourself "
            "without actually trusting your own judgement about what is good. If you truly "
            "valued your own opinion, the approval or disapproval of others would be interesting "
            "data, not an emotional emergency.\n\n"
            "Ask yourself today: whose opinion am I weighting more heavily than my own? If you "
            "have good reason to trust their judgement, that's wise counsel. If you're just "
            "outsourcing your self-worth, that's a habit worth examining."
        ),
    },
    {
        "quote": "It is not the man who has too little, but the man who craves more, that is poor. — SENECA",
        "reflection": (
            "Seneca was one of the wealthiest men in Rome, which makes this line either deeply "
            "hypocritical or deeply honest. He was both — he acknowledged the tension openly. "
            "His point was not that wealth is bad, but that craving is the actual poverty. A "
            "rich person consumed by desire for more is poorer, in lived experience, than a "
            "contented person with modest means.\n\n"
            "The hedonic treadmill confirms this at scale. Studies consistently show that beyond "
            "a moderate threshold, additional income has diminishing returns on happiness. The "
            "craving adapts — it simply relocates to the next rung. You don't arrive at enough "
            "by acquiring more. You arrive by recognising enough when you have it.\n\n"
            "Notice one craving today — for a purchase, a status marker, an upgrade. Ask: will "
            "this satisfy the craving or just move it? If the answer is 'move it,' the craving "
            "is the problem, not the lack."
        ),
    },
    {
        "quote": "Circumstances don't make the man, they only reveal him to himself. — EPICTETUS",
        "reflection": (
            "Epictetus taught that character is not created by circumstance — it is exposed by "
            "it. The person who is kind when everything is going well and cruel when things fall "
            "apart was never genuinely kind. The difficulty did not change them; it showed them "
            "who they had been all along.\n\n"
            "This is liberating rather than harsh. If circumstances reveal rather than create, "
            "then the work of self-improvement happens in the quiet moments, not in the crisis. "
            "The crisis is the exam; the daily practice is the studying. By the time the test "
            "arrives, the result is already determined.\n\n"
            "Consider a recent difficult moment. How did you behave? That behaviour was not an "
            "aberration — it was a data point about your current character. If you like what you "
            "see, the practice is working. If you don't, that is useful information, not a reason "
            "for shame."
        ),
    },
    {
        "quote": "When you wake up, think: What a privilege! What a gift! — MARCUS AURELIUS",
        "reflection": (
            "This is a compressed version of Marcus's morning meditation from Book V. The full "
            "passage acknowledges that he often did not want to get up — he describes the warmth "
            "of the bed, the temptation to stay comfortable. But he argues himself out of it: "
            "you were born for a purpose, and that purpose is not to lie under blankets.\n\n"
            "The word 'privilege' is important. Marcus lived during the Antonine Plague, which "
            "killed an estimated five million people. Waking up was not guaranteed. His gratitude "
            "was not sentimental — it was statistical. He made it through another night. Many "
            "did not.\n\n"
            "You do not have to feel grateful to practise gratitude. The feeling follows the "
            "practice, not the other way around. One conscious thought upon waking — even if you "
            "don't believe it yet — begins to reshape the lens through which the rest of the day "
            "is seen."
        ),
    },
    {
        "quote": "Difficulties come when you don't pay attention to life's whisper. — EPICTETUS",
        "reflection": (
            "Epictetus observed that most crises are not sudden — they are the loud version of "
            "a signal that was whispering for a long time. The relationship that collapsed had "
            "warning signs for months. The health problem that became acute started with subtle "
            "symptoms that were ignored. The project that failed had early indicators that nobody "
            "wanted to read.\n\n"
            "The whisper is always quieter than whatever you're busy with. That is why paying "
            "attention is a discipline, not a default. Attention means periodically stepping back "
            "from the noise of daily execution to ask: what am I not seeing? What is the small "
            "signal I've been dismissing because I'm too focused on the loud one?\n\n"
            "Today, listen for one whisper — a mild discomfort, an unresolved question, a nagging "
            "feeling that something is off. It may be nothing. But if it's something, hearing it "
            "now is vastly cheaper than hearing it later."
        ),
    },
    {
        "quote": "He suffers twice who thinks beforehand of his pain. — SENECA",
        "reflection": (
            "Seneca draws a clean distinction between preparation and pre-suffering. Preparation "
            "is thinking through what might happen and making a plan. Pre-suffering is feeling the "
            "pain of what might happen before it arrives — sometimes instead of it arriving at all. "
            "The first is strategic; the second is self-inflicted.\n\n"
            "The doubling effect is real. When the dreaded event actually occurs, the person who "
            "pre-suffered does not get a discount on the real pain. They pay full price twice — "
            "once in anticipation and once in reality. The person who prepared without pre-suffering "
            "pays once and arrives better equipped.\n\n"
            "The practical test: when you find yourself mentally rehearsing a bad outcome, ask "
            "whether the rehearsal is producing useful preparation or just early suffering. If "
            "you already have a plan, the continued rehearsal is not strategic — it's anxiety "
            "wearing the mask of responsibility."
        ),
    },
    {
        "quote": "How ridiculous and how strange to be surprised at anything which happens in life. — MARCUS AURELIUS",
        "reflection": (
            "Marcus kept a list in Book II of the Meditations of things he should expect from "
            "each day: ingratitude, rudeness, betrayal, incompetence. Not because he was a "
            "pessimist, but because he found that surprise amplified suffering. If you expect "
            "the world to be orderly and people to be reliable, every deviation feels like a "
            "personal affront. If you expect deviation, it arrives as confirmation rather than "
            "crisis.\n\n"
            "This is the Stoic practice of 'premeditatio malorum' applied to daily life. You "
            "are not hoping for the worst — you are inoculating yourself against surprise. The "
            "person who is never surprised is not jaded; they are prepared. And preparation is "
            "the foundation of calm.\n\n"
            "Before you start your day, acknowledge: people will be difficult, plans will change, "
            "things will break. Now proceed. You will handle all of it better for having expected "
            "it."
        ),
    },
    {
        "quote": "Associate with people who are likely to improve you. — SENECA",
        "reflection": (
            "Seneca was not being elitist. He was making a practical observation: character is "
            "contagious. You absorb the values, habits, and emotional patterns of the people you "
            "spend the most time with, whether you intend to or not. This is not a theory — it is "
            "a measurable social phenomenon that modern network science has confirmed.\n\n"
            "The reverse is equally true. Time spent with people who reinforce your worst "
            "tendencies — cynicism, laziness, complaint — does not stay neutral. It compounds. "
            "Seneca compared it to carrying a disease: you don't have to seek infection; "
            "proximity is enough.\n\n"
            "This does not mean abandoning old friends. It means being honest about the effect "
            "your social environment has on you, and being intentional about which influences "
            "you increase. Seek out the person who makes you want to be better — not through "
            "pressure, but through example."
        ),
    },
    {
        "quote": "First learn the meaning of what you say, and then speak. — EPICTETUS",
        "reflection": (
            "Epictetus noticed that his students often used philosophical terms they did not "
            "actually understand — 'virtue,' 'freedom,' 'nature' — parroting them in arguments "
            "to sound educated. He found this worse than ignorance, because it created the "
            "illusion of knowledge where none existed.\n\n"
            "The modern equivalent is everywhere. We use words like 'justice,' 'empathy,' "
            "'trauma,' and 'boundaries' with confidence but often without precision. The words "
            "become social signals rather than meaningful communication. When everyone is using "
            "the same terms to mean different things, conversation becomes performance rather "
            "than exchange.\n\n"
            "Before you deploy a strong word today — in an email, a conversation, an argument — "
            "pause and ask: do I know exactly what I mean by this? Can I define it without "
            "jargon? If not, find a simpler word that you actually own. Precision is a form of "
            "respect for both language and listener."
        ),
    },
    {
        "quote": "The key is to keep company only with people who uplift you. — MARCUS AURELIUS",
        "reflection": (
            "Marcus paired this advice with a candid admission: even as emperor, he struggled "
            "with the influence of negative people in his court. Proximity to power attracted "
            "flatterers, schemers, and cynics, and he had to actively guard his inner state "
            "against their influence. If the most powerful man in the world found this difficult, "
            "there is no shame in finding it difficult yourself.\n\n"
            "Uplifting does not mean comfortable. The best company often challenges you, tells "
            "you truths you would rather not hear, and holds you to standards you set for "
            "yourself but frequently slide on. Uplift is not about pleasant feelings — it is "
            "about becoming better.\n\n"
            "Identify one person in your life who consistently leaves you feeling more capable, "
            "more honest, or more energised after an interaction. Invest in that relationship. "
            "It is one of the few investments with guaranteed returns."
        ),
    },
    {
        "quote": "No person has the power to have everything they want, but it is in their power not to want what they don't have. — SENECA",
        "reflection": (
            "Seneca frames this as a power equation. Desire for what you don't have gives that "
            "absent thing power over your emotional state. The thing you crave — the promotion, "
            "the possession, the relationship — controls your mood from a distance, without "
            "even existing in your life yet. That is an extraordinary amount of power to grant "
            "something that isn't there.\n\n"
            "The Stoic move is to withdraw that power by withdrawing the desire. Not by forcing "
            "yourself not to want — that is just repression — but by examining whether the "
            "want is real. Most wants are borrowed from culture, comparison, or habit. When "
            "you strip those away, the genuine desires are far fewer and far more achievable.\n\n"
            "Today, examine one thing you want. Ask: if no one would ever know I had this, "
            "would I still want it? The answer separates genuine desire from social performance."
        ),
    },
    {
        "quote": "Be tolerant with others and strict with yourself. — MARCUS AURELIUS",
        "reflection": (
            "Marcus prescribed the exact opposite of what most people practise. The natural "
            "tendency is to judge others harshly and give yourself the benefit of the doubt. "
            "You know your own intentions, your context, your mitigating circumstances — you "
            "grant yourself infinite nuance. Others get their behaviour read at face value.\n\n"
            "Reversing this creates a remarkable shift. Tolerance with others means extending "
            "the same contextual understanding you give yourself — they, too, have reasons, "
            "pressures, and blind spots. Strictness with yourself means holding yourself to "
            "standards regardless of whether anyone is watching.\n\n"
            "This is not self-punishment. It is a recognition that the only behaviour you can "
            "actually improve is your own. The energy spent judging others produces nothing. "
            "The energy spent refining yourself compounds daily."
        ),
    },
    {
        "quote": "Think of the life you have lived until now as over and done with. — MARCUS AURELIUS",
        "reflection": (
            "This sounds morbid, but Marcus meant it as liberation. If your previous life is "
            "over — with all its mistakes, regrets, wasted time, and missed opportunities — then "
            "right now you are at the beginning of a new one. You are not dragging the past "
            "behind you; you are starting fresh, with the benefit of everything you learned.\n\n"
            "Most people carry their history like a debt they owe. Past failures become evidence "
            "of future incapacity. Past mistakes become identity. Marcus says: let the ledger "
            "close. The person who made those mistakes is gone. The person reading this is new, "
            "with new resources and a new opportunity.\n\n"
            "If your life started today, what would you do differently? That question is not "
            "hypothetical — Marcus is telling you it did start today. Act accordingly."
        ),
    },
    {
        "quote": "Our anxiety does not come from thinking about the future, but from wanting to control it. — SENECA",
        "reflection": (
            "Seneca isolates the mechanism with surgical precision. Thinking about the future is "
            "not inherently anxious. Planning, strategising, imagining possibilities — these can "
            "be calm, even enjoyable. Anxiety enters the moment you shift from 'what might happen' "
            "to 'what must happen.' The need for a specific outcome is the source of the tension.\n\n"
            "Control is the drug of choice for anxious minds. If I can just control this variable, "
            "then I'll feel safe. But the future has too many variables for any single mind to "
            "control, and the attempt to do so produces escalating anxiety as the impossibility "
            "becomes clearer.\n\n"
            "The antidote is not to stop thinking about the future but to release your grip on "
            "it. Think, plan, prepare — then let go of the outcome. The preparation was the part "
            "you controlled. The rest was never yours."
        ),
    },
    {
        "quote": "Nature does not hurry, yet everything is accomplished. — LAO TZU (Stoic influence)",
        "reflection": (
            "Though Lao Tzu predates the Greek Stoics by roughly two centuries, this insight "
            "resonates deeply with Stoic philosophy. Both traditions observed that the natural "
            "order operates without urgency — seasons turn, rivers carve canyons, trees grow — "
            "and the results are more durable than anything produced by human haste.\n\n"
            "Urgency is often a sign that you are fighting the natural rhythm of the work. Some "
            "things genuinely need speed. But most of what feels urgent is actually just anxious — "
            "you are rushing not because the task requires it, but because your nervous system "
            "wants the discomfort of incompleteness to end.\n\n"
            "Consider one project you're rushing through. What would it look like to do it at "
            "the pace it actually requires? Not slower for the sake of slowness — at the pace "
            "that produces the quality you actually want. That pace often feels uncomfortably "
            "slow, but the results speak for themselves."
        ),
    },
    {
        "quote": "Keep your attention focused entirely on what is truly your own concern. — MARCUS AURELIUS",
        "reflection": (
            "Marcus drew a hard line between his concern and everyone else's. His concern: his "
            "own character, judgement, and effort. Not his concern: other people's opinions of "
            "him, the outcome of battles he had already commanded as well as he could, the "
            "political manoeuvring of the Senate. This focus was not selfish — it was efficient.\n\n"
            "Most people spend the majority of their attention on things that are not their "
            "concern — other people's behaviour, events they cannot influence, problems that "
            "have not yet occurred. This feels productive because it feels busy. But it produces "
            "nothing except anxiety and the illusion of engagement.\n\n"
            "For one hour today, restrict your attention to what is genuinely yours: the task in "
            "front of you, the quality of your effort, the choices you are making. Notice how "
            "much quieter the hour is. That quiet is not emptiness — it is focus."
        ),
    },
    {
        "quote": "You could leave life right now. Let that determine what you do and say and think. — MARCUS AURELIUS",
        "reflection": (
            "Marcus did not write this as a dark thought. He wrote it as the ultimate priority "
            "filter. If you could leave life right now — and you could; no one has a guarantee — "
            "then everything trivial is instantly revealed as trivial. The grudge you're holding, "
            "the argument you're preparing, the pointless worry — none of it survives the "
            "proximity of mortality.\n\n"
            "The Stoics practiced 'memento mori' not to be morbid but to be awake. Death is not "
            "the enemy — sleepwalking through life is the enemy. The awareness that time is "
            "finite is the sharpest tool for cutting through distraction and focusing on what "
            "actually matters.\n\n"
            "Apply it right now: if this were your last day, would you spend it doing what you're "
            "about to do? If the answer is yes, proceed with full attention. If the answer is no, "
            "that's important information. You don't have to change everything — but you should "
            "at least notice."
        ),
    },
    {
        "quote": "If you aren't willing to have a bad day, you'll never have a good life. — SENECA",
        "reflection": (
            "Seneca's logic is airtight: a good life is not a life without bad days — it is a "
            "life in which bad days are accepted as part of the cost. The person who requires "
            "every day to be pleasant will either retreat from everything that carries risk "
            "(which is everything worthwhile) or collapse when a bad day inevitably arrives.\n\n"
            "Bad days are not failures of planning. They are the admission price for meaningful "
            "engagement with a world you don't control. The entrepreneur has bad quarters. The "
            "athlete has bad games. The parent has bad nights. None of these invalidate the "
            "overall endeavour — they are the endeavour.\n\n"
            "When today goes badly — and someday soon it will — resist the urge to conclude "
            "that something is fundamentally wrong. A bad day inside a good life is just weather. "
            "It passes."
        ),
    },
    {
        "quote": "It's not what happens to you, but how you handle it. — EPICTETUS",
        "reflection": (
            "This is a compressed restatement of Epictetus's core teaching, and the repetition "
            "across his works is deliberate — he believed students needed to hear the same truth "
            "in different forms until it became instinct rather than theory. Knowing the principle "
            "intellectually is easy. Living it when your plans collapse is the actual work.\n\n"
            "The word 'handle' is practical. Epictetus was not asking for philosophical "
            "detachment. He was asking for skilled response. A carpenter handles wood. A sailor "
            "handles wind. Neither denies the material — they work with it. Your circumstances "
            "are your material.\n\n"
            "Today, when something doesn't go as planned, catch the moment between event and "
            "response. That moment is your workshop. What you build there — patience, creativity, "
            "resilience — is more valuable than whatever the event took from you."
        ),
    },
    {
        "quote": "The best answer to anger is silence. — MARCUS AURELIUS",
        "reflection": (
            "Marcus learned this from observing the imperial court, where angry words spoken by "
            "the emperor became policy. A moment's rage could become a death sentence, a "
            "banishment, or a war. The stakes of his anger were uniquely high, but the principle "
            "scales down to every conversation you have.\n\n"
            "Silence in the face of anger is not passivity. It is the highest form of self-control. "
            "Anger wants a reaction — it wants you to escalate, to match intensity, to engage on "
            "its terms. Silence refuses the invitation. It creates a space where the anger, "
            "finding nothing to feed on, often burns itself out.\n\n"
            "The next time someone directs anger at you, try waiting five seconds before "
            "responding. Not five seconds of composing a retort — five seconds of genuine "
            "silence. You'll be surprised how often the situation de-escalates on its own."
        ),
    },
    {
        "quote": "He who is brave is free. — SENECA",
        "reflection": (
            "Seneca links courage and freedom because he understood that most unfreedom is "
            "voluntary — we choose captivity because the alternative is frightening. We stay "
            "in jobs we hate because leaving is scary. We stay silent about things that matter "
            "because speaking up is risky. We avoid hard conversations because conflict is "
            "uncomfortable. In each case, fear is the jailer.\n\n"
            "Bravery does not mean the absence of fear. It means acting despite fear. The brave "
            "person feels the same dread as the coward — they just refuse to let it make the "
            "decision. That refusal is freedom, because it means your choices are governed by "
            "your values, not your anxieties.\n\n"
            "Identify one thing you're avoiding out of fear today. You don't have to charge at "
            "it heroically. Just take one step toward it. Courage is not a single leap — it is "
            "a series of steps that eventually cover the distance."
        ),
    },
    {
        "quote": "What we do now echoes in eternity. — MARCUS AURELIUS",
        "reflection": (
            "Marcus wrote this not as a promise of personal immortality — the Stoics were "
            "uncertain about the afterlife — but as an observation about consequence. Every "
            "action sets something in motion that outlives the actor. The decision you make "
            "today affects people you will never meet, in ways you cannot predict, across "
            "timescales you will not witness.\n\n"
            "This is both inspiring and sobering. It means that your small, daily choices — how "
            "you treat the person in front of you, whether you do your work with care, whether "
            "you choose integrity when no one is looking — have consequences that compound far "
            "beyond your own life.\n\n"
            "You don't have to do something dramatic to echo in eternity. You have to do what "
            "you're doing with the awareness that it matters. Because it does — more than you "
            "can see from here."
        ),
    },
    {
        "quote": "Don't explain your philosophy. Embody it. — EPICTETUS",
        "reflection": (
            "Epictetus had little patience for students who could quote Chrysippus but couldn't "
            "control their temper. He taught that philosophy is not a body of knowledge — it is "
            "a way of living. The person who can recite Stoic principles but panics at the first "
            "inconvenience has learned nothing. The person who has never read a page of philosophy "
            "but meets difficulty with grace has learned everything.\n\n"
            "Explanation is easy and addictive. It lets you feel wise without being tested. But "
            "embodiment is the only proof that counts. Your philosophy is not what you say you "
            "believe — it is what you do under pressure, when no one is watching, when the cost "
            "of your principles becomes real.\n\n"
            "Today, instead of explaining what you believe to anyone (including yourself), "
            "demonstrate it. Let your actions be the lecture. The people around you will learn "
            "more from one consistent example than from a hundred eloquent explanations."
        ),
    },
    {
        "quote": "We are time's subjects, and time bids be gone. — MARCUS AURELIUS",
        "reflection": (
            "Marcus often wrote about impermanence because he was watching it in real time — "
            "plague, war, and the natural ageing of his own body. This line acknowledges a "
            "fact that most people spend enormous energy avoiding: time is not a resource you "
            "manage. It is a current you are carried by. You cannot save it, pause it, or "
            "reverse it. You can only decide what you do while it moves.\n\n"
            "The phrase 'bids be gone' is not grim — it is urgent. Time does not ask permission. "
            "It does not wait for you to be ready. The departure is happening now, in slow "
            "motion, and the only response that honours the reality is to be fully present for "
            "what remains.\n\n"
            "This is not a call to panic. It is a call to attention. You are not running out "
            "of time — you are made of time. Spend yourself on what matters."
        ),
    },
    {
        "quote": "To be free of passion and yet full of love. — MARCUS AURELIUS",
        "reflection": (
            "This line captures a distinction that is often lost in translation. The Stoic "
            "'apatheia' — freedom from destructive passion — is not emotional deadness. It is "
            "freedom from being controlled by emotion. Marcus is describing someone who loves "
            "deeply but is not enslaved by that love, who feels strongly but is not tossed "
            "around by their feelings.\n\n"
            "The difference is between being moved and being moved around. Love that is grounded "
            "in choice and character is stable — it endures disappointment, survives conflict, "
            "and deepens over time. Love that is driven by passion is volatile — it is intense "
            "but fragile, dependent on the other person behaving in ways that sustain the "
            "feeling.\n\n"
            "The aspiration is not to feel less but to feel clearly — to love without "
            "neediness, to care without anxiety, to engage without losing yourself. That is "
            "the Stoic ideal at its most human."
        ),
    },
    {
        "quote": "The impediment to action advances action. What stands in the way becomes the way. — MARCUS AURELIUS",
        "reflection": (
            "Marcus wrote this in the Meditations while managing a plague, border wars, and "
            "betrayal by a trusted general. It was not an affirmation taped to a mirror — it "
            "was a survival strategy written by a man who had every reason to quit.\n\n"
            "The idea is not that obstacles are secretly good. It is that your response to them "
            "is the only territory you actually control. A blocked path forces a creative "
            "reroute. A rejection sharpens your understanding of what you actually want. The "
            "obstacle does not disappear — but it stops being separate from the work.\n\n"
            "Today, when something blocks your progress, resist the urge to wait for the "
            "blockage to clear. Ask instead: what skill, patience, or perspective is this "
            "forcing me to develop? That development is not a detour — it is the point."
        ),
    },
    {
        "quote": "Do not act as if you were going to live ten thousand years. — MARCUS AURELIUS",
        "reflection": (
            "The full passage ends: 'Death hangs over thee. While thou livest, while it is in "
            "thy power, be good.' Marcus was not being melodramatic. He was correcting a "
            "cognitive bias that all humans share — the assumption that there is always more "
            "time. This assumption permits infinite postponement of everything that matters.\n\n"
            "The person who acts as if they have ten thousand years treats today as expendable. "
            "They defer meaningful work, avoid difficult conversations, and waste hours on "
            "trivia, confident that there will be time to course-correct later. But 'later' is "
            "a promissory note that may never be cashed.\n\n"
            "This does not mean live in panic. It means live in focus. If your time is finite — "
            "and it is — then how you spend today is not a rehearsal. It is the performance."
        ),
    },
    {
        "quote": "The man who has done his best shall not be injured by the results. — MARCUS AURELIUS",
        "reflection": (
            "Marcus separates effort from outcome with the precision of a surgeon. Your best "
            "effort is yours — it reflects your character, your preparation, your commitment. "
            "The result is not yours — it is the product of your effort combined with countless "
            "variables you did not control. Confusing the two is the source of most professional "
            "and personal anguish.\n\n"
            "This is not permission to be indifferent to results. It is a framework for "
            "interpreting them. If you gave your best and the result was poor, the result is "
            "information about the world, not a verdict on your worth. If you gave less than "
            "your best and the result was good, the result is luck, not evidence of your skill.\n\n"
            "Today, focus on the quality of your effort rather than the reception it gets. "
            "You cannot control applause. You can control whether you deserve it."
        ),
    },
    {
        "quote": "Loss is nothing else but change, and change is Nature's delight. — MARCUS AURELIUS",
        "reflection": (
            "Marcus reframes loss as transformation rather than destruction. The tree that loses "
            "its leaves in autumn is not diminished — it is changing form. The person who loses "
            "a job, a relationship, or a phase of life is not being robbed — they are being "
            "moved from one state to another. The loss is real, but it is also the mechanism "
            "by which something new becomes possible.\n\n"
            "This is not minimising grief. Loss hurts precisely because what was lost mattered. "
            "But Marcus asks: can you hold the grief and the understanding simultaneously? Can "
            "you feel the loss fully while also recognising that change — including painful "
            "change — is how the universe works?\n\n"
            "When you lose something today — even something small — notice the impulse to resist "
            "the change. Then notice what is becoming possible in the space that was created. "
            "Both are real. The loss and the opening exist at the same time."
        ),
    },
    {
        "quote": "A man's worth is no greater than his ambitions. — MARCUS AURELIUS",
        "reflection": (
            "Marcus is not praising ambition for its own sake. He is saying that your ambitions "
            "reveal what you value — and what you value determines your ceiling. The person who "
            "aspires only to comfort will never produce courage. The person who aspires only to "
            "wealth will never develop generosity. Your ambitions are not just goals; they are "
            "the mould in which your character is cast.\n\n"
            "This also works as a diagnostic. Look at your ambitions honestly. Not the ones you "
            "announce publicly — the real ones, the ones that drive your daily behaviour. If "
            "your actual ambitions are smaller than the person you want to be, the gap will "
            "show in your character.\n\n"
            "Consider raising the ambition — not in scale, but in depth. Not 'earn more' but "
            "'become someone who creates genuine value.' Not 'be respected' but 'be worth "
            "respecting.' The shift from external to internal ambition changes everything."
        ),
    },
    {
        "quote": "Never be afraid to raise your voice for honesty and truth and compassion. — MARCUS AURELIUS",
        "reflection": (
            "Marcus wrote this knowing the cost of speaking truth to power — he was power, and "
            "even he found it difficult to hear. The people around him had every incentive to "
            "flatter and none to challenge. Those rare individuals who spoke honestly to him "
            "were the ones he valued most, precisely because they took the risk.\n\n"
            "Speaking up for honesty and compassion is a risk because it often conflicts with "
            "convenience, social harmony, and self-interest. The easiest response is almost "
            "always silence. But silence in the face of dishonesty is not neutrality — it is "
            "permission. And silence in the face of cruelty is not peace — it is complicity.\n\n"
            "You do not have to be loud to raise your voice. Quiet, clear, consistent truth-telling "
            "is more powerful than any shout. The courage is in the speaking, not the volume."
        ),
    },
    {
        "quote": "Here is a rule to remember in future, when anything tempts you to feel bitter. — MARCUS AURELIUS",
        "reflection": (
            "The full passage continues: 'Not, this is a misfortune, but, to bear this worthily "
            "is good fortune.' Marcus is proposing a real-time reframe — a rule you can apply "
            "in the moment when bitterness starts to take hold. The event is fixed. Your "
            "interpretation is not.\n\n"
            "Bitterness is seductive because it feels like justice. Someone wronged you, and "
            "the bitterness is your way of registering the injustice. But Marcus saw that "
            "bitterness does not correct the injustice — it extends it. Now you are not only "
            "wronged by the event but also poisoned by your own response to it.\n\n"
            "The alternative is not forgiveness in the sentimental sense. It is pragmatism. "
            "The question is not 'do they deserve my bitterness?' but 'does holding bitterness "
            "serve me?' The answer is always no. Set it down — not for their sake, but for yours."
        ),
    },
    {
        "quote": "If it is not right do not do it; if it is not true do not say it. — MARCUS AURELIUS",
        "reflection": (
            "Marcus repeats this principle in slightly different forms across the Meditations — "
            "a sign that he needed to remind himself regularly. Knowing what is right and true "
            "is rarely the problem. Doing and saying it when there is a cost — social, "
            "professional, emotional — is where the difficulty lies.\n\n"
            "The elegance of the rule is its binary simplicity. There is no sliding scale, no "
            "'right enough' or 'mostly true.' The threshold is absolute, which eliminates the "
            "mental energy spent on rationalisation. You don't have to decide how much wrongness "
            "is acceptable. The answer is always: none.\n\n"
            "This is impossibly hard to follow perfectly — Marcus certainly didn't claim to. "
            "But the clarity of the standard is the point. Even imperfect adherence to a clear "
            "rule produces better results than perfect adherence to a vague one."
        ),
    },
    {
        "quote": "The universe is change; our life is what our thoughts make it. — MARCUS AURELIUS",
        "reflection": (
            "Marcus combines two observations into a single line. First: everything external is "
            "in constant flux — empires, bodies, seasons, relationships. Resistance to this flux "
            "is the primary source of suffering. Second: within the flux, the one stable element "
            "is the quality of your thinking. The universe changes around you; your interpretation "
            "of it is the only constant you control.\n\n"
            "These two ideas support each other. Because everything changes, attachment to any "
            "particular state guarantees disappointment. But because your thinking is yours, you "
            "always have the ability to adjust your relationship to whatever is happening. The "
            "world is a river; your mind is the bridge.\n\n"
            "When things shift today — and they will — notice whether you are resisting the "
            "change or adapting to it. Resistance feels strong but produces rigidity. Adaptation "
            "feels uncertain but produces resilience."
        ),
    },
    {
        "quote": "That which is really beautiful has no need of anything. — MARCUS AURELIUS",
        "reflection": (
            "Marcus observed that the things he found most beautiful — a ripe olive, a crack in "
            "bread, the face of an ageing person — had no need of explanation, justification, "
            "or enhancement. Their beauty was inherent, not added. It required no frame, no "
            "context, no audience.\n\n"
            "Apply this to character. The person who is genuinely kind does not need recognition "
            "for their kindness. The person who is genuinely skilled does not need constant "
            "validation. The need for external confirmation is a signal that the quality in "
            "question is not yet fully owned — it is still performative rather than intrinsic.\n\n"
            "Consider where you are seeking validation for something you already know to be true. "
            "If the work is good, it does not need applause to be good. If your character is "
            "solid, it does not need witnesses. The beautiful thing is complete in itself."
        ),
    },
    {
        "quote": "Be strict with yourself and lenient with others. — MARCUS AURELIUS",
        "reflection": (
            "This is a restatement of an earlier principle, and its repetition in the Meditations "
            "suggests Marcus struggled with it. He was the chief judge of the empire — literally "
            "tasked with judging others — and he knew the gravitational pull of harsh judgement. "
            "The power to condemn was always at hand, and restraint was a daily discipline.\n\n"
            "Leniency with others is not weakness. It is the recognition that you see only the "
            "surface of their situation — their actions — while they experience the full depth "
            "of their context, pressures, and limitations. Strictness with yourself is not "
            "punishment. It is the recognition that you see the full depth of your own situation "
            "and therefore have no excuse for less than your best.\n\n"
            "The practice is to extend to others the understanding you would want for yourself, "
            "while holding yourself to the standards you wish others would meet."
        ),
    },
    {
        "quote": "When you are offended at any man's fault, turn to yourself and study your own failings. — MARCUS AURELIUS",
        "reflection": (
            "Marcus used this as a daily practice — whenever he felt judgement rising toward "
            "someone, he turned the lens on himself. Not to find the same fault (though often "
            "he did), but to remember that he too was a work in progress. The recognition of "
            "shared imperfection dissolves the righteousness that fuels most interpersonal "
            "conflict.\n\n"
            "This is not self-flagellation. It is perspective. The anger you feel at someone "
            "else's fault is almost always amplified by a sense of moral distance — 'I would "
            "never do that.' But honest self-examination usually shrinks that distance. You may "
            "not share their specific fault, but you share the condition of being imperfect.\n\n"
            "When someone irritates you today, take thirty seconds to identify one of your own "
            "shortcomings. The irritation will not vanish, but it will lose its edge. That edge "
            "was never about them — it was about your unexamined self."
        ),
    },
    {
        "quote": "The art of living is more like wrestling than dancing. — MARCUS AURELIUS",
        "reflection": (
            "Marcus chose this metaphor deliberately. Dancing is choreographed, predictable, "
            "graceful — you know the steps in advance. Wrestling is reactive, unpredictable, "
            "and messy — your opponent dictates half of what happens, and you must respond in "
            "real time with whatever position you find yourself in.\n\n"
            "Life is wrestling. You cannot choreograph it. Plans break, people surprise you, "
            "and the ground shifts without warning. The skill that matters is not the ability "
            "to execute a perfect routine but the ability to maintain your footing when pushed "
            "off balance — to stay grounded regardless of what the opponent does.\n\n"
            "Today, when something disrupts your plan, notice the urge to force reality back "
            "into the choreography. Instead, wrestle with what is actually happening. Adapt "
            "your stance. Use the momentum of the disruption. That is the art."
        ),
    },
    {
        "quote": "How much more grievous are the consequences of anger than the causes of it. — MARCUS AURELIUS",
        "reflection": (
            "Marcus observed that anger almost always creates more damage than the event that "
            "triggered it. The original offence might be minor — a rude comment, a broken "
            "promise, an inconvenience. But the anger response — harsh words, damaged "
            "relationships, impulsive decisions — can be catastrophic and irreversible.\n\n"
            "Anger is biochemically designed to override judgement. It narrows your focus, "
            "speeds your heart rate, and prepares you for physical action. In a survival "
            "situation, this is useful. In a conversation, an email, or a meeting, it is "
            "a disaster. The action that feels justified in the moment of anger almost never "
            "looks justified an hour later.\n\n"
            "The Stoic practice is not to eliminate anger but to insert a delay. When you feel "
            "it rising, do nothing for sixty seconds. The anger may still be there after the "
            "delay — but the impulse to act on it rarely survives the pause."
        ),
    },
    {
        "quote": "The opinion of ten thousand men is of no value if none of them know anything about the subject. — MARCUS AURELIUS",
        "reflection": (
            "Marcus dealt with crowds, popular opinion, and political pressure daily. He learned "
            "that consensus is not correlated with truth — especially when the consensus is "
            "formed by people who lack relevant knowledge. Ten thousand people agreeing on "
            "something they don't understand is just a large group being wrong together.\n\n"
            "This principle is increasingly relevant. Social media amplifies opinion without "
            "filtering for expertise. Viral takes outperform careful analysis. The number of "
            "people who agree with a position is presented as evidence for it, when it is "
            "often just evidence of the position's emotional appeal.\n\n"
            "Before you accept or reject any widely held opinion, ask: who actually knows about "
            "this? Not who has opinions — who has knowledge? One informed voice is worth more "
            "than a million uninformed ones. Including, sometimes, your own."
        ),
    },
    {
        "quote": "Accept whatever comes to you woven in the pattern of your destiny. — MARCUS AURELIUS",
        "reflection": (
            "Marcus believed in a rational Providence — a cosmic order in which events unfold "
            "according to a logic that individual humans cannot always see. Accepting what comes "
            "'woven in the pattern' is not fatalism. It is trust that the fabric of reality is "
            "larger than your ability to understand it from any single thread.\n\n"
            "The practical implication is this: resistance to what has already happened is "
            "always wasted energy. The event is here. It is woven in. You cannot un-weave it. "
            "The only productive question is: given that this has happened, what is my best "
            "response?\n\n"
            "This is not passivity toward the future — you can and should act to shape it. But "
            "toward the past and the present, acceptance is the only rational posture. What is, "
            "is. Start there."
        ),
    },
    {
        "quote": "The best revenge is not to be like your enemy. — MARCUS AURELIUS",
        "reflection": (
            "This is a variation on an earlier entry, and its recurrence in the Meditations "
            "shows how much Marcus wrestled with the desire for retaliation. He was not above "
            "anger — he was a human being with immense power and constant provocation. The "
            "repetition is the practice: reminding himself, again and again, that revenge "
            "degrades the avenger.\n\n"
            "The logic is clean. Your enemy behaved badly. If you retaliate in kind, there are "
            "now two people behaving badly. The injury has not been corrected — it has been "
            "doubled. The only response that actually reduces the total amount of wrong in the "
            "situation is to refuse to add to it.\n\n"
            "This is not about being the bigger person for show. It is about preserving "
            "something more valuable than satisfaction: your own character. Revenge spends "
            "that currency for a momentary high. Restraint compounds it."
        ),
    },
    {
        "quote": "What we do now echoes in eternity. — MARCUS AURELIUS",
        "reflection": (
            "This quote appears twice in common collections, and its repetition is fitting — "
            "echoes, by definition, repeat. Marcus's point is about causal chains: your actions "
            "today set in motion consequences that ripple outward indefinitely. A decision to be "
            "kind, a choice to do careful work, a moment of courage — each one affects the next "
            "person, who affects the next, in a chain you will never see the end of.\n\n"
            "This can feel like pressure, but Marcus meant it as meaning. If your actions echo, "
            "then nothing you do is trivial. The small kindness matters. The careful work "
            "matters. The private integrity matters. All of it propagates.\n\n"
            "Live today as if your actions have consequences beyond what you can measure. They "
            "do. And the fact that you will never see most of those consequences does not "
            "diminish them — it magnifies the importance of getting the original action right."
        ),
    },
    {
        "quote": "We must take a higher view of all things. — MARCUS AURELIUS",
        "reflection": (
            "Marcus practised what he called 'the view from above' — a mental exercise in which "
            "he imagined looking down on his own situation from a great height. From that "
            "altitude, personal grievances shrink, political dramas diminish, and the patterns "
            "of nature become visible. The exercise did not make his problems disappear; it "
            "placed them in proportion.\n\n"
            "The higher view is not detachment — it is context. A traffic jam is maddening at "
            "ground level. From a satellite, it is a pattern of movement. A personal conflict "
            "feels all-consuming from the inside. From a year's distance, it is a small episode "
            "in a larger story. Both perspectives are true. The higher one is usually more "
            "useful.\n\n"
            "When you feel overwhelmed today, try zooming out. What does this look like from "
            "a year away? From ten years? From the perspective of someone who loves you and "
            "sees the whole picture? The facts don't change. The frame does."
        ),
    },
    {
        "quote": "Do every act of your life as though it were your very last. — MARCUS AURELIUS",
        "reflection": (
            "Marcus does not mean this literally — he is not suggesting you write goodbye letters "
            "before breakfast. He is proposing a quality filter. If this were your last act, "
            "would you phone it in? Would you do it resentfully? Would you cut corners? The "
            "answer is almost always no. The awareness of finality concentrates effort and "
            "eliminates waste.\n\n"
            "Applied practically, this means treating each task — even mundane ones — with a "
            "level of care and presence that reflects its actual importance. The email you write "
            "carelessly affects the person who reads it. The conversation you half-attend shapes "
            "the relationship. Nothing is too small to warrant your full attention.\n\n"
            "Pick one task today and do it as if it's the last thing you'll ever do. Not "
            "frantically — excellently. With full attention and genuine care. That quality of "
            "attention is transferable to everything else."
        ),
    },
    {
        "quote": "No man is happy who does not think himself so. — MARCUS AURELIUS",
        "reflection": (
            "Marcus makes an empirical claim: happiness requires self-recognition. You can have "
            "every ingredient of a good life — health, relationships, purpose, security — and "
            "still be miserable if your internal narrative does not acknowledge what you have. "
            "Conversely, a person with far less who recognises their own contentment is, by "
            "definition, content.\n\n"
            "This is not 'fake it till you make it.' It is an observation about the structure "
            "of happiness. External conditions are necessary but not sufficient. The final "
            "ingredient is always internal — the judgement that what you have is enough, that "
            "your life as it is has value.\n\n"
            "Ask yourself today: am I happy and not noticing, or am I unhappy for reasons that "
            "would survive honest examination? Sometimes the problem is real. But sometimes the "
            "problem is that you are looking through the wrong lens at a life that is already good."
        ),
    },
    {
        "quote": "The things you think about determine the quality of your mind. — MARCUS AURELIUS",
        "reflection": (
            "Marcus returns to the theme of mental cultivation because he believed it was the "
            "single most important practice available to a human being. Your thoughts are not "
            "random weather — they are crops you tend. Tend cynicism and you harvest a cynical "
            "mind. Tend gratitude and you harvest a grateful one. The harvest is determined by "
            "the seeds, and the seeds are your habitual thoughts.\n\n"
            "This is not about controlling every thought — that is impossible and exhausting. It "
            "is about choosing which thoughts you water. The anxious thought and the courageous "
            "thought both arrive uninvited. Which one you dwell on, return to, and build upon is "
            "your choice.\n\n"
            "Notice the three thoughts you return to most frequently today. Those are not just "
            "thoughts — they are the construction materials of your mind. Are you building "
            "something you want to live in?"
        ),
    },
    {
        "quote": "Very little is necessary to live a happy life. — MARCUS AURELIUS",
        "reflection": (
            "Marcus closes the Meditations with the same insight that opens much of Stoic "
            "philosophy: the good life is simpler than you think. Not easier — simpler. The "
            "requirements are few: sound judgement, honest relationships, meaningful work, "
            "physical health, and self-awareness. Everything beyond that is preference, not "
            "necessity.\n\n"
            "Consumer culture inverts this equation. It teaches that happiness is always one "
            "purchase, one achievement, one life change away. The result is a permanent state "
            "of insufficiency — the feeling that you don't yet have enough to be happy. Marcus, "
            "who had everything the material world could offer, reports from the summit: the "
            "view is the same.\n\n"
            "Take inventory today. Not of what you want, but of what you need. The list is "
            "shorter than you expect. And most of it — perhaps all of it — you already have."
        ),
    },
]

# --- All 101 quotes with reflections ---


OPENCLAW_HOME = os.environ.get('OPENCLAW_HOME', os.path.expanduser('~/.openclaw'))


def get_quote():
    day_of_year = datetime.now().timetuple().tm_yday
    entry = QUOTES[(day_of_year - 1) % len(QUOTES)]
    return entry


def main():
    entry = get_quote()
    quote = entry["quote"]
    reflection = entry["reflection"]

    msg = (
        f"\u2600\ufe0f *Daily Stoic*\n\n"
        f"_{quote}_\n\n"
        f"{reflection}\n\n"
        f"\u2014 via The Daily Stoic"
    )

    # Write to a file for the cron job to pick up
    output_path = os.path.join(OPENCLAW_HOME, 'stoic-quote.json')
    with open(output_path, 'w') as f:
        json.dump({'message': msg}, f)

    print(msg)


if __name__ == '__main__':
    main()
