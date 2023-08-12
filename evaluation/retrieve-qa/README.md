# Evaluation on Retrieve Augmented Question Answering

Here we evaluation the E2E question answering performance on [NaturalQuestion](https://ai.google.com/research/NaturalQuestions) dataset.
We collected 5332 nonredundant context documents and 6775 queries from [HuggingFace Dataset](https://huggingface.co/datasets/thinkall/NaturalQuestionsQA).

First, we created a document collection based on all the context corpus and stored them in a vector database; then we selected the some questions and answered them with RetrieveChat.
Next, to evaluate the performance of RetrieveChat in QA, we employ the metrics of exact match (EM), F1 score and Recall.
The EM score indicates the percentage of questions where the predicted answer matches the reference answer to the question exactly.
On the other hand, the F1 score measures the similarity between the predicted answer and the reference answer, taking into account both precision and recall.
However, our results imply that recall, which measures the proportion of tokens in the reference answer that are present in the predicted answer, is more highly correlated with correctness than lexical overlap metrics such as EM or F1. Which is also mentioned in [this paper](https://arxiv.org/pdf/2307.16877v1.pdf).

Results on the first 200 questions with gpt-4 are as below:
```
Average EM: 9.5
Average F1: 32.28
Average Recall: 60.98
```

Results on the first 200 questions with gpt-3.5-turbo are as below:
```
Average EM: 0.0
Average F1: 23.87
Average Recall: 62.38
```
The F1 score and Recall score are significantly higher than the results showed in [this paper](https://arxiv.org/pdf/2307.16877v1.pdf).

RetrieveChat's exceptional performance is a result of our unique and innovative functionality called 'Update Context'. Using this feature, the agents automatically request new context if they find the given context insufficient for answering questions, thereby remedying inaccuracies in retrieval tools. An example of its usage is demonstrated below:

```
from flaml.autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from flaml.autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb

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
        "chunk_token_size": 4900,
        "model": config_list[0]["model"],
        "client": chromadb.PersistentClient(path="/tmp/chromadb"),
        "collection_name": "natural-questions",
        "chunk_mode": "one_line",
        "embedding_model": "all-MiniLM-L6-v2",
    },
)

# reset the assistant. Always reset the assistant before starting a new conversation.
assistant.reset()

ragproxyagent._context_max_tokens = 500
qa_problem = "who is edmund on days of our lives"  # referenc answer is "Adam Caine"
ragproxyagent.initiate_chat(assistant, problem=qa_problem, n_results=50, search_string="Edmund")
```

The output of the code is:
```
doc_ids:  [['doc_4554', 'doc_287', 'doc_1586', 'doc_1302', 'doc_44', 'doc_1362', 'doc_691', 'doc_4155', 'doc_421', 'doc_541', 'doc_1170', 'doc_986', 'doc_2099']]
Adding doc_id doc_4554 to context.
ragproxyagent (to assistant):

You're a retrieve augmented chatbot. You answer user's questions based on your own knowledge and the
context provided by the user.
If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.
You must give as short an answer as possible.

User's question is: who is edmund on days of our lives

Context is: <P> Offstage , Goneril , her plans thwarted , commits suicide . The dying Edmund decides , though he admits it is against his own character , to try to save Lear and Cordelia ; however , his confession comes too late . Soon after , Albany sends men to countermand Edmund 's orders , Lear enters bearing Cordelia 's corpse in his arms , having survived by killing the executioner . Kent appears and Lear now recognises him . Albany urges Lear to resume his throne , but as with Gloucester , the trials Lear has been through have finally overwhelmed him , and he dies . Albany then asks Kent and Edgar to take charge of the throne . Kent declines , explaining that his master is calling him on a journey and he must follow . Finally , Albany ( in the Quarto version ) or Edgar ( in the Folio version ) implies that he will now become king . </P>



--------------------------------------------------------------------------------
assistant (to ragproxyagent):

UPDATE CONTEXT

--------------------------------------------------------------------------------
Updating context and resetting conversation.
Adding doc_id doc_287 to context.
ragproxyagent (to assistant):

You're a retrieve augmented chatbot. You answer user's questions based on your own knowledge and the
context provided by the user.
If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.
You must give as short an answer as possible.

User's question is: who is edmund on days of our lives

Context is: <Ul> <Li> Mark Wahlberg as Cade Yeager , a single father and inventor , who helped the Autobots during the events of Age of Extinction . </Li> <Li> Josh Duhamel as William Lennox , a former NEST commander and U.S. Army Ranger captain , who partnered with the Autobots prior to the events of Age of Extinction , and now a U.S. Army Colonel and reluctant member of the Transformer Reaction Force ( TRF ) . </Li> <Li> Stanley Tucci as Merlin , King Arthur 's wizard and Viviane 's ancestor . Tucci was originally reported to be reprising his role as Joshua Joyce from Age of Extinction . </Li> <Li> Anthony Hopkins as Sir Edmund Burton , 12th Earl of Folgan , an astronomer and historian who knows about the history of the Transformers on Earth . </Li> <Li> Laura Haddock as Viviane Wembly , a Professor of English Literature at the University of Oxford and a polo player , who turns out to be a descendant of Merlin . Minti Gorne portrays a younger Viviane . </Li> <Li> Isabela Moner as Izabella , a street-wise tomboy who was orphaned with Sqweeks and Canopy , her only friends , until meeting Cade . </Li> <Li> Jerrod Carmichael as Jimmy , a young man from South Dakota whom Cade hired through a want ad . </Li> <Li> Santiago Cabrera as Santos , a former Delta Force operative and commander of the TRF , who seeks to eradicate every Transformer and their human allies regardless of faction . </Li> <Li> John Turturro as Seymour Simmons , a former government agent with Sector Seven and NEST turned successful writer who hides out in Cuba , and was allied with the Autobots prior to the events of Age of Extinction . </Li> <Li> Glenn Morshower as General Morshower , the director of NEST in Revenge of the Fallen and Dark of the Moon who now supervises TRF operations . </Li> <Li> Liam Garrigan as King Arthur , the legendary knight who first fought with the Knights of Iacon . </Li> </Ul>



--------------------------------------------------------------------------------
assistant (to ragproxyagent):

UPDATE CONTEXT

--------------------------------------------------------------------------------
Updating context and resetting conversation.
Adding doc_id doc_1586 to context.
Skip doc_id doc_1302 as it is too long to fit in the context.
Adding doc_id doc_44 to context.
Skip doc_id doc_1362 as it is too long to fit in the context.
Skip doc_id doc_691 as it is too long to fit in the context.
Adding doc_id doc_4155 to context.
Skip doc_id doc_421 as it is too long to fit in the context.
Adding doc_id doc_541 to context.
Skip doc_id doc_1170 as it is too long to fit in the context.
ragproxyagent (to assistant):

You're a retrieve augmented chatbot. You answer user's questions based on your own knowledge and the
context provided by the user.
If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.
You must give as short an answer as possible.

User's question is: who is edmund on days of our lives

Context is: <P> But with the approach of Aslan , her magical winter thaws , and Edmund is rescued after his treason . He had been greeted with a hostile reception from the White Witch after arriving at her castle alone , and even more so after informing her that Aslan had come to Narnia . The harshness of the Witch 's winter had made Edmund realise that he had been wrong in thinking that her side was the right side to be on , and he realised the full extent of her evil when he witnessed her turning a party of creatures into stone after their revelation that Father Christmas had been in Narnia - much to the Witch 's horror after she had banished him . </P>
<P> Kristen 's attempt to force Susan into giving the child back ends with the death of Susan 's identical sister , Penelope Kent . Fearing she 'll be charged with murder , Kristen pretends to be Susan and is forced to marry Susan 's boyfriend , Edmund Crumb ( Adam Caine ) . In the meantime , `` Susan '' and Edmund go on a honeymoon and Laura is arrested for Kristen 's murder . Edmund admits to Kristen 's `` murder '' and they soon run into the real Susan who explains that Kristen sold her into a harem ; it is then revealed that the dead person was Susan 's other sibling , Penelope Kent . To get revenge against Kristen , Susan exchanges her freedom for Kristen to be sold to the harem . </P>
<P> `` I Knew the Bride ( When She Used to Rock ' n ' Roll ) '' is a song written by Nick Lowe and first popularized by Dave Edmunds . It was released on Edmunds 's 1977 album Get It and a year later in a live version by Nick Lowe 's Last Chicken in the Shop on Live Stiffs Live . </P>
<P> The Governor Edmund G. Brown California Aqueduct is a system of canals , tunnels , and pipelines that conveys water collected from the Sierra Nevada Mountains and valleys of Northern and Central California to Southern California . Named after California Governor Edmund Gerald `` Pat '' Brown Sr. , the over 400 - mile ( 640 km ) aqueduct is the principal feature of the California State Water Project . </P>



--------------------------------------------------------------------------------
assistant (to ragproxyagent):

Edmund Crumb (Adam Caine) is a character on Days of Our Lives, who married Susan/"Kristen" in the storyline involving Kristen, Susan, and Penelope Kent.

--------------------------------------------------------------------------------
```

Upon examining the output, it is evident that our agent was unable to generate an answer to the question based on the initial group of context. In response, the agent automatically requested new context and, after a few rounds of updating, was able to produce a satisfactory answer.
