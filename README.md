# rezkaAPI

Python library for getting various information from the site [hdrezka.ag](https://hdrezka.ag/) and for interacting with it.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install rezkaAPI.

```bash
pip install rezkaAPI
```

## Usage

```python
from rezkaAPI import Rezka

obj = Rezka("Breaking bad")

obj.search()
# Allows you to search for content on the site
# Returns a JSON object with search results

result_id = 2
obj.select_result(result_id)
# Allows you to select a search result by id
# Returns the movie/series name on success

obj.information()
# Get detailed information about a movie/series as JSON

obj.get_links()
# Get streaming links

# Access to class fields
obj.search_request
obj.name
obj.url
obj.search_results
obj.info
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)