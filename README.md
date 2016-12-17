# Jack Holmes - The Georgia Tech OMSCS Student's best friend.

Jack Holmes is a slack-bot designed to help Georgia Tech OMSCS Students out with their course selection.<br />
This robot can answer a number of questions (listed below) about all your favorite courses and their instructors 
in the GT OMSCS Program. It can even record your preferences, and make a course-plan tailored for you.<br />
Similarly, it can recommend courses that you will find more interesting!<br />
You can find Jack Holmes at 
[jack-holmes.slack.com](http://jack-holmes.slack.com). Please contact me at chitaliayc@gmail.com to get access to the team.
# Types of questions:
You can ask two types of questions to the agent, Objective and Subjective.<br />

# Objective Questions:
The list of Objective questions that can be asked is as follows:.<br />
1. What are the prerequisites for CS 6601?
2. What is the required reading material for the Embedded Systems class?
3. What is the grading policy for Data and Visual Analytics?
4. What is CSE 6242 about?
5. What computer do I need to watch KBAI lectures?
6. What is the course name of CS 6262?
7. What is the course number of Artificial Intelligence?
8. What is the likelihood of getting an A grade in KBAI? (same questions can be asked for B, C and D grades)
9. What's the chance of passing Machine Learning? (same question can be asked about failing)
10. What's the average GPA of a student taking Machine Learning for Trading?
11. Who is the instructor for CS 6300?
  You can follow up the instructor question with the following questions:  
  1. Is he/she helpful? (helpfulness)
  2. Is he/she easygoing? (easiness)
  3. Is he/she a good professor? (teacher quality)
  4. What do others have to say about him/her? (top comments from other students) 
  5. Is he/she hot/cute? (hotness)
  6. Is he/she rich? (wealth)
  7. Does he/she like to eat frogs? (culinary-preferences)

# Subjective Questions:
In order for Jack to answer subjective questions, he should have some knowledge of your preferences.<br />
He already has a set of preferences stored in his Episodic Memory, but you can edit the same by saying _"Change my preferences"_ or _"modify preferences"_, or something like that.<br />
Then Jack will proceed to ask you a number of questions that help him understand your needs better (like GPA, major, etc.).<br />
Using this data, Jack can answer questions like:<br />
1. Is KBAI *better for me* than AI?
2. Is CS 6400 *easier* than CS 6440?
3. *Plan* my Online Masters.
<br />
If you want an explanation of why the agent made a certain choice for you, you can simply ask,
1. Why did you say that?
2. Why did you infer that?
3. Analysis (This will actually cause Jack to reveal the pseudocode that resulted in the previous answer!)
<br />

The Analysis funcitonality has been taken from the TV Show Westworld, where the robot programmers use this functionality to debug their robots, like so:<br />
![Jack Holmes' analysis mode](/docs/analysis_mode.png?raw=true "Analysis mode demo")

Whereas, if you use the regular _"Why did you say that?"_, you get the following reply:<br />
![Jack Holmes' layman mode](/docs/layman_mode.png?raw=true "Layman mode demo")

# Goodbye mode:
To all the 90s kids like me, you can have your John Conner moment with Jack, if you say the following cheat _"Are there any more chips left?"_. This will trigger a _"Script"_, which, if followed, will result in a Terminator 2 style goodbye from Jack. Like so:<br />
![Adriaaan!](/docs/goodbye.png?raw=true "Adriaan! Adriaaaaan!")

# Finally how to use the code:
If you want to play around with the code, feel free to do so!<br />
Please cite me if you do so tho!<br />
1. Create an account on API.ai and make an agent. Define intents and contexts.
2. Clone the repo, all the code is in app.py. The "data collection" subdirectory has 
all the code I used to scrape the OMSCS website, Rate My Professor, and Course Critique.<br />
3. Modify the code to tackle the JSON being sent from your API agent. 
4. Finally, once you're done editing, deploy using Heroku!<br />
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


