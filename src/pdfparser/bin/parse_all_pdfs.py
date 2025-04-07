

def main(): 
    import dotenv
    dotenv.load_dotenv(".env")

    from concurrent.futures import Future, ThreadPoolExecutor
    from pdfparser.util import parse_args
    from pdfparser import PdfParser
    from pathlib import Path
    from tqdm import tqdm
    import os

    args = parse_args()

    if args.get("help", False):
        print("Usage: parse_all_pdfs.py [--dir <dir>] [--output <output>] [--overwrite] [--verbose] [--analyse-images] [--use-iterative-image-analyser]")
        return

    parser = PdfParser(args)
    dir = args.get("dir")
    if dir is None: dir = args.get("0")
    if dir is None: raise Exception("No dir specified. Provide the '--dir' argument (or the first positional argument) to specify the dir to parse.")

    dir = Path(dir)
    if not dir.exists(): raise Exception(f"Dir '{dir}' does not exist.")
    if not dir.is_dir(): raise Exception(f"'{dir}' is not a dir.")
    
    output = args.get("output")
    if output is None: output = dir / "output"

    if not output.exists(): output.mkdir(parents=True)

    concurrency = int(args.get("--concurrency", os.getenv('CONCURRENCY', 4)))
    counter = 0
    parser = PdfParser(args)
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = list[Future]()
        for file in dir.iterdir():
            if file.is_file() and file.suffix.lower() == ".pdf":
                counter += 1
                def parse_file(file:Path, parser:PdfParser, target_dir:Path):
                    result = parser.parse(file, analyse_images=args.get("analyse-images", True), use_iterative_image_analyser=args.get("use-iterative-image-analyser", True))
                    with open(target_dir / f"{file.stem}.md", "w", encoding="utf-8") as f:
                        f.write(result.markdown)
                    return True
                
                futures.append(executor.submit(parse_file, file, parser, output))
            elif file.suffix.lower() == ".identifier":
                continue
            else: 
                print(f"Skipping file: {file.name} - Not a PDF file")

        progress_bar = tqdm(total=len(list(dir.iterdir())), desc="Processing files", unit="file", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")
        executor.shutdown(wait=True)

        success_count = 0
        fail_count = 0
        for f in futures:
            progress_bar.update(1)
            if f.result() == True: 
                success_count += 1
            else: 
                fail_count += 1

    print(f"Done, {success_count} files processed successfully, {fail_count} files failed to be processed.")


if __name__ ==  '__main__':
    main()