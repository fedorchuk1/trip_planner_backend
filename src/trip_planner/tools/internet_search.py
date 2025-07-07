from concurrent.futures import ThreadPoolExecutor
from functools import partial
from textwrap import dedent

from agno.tools import tool
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from litellm import completion

_executor = ThreadPoolExecutor(max_workers=10)


@tool(
    name="get_top_internet_search_results",
    description="Get top search results from the internet",
    show_result=True,
)
def get_top_internet_search_results(search_query: str) -> str:
    """
    Get top k search results from the internet

    Args:
        num_stories: Number of stories to fetch (default: 5)

    Returns:
        str: The top stories in text format
    """
    search_results = SerperDevTool()._run(search_query=search_query, n_results=5)
    parsed_results = _split_search_results(search_results)

    _scrape_site_partial = partial(_scrape_site, search_query=search_query)
    scraped_results = _executor.map(_scrape_site_partial, parsed_results)

    for i, scraped_result in enumerate(scraped_results):
        if scraped_result is None:
            continue
    
        parsed_results[i]["text"] = scraped_result

    return parsed_results

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


def _scrape_site(search_results: dict[str, str], search_query: str) -> str | None:
    url = search_results.get("link")
    if not url:
        return None
    try:
        url_text = ScrapeWebsiteTool()._run(website_url=url)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

    prompt = dedent(f"""\
        Summarize this website text about [events/restaurants/landmarks] in [city].
        Search query: {search_query}
        Filter all the information that is not related to the search query, e.g. unrelevant dates, locations, etc.

        Extract only essential information in this format:
        Name: [Official name]
        Location: [Address/area/neighborhood]
        Date/Hours: [When available/open]
        Price: [Cost/pricing range]
        Type: [Category - event type, cuisine style, landmark type]
        Key Details: [1-2 most important features/highlights]
                    
        Here is the website content:
        {url_text}
        Return the summary in markdown format.
    """)


    response = completion(
        model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes websites."},
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content
