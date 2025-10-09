
# Spending Analyser 

Hello, thank you for considering my application, I  have enjoyed doing this task and hope you like what I have come up with!

I chose the Spending Analyser task. 


## The requirements/features I have included and some of my thinking behind them:


1. ### Synthetic but realistic transaction data 
 This included data on merchants, spending catagories, amounts in £ and times of purchase. Also set with a realistic budget. 



2. ### Statistics & Visualisations 
I added two interactive Plotly visualisations 
- A bar chart showing spending by catagory 
- A line chart showing spending over the month 

Aditionally I included:

- A table list view of all transaction data 
- Three KPI cards showing: total spending, total transactions and avarage transaction price to summarise spending behaviour at a glance

I believe that all these visualsations would be valuable to end customers as they aggregate complex data intio insights. 


3. ### AI summarisation 
 I used OpenAI model API in order to generate a natural language summary of the customers spending. My prompt design aimed for a human like and conversational tone to create an intuitive insight which  highlights patterns and catagories of spending. I also designed the prompt to give a budgeting/financial tip to develop the analysis further. This has turned complex numbers into helpful text. 

I made the decision to have the AI summary only load after the user presses the primary CTA button.

This:

- Gives users control over when to use the feature
- Prevents unnecessary credit use if a user reloads the app repeatedly

I was very close to having it auto-generate on load as I think users would feel the benefit from having this insight readily available, however I ultimately held off to avoid running out of credits while I was testing and to ensure that you can see the AI summary in action before I run out 😅 ! 



4. ### Web interface 
I used the  Streamlit as it allowed me to build a interactive dashboard prototype and:

- Supported rapid prototyping with python 
- intergrated easily with Pandas, Plotly and the OpenAI API
- It let me focus on functionality, iteration and deploying to the Web

Streamlit UI components were perfect for this task with all the cards/metrics I wanted to include. The result is a clean, modern dashboard with interactive and intuitive UI components. 





## Deliverables:

## Public web app

Link to the publicly accessbile web app: https://charlourdes-spending-analyser-app-ps2t2f.streamlit.app




## How to run this app locally:


1. ### Clone or download this repository

Either download the ZIP from GitHub 

https://github.com/charlourdes/spending-analyser

OR

if you have Git installed 

```bash
git clone https://github.com/charlourdes/spending-analyser.git
cd spending-analyser
```



2. ### Create and activate a virtual enviroment (optional)

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


3. ### Install dependecies 

```bash
pip install -r requirements.txt
```


4. ### Add your OpenAI key 
you will have to create a `.streamlit/secrets.toml` file in you project and add your OpenAI key. 

use this line below and add your key. 


openai_api_key = "your-openAI-key-should-go-here"


5. ### Run the streamlit app

```bash
streamlit run app.py
```

The browser should open like this automatically OR visit it manually
http://localhost:8501


