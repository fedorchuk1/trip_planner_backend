from textwrap import dedent


INSTRUCTIONS = [
    dedent("""
           Create a detailed, personalized travel itinerary by researching activities, events, 
           and attractions in specified cities, then optimally distributing time across locations based on available 
           opportunities and traveler preferences.
    """),
    
    dedent("""\
        Task description:
        ### 1. Research Phase
        - City-specific research: For each city, gather information about:
           1. Current events and festivals during the travel period
           2. Popular attractions and landmarks
           3. Age-appropriate activities and entertainment
           4. Local experiences and cultural highlights
        
        If no information is found for the event than skip this step.

        ### 2. Analysis Phase
        - Interest matching: Analyze gathered information to identify activities that align with the traveler's age group and likely interests
        - Time optimization: Determine how many days each city warrants based on:
        - Number and significance of available activities
        - Special events occurring during the travel window
        - Seasonal factors affecting accessibility
        - Travel logistics between cities

        ### 3. Planning Phase
        - Date allocation: Distribute the total travel days across cities to maximize experience value
        - Itinerary creation: Develop a day-by-day schedule including:
        - Specific dates for each city
        - Recommended activities with timing
        - Must-see attractions prioritized by relevance
        - Backup options for weather-dependent activities
        - Each day in the trip should be planned
    """),
]