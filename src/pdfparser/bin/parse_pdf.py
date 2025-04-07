
import dotenv
dotenv.load_dotenv(".env")

from pdfparser.util import parse_args

def main(): 
    args = parse_args()

    if args.get("help", False): 
        print("Usage: parse_pdf.py [--file <file>] [--output <output>] [--overwrite] [--verbose] [--analyse-images] [--use-iterative-image-analyser]")
        return

    from pdfparser import PdfParser
    from pathlib import Path

    parser = PdfParser(args)
    file = args.get("file")
    if file is None: file = args.get("0")
    if file is None: raise Exception("No file specified. Provide the '--file' argument (or the first positional argument) to specify the file to parse.")

    file = Path(file)
    if not file.exists(): raise Exception(f"File '{file}' does not exist.")
    if not file.is_file(): raise Exception(f"File '{file}' is not a file.")
    if not file.suffix in [".pdf", ".PDF"]: raise Exception(f"File '{file}' is not a PDF file.")

    output = args.get("output")
    if output is None: output = file.parent / "output" / (file.stem + ".md")
    if output is None: raise Exception("No output file specified. Provide the '--output' argument to specify the output file to write to.")

    if output == file: raise Exception("Output file cannot be the same as the input file. Provide a different output file using the '--output' argument.")
    if output.exists() and not args.get("overwrite", False):
        raise Exception(f"Output file '{output}' already exists. Use the '--overwrite' argument to overwrite it.")
    if output.exists(): output.unlink()
    if not output.parent.exists(): output.parent.mkdir(parents=True)
    if not output.parent.is_dir(): raise Exception(f"Output file '{output}' is not a directory.")
    if not output.parent.is_dir(): output.parent.mkdir(parents=True)

    verbose = args.get("verbose", "false") == "true"

    if verbose: print(f"Parsing file '{file}' and writing to '{output}'...")
    result = parser.parse(file, analyse_images=args.get("analyse-images", True), use_iterative_image_analyser=args.get("use-iterative-image-analyser", True))

    if verbose: print(f"Writing to '{output}'...")
    with open(output, "w", encoding="utf-8") as f:
        f.write(result.markdown)

    if verbose: 
        print(f"Finished analysing: {result.title}")
        print(f"Output markdown written to '{output}'.")


if __name__ ==  '__main__':
    main()