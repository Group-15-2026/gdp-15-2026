from geo_agent.OrchestratorClient.llm_agent import run_task

#import pytest
import asyncio

# XX TODO: add unit tests. Currently just seeing if the code runs

async def main():
    result = await run_task()    
    print("\nResult:", result)

if __name__ == "__main__":
    asyncio.run(main())