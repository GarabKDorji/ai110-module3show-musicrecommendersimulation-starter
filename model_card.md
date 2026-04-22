# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder 1.0 tries to predict which songs a user will enjoy based on their stated taste preferences. Given a user profile — a favorite genre, a favorite mood, and numeric targets for energy, acousticness, tempo, and valence — it scores every song in the catalog and returns the top 5 most similar matches. The goal is not to learn from listening history but to show how measurable song features can be compared directly to a listener's preferences.

---

## 3. Data Used

- **Catalog size:** 18 songs
- **Features per song:** genre, mood, energy (0–1), tempo in BPM, valence (0–1), danceability (0–1), acousticness (0–1)
- **Genres covered:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, country, EDM, R&B, metal, folk, electronic, blues
- **Moods covered:** happy, chill, intense, relaxed, moody, focused, sad, nostalgic, euphoric, romantic, angry
- **Limits:** Most genres have only one song. Lofi has 3, pop has 2, and every other genre has 1. This means users who prefer metal, blues, folk, or country will get very little variety in their results. The data does not include lyrics, language, cultural context, or listening history.

---

## 4. Algorithm Summary

The system compares each song to the user's preferences using a point-based scoring rule:

- If a song's **genre** matches the user's favorite genre, it earns **+1.5 points**
- If a song's **mood** matches the user's favorite mood, it earns **+1.0 point**
- For **energy**, the system measures how close the song's energy is to what the user wants. A perfect match scores the full **1.5 points**; a big mismatch scores close to 0.
- The same closeness calculation is applied to **acousticness** (worth up to 1.25 points), **tempo** (up to 0.75 points), and **valence** (up to 0.50 points)

All points are added up. The maximum any song can score is **6.50**. Songs are then sorted from highest to lowest score and the top 5 are returned with a plain-language explanation of why each one was chosen.

---

## 5. Observed Behavior / Biases

**The genre bonus is too powerful.** A genre match alone gives a song 1.5 points before any numeric features are checked. This means a song that matches your genre but sounds nothing like what you described can still beat a song that is numerically perfect but in the wrong genre. In testing, a slow blues song (energy 0.39) ranked #1 for a user who wanted high-energy (0.90) sad music — only because the genre and mood bonuses outweighed the energy mismatch.

**Single-genre users are poorly served.** If your favorite genre has only one song in the catalog (metal, blues, folk, country), you get one strong result followed by four unrelated filler songs. The system was not designed with catalog balance in mind.

**No surprises.** The system always recommends the most similar songs, never the most interesting. A lofi user will always see the same three lofi songs at the top, in almost the same order, every time. There is no mechanism to introduce variety or help users discover something outside their usual taste.

---

## 6. Evaluation Process

Six user profiles were tested against the 18-song catalog:

| Profile | Genre | Mood | Energy |
|---|---|---|---|
| High-Energy Pop | pop | happy | 0.90 |
| Chill Lofi | lofi | chill | 0.38 |
| Deep Intense Rock | rock | intense | 0.95 |
| Conflicting (edge case) | blues | sad | 0.90 |
| Genre Orphan (edge case) | metal | angry | 0.96 |
| All-Middle (edge case) | jazz | relaxed | 0.50 |

**High-Energy Pop vs. Chill Lofi** — These are near-opposites and the results were clearly different. Pop got loud, fast tracks; lofi got quiet, slow ones. One surprise: "Gym Hero" kept appearing for pop users even though its mood is "intense" not "happy." The system saw that it was a pop song with matching energy and gave it a high score. It did not notice the mood difference mattered.

**Chill Lofi vs. Deep Intense Rock** — The system handled these correctly. Once the one rock song was matched, the remaining slots filled with high-energy genres (EDM, electronic). For the lofi user, the remaining slots filled with calm genres (ambient, blues). The system genuinely separated the two listening contexts.

**Deep Intense Rock vs. Conflicting (high energy + sad mood)** — The rock user correctly got Storm Runner at #1. The conflicting user got Rainy Season — a slow blues song — at #1, even though they wanted high-energy music. The genre and mood bonuses overrode a large energy mismatch. The system was "tricked" by a label match into ignoring what the numbers were saying.

**Genre Orphan vs. All-Middle** — Metal had only one catalog song so the orphan user got one near-perfect result and four unrelated ones. The all-middle user got Coffee Shop Stories at the top because its jazz/relaxed labels matched the profile's genre and mood — even though the user set every numeric target to 0.5 and the song's acousticness was 0.89. In both cases the categorical bonus dominated the result in a way that felt unfair.

A weight-shift experiment was also run — energy doubled, genre halved. It fixed the conflicting profile but made the genre orphan result worse. One fix broke another user type, which confirmed that there is no single set of weights that works well for all users with this small a catalog.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- Classroom exploration of how content-based recommendation systems work
- Learning how numeric features and weighted scoring produce ranked results
- Demonstrating bias and limitations of simple scoring rules

**Not intended for:**
- Real music listeners expecting accurate or diverse recommendations
- Any production or commercial use
- Representing or profiling real users — the user profiles are fictional test cases
- Drawing conclusions about actual music taste — the 18-song catalog is far too small to generalize

---

## 8. Ideas for Improvement

1. **Add diversity enforcement.** After scoring, check if the top 5 all share the same genre. If they do, replace the lowest-scoring duplicate with the highest-scoring song from a different genre. This would help users discover music outside their usual bubble.

2. **Balance the catalog.** Every genre should have at least 3 songs before it can serve users meaningfully. Right now, 9 of 15 genres have only one song — making the system essentially useless for those listeners beyond the first result.

3. **Make the energy gap directional.** Instead of treating "too calm" and "too loud" as equally bad, add a preference flag. A high-energy user who gets a quiet song should be penalized more than a quiet user who gets a slightly loud song. This would make the scoring match how real listeners actually experience mismatches.

---

## 9. Personal Reflection

**Biggest learning moment**

The biggest learning moment came during the edge case experiments, specifically when the conflicting profile — a user who wanted high-energy but sad music — returned Rainy Season as the top result. Rainy Season has an energy of 0.39, and the user wanted 0.90. That is a massive mismatch. But the genre and mood bonuses added up to 2.5 points before a single numeric feature was even checked, and nothing else in the catalog could overcome that head start. That moment made it click that a recommender is not just math — it is a set of priorities encoded as numbers, and whoever chose those numbers decided what matters most. I chose them, and my choices had real consequences on what the system said. That is not obvious until you see it break.

**How AI tools helped, and when I had to double-check**

AI tools were genuinely useful for structuring the project — generating the initial song data in CSV format, suggesting weight strategies, explaining the difference between `.sort()` and `sorted()`, and helping format the terminal output cleanly. Where I had to slow down and verify was when the AI suggested code that looked correct but had subtle issues: the first version of `main.py` used a relative path for `songs.csv` that only worked if you ran the script from a specific directory. The AI did not flag that. I only caught it when the script crashed with a `FileNotFoundError`. The lesson is that AI tools are good at producing plausible-looking answers quickly, but plausible is not the same as correct — you still have to run the code and watch what actually happens.

**What surprised me about simple algorithms feeling like recommendations**

The most surprising thing was how quickly a handful of arithmetic operations started to feel like taste. When the Chill Lofi profile returned Library Rain and Midnight Coding at the top, those results genuinely made sense — not because the system understood music, but because the numbers happened to align. The system has no idea what lofi sounds like. It just knows that Library Rain has an energy value close to what the user typed in. But to someone listening, the output looks like the system "gets" them. That gap between what is actually happening inside the algorithm and what it feels like from the outside is probably the most important thing I will take from this project. Real recommendation systems exploit that gap at massive scale, and most users never think about what is behind it.

**What I would try next**

If I extended this project, the first thing I would add is a diversity rule — a check that prevents the top 5 from being dominated by one genre. After that, I would try replacing the flat genre bonus with a similarity score based on audio features alone, removing genre as a label entirely, and seeing whether the system can cluster similar-sounding songs without being told what genre they are. That would be a step toward how real systems like Spotify actually work — they do not just match labels, they compare audio fingerprints. I would also want to try a collaborative filtering layer: track which songs multiple user profiles agree on, and use that agreement as an additional signal. Two very different users both liking the same song is more interesting information than one user liking a song that fits their stated preferences perfectly.
