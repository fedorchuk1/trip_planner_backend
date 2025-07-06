from typing import Any, Type
from pydantic import BaseModel, Field

from crewai_tools import BaseTool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

from concurrent.futures import ThreadPoolExecutor


class GetTopKSearchResultsToolSchema(BaseModel):
    search_query: str = Field(..., description="The query to search the internet for")
    top_k: int = Field(..., description="The number of search results to return")


_executor = ThreadPoolExecutor(max_workers=10)

class GetTopKSearchResultsTool(BaseTool):
    name: str = "GetTopKSearchResults"
    description: str = (
        "Given a search query returns text from top k search sites"
    )
    args_schema: Type[BaseModel] = GetTopKSearchResultsToolSchema

    def _run(self, **kwargs: Any) -> Any:
        search_query = kwargs.get("search_query")
        top_k = kwargs.get("top_k")
        search_results = SerperDevTool()._run(search_query=search_query, n_results=1)
        parsed_results = self._split_search_results(search_results)

        scraped_results = _executor.map(self._scrape_site, parsed_results)

        for i, scraped_result in enumerate(scraped_results):
            if scraped_result is None:
                continue
        
            parsed_results[i]["text"] = scraped_result

        return parsed_results
    
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

