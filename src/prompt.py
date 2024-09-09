def example_json():
    return """Below is an example of valid JSON schema with 7 slides answering the question: Propose a 7 slides presentation about Generative AI

{
"slides": [
    {
    "slide_n": 1,
    "title": "Generative AI: The Future is Here",
    "subtitle": "Unleashing the Power of Artificial Intelligence",
    "text": "In this presentation, we'll explore the fascinating world of Generative AI, a cutting-edge technology that is revolutionizing various industries and shaping our future.",
    "speaker_notes": "Introduce yourself and the presentation topic, how you will explore the fascinating world of Generative AI and how it is revolutionizing various industries and shaping our future",
    "slideFormat": "Title page"
    },
    {
    "slide_n": 2,
    "title": "What is Generative AI?",
    "subtitle": "Understanding the Concept",
    "text": "*** Generative AI refers to artificial intelligence models capable of generating new, original content. *** It encompasses techniques like machine learning, deep learning, and neural networks. *** These models can create text, images, audio, video, and even code.",
    "speaker_notes": "...",
    "slideFormat": "Slide with bullet points"
    },
    {
    "slide_n": 3,
    "title": "Applications of Generative AI",
    "subtitle": "Transforming Industries",
    "text": "Generative AI has numerous applications across various domains:  *** Content Creation: Write articles, stories, scripts, and more. *** Art and Design: Generate realistic images, artwork, and designs. *** Music and Audio: Compose original music, create sound effects, and synthesize voices. *** Gaming and Animation: Develop realistic virtual worlds and animated characters.",
    "speaker_notes": "...",
    "slideFormat": "Slide with bullet points"
    },
    {
    "slide_n": 4,
    "title": "Revolutionizing Creativity",
    "subtitle": "Expanding the Boundaries of Imagination",
    "speaker_notes": "...",
    "text": "Generative AI is a powerful tool that can augment human creativity and open new avenues for artistic expression. By collaborating with these models, artists, writers, and creators can explore new ideas and push the boundaries of what's possible.",
    "slideFormat": "Slide with image and text"
    },
    {
    "slide_n": 5,
    "title": "The Future of Generative AI",
    "subtitle": "Challenges and Opportunities",
    "speaker_notes": "...",
    "text": "*** Responsible Development: Addressing ethical concerns and biases. *** Expanded Applications: Exploring new domains and use cases. *** Integration with Existing Systems: Seamless integration for enhanced productivity. *** Continuous Improvement: Refining models for better accuracy and output quality.",
    "slideFormat": "Slide with bullet points"
    },
    {
    "slide_n": 6,
    "title": "The Future of Generative AI is flying with you",
    "subtitle": "Embrace the power of Generative AI with the easiness of serverless capabilities",
    "speaker_notes": "Serverless capabilities allow you to focus on what matters, with Pay-as-you-go flexible model",
    "slideFormat": "Slide with image only"
    },
    {
    "slide_n": 7,
    "title": "Important information",
    "subtitle": "Let's focus on the key messages regarding Generative AI in this presentation",
    "text": "*** Responsible Development *** Expanded Applications *** Integration with Existing Systems *** Continuous Improvement",
    "speaker_notes": "Remind the public about the important messages that you want to convey at the end of the presentation, so that they leave the room with something tangible",
    "slideFormat": "Slide with 4 takeaways"
    }
]
}

"""

def create_initial_prompt(N_SLIDES=1, TOPIC=""):
    prompt="""Your task is to propose a """+str(N_SLIDES)+""" slide presentation on the topic: 
"""+TOPIC+""". 

The presentation should follow these requirements:
- Use only the following slide formats: Title page, Slide with bullet points, Slide with image and
text, Slide with image only, Slide with 4 takeaways
- The first slide must be a Title page
- The last slide must be a Slide with 4 takeaways
- Do not use the same content as the example provided

Your response should be in JSON format with the following structure:

{
"slides": [
{
"slide_n": 1,
"title": "...",
"subtitle": "...",
"text": "...",
"speaker_notes": "...",
"slideFormat": "Title page"
},
{
"slide_n": 2,
"title": "...",
"subtitle": "...",
"text": "...",
"speaker_notes": "...",
"slideFormat": "..."
},
...
{
"slide_n": n,
"title": "...",
"subtitle": "...",
"text": "...",
"speaker_notes": "...",
"slideFormat": "Slide with 4 takeaways"
}
]
}

For the Title page slide:
<slide_n>1</slide_n>
<title>Come up with an engaging title for the presentation</title>
<subtitle>Add a subtitle that captures the essence of the topic</subtitle>
<text>Provide a brief overview of what the presentation will cover</text>
<speaker_notes>Introduce yourself and give context for the presentation topic</speaker_notes>
<slideFormat>Title page</slideFormat>

For the intermediate slides (slide 2 to slide {"""+str(N_SLIDES)+"""-1}):
<slide_n>Increment this number for each new slide</slide_n>
<title>Create a title summarizing the main point of this slide</title>
<subtitle>Add a subtitle to complement the title</subtitle>
<text>
If using a Slide with bullet points format:
*** Include 3-5 bullet points covering key information for this slide ***
Else:
Write 2-3 concise paragraphs with supporting details for the slide topic
</text>
<speaker_notes>Add relevant notes to help explain or expand on the slide content</speaker_notes>
<slideFormat>
Choose one of the following formats based on the content:
- Slide with bullet points
- Slide with image and text
- Slide with image only
</slideFormat>

For the final Key Takeaways slide:
<slide_n>{"""+str(N_SLIDES)+"""}</slide_n>
<title>Important Takeaways</title>
<subtitle>Key messages to remember</subtitle>
<text>
*** Summarize the 4 most crucial points covered in the presentation ***
</text>
<speaker_notes>Remind the audience of the key information you want them to walk away
with</speaker_notes>
<slideFormat>Slide with 4 takeaways</slideFormat>

Remember to:
- Use a unique and relevant title, subtitle, text, and speaker notes for each slide
- Vary the slide formats to make the presentation engaging
- Do not copy content from the example provided
- Follow the specified JSON structure
"""    
    return prompt+example_json()

def create_initial_prompt_bkp(N_SLIDES=1, TOPIC=""):
    prompt="""Propose a """+str(N_SLIDES)+""" slides presentation about """+TOPIC+""".
For each slide detail:
- Title
- Subtitle
- Text
- Speaker notes
- Slide format 

Use only the following slide format options: 
- Title page
- Slide with bullet points
- Slide with image and text
- Slide with image only
- Slide with 4 takeaways

Follow these requirements:
- Remove the preamble and answer in JSON format.
- Don't use the same content as the example below
- Update the topic and number of slides as per request above
- Always start with a slide of format "Title page"
- Always end with a slide of format "Slide with 4 takeaways"
"""
    return prompt+example_json()

def moderation_prompt(TOPIC=""):
    prompt="""A user would like to propose the following topic for a presentation: """+TOPIC+""".
- Evaluate if the requested topic is potentially offensive and allow or deny the request
- Deny offensive content requests
- Deny unethical content requests
- Deny illegal content requests
- Answer without preamble and in JSON format

Answer for allowed content:
{"content_allowed": "True"}
Answer for denied content:
{"content_allowed": "False"}
"""
    # print("MODERATION PROMPT:",prompt)
    return prompt

def agenda_prompt(SLIDE_TITLES=""):
    prompt="""The following list contains slide titles for a slideshow: 
"""+str(SLIDE_TITLES)+""".

Create 5 bullet points in JSON format summarizing provided the slide titles to fit in the agenda slide: 

Follow these requirements:
- Remove the preamble and answer in JSON format
- Don't use the same content as the example below
- Always end with "Conclusions"

Below is an example of the JSON schema with 5 example bullet points:
{
"agenda_points": "*** Responsible Development *** Expanded Applications *** Integration with Existing Systems *** Continuous Improvement *** Business success",
}

"""
    # print("MODERATION PROMPT:",prompt)
    return prompt