# contextify
Standalone context building application that performs in-depth 
github repository analysis and website crawl. Output is a summary 
that can be used for context in AI applications like Devplan or 
for input into other process (or simply for better understanding of 
code or website content).

# Quick Start:

## Pre-requisites
To run quick start you need **Python 3.12+**, **uv** and **Node.js 18+**.

On Mac, install them using:
```bash
brew install python node
```
then for uv (if you don't have it yet):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Get your Google API Key:
1. Visit https://aistudio.google.com/prompts/new_chat
2. Click "Get API key"
3. Create an API key and copy it

## Run quick start:

```bash
GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY> ./examples/quick-start/start.sh
```

Then open http://localhost:5173.

Add your repository or website, then navigate to it and click Rescan. After
a few seconds repo/site analysis should appear.
