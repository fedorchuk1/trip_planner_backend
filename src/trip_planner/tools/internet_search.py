from concurrent.futures import ThreadPoolExecutor
from functools import partial
from textwrap import dedent
from typing import Any, Dict, List, Optional

from agno.tools import tool
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from litellm import completion

MAX_WORKERS = 10
DEFAULT_SEARCH_RESULTS = 5
DEFAULT_MODEL = "groq/meta-llama/llama-4-scout-17b-16e-instruct"


_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)


@tool(
    name="get_top_internet_search_results",
    description="Get top search results from the internet with scraped content",
    show_result=True,
)
def get_top_internet_search_results(search_query: str) -> str:
    """
    Get top search results from the internet and scrape their content.

    Args:
        search_query: The search query to execute
        num_results: Number of search results to fetch and scrape, max 5

    Returns:
        List of dictionaries containing search results with scraped content
    """
    try:
        search_results = SerperDevTool()._run(search_query=search_query, n_results=DEFAULT_SEARCH_RESULTS)
        parsed_results = _parse_search_results(search_results)

        scrape_partial = partial(_scrape_and_summarize_site, search_query=search_query)
        scraped_contents = list(_executor.map(scrape_partial, parsed_results))

        output_content = ""
        for i, content in enumerate(scraped_contents):
            if content:
                # parsed_results[i]["scraped_content"] = content
                output_content += f"{content}\n\n"
            # else:
                # parsed_results[i]["scraped_content"] = ""

        return output_content
        
    except Exception as e:
        raise e

def _parse_search_results(search_results: str) -> List[Dict[str, str]]:
    """
    Parse search results string into structured data.
    
    Args:
        search_results: Raw search results string from SerperDevTool
        
    Returns:
        List of dictionaries with parsed search result data
    """
    if not search_results:
        return []
        
    clean_results = search_results.replace("Search results: ", "")
    sites_info = clean_results.split("---")
    
    parsed_results = []
    for site in sites_info:
        site_mapping = {}
        for line in site.split("\n"):
            if not line.strip():
                continue
                
            try:
                key, value = line.split(": ", 1)
                site_mapping[key.lower().strip()] = value.strip()
            except ValueError:
                continue
                
        if site_mapping:
            parsed_results.append(site_mapping)
            
    return parsed_results


def _scrape_and_summarize_site(search_result: Dict[str, str], search_query: str) -> Optional[str]:
    """
    Scrape a website and summarize its content relevant to the search query.
    
    Args:
        search_result: Dictionary containing search result data including 'link'
        search_query: Original search query for context
        
    Returns:
        Summarized content or None if scraping fails
    """
    url = search_result.get("link")
    if not url:
        return None
        
    try:
        scraped_content = ScrapeWebsiteTool()._run(website_url=url)
        
        if not scraped_content:
            return None
            
        summary = _summarize_content(scraped_content, search_query)

        print("-" * 40)
        print(summary)
        print("-" * 40)

        return summary
        
    except Exception:
        return None


def _summarize_content(content: str, search_query: str) -> Optional[str]:
    """
    Summarize website content using AI model.
    
    Args:
        content: Raw website content
        search_query: Original search query for context
        
    Returns:
        Summarized content or None if summarization fails
    """
    prompt = dedent(f"""\
        Summarize this website content related to the search query: "{search_query}"
        
        Focus on extracting information about events, restaurants, or landmarks.
        Filter out information not related to the search query (irrelevant dates, locations, etc.)

        Extract essential information in this format:
        **Name:** [Official name]
        **Location:** [Address/area/neighborhood]
        **Date/Hours:** [When available/open]
        **Price:** [Cost/pricing range]
        **Type:** [Category - event type, cuisine style, landmark type]
        **Key Details:** [1-2 most important features/highlights]
                    
        Website content:
        {content}
        
        Return the summary in markdown format. If no relevant information is found, return "No relevant information found."
    """)

    try:
        response = completion(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes travel-related website content."},
                {"role": "user", "content": prompt}
            ],
        )
        
        return response.choices[0].message.content # type: ignore
        
    except Exception:
        return None
