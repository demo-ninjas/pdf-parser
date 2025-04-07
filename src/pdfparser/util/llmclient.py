from openai import AzureOpenAI
from openai.types.responses import ResponseInputParam

class LLMClient:
    _model:str = None
    _api_key:str = None
    _api_version:str = None
    _endpoint:str = None
    _client = None
    _default_instruction:str = None
    _default_temperature:float = 0.6
    _default_max_tokens:int = 4092
    _default_top_p:float = 1.0
    

    def __init__(self, args:dict[str, str]):
        import os
        
        self._model = args.get('llm-model', os.environ.get("LLM_MODEL", "gpt-4o"))
        self._api_key = args.get('llm-api-key', os.environ.get("LLM_API_KEY", None))
        if self._api_key is None: raise Exception("LLM API key not specified. Provide either the '--llm-api-key' argument or specify the 'LLM_API_KEY' environment variable")
        self._api_version = args.get('llm-api-version', os.environ.get("LLM_API_VERSION", "2024-02-15-preview"))
        self._endpoint = args.get('llm-endpoint', os.environ.get("LLM_ENDPOINT", os.environ.get("AZURE_OPENAI_ENDPOINT", None))) 
        if self._endpoint is None: raise Exception("LLM endpoint not specified. Provide either the '--llm-endpoint' argument or specify the 'LLM_ENDPOINT' environment variable")

        self._default_instruction = args.get('llm-instruction', os.environ.get("LLM_INSTRUCTION", "You are a helpful assistant. Answer the question as best you can."))

        self._client = AzureOpenAI(
            azure_endpoint=self._endpoint,
            azure_deployment=self._model,
            api_key=self._api_key,
            api_version=self._api_version,
        )


    def generate(self, messages:list[dict|ResponseInputParam], model:str = None, temperature:float = None, max_tokens:int = None, top_p:float = None) -> str:
        if model is None or len(model) == 0:
            model = self._model
        if temperature is None or len(temperature) == 0:
            temperature = self._default_temperature
        if max_tokens is None or len(max_tokens) == 0:
            max_tokens = self._default_max_tokens
        if top_p is None or len(top_p) == 0:
            top_p = self._default_top_p

        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        return response.choices[0].message.content
    
    def generate_text(self, prompt: str, instruction:str = None, model:str = None, temperature:float = None, max_tokens:int = None, top_p:float = None) -> str:
        if model is None or len(model) == 0:
            model = self._model
        if temperature is None or len(temperature) == 0:
            temperature = self._default_temperature
        if max_tokens is None or len(max_tokens) == 0:
            max_tokens = self._default_max_tokens
        if top_p is None or len(top_p) == 0:
            top_p = self._default_top_p
        if instruction is None or len(instruction) == 0:
            instruction = self._default_instruction

        response = self._client.responses.create(
            model=model,
            instructions=instruction,
            input=prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=top_p,
        )
        return response.output_text