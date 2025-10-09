
# Spending Analyser 

Hello, and thank you for considering my application. I have really enjoyed working on this task and hope you like what I have come up with!



## How I have met the requirements and how this app works


1. ### Synthetic but realistic transaction data 
 This included data on merchants, spending categories, amounts in £ and times of purchase. I also set a realistic budget to average spending behaviour. 

I created data for August and September to replicate realistic month-to-month themes. This allowed me to compare and contrast the data across both months.



2. ### Statistics & Visualisations 
I added two interactive Plotly visualisations 
- A bar chart showing spending by category 
- A line chart showing spending over the month 

Additionally I included:

- A table list view of all transaction data 
- Three KPI cards showing: total spending, total transactions and average transaction price to summarise spending behaviour at a glance

I believe that all these visualisations would be valuable to end customers as they aggregate complex data into insights. 


3. ### AI summarisation 
 I used the OpenAI model API in order to generate a natural language summary of the customer's spending. My prompt design aimed for a human-like tone to create an intuitive summary that highlights patterns and categories of spending. I also designed the prompt to offer a budgeting/financial tip to develop the analysis further. I made the decision to have the AI summary only load after the user presses the primary CTA button.

This:

- Gives users control over when to use the feature
- Prevents unnecessary credit use if a user reloads the app repeatedly

I strongly considered having it auto-generate on load, as I think users would benefit from having this insight readily available. However I ultimately held off to avoid running out of credits while I was testing and to ensure that you can see the AI summary in action before I run out 😅 ! 



4. ### Web interface 
I used Streamlit as it allowed me to build an interactive modern dashboard prototype it also:

- Supported rapid prototyping with Python 
- Integrated easily with Pandas, Plotly and the OpenAI API
- It let me focus on functionality, iteration and deploying to the Web

Streamlit UI components were perfect as it supported all the card metrics I wanted to include. 





## Deliverables:

## Public web app

Link to the publicly accessible web app: https://charlourdes-spending-analyser-app-ps2t2f.streamlit.app




## How to run this app locally:


1. ### Clone or download this repository

Either download the ZIP from GitHub 

https://github.com/charlourdes/spending-analyser

OR

If you have Git installed 

```bash
git clone https://github.com/charlourdes/spending-analyser.git
cd spending-analyser
```



2. ### Create and activate a virtual environment (optional)

Creating a virtual environment is recommended so this project’s Python packages don’t conflict with other projects you have. 

Depending on your system: 

### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (Command Prompt):
```bash
python -m venv venv
venv\Scripts\activate
```

### Windows (PowerShell):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```


3. ### Install dependencies 

```bash
pip install -r requirements.txt
```


4. ### Add your OpenAI key 
You will have to create a `.streamlit/secrets.toml` file in your project and add your OpenAI key. 

Use this line below and add your key. 


```toml
 openai_api_key = "your-openAI-key-should-go-here"
 ```

5. ### Run the streamlit app

```bash
streamlit run app.py
```

The browser should open like this automatically OR visit it manually
http://localhost:8501


Thank you for taking the time to look at my task, I hope you enjoyed what I created!