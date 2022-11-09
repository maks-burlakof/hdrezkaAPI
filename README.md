# rezkaAPI

Python library for getting various information from the site [hdrezka.ag](https://hdrezka.ag/) and for interacting with it.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install rezkaAPI.

```bash
pip install rezkaAPI
```

## Usage

```python
from rezkaAPI.parser import Rezka

movie = Rezka("Interstellar")

movie.search()
# Allows you to search for content on the site
# Returns a JSON object with search results

result_id = 2
movie.select_result(result_id)
# Allows you to select a search result by id
# Returns the movie/series name on success

movie.information()
# Get detailed information about a movie/series as JSON

movie.get_links()
# Get streaming links

# Access to class fields
movie.search_request
movie.name
movie.url
movie.search_results
movie.info
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
