# R4A — What companies ship today (frontier labs + Eedi + Khan Academy)

Research date: 2026-10-04 IST. Scope: products and evidence relevant to misconception diagnosis, targeted practice, learner memory, verified generation for Perceptron Hackathon 2026 Problem 8.

## TL;DR

- _Draft in progress; citations appended as sources are opened._

## Eedi

## Google / Google DeepMind

## OpenAI

## Anthropic

## Microsoft

## Khan Academy / Khanmigo

## Comparison table

| company | product | explicit misconception diagnosis? | targeted practice generation? | cross-session learner model? | verified generation? | published evidence |
|---|---|---|---|---|---|---|

## UNVERIFIED

- Claims not backed by an opened source will be listed here or omitted.

<!-- Research log appended 2026-10-04: opened sources 1–5 -->

### Source notes — Eedi Misconception Graph and LearnLM tutoring

- Eedi says its Misconception Graph became an open public good through Learning Commons/Hugging Face, mapping 8,000+ common maths misconceptions informed by 200M real student responses under CC BY 4.0; Eedi describes its diagnostic questions as four options with one right answer and three wrong distractors, each wrong option tied to a specific misconception. URL: https://www.eedi.com/news/eedis-misconception-graph-is-now-a-public-good (accessed 2026-10-04).
- Hugging Face dataset card for Eedi Misconceptions Graph v1.0 says it covers 8,117 misconceptions and 2,258 constructs; `misconception-map.csv` has 19,294 misconception↔construct weighted edges and `construct-map.csv` has 2,258 constructs. It explicitly does **not** include diagnostic questions, distractors, question images, or student-level response data. URL: https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph (accessed 2026-10-04).
- Eedi’s Nov. 2025 exploratory classroom trial with Google DeepMind says 165 students and 17 tutors across five UK secondary classrooms used LearnLM under expert tutor supervision. Human+AI matched human tutors on immediate mistake fixing (93.0% vs 91.2%) and misconception resolution (95.4% vs 94.9%), improved knowledge transfer by 10 percentage points versus 4.5 points for human tutors over standard hints, had zero harmful/risky content, 0.1% factual inaccuracies, and 82.3% AI suggestions approved with no/minimal edits. Eedi also cites a 2023–24 RCT with 2,901 students in 20 UK classrooms showing two to four additional months of maths gains from static diagnostic content. URL: https://www.eedi.com/news/new-exploratory-research-from-eedi-and-google-deepmind-reveals-human-in-the-loop-ai-tutoring-outperforms-human-only-support (accessed 2026-10-04).

### Source notes — OpenAI and Anthropic

- OpenAI Study Mode source still needs a cleaner opened source because the official launch URL returned page content not matching the launch page in this fetch; do not cite for product facts yet. URL attempted: https://openai.com/index/chatgpt-study-mode/ (accessed 2026-10-04).
- Anthropic launched Claude for Education with Learning mode, campus availability, Canvas/Instructure work, and student programs. Learning mode works inside Projects and guides rather than answers, asks Socratic questions, emphasizes core concepts, and provides templates. URL: https://www.anthropic.com/news/introducing-claude-for-education (accessed 2026-10-04).

<!-- Research log appended 2026-10-04: opened sources 6–10 -->

### Source notes — Google / LearnLM / Gemini

- ar5iv rendering of Google DeepMind's LearnLM paper reports a comparison against GPT-4o, Claude 3.5 Sonnet, and Gemini 1.5 Pro as of 2024-10-01; the study collected 2,360 conversations, 58,459 learner/model messages, and 10,192 expert assessments, with pedagogy experts preferring LearnLM most strongly over GPT-4o and also preferring it over Claude 3.5 and Gemini 1.5 Pro; LearnLM rated highest across the pedagogy rubric and stood out on active learning, metacognition, and curiosity. URL: https://ar5iv.labs.arxiv.org/html/2412.16429 (accessed 2026-10-04).
- Google's Aug. 2025 student tools post says Gemini added Guided Learning for everyone: a mode designed to foster critical thinking and deeper understanding, break down problems step-by-step, adapt explanations to learner needs, and help with study guides from course files plus videos/visuals. URL: https://blog.google/products-and-platforms/products/gemini/new-gemini-tools-students-august-2025/ (accessed 2026-10-04).

### Source notes — Microsoft

- Microsoft’s Oct. 2025 education blog announced AI teaching/learning experiences at no additional cost: Teach creates lesson plans, quizzes, rubrics and modifications by language, reading level, length, difficulty, and standards; Study and Learn Agent is a learning-science-grounded adaptive student agent for understanding, practice, topic study, chat, flashcards, matching, fill-in-the-blank, and quizzes, planned for preview in Nov. 2025; Copilot Chat uses GPT-5 with enterprise data protection and has LMS integration coming Dec. 2025. URL: https://www.microsoft.com/en-us/education/blog/2025/10/designing-microsoft-365-copilot-to-empower-educators-students-and-staff/ (accessed 2026-10-04).
- Microsoft Learning Zone landing page fetched only one verified line: it claims secure, classroom-ready AI with safeguards for learners under 18 and educator review/oversight/control. URL: https://learningzone.microsoft.com/ (accessed 2026-10-04).

<!-- Research log appended 2026-10-04: opened sources 11–16 -->

### Source notes — Khan Academy / Khanmigo

- Khan Academy’s 2026 independent RCT commentary says Oreopoulos & Low ran a true RCT across 18 middle schools over school years 2024–25 and 2025–26 in Hamilton County, TN; below-grade-level intervention students assigned to Khan Academy/Khanmigo gained 0.06 SD overall, 0.08 SD in year 2, and 0.14 SD in a secondary analysis of students active for a full year, against a business-as-usual control that often used Waggle, IXL, Zearn, and DeltaMath. Students used Khanmigo infrequently, so the study mostly measured Khan Academy practice. URL: https://blog.khanacademy.org/what-i-found-compelling-in-a-new-randomized-trial-of-khan-academy-in-math-intervention/ (accessed 2026-10-04).
- Khan Academy’s evidence roundup repeats the two-year cluster RCT numbers (~6,900 students; 18 middle schools; 0.06 SD/year, 0.08 SD in year 2, 0.14 SD active-participation implied effect) and says students messaged Khanmigo in only 17% of exercise sessions where they made a mistake. URL: https://blog.khanacademy.org/multiple-studies-show-khan-academy-drives-learning-gains-evidence-for-our-platforms-effectiveness/ (accessed 2026-10-04).
- Khan Academy says Khanmigo math reliability uses a backend calculator for numerical problems, upgraded parts to GPT-4 Turbo, tested GPT-4o/other models, improved hidden reasoning about possible student solution paths, and maintains math tutoring examples to regression-test new fixes; it acknowledges remaining errors. URL: https://blog.khanacademy.org/why-were-deeply-invested-in-making-ai-better-at-math-tutoring-and-what-weve-been-up-to-lately/ (accessed 2026-10-04).
- Khan Academy’s 2026 product-testing post says it measures response latency, next-item correctness, and cognitive engagement quality; uses guardrails including answer-giving, math error rates, and interactions/thread; A/B ships only when chance-to-win > .95 without guardrail harm. Giving Khanmigo structured learning-history signals improved next-item correctness: recent problem-solving history +3.4% over 608k threads; unmet prerequisite skills +2.7% over 1.36M threads; 24h skill conversation logs +5.09% cognitive engagement; 20 tests covered >15M tutoring threads and yielded 6.1% total next-item-correctness improvement. URL: https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor-our-most-recent-learnings/ (accessed 2026-10-04).
- Khan Academy + Google.org 2026 post says Khanmigo can generate interactive diagrams for math/science when visuals help, respond to students manipulating diagrams, and supports teacher-generated targeted multiple-choice practice through Practice My Knowledge with teacher review/refinement before assigning. It reports preliminary signs of increased engagement and next-item correctness but no final effect size. URL: https://blog.khanacademy.org/new-ai-tools-bring-interactive-diagrams-and-targeted-practice-thanks-to-khan-academys-partnership-with-google-org/ (accessed 2026-10-04).

### Source notes — Microsoft Learning Accelerators

- Microsoft Learn says Learning Accelerators are included in Microsoft 365 Education and streamline creation, review, and analysis of practice assignments while providing students real-time coaching to catch up, keep up, and get ahead; updated 2026-09-17. URL: https://learn.microsoft.com/en-us/training/educator-center/product-guides/learning-accelerators (accessed 2026-10-04).
- Microsoft Learn says Math Progress in Teams helps learners build math skills through educator-led/assigned activities, saves educators time with problem generation and grading, and provides progress data/Insights; learning objectives include setup, learner experience, educator review, manual review, and individual/class/system analytics. URL: https://learn.microsoft.com/en-us/training/modules/support-building-mathematics-skills-math-progress/ (accessed 2026-10-04).
