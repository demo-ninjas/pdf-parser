from pathlib import Path
from fitz import Page as FitzPage
from .docintel import DocIntelAnalyser, DocIntelAnalysisPage, DocIntelAnalysis

from pdfparser.util import LLMClient
from pdfparser.util import markdown as MarkdownUtils

class ResultPage:
    page_number:int = None
    doc_page:DocIntelAnalysisPage = None
    pdf_page:FitzPage = None
    xRatio:float = None
    yRatio:float = None
    
class ParseResult:
    markdown:str = None
    pages:list[ResultPage] = None
    images:list[Path] = None
    title:str = None
    analysis:DocIntelAnalysis = None

class PdfParser():
    analyser:DocIntelAnalyser = None
    llmclient:LLMClient = None
    concurrency:int = None
    save_images:bool = None

    def __init__(self, args:dict[str, str]):
        self.analyser = DocIntelAnalyser(args)
        self.llm = LLMClient(args) if args.get('use-llm', True) else None
        self.concurrency = int(args.get('concurrency', 0))
        self.save_images = args.get('save-images', True)

    def parse(self, file:Path, analyse_images:bool = True, use_iterative_image_analyser:bool = True, verbose:bool = True):
        import os
        from concurrent.futures import ThreadPoolExecutor
        from fitz import Pixmap, Matrix
        from fitz import open as FitzOpen
        from .docintel import DocIntelAnalysis

        image_file_prefix = file.stem.replace(' ', '_')
        file_folder = file.parent
        image_folder = file_folder / "images"
        if not image_folder.exists():
            image_folder.mkdir(parents=True)
        if not image_folder.is_dir():
            raise Exception(f"Image folder '{image_folder}' is not a directory.")

        output_result = ParseResult()

        ## Step 1: Analyse the document using Azure Document Intelligence
        cached_analysis = file_folder / f"{file.stem}.analysis.json"
        analysis = None
        if cached_analysis.exists():
            if verbose: print(f" - Loading cached analysis from '{cached_analysis}'")
            with open(cached_analysis, "r", encoding="utf-8") as f:
                json_data = f.read()
                if len(json_data) > 0:
                    try:
                        import json
                        analysis = DocIntelAnalysis.from_json(json.loads(json_data))
                    except Exception as e:
                        print(f"Error loading cached analysis, will fallback to re-analysing the document. Error: {e}")
                        analysis = None
        
        if analysis is None:
            if verbose: print(f" - Analysing PDF and saving to '{cached_analysis}'")
            analysis = self.analyser.analyse(file)
            with open(cached_analysis, "w", encoding="utf-8") as f:
                import json
                f.write(json.dumps(analysis.to_json(), indent=4))

        if not analysis:
            raise Exception(f"Error analysing PDF file '{file}'. No analysis result returned.")
        
        ## Save the analysis result to the output result
        output_result.markdown = analysis.markdown
        output_result.analysis = analysis

        ## Step 2: Go through each page and parse out the images and markdown
    
        if verbose: print("  - Loading PDF")
        pdf_document = FitzOpen(file)
        output_result.pages = []
        for page in analysis.pages:
            pdfpage = pdf_document.load_page(page.page_number - 1)
            xRatio = (pdfpage.rect.x1 - pdfpage.rect.x0) / page.width
            yRatio = (pdfpage.rect.y1 - pdfpage.rect.y0) / page.height
            result_page = ResultPage()
            result_page.page_number = page.page_number - 1
            result_page.doc_page = page
            result_page.pdf_page = pdfpage
            result_page.xRatio = xRatio
            result_page.yRatio = yRatio
            output_result.pages.append(result_page)
            
        with ThreadPoolExecutor(max_workers=self.concurrency if self.concurrency > 0 else None) as executor:
            futures = []
            replacements = []
            if analysis.figures and len(analysis.figures) > 0:
                output_result.images = []
                for idx, figure in enumerate(analysis.figures):
                    for span in figure.spans:
                        # print(f"  Span: {span.offset} ({span.length}) [In MD: {markdown[span.offset:span.offset+span.length]}]")
                        figure_content = output_result.markdown[span.offset:span.offset+span.length]
                        caption_start = 0
                        if '<figure>' in figure_content:
                            caption_start = figure_content.find('<figure>') + len('<figure>')
                        elif '<figcaption>' in figure_content:
                            caption_start = figure_content.find('<figcaption>') + len('<figcaption>')
                        
                        caption_end = -1
                        if '</figure>' in figure_content:
                            caption_end = figure_content.find('</figure>')
                        elif '</figcaption>' in figure_content:
                            caption_end = figure_content.find('</figcaption>')
                        if caption_start == -1 or caption_end == -1:
                            caption_start = 0
                            caption_end = len(figure_content)
                        if caption_start > caption_end:
                            caption_start = 0
                            caption_end = len(figure_content)
                        if caption_start == -1:
                            caption_start = 0
                        if caption_end == -1:
                            caption_end = len(figure_content)
                        caption = figure_content[caption_start:caption_end]
                        replacements.append({
                            "content": caption.strip().replace("\\n", " "),
                            "start": span.offset,
                            "end": span.offset+span.length,
                            "figure_id": idx,
                            "description": "<!-- No description available -->",
                            "image_name": ""
                        })

                    for region_idx,region in enumerate(figure.bounding_regions):
                        try:
                            page_info = output_result.pages[region.page_number-1]
                            xRatio = page_info.xRatio
                            yRatio = page_info.yRatio
                            pdf_page = page_info.pdf_page
                            x0 = region.polygon[0] * xRatio
                            y0 = region.polygon[1] * yRatio
                            x1 = region.polygon[4] * xRatio
                            y1 = region.polygon[5] * yRatio
                            image_name = f"{image_file_prefix}_{region.page_number}_{idx}_{region_idx}.png"
                            if verbose: print(f"  - Extracting image: {image_name}")
                            pix = pdf_page.get_pixmap(clip=[x0, y0, x1, y1], matrix=Matrix(2, 2))
                            img_path = os.path.join(image_folder, image_name)
                            if self.save_images:
                                if verbose: print(f"  - Saving image to '{img_path}'")
                                pix.save(img_path)
                            output_result.images.append(Path(img_path))
                            image_bytes = pix.tobytes("png")

                            if analyse_images and self.llm is not None:
                                section_name = MarkdownUtils.determine_section_name_at_offset(output_result.markdown, span.offset)
                                prior_context = MarkdownUtils.find_prior_context(output_result.markdown, span.offset)
                                post_context = MarkdownUtils.find_post_context(output_result.markdown, span.offset+span.length)
                                cached_image_analysis_file = image_folder / f"{image_file_prefix}_{region.page_number}_{idx}_{region_idx}.analysis.json"
                                def describe_image(image_bytes, figure_id, llm, section_name, prior_context, post_context, image_name, cached_image_analysis_file):
                                    from .image_analysis import analyse_image_data, analyse_image_data_iteratively
                                    try:
                                        image_analysis = None
                                        if cached_image_analysis_file.exists():
                                            if verbose: print(f" - Loading cached image analysis from '{cached_image_analysis_file}'")
                                            with open(cached_image_analysis_file, "r", encoding="utf-8") as f:
                                                json_data = f.read()
                                                if len(json_data) > 0:
                                                    try:
                                                        import json
                                                        image_analysis = json.loads(json_data)
                                                    except Exception as e:
                                                        print(f"Error loading cached image analysis, will fallback to re-analysing the image. Error: {e}")
                                                        image_analysis = None
                                        
                                        if image_analysis is None:
                                            if use_iterative_image_analyser:
                                                result = analyse_image_data_iteratively(image_bytes, "png", llm, section_name=section_name, prior_context=prior_context, post_context=post_context)
                                            else: 
                                                result = analyse_image_data(image_bytes, "png", llm, section_name=section_name, prior_context=prior_context, post_context=post_context)
                                            
                                            if result is not None: 
                                                with open(cached_image_analysis_file, "w", encoding="utf-8") as f:
                                                    import json
                                                    f.write(json.dumps({
                                                        "description": result,
                                                        "section_name": section_name,
                                                        "prior_context": prior_context,
                                                        "post_context": post_context
                                                    }, indent=4))
                                        else:
                                            result = image_analysis.get("description", "<!-- No description available -->")
                                    except Exception as e:
                                        result = "<!-- There was an error analysing the image -->"
                                        print(f"Error analysing image: {e}")
                                    return (figure_id, result, image_name)
                                
                                futures.append(executor.submit(describe_image, image_bytes, figure_id=idx, llm=self.llm, section_name=section_name, prior_context=prior_context, post_context=post_context, image_name=image_name, cached_image_analysis_file=cached_image_analysis_file))
                        except Exception as e:
                            print(f"Error processing region {region_idx} of figure {idx} in pdf {file.stem}: {e}")
                            continue
                    
            ## Wait for all futures to complete1
            if verbose: print("  - Analysing Images...")
            for future in futures:
                figure_id, desc, image_name = future.result()
                for rep in replacements:
                    if rep["figure_id"] == figure_id:
                        rep["description"] = desc
                        rep["image_name"] = image_name
                        break
            
            # Sort the replacements in reverse order of start index (to avoid messing up the indexes as we apply the replacements)
            replacements.sort(key=lambda x: x["start"], reverse=True)

            # Replace the content in the markdown
            if verbose: print("  - Applying image replacements")
            for rep in replacements:
                output_result.markdown = output_result.markdown[:rep["start"]] + "<!-- Start of description of image at this position in the source document -->\n\n<!-- Image Path: " + rep["image_name"] + " -->\n\n**Caption:** " + rep["content"] + "\n\n**Description:** " + rep["description"] + "\n<!-- End of Image Description -->" + output_result.markdown[rep["end"]:]

        ## Find the first header in the document
        if verbose: print("  - Determining Title")

        ## Option 1: Look through the paragraphs list for any with a role of "title"
        title = None
        
        for para in analysis.paragraphs:
            if para.role == "title":
                title = para.content
                break

        ## Option 2: Look for the first header in the markdown  
        if title is None:
            first_header = output_result.markdown.find("\n# ")
            if first_header != -1:
                first_header_end = output_result.markdown.find("\n", first_header + 2)
                if first_header_end == -1:
                    first_header_end = len(output_result.markdown)
                title = output_result.markdown[first_header + 2:first_header_end].strip()

        ## Option 3: Use the filename as the title
        if title is None:
            title = file.stem

        output_result.title = title
        return output_result