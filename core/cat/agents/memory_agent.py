
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.output_parsers.string import StrOutputParser

from cat.looking_glass.callbacks import NewTokenHandler
from cat.agents.base_agent import BaseAgent, AgentOutput

class MemoryAgent(BaseAgent):

    async def execute(self, stray, prompt_prefix, prompt_suffix) -> AgentOutput:
            
        final_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    template=prompt_prefix + prompt_suffix
                ),
                *(stray.langchainfy_chat_history()),
            ]
        )

        memory_chain = (
            final_prompt
            #| RunnableLambda(lambda x: self._log_prompt(x))
            | stray._llm
            | StrOutputParser()
        )

        output = memory_chain.invoke(
            # convert to dict before passing to langchain
            # TODO: ensure dict keys and prompt placeholders map, so there are no issues on mismatches
            stray.working_memory.agent_input.dict(),
            config=RunnableConfig(callbacks=[NewTokenHandler(stray)])
        )

        return AgentOutput(output=output)
    
