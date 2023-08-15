# Evaluation on Retrieve Augmented Question Answering

Here we evaluation the E2E question answering performance on [NaturalQuestion](https://ai.google.com/research/NaturalQuestions) dataset.
We collected 5332 nonredundant context documents and 6775 queries from [HuggingFace Dataset](https://huggingface.co/datasets/thinkall/NaturalQuestionsQA).

First, we created a document collection based on all the context corpus and stored them in a vector database; then we selected the some questions and answered them with RetrieveChat.
Next, to evaluate the performance of RetrieveChat in QA, we employ the metrics of exact match (EM), F1 score and Recall.
The EM score indicates the percentage of questions where the predicted answer matches the reference answer to the question exactly.
On the other hand, the F1 score measures the similarity between the predicted answer and the reference answer, taking into account both precision and recall.
However, our results imply that recall, which measures the proportion of tokens in the reference answer that are present in the predicted answer, is more highly correlated with correctness than lexical overlap metrics such as EM or F1. Which is also mentioned in [this paper](https://arxiv.org/pdf/2307.16877v1.pdf).

Results on the first 500 questions with gpt-4 are as below:
```
Average EM: 5.69
Average F1: 31.83
Average Recall: 72.94
```

Results on the first 500 questions with gpt-3.5-turbo are as below:
```
Average EM: 0.2
Average F1: 23.73
Average Recall: 66.61
```
The F1 score and Recall score are significantly higher than the results showed in [this paper](https://arxiv.org/pdf/2307.16877v1.pdf).

RetrieveChat's exceptional performance is a result of our unique and innovative functionality called 'Update Context'. Using this feature, the agents automatically request new context if they find the given context insufficient for answering questions, thereby remedying inaccuracies in retrieval tools. An example of its usage is demonstrated below:

```
from flaml.autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from flaml.autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from flaml import autogen
import chromadb

config_list = autogen.config_list_from_json(
    env_or_file=".config.local",
    file_location=".",
    filter_dict={
        "model": {
            "gpt-35-turbo",
            "gpt-3.5-turbo",
        }
    },
)

assert len(config_list) > 0
config_list[0]['model'] = 'gpt-35-turbo'

# 1. create an RetrieveAssistantAgent instance named "assistant"
assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config={
        "request_timeout": 600,
        "seed": 42,
        "config_list": config_list,
    },
)

# 2. create the RetrieveUserProxyAgent instance named "ragproxyagent"
corpus_file = "https://huggingface.co/datasets/thinkall/NaturalQuestionsQA/resolve/main/corpus.txt"

# Create a new collection for NaturalQuestions dataset
ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    retrieve_config={
        "task": "qa",
        "docs_path": corpus_file,
        "chunk_token_size": 2000,
        "model": config_list[0]["model"],
        "client": chromadb.PersistentClient(path="/tmp/chromadb"),
        "collection_name": "natural-questions",
        "chunk_mode": "one_line",
        "embedding_model": "all-MiniLM-L6-v2",
    },
)

# reset the assistant. Always reset the assistant before starting a new conversation.
assistant.reset()

qa_problem = "who carried the usa flag in opening ceremony"  # referenc answer is "Erin Hamlin"
ragproxyagent.initiate_chat(assistant, problem=qa_problem, n_results=30)
```

The output of the code is:
```
doc_ids:  [['doc_20', 'doc_2943', 'doc_2059', 'doc_3293', 'doc_4056', 'doc_1914', 'doc_2749', 'doc_1796', 'doc_3468', 'doc_1793', 'doc_876', 'doc_2577', 'doc_27', 'doc_2780', 'doc_366', 'doc_321', 'doc_3103', 'doc_715', 'doc_3534', 'doc_142', 'doc_5337', 'doc_2426', 'doc_5346', 'doc_3021', 'doc_1596', 'doc_316', 'doc_1103', 'doc_1670', 'doc_2853', 'doc_3256']]
Adding doc_id doc_20 to context.
Adding doc_id doc_2943 to context.
Adding doc_id doc_2059 to context.
Adding doc_id doc_3293 to context.
Adding doc_id doc_4056 to context.
Adding doc_id doc_1914 to context.
Adding doc_id doc_2749 to context.
Adding doc_id doc_1796 to context.
Adding doc_id doc_3468 to context.
Adding doc_id doc_1793 to context.
Adding doc_id doc_876 to context.
Adding doc_id doc_2577 to context.
Adding doc_id doc_27 to context.
Adding doc_id doc_2780 to context.
ragproxyagent (to assistant):

You're a retrieve augmented chatbot. You answer user's questions based on your own knowledge and the
context provided by the user.
If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.
You must give as short an answer as possible.

User's question is: who carried the usa flag in opening ceremony

Context is: <P> On January 17 , 1899 , under orders from President William McKinley , Commander Edward D. Taussig of USS Bennington landed on Wake and formally took possession of the island for the United States . After a 21 - gun salute , the flag was raised and a brass plate was affixed to the flagstaff with the following inscription : </P>
<Li> 1960 Flag with 50 stars ( Hawaii ) </Li>
<P> The flag of the United States of America , often referred to as the American flag , is the national flag of the United States . It consists of thirteen equal horizontal stripes of red ( top and bottom ) alternating with white , with a blue rectangle in the canton ( referred to specifically as the `` union '' ) bearing fifty small , white , five - pointed stars arranged in nine offset horizontal rows , where rows of six stars ( top and bottom ) alternate with rows of five stars . The 50 stars on the flag represent the 50 states of the United States of America , and the 13 stripes represent the thirteen British colonies that declared independence from the Kingdom of Great Britain , and became the first states in the U.S. Nicknames for the flag include The Stars and Stripes , Old Glory , and The Star - Spangled Banner . </P>
<P> The Pledge of Allegiance of the United States is an expression of allegiance to the Flag of the United States and the republic of the United States of America . It was originally composed by Captain George Thatcher Balch , a Union Army Officer during the Civil War and later a teacher of patriotism in New York City schools . The form of the pledge used today was largely devised by Francis Bellamy in 1892 , and formally adopted by Congress as the pledge in 1942 . The official name of The Pledge of Allegiance was adopted in 1945 . The most recent alteration of its wording came on Flag Day in 1954 , when the words `` under God '' were added . </P>
<P> In modern times , the U.S. military plays ( or sounds ) `` Reveille '' in the morning , generally near sunrise , though its exact time varies from base to base . On U.S. Army posts and Air Force bases , `` Reveille '' is played by itself or followed by the bugle call `` To the Colors '' at which time the national flag is raised and all U.S. military personnel outdoors are required to come to attention and present a salute in uniform , either to the flag or in the direction of the music if the flag is not visible . While in formation , soldiers are brought to the position of parade rest while `` Reveille '' plays then called to attention and present arms as the national flag is raised . On board U.S. Navy , Marine Corps , and Coast Guard facilities , the flag is generally raised at 0800 ( 8 am ) while `` The Star Spangled Banner '' or the bugle call `` To the Colors '' is played . On some U.S. military bases , `` Reveille '' is accompanied by a cannon shot . </P>
<P> When the National Anthem was first recognized by law in 1932 , there was no prescription as to behavior during its playing . On June 22 , 1942 , the law was revised indicating that those in uniform should salute during its playing , while others should simply stand at attention , men removing their hats . ( The same code also required that women should place their hands over their hearts when the flag is displayed during the playing of the Anthem , but not if the flag was not present . ) On December 23 , 1942 the law was again revised instructing men and women to stand at attention and face in the direction of the music when it was played . That revision also directed men and women to place their hands over their hearts only if the flag was displayed . Those in uniform were required to salute . On July 7 , 1976 , the law was simplified . Men and women were instructed to stand with their hands over their hearts , men removing their hats , irrespective of whether or not the flag was displayed and those in uniform saluting . On August 12 , 1998 , the law was rewritten keeping the same instructions , but differentiating between `` those in uniform '' and `` members of the Armed Forces and veterans '' who were both instructed to salute during the playing whether or not the flag was displayed . Because of the changes in law over the years and confusion between instructions for the Pledge of Allegence versus the National Anthem , throughout most of the 20th century many people simply stood at attention or with their hands folded in front of them during the playing of the Anthem , and when reciting the Pledge they would hold their hand ( or hat ) over their heart . After 9 / 11 , the custom of placing the hand over the heart during the playing of the Anthem became nearly universal . </P>
<P> A flag designed by John McConnell in 1969 for the first Earth Day is a dark blue field charged with The Blue Marble , a famous NASA photo of the Earth as seen from outer space . The first edition of McConnell 's flag used screen - printing and used different colors : ocean and land were blue and the clouds were white . McConnell presented his flag to the United Nations as a symbol for consideration . </P>
<P> The torch - bearing arm was displayed at the Centennial Exposition in Philadelphia in 1876 , and in Madison Square Park in Manhattan from 1876 to 1882 . Fundraising proved difficult , especially for the Americans , and by 1885 work on the pedestal was threatened by lack of funds . Publisher Joseph Pulitzer , of the New York World , started a drive for donations to finish the project and attracted more than 120,000 contributors , most of whom gave less than a dollar . The statue was built in France , shipped overseas in crates , and assembled on the completed pedestal on what was then called Bedloe 's Island . The statue 's completion was marked by New York 's first ticker - tape parade and a dedication ceremony presided over by President Grover Cleveland . </P>
<P> The horizontal stripes on the flag represent the nine original departments of Uruguay , based on the U.S flag , where the stripes represent the original 13 colonies . The first flag designed in 1828 had 9 light blue stripes ; this number was reduced to 4 in 1830 due to visibility problems from distance . The Sun of May represents the May Revolution of 1810 ; according to the historian Diego Abad de Santillán , the Sun of May is a figurative sun that represents Inti , the sun god of the Inca religion . It also appears in the Flag of Argentina and the Coat of Arms of Bolivia . </P>
<P> The anthem has been recorded and performed in many different languages , usually as a result of the hosting of either form of the Games in various countries . The IOC does n't require that the anthem be performed in either English or Greek . But in the 2008 Olympic opening and closing ceremonies in Beijing , China , Greek was sung instead of the host country 's official language , Mandarin . Also in the 2016 Olympic opening ceremonies in Rio de Janeiro , Brazil , English was also sung instead of host country 's official language , Portuguese . </P>
<P> The United States Oath of Allegiance , officially referred to as the `` Oath of Allegiance , '' 8 C.F.R. Part 337 ( 2008 ) , is an allegiance oath that must be taken by all immigrants who wish to become United States citizens . </P>
<P> During the first half of the 19th century , seven stars were added to the flag to represent the seven signatories to the Venezuelan declaration of independence , being the provinces of Caracas , Cumaná , Barcelona , Barinas , Margarita , Mérida , and Trujillo . </P>
<P> With the annexation of Hawaii in 1898 and the seizure of Guam and the Philippines during the Spanish -- American War that same year , the United States began to consider unclaimed and uninhabited Wake Island , located approximately halfway between Honolulu and Manila , as a good location for a telegraph cable station and coaling station for refueling warships of the rapidly expanding United States Navy and passing merchant and passenger steamships . On July 4 , 1898 , United States Army Brigadier General Francis V. Greene of the 2nd Brigade , Philippine Expeditionary Force , of the Eighth Army Corps , stopped at Wake Island and raised the American flag while en route to the Philippines on the steamship liner SS China . </P>
<P> On Opening Day , April 9 , 1965 , a sold - out crowd of 47,879 watched an exhibition game between the Houston Astros and the New York Yankees . President Lyndon B. Johnson and his wife Lady Bird were in attendance , as well as Texas Governor John Connally and Houston Mayor Louie Welch . Governor Connally tossed out the first ball for the first game ever played indoors . Dick `` Turk '' Farrell of the Astros threw the first pitch . Mickey Mantle had both the first hit ( a single ) and the first home run in the Astrodome . The Astros beat the Yankees that night , 2 - 1 . </P>



--------------------------------------------------------------------------------
assistant (to ragproxyagent):

Sorry, I cannot find any information about who carried the USA flag in the opening ceremony. UPDATE CONTEXT.

--------------------------------------------------------------------------------
Updating context and resetting conversation.
Adding doc_id doc_366 to context.
ragproxyagent (to assistant):

You're a retrieve augmented chatbot. You answer user's questions based on your own knowledge and the
context provided by the user.
If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.
You must give as short an answer as possible.

User's question is: who carried the usa flag in opening ceremony

Context is: <Table> <Tr> <Th> # </Th> <Th> Event year </Th> <Th> Season </Th> <Th> Ceremony </Th> <Th> Flag bearer </Th> <Th> Sex </Th> <Th> State / Country </Th> <Th> Sport </Th> </Tr> <Tr> <Td> 62 </Td> <Td> 2018 </Td> <Td> Winter </Td> <Td> Closing </Td> <Td> Diggins , Jessica Jessica Diggins </Td> <Td> </Td> <Td> Minnesota </Td> <Td> Cross-country skiing </Td> </Tr> <Tr> <Td> 61 </Td> <Td> 2018 </Td> <Td> Winter </Td> <Td> Opening </Td> <Td> Hamlin , Erin Erin Hamlin </Td> <Td> </Td> <Td> New York </Td> <Td> Luge </Td> </Tr> <Tr> <Td> 60 </Td> <Td> 2016 </Td> <Td> Summer </Td> <Td> Closing </Td> <Td> Biles , Simone Simone Biles </Td> <Td> </Td> <Td> Texas </Td> <Td> Gymnastics </Td> </Tr> <Tr> <Td> 59 </Td> <Td> 2016 </Td> <Td> Summer </Td> <Td> Opening </Td> <Td> Phelps , Michael Michael Phelps </Td> <Td> </Td> <Td> Maryland </Td> <Td> Swimming </Td> </Tr> <Tr> <Td> 58 </Td> <Td> 2014 </Td> <Td> Winter </Td> <Td> Closing </Td> <Td> Chu , Julie Julie Chu </Td> <Td> </Td> <Td> Connecticut </Td> <Td> Hockey </Td> </Tr> <Tr> <Td> 57 </Td> <Td> 2014 </Td> <Td> Winter </Td> <Td> Opening </Td> <Td> Lodwick , Todd Todd Lodwick </Td> <Td> </Td> <Td> Colorado </Td> <Td> Nordic combined </Td> </Tr> <Tr> <Td> 56 </Td> <Td> 2012 </Td> <Td> Summer </Td> <Td> Closing </Td> <Td> Nellum , Bryshon Bryshon Nellum </Td> <Td> </Td> <Td> California </Td> <Td> Athletics </Td> </Tr> <Tr> <Td> 55 </Td> <Td> 2012 </Td> <Td> Summer </Td> <Td> Opening </Td> <Td> Zagunis , Mariel Mariel Zagunis </Td> <Td> </Td> <Td> Oregon </Td> <Td> Fencing </Td> </Tr> <Tr> <Td> 54 </Td> <Td> </Td> <Td> Winter </Td> <Td> Closing </Td> <Td> Demong , Bill Bill Demong </Td> <Td> </Td> <Td> New York </Td> <Td> Nordic combined </Td> </Tr> <Tr> <Td> 53 </Td> <Td> </Td> <Td> Winter </Td> <Td> Opening </Td> <Td> Grimmette , Mark Mark Grimmette </Td> <Td> </Td> <Td> Michigan </Td> <Td> Luge </Td> </Tr> <Tr> <Td> 52 </Td> <Td> 2008 </Td> <Td> Summer </Td> <Td> Closing </Td> <Td> Lorig , Khatuna Khatuna Lorig </Td> <Td> </Td> <Td> Georgia ( country ) </Td> <Td> Archery </Td> </Tr> <Tr> <Td> 51 </Td> <Td> 2008 </Td> <Td> Summer </Td> <Td> Opening </Td> <Td> Lomong , Lopez Lopez Lomong </Td> <Td> </Td> <Td> Sudan ( now South Sudan ) </Td> <Td> Athletics </Td> </Tr> <Tr> <Td> 50 </Td> <Td> 2006 </Td> <Td> Winter </Td> <Td> Closing </Td> <Td> Cheek , Joey Joey Cheek </Td> <Td> </Td> <Td> North Carolina </Td> <Td> Speed skating </Td> </Tr> <Tr> <Td> 49 </Td> <Td> 2006 </Td> <Td> Winter </Td> <Td> Opening </Td> <Td> Witty , Chris Chris Witty </Td> <Td> </Td> <Td> Wisconsin </Td> <Td> Speed skating </Td> </Tr> <Tr> <Td> 48 </Td> <Td> </Td> <Td> Summer </Td> <Td> Closing </Td> <Td> Hamm , Mia Mia Hamm </Td> <Td> </Td> <Td> Texas </Td> <Td> Women 's soccer </Td> </Tr> <Tr> <Td> 47 </Td> <Td> </Td> <Td> Summer </Td> <Td> Opening </Td> <Td> Staley , Dawn Dawn Staley </Td> <Td> </Td> <Td> Pennsylvania </Td> <Td> Basketball </Td> </Tr> <Tr> <Td> 46 </Td> <Td> 2002 </Td> <Td> Winter </Td> <Td> Closing </Td> <Td> Shimer , Brian Brian Shimer </Td> <Td> </Td> <Td> Florida </Td> <Td> Bobsleigh </Td> </Tr> <Tr> <Td> 45 </Td> <Td> 2002 </Td> <Td> Winter </Td> <Td> Opening </Td> <Td> Peterson , Amy Amy Peterson </Td> <Td> </Td> <Td> Minnesota </Td> <Td> Short track speed skating </Td> </Tr> <Tr> <Td> 44 </Td> <Td> 2000 </Td> <Td> Summer </Td> <Td> Closing </Td> <Td> Gardner , Rulon Rulon Gardner </Td> <Td> </Td> <Td> Wyoming </Td> <Td> Wrestling </Td> </Tr> <Tr> <Td> 43 </Td> <Td> 2000 </Td> <Td> Summer </Td> <Td> Opening </Td> <Td> Meidl , Cliff Cliff Meidl </Td> <Td> </Td> <Td> California </Td> <Td> Canoeing </Td> </Tr> <Tr> <Td> 42 </Td> <Td> 1998 </Td> <Td> Winter </Td> <Td> Closing </Td> <Td> Granato , Cammi Cammi Granato </Td> <Td> </Td> <Td> Illinois </Td> <Td> Hockey </Td> </Tr> <Tr> <Td> 41 </Td> <Td> 1998 </Td> <Td> Winter </Td> <Td> Opening </Td> <Td> Flaim , Eric Eric Flaim </Td> <Td> </Td> <Td> Massachusetts </Td> <Td> Speed skating </Td> </Tr> <Tr> <Td> 40 </Td> <Td> </Td> <Td> Summer </Td> <Td> Closing </Td> <Td> Matz , Michael Michael Matz </Td> <Td> </Td> <Td> Pennsylvania </Td> <Td> Equestrian </Td> </Tr> <Tr> <Td> 39 </Td> <Td> </Td> <Td> Summer </Td> <Td> Opening </Td> <Td> Baumgartner , Bruce Bruce Baumgartner </Td> <Td> </Td> <Td> New Jersey </Td> <Td> Wrestling </Td> </Tr> <Tr> <Td> 38 </Td> <Td> 1994 </Td> <Td> Winter </Td> <Td> Closing </Td> <Td> Jansen , Dan Dan Jansen </Td> <Td> </Td> <Td> Wisconsin </Td> <Td> Speed skating </Td> </Tr> <Tr> <Td> 37 </Td> <Td> 1994 </Td> <Td> Winter </Td> <Td> Opening </Td> <Td> Myler , Cammy Cammy Myler </Td> <Td> </Td> <Td> New York </Td>



--------------------------------------------------------------------------------
assistant (to ragproxyagent):

Erin Hamlin carried the USA flag in the opening ceremony.

--------------------------------------------------------------------------------
```

Upon examining the output, it is evident that our agent was unable to generate an answer to the question based on the initial group of context. In response, the agent automatically requested new context and, after updating, was able to produce a satisfactory answer.
