# Basic PDF to Markdown

This is a simple library for converting PDF files into markdown. 

The parser takes 2 steps to convert the PDF into markdown: 

1. Use **Azure DocumentIntelligence** to parse the PDF into markdown
2. Extract all figures + images from the PDF, and create a markdown representation using an LLM to support


## Install 

You can pip install this libarary like this: 

```bash
pip install git+https://github.com/demo-ninjas/pdf-parser
```

NB: It is best to do this in a virtual environment :)

## Library Use

To use this as a library, simply add this library to your requirements.txt: 

```
git+https://github.com/demo-ninjas/pdf-parser
```

Then, use the library, like this: 

```Python
from pdfparser.util import parse_args
args = parse_args() ## or create a dict of config arguments ({ "arg1name":"arg1val", "arg2name":"arg2val", etc... }), or pass an empty dictionary and rely on the ENV

from pdfparser import PdfParser
parser = PdfParser(args)

from pathlib import Path
file = Path('path/to/pdf-file.pdf')

# Parse the File into Markdown
result = parser.parse(file)

# Result contains the file as a markdown string, along with the resolved title of the document + a  list of paths to the images that were saved  
markdown_content = result.markdown
document_title = result.title
```

## Command Line

The install will add 2 command line programs to your environment: 

* `parse-pdf` - parse a single pdf into markdown
* `parse-all-pdfs` - parse a folder of pdf's into markdown

