# Imports
import streamlit as st
import scraper as sc
import pickle
import random

def main():

    if 'scraper_object' not in st.session_state:
        st.session_state.scraper_object = None

    if 'view_object' not in st.session_state:
        st.session_state.view_object = False

    if 'run_scraper' not in st.session_state:
        st.session_state.run_scraper = False

    if 'scrape_done' not in st.session_state:
        st.session_state.scrape_done = False

    if 'loaded_object' not in st.session_state:
        st.session_state.loaded_object = False

    if 'posts' not in st.session_state:
        st.session_state.posts = None

    def create_object_callback():
        st.session_state.view_object = True
        st.session_state.run_scraper = False
        # Problematic code in next three lines:
        if 'uploaded_file' in st.session_state:
            st.session_state.loaded_object = False
            del st.session_state['uploaded_file']

    def view_object_callback():
        st.session_state.view_object = True
        st.session_state.run_scraper = False

    def run_scraper_callback():
        st.session_state.view_object = False
        st.session_state.run_scraper = True
        st.session_state.scrape_done = False

    def load_scraper_object(scraper_object):
        if scraper_object is not None:
            st.session_state.scraper_object = pickle.load(scraper_object)
            # Unsure if the following line does anything:
            st.session_state['uploaded_file'] = uploaded_file
            st.session_state.view_object = True
            st.session_state.loaded_object = True

    st.title("Dynamic Web Scraper Tool")
    st.write("This tool allows you to create a dynamic web scraper object for any website.")
    st.write("Enter the *URL*, the data *classes*, the number of initial initial inputs (OPTIONAL), and the *XPath* of the objects you want to interact with. Also specify the repeated input type to load more data and, if click, define the *XPath* of the button to click.")
    st.write("When utilizing this tool, consider *every single input type and the order in which they are to be executed* to access the data you want to scrape.")
    st.divider()


    with st.sidebar:

        uploaded_file = st.file_uploader("Upload Object", type=["pkl"])
        load_scraper_object(uploaded_file)
        num_inputs = st.number_input("Number of Initial Inputs", min_value=0, step=1, help="The number of initial inputs required to access the posts. (OPTIONAL)")
        create_object = st.button("Create Object", on_click=create_object_callback)

    # Collect user inputs

    with st.expander('Target Elements'):

        col1, col2 = st.columns(2)

        with col1:
            num_posts = st.number_input("Number of Posts", min_value=1, step=1, help="The number of posts to scrape.")
            post_title_class = st.text_input("Post Title Class*",
                                            help="The class that contains the post title. (REQUIRED)"
                                            )
            post_body_class = st.text_input("Post Body Class*",
                                            help="The class that contains the post body. (REQUIRED)"
                                            )

        with col2:
            url = st.text_input("URL*")
            avoid_class = st.text_input("Avoid Class",
                                        help="The class you want to target may include other classes you want to avoid. If so, enter the class to avoid here. (OPTIONAL)"
                                        )

    with st.expander('Initial Inputs'):

        if num_inputs == 0:
            st.markdown("<p style='font-size:12px;'>Initial inputs may be required when narrowing down data you'd like to scrape. If they're required, adjust the number of initial inputs in the sidebar.</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        if num_inputs > 0:

            inputs = [] # List to store the inputs

            for i in range(1, num_inputs + 1):
                with col1:
                    input_type = st.radio(f'Input Type [{i}]', ('Click', 'Text Entry'), key=f"radio_{i}")

                if input_type == 'Text Entry':
                    with col2:
                        text_entry_input = st.text_input(f"Text to Enter:", key=f"input_{i}", help="The text to enter in the text entry field.")
                        inputs.append((f"input_{i}", text_entry_input))

                if input_type == 'Click':
                    with col2:
                        click_xpath = st.text_input(f"Click XPath:", key=f"click_{i}", help="The XPath of the button to click along the path to accessing the posts.")
                        inputs.append((f"click_{i}", click_xpath))

    with st.expander('Repeated Input'):

        col1, col2 = st.columns(2)
        repeated_click_xpath = None
        paginated = False

        with col1:
            repeated_input_type = st.radio("Repeated Input Type*", ('Click', 'Scroll'), help="The type of input to load more posts.")

        if repeated_input_type == 'Click':
            with col2:
                repeated_click_xpath = st.text_input("Repeated Click Button XPath*", help="The XPath of the button to click repeatedly to load more posts.")
            paginated = st.checkbox('Paginated',help='Are the posts you\'re trying to scrape on a page that can endlessly load posts or is it paginated?')

    if create_object:
        # Create a dictionary with user inputs
        if not url:
            st.error("Please enter a URL")
        elif not post_title_class:
            st.error("Please enter a Post Title Class")
        elif not post_body_class:
            st.error("Please enter a Post Body Class")
        elif not repeated_input_type:
            st.error("Please select a Repeated Input Type")
        elif repeated_input_type == 'Click' and not repeated_click_xpath:
            st.error("Please enter a Repeated Click Button XPath")
        elif num_inputs > 0 and not all(input_selector for input_name, input_selector in inputs):
            st.error("All initial click selectors are required.")
        else:
            user_input = {
                "url": url.strip(),
                "post_title_class": post_title_class.strip(),
                "avoid_class": None if avoid_class == '' else avoid_class.strip(),
                "post_body_class": post_body_class.strip(),
                "repeated_input_type": repeated_input_type,
                "repeated_click_xpath": repeated_click_xpath.strip() if repeated_click_xpath else None,
                "paginated": paginated,
                "num_posts": num_posts,
                "num_inputs": num_inputs,
                "actions": {}
            }
            if num_inputs > 0:
                for input_name, input_selector in inputs:
                    user_input["actions"][input_name] = input_selector

            # Add the scraper_object to the session state:
            st.session_state.scraper_object = sc.ScraperObject(**user_input)


    # Instantiate the scraper object:
    scraper_object = st.session_state.scraper_object

    # If scraper_object exists, announce successful creation and display the sidebar buttons:
    if scraper_object and st.session_state.loaded_object:
        st.success("Scraper object loaded from file.")

    elif scraper_object:
        st.success(f'Scraper object created with {scraper_object.num_inputs} inputs.')

    if scraper_object:
        st.session_state.serialized_object = pickle.dumps(scraper_object)

        with st.sidebar:

            if uploaded_file:
                st.download_button(label="Download Object", data=st.session_state.serialized_object, file_name="scraper_object.pkl", mime="application/octet-stream", disabled=True)
            else:
                st.download_button(label="Download Object", data=st.session_state.serialized_object, file_name="scraper_object.pkl", mime="application/octet-stream")

            st.button("View Object", on_click=view_object_callback)
            st.button("RUN", on_click=run_scraper_callback)


        with st.expander('OUTPUT:'):
            if st.session_state.view_object:
                st.write(scraper_object)

            if st.session_state.run_scraper and not st.session_state.scrape_done:
                posts = sc.run(scraper_object)
                st.session_state.posts = posts
                st.session_state.scrape_done = True

            if st.session_state.posts:
                posts = st.session_state.posts

            if st.session_state.scrape_done:
                print_posts = st.number_input("Print Posts", min_value=0, max_value=scraper_object.num_posts, step=1, value=0, help="The number of posts to show.")
                if print_posts > 0:
                    st.write(posts[:print_posts])

if __name__ == "__main__":
    main()
