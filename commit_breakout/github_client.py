"""
GitHub API client for fetching contribution data.
"""
import os
import requests
from datetime import datetime, date
from typing import Optional
from .models import ContributionData, ContributionWeek, ContributionDay
from .constants import GITHUB_API_URL, GITHUB_TIMEOUT


class GitHubClient:
    """Client for fetching GitHub contribution graph data."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token (read:user scope required).
                   If None, will attempt to read from GITHUB_TOKEN env var.
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError(
                "GitHub token required. Set GITHUB_TOKEN environment variable "
                "or pass token to GitHubClient constructor."
            )
    
    def get_contributions(self, username: str) -> ContributionData:
        """
        Fetch contribution data for a GitHub user.
        
        Args:
            username: GitHub username
            
        Returns:
            ContributionData object with full contribution graph
            
        Raises:
            requests.HTTPError: If API request fails
            ValueError: If response data is invalid
        """
        query = """
        query($username: String!) {
          user(login: $username) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                    contributionLevel
                  }
                }
              }
            }
          }
        }
        """
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'query': query,
            'variables': {'username': username}
        }
        
        try:
            response = requests.post(
                GITHUB_API_URL,
                json=payload,
                headers=headers,
                timeout=GITHUB_TIMEOUT
            )
            response.raise_for_status()
            
        except requests.RequestException as e:
            raise requests.HTTPError(
                f"Failed to fetch GitHub data for user '{username}': {e}"
            )
        
        data = response.json()
        
        # Validate response structure
        if 'errors' in data:
            raise ValueError(f"GitHub API error: {data['errors']}")
        
        if 'data' not in data or 'user' not in data['data']:
            raise ValueError(f"User '{username}' not found or data unavailable")
        
        # Handle case where user exists but contributionsCollection is None (though unlikely with GraphQL schema)
        if not data['data']['user']['contributionsCollection']:
             raise ValueError(f"Contribution data unavailable for user '{username}'")

        calendar = data['data']['user']['contributionsCollection']['contributionCalendar']
        
        return self._parse_contribution_data(username, calendar)
    
    def _parse_contribution_data(self, username: str, calendar: dict) -> ContributionData:
        """Parse raw GitHub calendar data into ContributionData model."""
        weeks = []
        all_dates = []
        
        for week_data in calendar['weeks']:
            days = []
            for day_data in week_data['contributionDays']:
                day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
                all_dates.append(day_date)
                
                # Map GitHub's contribution level (NONE, FIRST_QUARTILE, etc.) to 0-4
                level = self._parse_contribution_level(day_data['contributionLevel'])
                
                day = ContributionDay(
                    date=day_date,
                    count=day_data['contributionCount'],
                    level=level
                )
                days.append(day)
            
            weeks.append(ContributionWeek(days=days))
        
        # Handle empty data case
        if not all_dates:
             # Just return empty or raise? Spec says "No contributions... Generate empty grid" in edge cases.
             # But here we are parsing. If no dates, we can't determine start/end.
             # Let's assume there's always at least one day if the user exists.
             # If not, let's use today as fallback.
             today = date.today()
             start_date = today
             end_date = today
        else:
             start_date = min(all_dates)
             end_date = max(all_dates)

        return ContributionData(
            username=username,
            total_contributions=calendar['totalContributions'],
            weeks=weeks,
            start_date=start_date,
            end_date=end_date
        )
    
    @staticmethod
    def _parse_contribution_level(level_str: str) -> int:
        """
        Convert GitHub's contribution level string to numeric 0-4.
        
        GitHub levels: NONE, FIRST_QUARTILE, SECOND_QUARTILE, 
                       THIRD_QUARTILE, FOURTH_QUARTILE
        """
        level_map = {
            'NONE': 0,
            'FIRST_QUARTILE': 1,
            'SECOND_QUARTILE': 2,
            'THIRD_QUARTILE': 3,
            'FOURTH_QUARTILE': 4,
        }
        return level_map.get(level_str, 0)
    
    def save_contribution_data(self, data: ContributionData, filepath: str):
        """Save contribution data to JSON file for caching."""
        import json
        
        def date_serializer(obj):
            if isinstance(obj, date):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        # We need to convert the dataclass to a dict recursively.
        # simple .__dict__ on the top object works if children are also dicts, but they are objects.
        # Let's construct the dict structure manually to be safe and clear.
        
        data_dict = {
            'username': data.username,
            'total_contributions': data.total_contributions,
            'start_date': data.start_date,
            'end_date': data.end_date,
            'weeks': []
        }
        
        for week in data.weeks:
            week_dict = {'days': []}
            for day in week.days:
                week_dict['days'].append({
                    'date': day.date,
                    'count': day.count,
                    'level': day.level
                })
            data_dict['weeks'].append(week_dict)

        with open(filepath, 'w') as f:
            json.dump(data_dict, f, default=date_serializer, indent=2)
    
    @staticmethod
    def load_contribution_data(filepath: str) -> ContributionData:
        """Load contribution data from JSON file."""
        import json
        from datetime import datetime
        
        with open(filepath, 'r') as f:
            data_dict = json.load(f)
        
        # Reconstruct date objects
        weeks = []
        for week_data in data_dict['weeks']:
            days = []
            for day_data in week_data['days']:
                day = ContributionDay(
                    date=datetime.fromisoformat(day_data['date']).date(),
                    count=day_data['count'],
                    level=day_data['level']
                )
                days.append(day)
            weeks.append(ContributionWeek(days=days))
        
        return ContributionData(
            username=data_dict['username'],
            total_contributions=data_dict['total_contributions'],
            weeks=weeks,
            start_date=datetime.fromisoformat(data_dict['start_date']).date(),
            end_date=datetime.fromisoformat(data_dict['end_date']).date()
        )
