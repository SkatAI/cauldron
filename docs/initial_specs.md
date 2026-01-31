# Specs

these are the initial specs for agent service

stack:
- python
- langchain
- langgraph
- langsmith


LLMs are obtained from **openrouter.ai** API
- allows the possibility of swapping and testing different LLMs

--- codebase

- automated  tests
- Makefile
- Docker based with docker-compose.yaml for local dev
- .env.example
- FastAPI

--- agent tasks v1
this is a first version of the system. other tasks will be added later

###  main task

receives a text
must validate the text :
- presence of sections
- no toxic or NSFW content


The received text is a system prompt for a AI personna. it is written in markdown.

the agent must return
- if the input text is valid : code that ackownledges the validation
- if the input text is invalid : invalid code and a message explaining why


### Client

The agent will be called from a BFF client application.

protocol must be specified and clear so that the BFF can act upon the agent's response.



