# Forum Parser
A friend at work told me that they were looking through community posts individually to spot opportunities where they could share our platform with the users. I immediately thought about how painful and inefficient that must be and thought to work on this project.
## Functionality
### Parsing Through Forum Pages
- Pulls the title and URL of each post across multiple pages
- Adds them as a key:value pair in a dictionary
- Appends that dictionary to a list
### Parsing Through Individual Posts
- Utilizes the dictionary of post titles and URLs to parse through each post and extract the text within their paragraphs
- Creates a new key:value pair for the post body within each index of the list of dictionaries
- Adds the paragraph and the URL to a vector database
### LLM Context Matching and URL Extraction
- Utilizing RAG, an LLM will look through the database after being given a context
- If a post matches the context, it's title, URL and body are extracted as a dictionary and appended to another object
### URL Object Return
- Once the process has been finished, the dictionaries with post bodies that match provided context are returned to the user

## Observations
### July 21, 2024
- Will opt for Selenium and utilize ChromeDriver to scrape and extract pages
- This will take longer, but we'll have more control of the results
- Have established a [basic wireframe](https://excalidraw.com/#json=q1TqwTFVsN3N6ECkSrmcq,j0LBYtEevliiVQMi_9qUYQ) detailing the required objects and functions to allow it to be run on virtually any forum.
### July 22, 2024
- Created an object class that can be loaded with n values via a Streamlit form and be passed into a function that executes n amount of clicks/scrapes. Pretty exciting!
### August 16, 2024
- Optimized the code to wrap any repeated code in functions that can be called throughout the scraper.py script.
- Expanded the object class to include a paginated option.
