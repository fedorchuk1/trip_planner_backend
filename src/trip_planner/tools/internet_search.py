import json

from typing import Any, Type
from pydantic import BaseModel, Field

from crewai_tools import BaseTool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

from concurrent.futures import ThreadPoolExecutor


class GetTopKSearchResultsToolSchema(BaseModel):
    search_query: str = Field(..., description="The query to search the internet for")
    # top_k: int = Field(..., description="The number of search results to return")


from litellm import completion


_executor = ThreadPoolExecutor(max_workers=10)

class GetTopKSearchResultsTool(BaseTool):
    name: str = "GetTopKSearchResults"
    description: str = (
        "Given a search query returns text from top k search sites"
    )
    args_schema: Type[BaseModel] = GetTopKSearchResultsToolSchema

    def _run(self, **kwargs: Any) -> Any:
        search_query = kwargs.get("search_query")
        # top_k = kwargs.get("top_k")
        search_results = SerperDevTool()._run(search_query=search_query, n_results=5)
        parsed_results = self._split_search_results(search_results)

        scraped_results = _executor.map(self._scrape_site, parsed_results)

        for i, scraped_result in enumerate(scraped_results):
            if scraped_result is None:
                continue
        
            parsed_results[i]["text"] = scraped_result

        return json.dumps(parsed_results)
    
    def _split_search_results(self, search_results: str) -> list[dict[str, str]]:
        search_results = search_results.replace("Search results: ", "")
        sites_info = search_results.split("---")
        
        parsed_results = []
        for site in sites_info:
            site_mapping = {}
            for x in site.split("\n"):
                if not x:
                    continue
                key, value = x.split(": ", 1)
                site_mapping[key.lower()] = value
            parsed_results.append(site_mapping)
        return parsed_results

    def _scrape_site(self, search_results: dict[str, str]) -> str | None:
        url = search_results.get("link")
        if not url:
            return None
        try:
            url_text = ScrapeWebsiteTool()._run(website_url=url)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
        
        return url_text
        # response = completion(
        #     model="groq/llama-3.1-8b-instant",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant that summarizes websites."},
        #         {"role": "user", "content": url_text}
        #     ]
        # )

        # return response.choices[0].message.content


from agno.tools import tool


@tool(
    name="get_top_k_internet_search_results",
    description="Get top k search results from the internet",
    show_result=True,
)
def get_top_k_internet_search_results(search_query: str, top_k: int = 5) -> str:
    """
    Get top k search results from the internet

    Args:
        num_stories: Number of stories to fetch (default: 5)

    Returns:
        str: The top stories in text format
    """
    search_results = SerperDevTool()._run(search_query=search_query, n_results=5)
    parsed_results = _split_search_results(search_results)

    scraped_results = _executor.map(_scrape_site, parsed_results)

    for i, scraped_result in enumerate(scraped_results):
        if scraped_result is None:
            continue
    
        parsed_results[i]["text"] = scraped_result

    return json.dumps(parsed_results)

def _split_search_results(search_results: str) -> list[dict[str, str]]:
    search_results = search_results.replace("Search results: ", "")
    sites_info = search_results.split("---")
    
    parsed_results = []
    for site in sites_info:
        site_mapping = {}
        for x in site.split("\n"):
            if not x:
                continue
            key, value = x.split(": ", 1)
            site_mapping[key.lower()] = value
        parsed_results.append(site_mapping)
    return parsed_results


def _scrape_site(search_results: dict[str, str]) -> str | None:
    url = search_results.get("link")
    if not url:
        return None
    try:
        url_text = ScrapeWebsiteTool()._run(website_url=url)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
    
    response = completion(
        model="groq/llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes websites."},
            {"role": "user", "content": url_text}
        ]
    )

    return response.choices[0].message.content
