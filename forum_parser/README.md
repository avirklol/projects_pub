# Forum Parser
A friend at work told me that they were looking through community posts individually to spot opportunities where they could share our platform with the users. I immediately thought about how painful and inefficient that must be and thought to work on this project.
## Functionality
### Parsing Through Forum Pages
- Pulls the title and URL of each post across multiple pages
- Adds them as a key:value pair in a dictionary
### Parsing Through Individual Posts
- Utilizes the dictionary of posts and URLs to parse through each post and extract the text within their paragraphs
- Adds the paragraph and the URL to a vector database
### LLM Context Matching and URL Extraction
- Utilizing RAG, an LLM will look through the database after being given a context
- If a post matches the context, it's URL is extracted and appended to another object
### URL Object Return
- Once the process has been finished, the URLs relevant to the provided context are returned to the user
