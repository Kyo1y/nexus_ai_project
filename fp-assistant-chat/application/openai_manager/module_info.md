
# Goal
Have a centralized module that handles interacting with any of the OpenAI endpoints. Controls for using synchronus calls versus asysynchronus calls should be handled here. Key management will also be managed with in this module. 

# Specification
- No logic specific information for content of the calls.
    - Meaning, no prompt text stored here, no logic tied in with what to do with processing content of response, etc...
- Controls for synchronous vs asynchronous calls will be handled within the module
- Key management will be handled within this module too

Request parameters:
- api_key
- engine
- id
- api_version
- api_type
- organization
- response_ms
- api_base

# Information
Metadata is used to keep track of information in async calls. Data is used to pass in information to the requests, including the expected parameters and others (temperature, top_p, api_key, engine, ...)