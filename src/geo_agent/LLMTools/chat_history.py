from ollama import AsyncClient
from pydantic.json_schema import JsonSchemaValue
from typing import Any, Callable, Literal

message = dict[str, str]

def format_message(role: Literal["system", "user", "assistant"], content: str) -> message:
    return {
        "role": role,
        "content": content
    }

# Base Class for assessing model responses in multi-attempt loops
# Using a class allows for marker specific data to be held
class BaseResponseMarker:
    # Provide an error message for the response, or 'None' if the response is valid
    def mark(self, response: str) -> str | None:
        return NotImplemented
    
    # Clear any saved context for reset
    def reset(self):
        pass

# Class to help maintain conversation context over multiple LLM 'turns'
class ChatHistory:
    def __init__(
            self, 
            ollama_client: AsyncClient,
            model: str, 

            system_prompt: str | None = None, 
            think: bool | Literal["low", "medium", "high"] | None = None,

            json: JsonSchemaValue | None = None,
            context: int | None = None,
            tools: list[Callable] | None = None,

            allowed_attempts: int | Literal["inf"] = 1,
            response_marker: BaseResponseMarker | None = None
        ):
        self.client = ollama_client
        self.messages: list[message] = []
        if system_prompt is not None:
            self.messages.append(format_message("system", system_prompt))

        self.config: dict[str, Any] = {"model": model}
        if think:
            self.config["think"] = think
        if json:
            self.config["format"] = json
        if context:
            self.config["options"] = {
                "num_ctx": context
            }
        if tools:
            self.config["tools"] = tools

        self.allowed_attempts = allowed_attempts
        if allowed_attempts:
            assert response_marker is not None, "If model looping is allowed, a response assessing function must be provided" 
            self.response_marker = response_marker
    
    # Give the model a prompt, extract its response and record the interaction in the message history
    async def chat_single(self, prompt: str, record_response: bool = True) -> str:
        self.messages.append(format_message("user", prompt))
        response = await self.client.chat(messages=self.messages, **self.config)
        output = response.message.content or ""
        if record_response:
            self.messages.append(format_message("assistant", output))
        return output

    # Give the model feedback on its erroneous responses, and allow it to try again. Most useful when using smaller LLMs
    async def chat_multiple(self, prompt: str, cull_mistakes: bool = True) -> str:
        output: str = ""    # appease static compiler analysis
        archived_messages = self.messages.copy() + [format_message("user", prompt)] if cull_mistakes else []
        
        attempts = 0
        while True:
            output = await self.chat_single(prompt, record_response=True)

            # XX add support for tool calling here if the model attempts to call a tool

            error_message = self.response_marker.mark(output)
            if error_message is None:
                if cull_mistakes:
                    self.messages = archived_messages                       # remove model's 'debugging' messages from history
                self.messages.append(format_message("assistant", output))   # record correct response
                return output
            else:
                prompt = error_message
                attempts += 1
                if self.allowed_attempts != "inf" and attempts >= int(self.allowed_attempts):
                    break

        return output
    
    # Auto select response method based off of object configuration
    async def chat(self, prompt: str) -> str:
        if self.allowed_attempts == 1:
            return await self.chat_single(prompt)
        else:
            return await self.chat_multiple(prompt)
    
    # Keep LLM client config, but clear the message record 
    def clear_history(self):
        self.messages = []
        self.response_marker.reset()