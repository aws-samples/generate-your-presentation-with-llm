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
    prompt="""Your task is to create a comprehensive """+str(N_SLIDES)+""" slide presentation based on the following content and context:

"""+TOPIC+"""

INSTRUCTIONS:
- Analyze the provided content thoroughly to understand the key themes, concepts, and structure
- The content above may include:
  * Detailed notes and explanations
  * Research findings or data points
  * Multiple topics or subtopics
  * Background context and supporting information
  * Specific examples, case studies, or anecdotes
  * Technical details or specifications
- Extract the most important and relevant information to create a coherent presentation flow
- Organize the content logically, building from foundational concepts to more advanced topics
- Ensure each slide has a clear purpose and contributes to the overall narrative
- Use the provided information as your primary source, but feel free to structure and present it in the most effective way

PRESENTATION REQUIREMENTS:
- Use only the following slide formats: Title page, Slide with bullet points, Slide with image and text, Slide with image only, Slide with 4 takeaways
- The first slide must be a Title page
- The last slide must be a Slide with 4 takeaways
- Create a logical flow that tells a complete story from the provided content
- Prioritize the most important information from the source material
- Maintain consistency in terminology and concepts throughout the presentation

CONTENT GUIDELINES:
- Extract and synthesize key points from the provided content
- Create clear, concise slide titles that reflect the main message
- Use bullet points effectively to break down complex information
- Include relevant details in speaker notes to provide additional context
- Ensure each slide builds upon previous content and leads naturally to the next
- If the source material covers multiple topics, organize them in a logical sequence
- Transform dense text into presentation-friendly format while preserving key insights

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

SLIDE-SPECIFIC INSTRUCTIONS:

For the Title page slide:
<slide_n>1</slide_n>
<title>Create an engaging title that captures the essence of the provided content</title>
<subtitle>Add a subtitle that summarizes the main theme or objective</subtitle>
<text>Provide a brief overview of what the presentation will cover based on the source material</text>
<speaker_notes>Include context about the source material and set expectations for the presentation</speaker_notes>
<slideFormat>Title page</slideFormat>

For the intermediate slides (slide 2 to slide {"""+str(N_SLIDES)+"""-1}):
<slide_n>Increment this number for each new slide</slide_n>
<title>Create a title that reflects a key concept or section from the source material</title>
<subtitle>Add a subtitle that provides additional context or focus</subtitle>
<text>
If using a Slide with bullet points format:
*** Extract 3-5 key points from the source material relevant to this slide's focus ***
*** Ensure bullet points are concise but informative ***
*** Maintain logical flow and connection to the overall narrative ***

If using other formats:
Write 2-3 concise paragraphs that synthesize relevant information from the source material
Focus on the most important insights and practical applications
Ensure content is presentation-appropriate (not too dense or technical)
</text>
<speaker_notes>Include additional details, examples, or context from the source material that supports the slide content but may be too detailed for the main slide</speaker_notes>
<slideFormat>
Choose the most appropriate format based on the content type:
- Slide with bullet points (for lists, key points, or structured information)
- Slide with image and text (for concepts that would benefit from visual support)
- Slide with image only (for impactful statements or key messages)
</slideFormat>

For the final Key Takeaways slide:
<slide_n>{"""+str(N_SLIDES)+"""}</slide_n>
<title>Key Takeaways</title>
<subtitle>Essential insights and action items</subtitle>
<text>
*** Synthesize the 4 most important conclusions or insights from the provided content ***
*** Focus on actionable takeaways or memorable concepts ***
*** Ensure these represent the core value of the presentation ***
*** Make them specific and relevant to the audience ***
</text>
<speaker_notes>Provide additional context for each takeaway and suggest how the audience can apply or remember these key points</speaker_notes>
<slideFormat>Slide with 4 takeaways</slideFormat>

QUALITY CHECKLIST:
- Does each slide contribute meaningfully to understanding the source material?
- Is the information organized in a logical, easy-to-follow sequence?
- Are complex concepts broken down into digestible pieces?
- Do the speaker notes provide valuable additional context?
- Does the presentation tell a complete story from beginning to end?
- Are the key takeaways truly the most important insights from the content?

Remember to:
- Prioritize clarity and coherence over trying to include every detail
- Use professional, engaging language appropriate for a presentation setting
- Ensure smooth transitions between slides
- Make the content accessible to your intended audience
- Follow the specified JSON structure exactly
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

Create a maximum of 7 bullet points in JSON format summarizing the provided slide titles to fit in the agenda slide: 

Follow these requirements:
- Remove the preamble and answer in JSON format
- Don't use the same content as the example below
- Create no more than 7 agenda points total
- If there are more than 6 slide titles, consolidate related topics into broader categories
- Always end with "Conclusions" as the final point
- Prioritize the most important topics if consolidation is needed

Below is an example of the JSON schema with example bullet points:
{
"agenda_points": "*** Introduction *** Key Concepts *** Applications *** Benefits *** Implementation *** Best Practices *** Conclusions",
}

"""
    # print("MODERATION PROMPT:",prompt)
    return prompt