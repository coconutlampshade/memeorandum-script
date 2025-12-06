# Memeorandum to Boingboing Post Generator

A Python script that scrapes top political headlines from Memeorandum and generates Boingboing-style blog posts using Claude AI.

## Features

- Scrapes the top 20 headlines from [memeorandum.com/river](https://www.memeorandum.com/river)
- Lets you select which stories to write about
- Fetches full article content
- Generates ~250 word blog posts in Boingboing's style
- Provides 5 headline options in sentence case
- Includes proper source attribution

## Requirements

```bash
pip install requests beautifulsoup4 anthropic
```

## Setup

1. Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com)

2. Set the API key as an environment variable:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Usage

Run the script:
```bash
./memeorandum
```

The script will:
1. Display the top 20 headlines from Memeorandum
2. Prompt you to select which articles to write about (e.g., `1,3,5`)
3. Generate a Boingboing-style post for each selected article with:
   - ~250 word blog post with source attribution
   - 5 headline options in sentence case
   - Original source URL

## Example Output

```
POST:
As reported in the New York Times, [engaging 250-word post about the story...]

HEADLINES:
1. [First headline option in sentence case]
2. [Second headline option in sentence case]
3. [Third headline option in sentence case]
4. [Fourth headline option in sentence case]
5. [Fifth headline option in sentence case]

Source URL: https://example.com/article
```
