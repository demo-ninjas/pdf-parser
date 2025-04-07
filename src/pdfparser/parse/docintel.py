from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, DocumentContentFormat, DocumentAnalysisFeature
import azure.ai.documentintelligence.models as models

class DocIntelAnalysisSpan:
    offset:int = None
    length:int = None

    def from_result_span(span:models.DocumentSpan):
        dspan = DocIntelAnalysisSpan()
        dspan.offset = span.offset
        dspan.length = span.length
        return dspan
    
    def to_json(self):
        return {
            "offset": self.offset,
            "length": self.length
        }
    def from_json(json:dict):
        dspan = DocIntelAnalysisSpan()
        dspan.offset = json.get("offset", None)
        dspan.length = json.get("length", None)
        return dspan

class DocIntelAnalysisWord:
    content:str = None
    polygon:list[float] = None
    span:DocIntelAnalysisSpan = None
    confidence:float = None

    def from_result_word(word:models.DocumentWord):
        dword = DocIntelAnalysisWord()
        dword.content = word.content
        dword.polygon = word.polygon
        dword.span = DocIntelAnalysisSpan.from_result_span(word.span)
        dword.confidence = word.confidence
        return dword
    
    def to_json(self):
        return {
            "content": self.content,
            "polygon": self.polygon,
            "span": self.span.to_json(),
            "confidence": self.confidence
        }
    def from_json(json:dict):
        dword = DocIntelAnalysisWord()
        dword.content = json.get("content", None)
        dword.polygon = json.get("polygon", None)
        dword.span = DocIntelAnalysisSpan.from_json(json.get("span", None))
        dword.confidence = json.get("confidence", None)
        return dword

class DocIntelAnalysisLine:
    content:str = None
    polygon:list[float] = None
    spans:list[DocIntelAnalysisSpan] = None

    def from_result_line(line:models.DocumentLine):
        dline = DocIntelAnalysisLine()
        dline.content = line.content
        dline.polygon = line.polygon
        dline.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in line.spans]
        return dline
    def to_json(self):
        return {
            "content": self.content,
            "polygon": self.polygon,
            "spans": [span.to_json() for span in self.spans]
        }
    def from_json(json:dict):
        dline = DocIntelAnalysisLine()
        dline.content = json.get("content", None)
        dline.polygon = json.get("polygon", None)
        dline.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        return dline
    

class DocIntelBarcode: 
    kind:str = None # "QRCode", "PDF417", "UPCA", "UPCE", "Code39", "Code128", "EAN8", "EAN13", "DataBar", "Code93", "Codabar", "DataBarExpanded", "ITF", "MicroQRCode", "Aztec", "DataMatrix", and "MaxiCode".
    value:str = None
    polygon:list[float] = None
    span:DocIntelAnalysisSpan = None
    confidence:float = None

    def from_result_barcode(barcode:models.DocumentBarcode):
        dbarcode = DocIntelBarcode()
        dbarcode.kind = barcode.kind
        dbarcode.value = barcode.value
        dbarcode.polygon = barcode.polygon
        dbarcode.span = DocIntelAnalysisSpan.from_result_span(barcode.span)
        dbarcode.confidence = barcode.confidence
        return dbarcode
    def to_json(self):
        return {
            "kind": self.kind,
            "value": self.value,
            "polygon": self.polygon,
            "span": self.span.to_json(),
            "confidence": self.confidence
        }
    def from_json(json:dict):
        dbarcode = DocIntelBarcode()
        dbarcode.kind = json.get("kind", None)
        dbarcode.value = json.get("value", None)
        dbarcode.polygon = json.get("polygon", None)
        dbarcode.span = DocIntelAnalysisSpan.from_json(json.get("span", None))
        dbarcode.confidence = json.get("confidence", None)
        return dbarcode

class DocIntelAnalysisFormula:
    kind:str = None     # "inline" or "display"
    value:str = None    # In LaTeX format
    polygon:list[float] = None
    span:DocIntelAnalysisSpan = None
    confidence:float = None

    def from_result_formula(formula:models.DocumentFormula):
        dformula = DocIntelAnalysisFormula()
        dformula.kind = formula.kind
        dformula.value = formula.value
        dformula.polygon = formula.polygon
        dformula.span = DocIntelAnalysisSpan.from_result_span(formula.span)
        dformula.confidence = formula.confidence
        return dformula
    def to_json(self):
        return {
            "kind": self.kind,
            "value": self.value,
            "polygon": self.polygon,
            "span": self.span.to_json(),
            "confidence": self.confidence
        }
    def from_json(json:dict):
        dformula = DocIntelAnalysisFormula()
        dformula.kind = json.get("kind", None)
        dformula.value = json.get("value", None)
        dformula.polygon = json.get("polygon", None)
        dformula.span = DocIntelAnalysisSpan.from_json(json.get("span", None))
        dformula.confidence = json.get("confidence", None)
        return dformula

class DocIntelAnalysisPage: 
    page_number:int = None
    angle:float = None
    width:int = None
    height:int = None
    unit:str = None #  Either "pixel" or "inch"
    words:list[DocIntelAnalysisWord] = None
    lines:list[DocIntelAnalysisLine] = None
    barcodes:list[DocIntelBarcode] = None
    formulas:list[DocIntelAnalysisFormula] = None

    def from_result_page(page:models.DocumentPage):
        dpage = DocIntelAnalysisPage()
        dpage.page_number = page.page_number
        dpage.angle = page.angle
        dpage.width = page.width
        dpage.height = page.height
        dpage.unit = page.unit
        dpage.words = [DocIntelAnalysisWord.from_result_word(word) for word in page.words] if page.words is not None else []
        dpage.lines = [DocIntelAnalysisLine.from_result_line(line) for line in page.lines] if page.lines is not None else []
        dpage.barcodes = [DocIntelBarcode.from_result_barcode(barcode) for barcode in page.barcodes] if page.barcodes is not None else []
        dpage.formulas = [DocIntelAnalysisFormula.from_result_formula(formula) for formula in page.formulas] if page.formulas is not None else []
        return dpage
    def to_json(self):
        return {
            "page_number": self.page_number,
            "angle": self.angle,
            "width": self.width,
            "height": self.height,
            "unit": self.unit,
            "words": [word.to_json() for word in self.words],
            "lines": [line.to_json() for line in self.lines],
            "barcodes": [barcode.to_json() for barcode in self.barcodes],
            "formulas": [formula.to_json() for formula in self.formulas]
        }
    def from_json(json:dict):
        dpage = DocIntelAnalysisPage()
        dpage.page_number = json.get("page_number", None)
        dpage.angle = json.get("angle", None)
        dpage.width = json.get("width", None)
        dpage.height = json.get("height", None)
        dpage.unit = json.get("unit", None)
        dpage.words = [DocIntelAnalysisWord.from_json(word) for word in json.get("words", [])]
        dpage.lines = [DocIntelAnalysisLine.from_json(line) for line in json.get("lines", [])]
        dpage.barcodes = [DocIntelBarcode.from_json(barcode) for barcode in json.get("barcodes", [])]
        dpage.formulas = [DocIntelAnalysisFormula.from_json(formula) for formula in json.get("formulas", [])]
        return dpage

class DocIntelAnalysisBoundingRegion:
    page_number:int = None
    polygon:list[float] = None

    def from_result_bounding_region(bounding_region:models.BoundingRegion):
        dbounding_region = DocIntelAnalysisBoundingRegion()
        dbounding_region.page_number = bounding_region.page_number
        dbounding_region.polygon = bounding_region.polygon
        return dbounding_region
    def to_json(self):
        return {
            "page_number": self.page_number,
            "polygon": self.polygon
        }
    def from_json(json:dict):
        dbounding_region = DocIntelAnalysisBoundingRegion()
        dbounding_region.page_number = json.get("page_number", None)
        dbounding_region.polygon = json.get("polygon", None)
        return dbounding_region
    

class DocIntelAnalysisParagraph:
    role:str = None # "pageHeader", "pageFooter", "pageNumber", "title", "sectionHeading", "footnote", and "formulaBlock"
    content:str = None
    bounding_regions:list[DocIntelAnalysisBoundingRegion] = None
    spans:list[DocIntelAnalysisSpan] = None

    def from_result_paragraph(paragraph:models.DocumentParagraph):
        dparagraph = DocIntelAnalysisParagraph()
        dparagraph.role = paragraph.role
        dparagraph.content = paragraph.content
        dparagraph.bounding_regions = [DocIntelAnalysisBoundingRegion.from_result_bounding_region(bounding_region) for bounding_region in paragraph.bounding_regions]
        dparagraph.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in paragraph.spans]
        return dparagraph
    def to_json(self):
        return {
            "role": self.role,
            "content": self.content,
            "bounding_regions": [bounding_region.to_json() for bounding_region in self.bounding_regions],
            "spans": [span.to_json() for span in self.spans]
        }
    def from_json(json:dict):
        dparagraph = DocIntelAnalysisParagraph()
        dparagraph.role = json.get("role", None)
        dparagraph.content = json.get("content", None)
        dparagraph.bounding_regions = [DocIntelAnalysisBoundingRegion.from_json(bounding_region) for bounding_region in json.get("bounding_regions", [])]
        dparagraph.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        return dparagraph

class DocIntelAnalysisTableCell:
    kind:str = None # \"content\", \"rowHeader\", \"columnHeader\", \"stubHead\", and \"description\"
    row_index:int = None
    column_index:int = None
    row_span:int = None
    column_span:int = None
    content:str = None
    bounding_regions:list[DocIntelAnalysisBoundingRegion] = None
    spans:list[DocIntelAnalysisSpan] = None
    elements:list[str] = None

    def from_result_table_cell(table_cell:models.DocumentTableCell):
        dtable_cell = DocIntelAnalysisTableCell()
        dtable_cell.kind = table_cell.kind
        dtable_cell.row_index = table_cell.row_index
        dtable_cell.column_index = table_cell.column_index
        dtable_cell.row_span = table_cell.row_span
        dtable_cell.column_span = table_cell.column_span
        dtable_cell.content = table_cell.content
        dtable_cell.bounding_regions = [DocIntelAnalysisBoundingRegion.from_result_bounding_region(bounding_region) for bounding_region in table_cell.bounding_regions]
        dtable_cell.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in table_cell.spans]
        return dtable_cell
    def to_json(self):  
        return {
            "kind": self.kind,
            "row_index": self.row_index,
            "column_index": self.column_index,
            "row_span": self.row_span,
            "column_span": self.column_span,
            "content": self.content,
            "bounding_regions": [bounding_region.to_json() for bounding_region in self.bounding_regions],
            "spans": [span.to_json() for span in self.spans]
        }
    def from_json(json:dict):
        dtable_cell = DocIntelAnalysisTableCell()
        dtable_cell.kind = json.get("kind", None)
        dtable_cell.row_index = json.get("row_index", None)
        dtable_cell.column_index = json.get("column_index", None)
        dtable_cell.row_span = json.get("row_span", None)
        dtable_cell.column_span = json.get("column_span", None)
        dtable_cell.content = json.get("content", None)
        dtable_cell.bounding_regions = [DocIntelAnalysisBoundingRegion.from_json(bounding_region) for bounding_region in json.get("bounding_regions", [])]
        dtable_cell.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        return dtable_cell

class DocIntelAnalysisFootnote:
    content:str = None
    bounding_regions:list[DocIntelAnalysisBoundingRegion] = None
    spans:list[DocIntelAnalysisSpan] = None
    elements:list[str] = None

    def from_result_footnote(footnote:models.DocumentFootnote):
        dfootnote = DocIntelAnalysisFootnote()
        dfootnote.content = footnote.content
        dfootnote.bounding_regions = [DocIntelAnalysisBoundingRegion.from_result_bounding_region(bounding_region) for bounding_region in footnote.bounding_regions]
        dfootnote.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in footnote.spans]
        return dfootnote
    def to_json(self):
        return {
            "content": self.content,
            "bounding_regions": [bounding_region.to_json() for bounding_region in self.bounding_regions],
            "spans": [span.to_json() for span in self.spans]
        }
    def from_json(json:dict):
        dfootnote = DocIntelAnalysisFootnote()
        dfootnote.content = json.get("content", None)
        dfootnote.bounding_regions = [DocIntelAnalysisBoundingRegion.from_json(bounding_region) for bounding_region in json.get("bounding_regions", [])]
        dfootnote.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        return dfootnote


class DocIntelAnalysisTable:
    row_count:int = None
    column_count:int = None
    cells:list[DocIntelAnalysisTableCell] = None
    bounding_regions:list[DocIntelAnalysisBoundingRegion] = None
    spans:list[DocIntelAnalysisSpan] = None
    caption:str = None
    footnotes:list[DocIntelAnalysisFootnote] = None

    def from_result_table(table:models.DocumentTable):
        dtable = DocIntelAnalysisTable()
        dtable.row_count = table.row_count
        dtable.column_count = table.column_count
        dtable.cells = [DocIntelAnalysisTableCell.from_result_table_cell(cell) for cell in table.cells]
        dtable.bounding_regions = [DocIntelAnalysisBoundingRegion.from_result_bounding_region(bounding_region) for bounding_region in table.bounding_regions]
        dtable.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in table.spans]
        dtable.caption = table.caption.content if table.caption is not None else None
        return dtable
    def to_json(self):
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "cells": [cell.to_json() for cell in self.cells],
            "bounding_regions": [bounding_region.to_json() for bounding_region in self.bounding_regions],
            "spans": [span.to_json() for span in self.spans], 
            "caption": self.caption,
        }
    def from_json(json:dict):
        dtable = DocIntelAnalysisTable()
        dtable.row_count = json.get("row_count", None)
        dtable.column_count = json.get("column_count", None)
        dtable.cells = [DocIntelAnalysisTableCell.from_json(cell) for cell in json.get("cells", [])]
        dtable.bounding_regions = [DocIntelAnalysisBoundingRegion.from_json(bounding_region) for bounding_region in json.get("bounding_regions", [])]
        dtable.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        dtable.caption = json.get("caption", None)
        return dtable

class DocIntelAnalysisFigure:
    bounding_regions:list[DocIntelAnalysisBoundingRegion] = None
    spans:list[DocIntelAnalysisSpan] = None
    elements:list[str] = None
    caption:str = None
    footnotes:list[DocIntelAnalysisFootnote] = None
    id:str = None

    def from_result_figure(figure:models.DocumentFigure):
        dfigure = DocIntelAnalysisFigure()
        dfigure.bounding_regions = [DocIntelAnalysisBoundingRegion.from_result_bounding_region(bounding_region) for bounding_region in figure.bounding_regions]
        dfigure.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in figure.spans]
        dfigure.caption = figure.caption.content if figure.caption is not None else None
        dfigure.footnotes = [DocIntelAnalysisFootnote.from_result_footnote(footnote) for footnote in figure.footnotes] if figure.footnotes is not None else []
        return dfigure
    
    def to_json(self):  
        return {
            "bounding_regions": [bounding_region.to_json() for bounding_region in self.bounding_regions],
            "spans": [span.to_json() for span in self.spans],
            "caption": self.caption,
            "footnotes": [footnote.to_json() for footnote in self.footnotes]
        }
    def from_json(json:dict):
        dfigure = DocIntelAnalysisFigure()
        dfigure.bounding_regions = [DocIntelAnalysisBoundingRegion.from_json(bounding_region) for bounding_region in json.get("bounding_regions", [])]
        dfigure.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        dfigure.caption = json.get("caption", None)
        dfigure.footnotes = [DocIntelAnalysisFootnote.from_json(footnote) for footnote in json.get("footnotes", [])] if json.get("footnotes", None) is not None else []
        return dfigure

class DocIntelAnalysisSection:
    spans:list[DocIntelAnalysisSpan] = None
    elements:list[str] = None

    def from_result_section(section:models.DocumentSection):
        dsection = DocIntelAnalysisSection()
        dsection.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in section.spans]
        dsection.elements = section.elements
        return dsection
    def to_json(self):
        return {
            "spans": [span.to_json() for span in self.spans],
            "elements": self.elements
        }
    def from_json(json:dict):
        dsection = DocIntelAnalysisSection()
        dsection.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        dsection.elements = json.get("elements", None)
        return dsection

class DocIntelAnalysisKeyValuePairElement:
    content:str = None
    bounding_regions:list[DocIntelAnalysisBoundingRegion] = None
    spans:list[DocIntelAnalysisSpan] = None

    def from_result_key_value_pair_element(key_value_pair_element:models.DocumentKeyValueElement):
        dkey_value_pair_element = DocIntelAnalysisKeyValuePairElement()
        dkey_value_pair_element.content = key_value_pair_element.content
        dkey_value_pair_element.bounding_regions = [DocIntelAnalysisBoundingRegion.from_result_bounding_region(bounding_region) for bounding_region in key_value_pair_element.bounding_regions]
        dkey_value_pair_element.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in key_value_pair_element.spans]
        return dkey_value_pair_element
    def to_json(self):
        return {
            "content": self.content,
            "bounding_regions": [bounding_region.to_json() for bounding_region in self.bounding_regions],
            "spans": [span.to_json() for span in self.spans]
        }
    def from_json(json:dict):
        dkey_value_pair_element = DocIntelAnalysisKeyValuePairElement()
        dkey_value_pair_element.content = json.get("content", None)
        dkey_value_pair_element.bounding_regions = [DocIntelAnalysisBoundingRegion.from_json(bounding_region) for bounding_region in json.get("bounding_regions", [])]
        dkey_value_pair_element.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        return dkey_value_pair_element

class DocIntelAnalysisKeyValuePair:
    key:DocIntelAnalysisKeyValuePairElement = None
    value:DocIntelAnalysisKeyValuePairElement = None
    confidence:float = None

    def from_result_key_value_pair(key_value_pair:models.DocumentKeyValuePair):
        dkey_value_pair = DocIntelAnalysisKeyValuePair()
        dkey_value_pair.key = DocIntelAnalysisKeyValuePairElement.from_result_key_value_pair_element(key_value_pair.key)
        dkey_value_pair.value = DocIntelAnalysisKeyValuePairElement.from_result_key_value_pair_element(key_value_pair.value)
        dkey_value_pair.confidence = key_value_pair.confidence
        return dkey_value_pair
    def to_json(self):
        return {
            "key": self.key.to_json(),
            "value": self.value.to_json(),
            "confidence": self.confidence
        }
    def from_json(json:dict):
        dkey_value_pair = DocIntelAnalysisKeyValuePair()
        dkey_value_pair.key = DocIntelAnalysisKeyValuePairElement.from_json(json.get("key", None))
        dkey_value_pair.value = DocIntelAnalysisKeyValuePairElement.from_json(json.get("value", None))
        dkey_value_pair.confidence = json.get("confidence", None)
        return dkey_value_pair

class DocIntelAnalysisLanguage:
    locale:str = None
    spans:list[DocIntelAnalysisSpan] = None
    confidence:float = None

    def from_result_language(language:models.DocumentLanguage):
        dlanguage = DocIntelAnalysisLanguage()
        dlanguage.locale = language.locale
        dlanguage.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in language.spans]
        dlanguage.confidence = language.confidence
        return dlanguage
    
    def to_json(self):
        return {
            "locale": self.locale,
            "spans": [span.to_json() for span in self.spans],
            "confidence": self.confidence
        }
    def from_json(json:dict):
        dlanguage = DocIntelAnalysisLanguage()
        dlanguage.locale = json.get("locale", None)
        dlanguage.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        dlanguage.confidence = json.get("confidence", None)
        return dlanguage

class DocIntelAnalysisStyle:
    is_handwritten:bool = None
    similar_font_family:str = None
    font_style:str = None # Normal, Italic
    font_weight:str = None # Normal, Bold
    color:str = None
    background_colour:str = None
    spans:list[DocIntelAnalysisSpan] = None
    confidence:float = None

    def from_result_style(style:models.DocumentStyle):
        dstyle = DocIntelAnalysisStyle()
        dstyle.is_handwritten = style.is_handwritten
        dstyle.similar_font_family = style.similar_font_family
        dstyle.font_style = style.font_style
        dstyle.font_weight = style.font_weight
        dstyle.color = style.color
        dstyle.background_colour = style.background_color
        dstyle.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in style.spans]
        dstyle.confidence = style.confidence
        return dstyle
    def to_json(self):
        return {
            "is_handwritten": self.is_handwritten,
            "similar_font_family": self.similar_font_family,
            "font_style": self.font_style,
            "font_weight": self.font_weight,
            "color": self.color,
            "background_colour": self.background_colour,
            "spans": [span.to_json() for span in self.spans],
            "confidence": self.confidence
        }
    def from_json(json:dict):
        dstyle = DocIntelAnalysisStyle()
        dstyle.is_handwritten = json.get("is_handwritten", None)
        dstyle.similar_font_family = json.get("similar_font_family", None)
        dstyle.font_style = json.get("font_style", None)
        dstyle.font_weight = json.get("font_weight", None)
        dstyle.color = json.get("color", None)
        dstyle.background_colour = json.get("background_colour", None)
        dstyle.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        dstyle.confidence = json.get("confidence", None)
        return dstyle

class DocIntelAnalysisDocumentField:
    value_type:str = None #  "string", "date", "time", "phoneNumber", "number", "integer", "selectionMark", "countryRegion", "signature", "array", "object", "currency", "address", "boolean", and "selectionGroup"
    value:str = None
    bounding_regions:list[DocIntelAnalysisBoundingRegion] = None
    spans:list[DocIntelAnalysisSpan] = None
    confidence:float = None

    def from_result_document_field(document_field:models.DocumentField):
        ddocument_field = DocIntelAnalysisDocumentField()
        ddocument_field.value_type = document_field.type
        ddocument_field.value = document_field.content
        ddocument_field.bounding_regions = [DocIntelAnalysisBoundingRegion.from_result_bounding_region(bounding_region) for bounding_region in document_field.bounding_regions]
        ddocument_field.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in document_field.spans]
        ddocument_field.confidence = document_field.confidence
        return ddocument_field
    def to_json(self):
        return {
            "value_type": self.value_type,
            "value": self.value,
            "bounding_regions": [bounding_region.to_json() for bounding_region in self.bounding_regions],
            "spans": [span.to_json() for span in self.spans],
            "confidence": self.confidence
        }
    def from_json(json:dict):
        ddocument_field = DocIntelAnalysisDocumentField()
        ddocument_field.value_type = json.get("value_type", None)
        ddocument_field.value = json.get("value", None)
        ddocument_field.bounding_regions = [DocIntelAnalysisBoundingRegion.from_json(bounding_region) for bounding_region in json.get("bounding_regions", [])]
        ddocument_field.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        ddocument_field.confidence = json.get("confidence", None)
        return ddocument_field

class DocIntelAnalysisDocument:
    doc_type:str = None 
    bounding_regions:list[DocIntelAnalysisBoundingRegion] = None
    spans:list[DocIntelAnalysisSpan] = None
    fields: list[DocIntelAnalysisDocumentField] = None
    confidence:float = None

    def from_result_document(document:models.AnalyzedDocument):
        ddocument = DocIntelAnalysisDocument()
        ddocument.doc_type = document.doc_type
        ddocument.bounding_regions = [DocIntelAnalysisBoundingRegion.from_result_bounding_region(bounding_region) for bounding_region in document.bounding_regions]
        ddocument.spans = [DocIntelAnalysisSpan.from_result_span(span) for span in document.spans]
        ddocument.fields = [DocIntelAnalysisDocumentField.from_result_document_field(field) for field in document.fields]
        ddocument.confidence = document.confidence
        return ddocument
    def to_json(self):
        return {
            "doc_type": self.doc_type,
            "bounding_regions": [bounding_region.to_json() for bounding_region in self.bounding_regions],
            "spans": [span.to_json() for span in self.spans],
            "fields": [field.to_json() for field in self.fields],
            "confidence": self.confidence
        }
    def from_json(json:dict):
        ddocument = DocIntelAnalysisDocument()
        ddocument.doc_type = json.get("doc_type", None)
        ddocument.bounding_regions = [DocIntelAnalysisBoundingRegion.from_json(bounding_region) for bounding_region in json.get("bounding_regions", [])]
        ddocument.spans = [DocIntelAnalysisSpan.from_json(span) for span in json.get("spans", [])]
        ddocument.fields = [DocIntelAnalysisDocumentField.from_json(field) for field in json.get("fields", [])]
        ddocument.confidence = json.get("confidence", None)
        return ddocument
    

class DocIntelAnalysisWarning:
    code:str = None
    message:str = None
    target:str = None

    def from_result_warning(warning:models.DocumentIntelligenceWarning):
        dwarning = DocIntelAnalysisWarning()
        dwarning.code = warning.code
        dwarning.message = warning.message
        dwarning.target = warning.target
        return dwarning
    def to_json(self):
        return {
            "code": self.code,
            "message": self.message,
            "target": self.target
        }
    def from_json(json:dict):
        dwarning = DocIntelAnalysisWarning()
        dwarning.code = json.get("code", None)
        dwarning.message = json.get("message", None)
        dwarning.target = json.get("target", None)
        return dwarning
    

class DocIntelAnalysis:
    markdown:str = None
    pages:list[DocIntelAnalysisPage] = None
    paragraphs:list[DocIntelAnalysisParagraph] = None
    tables:list[DocIntelAnalysisTable] = None
    figures:list[DocIntelAnalysisFigure] = None
    sections:list[DocIntelAnalysisSection] = None
    key_value_pairs:list[DocIntelAnalysisKeyValuePair] = None
    languages:list[DocIntelAnalysisLanguage] = None
    styles:list[DocIntelAnalysisStyle] = None
    documents:list[DocIntelAnalysisDocument] = None
    warnings:list[DocIntelAnalysisWarning] = None

    def from_result(result:AnalyzeResult):
        analysis = DocIntelAnalysis()
        analysis.markdown = result.content
        analysis.pages = [DocIntelAnalysisPage.from_result_page(page) for page in result.pages] if result.pages is not None else []
        analysis.paragraphs = [DocIntelAnalysisParagraph.from_result_paragraph(paragraph) for paragraph in result.paragraphs] if result.paragraphs is not None else []
        analysis.tables = [DocIntelAnalysisTable.from_result_table(table) for table in result.tables] if result.tables is not None else []
        analysis.figures = [DocIntelAnalysisFigure.from_result_figure(figure) for figure in result.figures] if result.figures is not None else []
        analysis.sections = [DocIntelAnalysisSection.from_result_section(section) for section in result.sections] if result.sections is not None else []
        analysis.key_value_pairs = [DocIntelAnalysisKeyValuePair.from_result_key_value_pair(key_value_pair) for key_value_pair in result.key_value_pairs] if result.key_value_pairs is not None else []
        analysis.languages = [DocIntelAnalysisLanguage.from_result_language(language) for language in result.languages] if result.languages is not None else []
        analysis.styles = [DocIntelAnalysisStyle.from_result_style(style) for style in result.styles] if result.styles is not None else []
        analysis.documents = [DocIntelAnalysisDocument.from_result_document(document) for document in result.documents] if result.documents is not None else []
        analysis.warnings = [DocIntelAnalysisWarning.from_result_warning(warning) for warning in result.warnings] if result.warnings is not None else []
        return analysis
    
    def to_json(self):
        return {
            "markdown": self.markdown,
            "pages": [page.to_json() for page in self.pages],
            "paragraphs": [paragraph.to_json() for paragraph in self.paragraphs],
            "tables": [table.to_json() for table in self.tables],
            "figures": [figure.to_json() for figure in self.figures],
            "sections": [section.to_json() for section in self.sections],
            "key_value_pairs": [key_value_pair.to_json() for key_value_pair in self.key_value_pairs],
            "languages": [language.to_json() for language in self.languages],
            "styles": [style.to_json() for style in self.styles],
            "documents": [document.to_json() for document in self.documents],
            "warnings": [warning.to_json() for warning in self.warnings]
        }
    def from_json(json:dict):
        analysis = DocIntelAnalysis()
        analysis.markdown = json.get("markdown", None)
        analysis.pages = [DocIntelAnalysisPage.from_json(page) for page in json.get("pages", [])]
        analysis.paragraphs = [DocIntelAnalysisParagraph.from_json(paragraph) for paragraph in json.get("paragraphs", [])]
        analysis.tables = [DocIntelAnalysisTable.from_json(table) for table in json.get("tables", [])]
        analysis.figures = [DocIntelAnalysisFigure.from_json(figure) for figure in json.get("figures", [])]
        analysis.sections = [DocIntelAnalysisSection.from_json(section) for section in json.get("sections", [])]
        analysis.key_value_pairs = [DocIntelAnalysisKeyValuePair.from_json(key_value_pair) for key_value_pair in json.get("key_value_pairs", [])]
        analysis.languages = [DocIntelAnalysisLanguage.from_json(language) for language in json.get("languages", [])]
        analysis.styles = [DocIntelAnalysisStyle.from_json(style) for style in json.get("styles", [])]
        analysis.documents = [DocIntelAnalysisDocument.from_json(document) for document in json.get("documents", [])]
        analysis.warnings = [DocIntelAnalysisWarning.from_json(warning) for warning in json.get("warnings", [])]
        return analysis
        

class DocIntelAnalyser:
    _endpoint:str = None    
    _key:str = None
    _api_version:str = None
    client:DocumentIntelligenceClient = None

    def __init__(self, args:dict[str, str]):
        import os
        self._endpoint = args.get('docintel-endpoint', os.environ.get("DOCINTEL_ENDPOINT", os.environ.get("AZURE_FORM_RECOGNIZER_ENDPOINT", None)))
        if self._endpoint is None: raise Exception("Document Intelligence endpoint not specified. Provide either the '--docintel-endpoint' argument or specify the 'DOCINTEL_ENDPOINT' environment variable")
        
        self._key = args.get('docintel-key', os.environ.get("DOCINTEL_KEY", os.environ.get("AZURE_FORM_RECOGNIZER_KEY", None)))
        if self._key is None: raise Exception("Document Intelligence key not specified. Provide either the '--docintel-key' argument or specify the 'DOCINTEL_KEY' environment variable")

        self._api_version = args.get('docintel-api-version', os.environ.get("DOCINTEL_API_VERSION", os.environ.get("AZURE_FORM_RECOGNIZER_API_VERSION", "2024-07-31-preview")))

        self.client = DocumentIntelligenceClient(endpoint=self._endpoint, credential=AzureKeyCredential(self._key), api_version=self._api_version)

    def analyse(self, file:Path, features:list[DocumentAnalysisFeature] = [ DocumentAnalysisFeature.FORMULAS, DocumentAnalysisFeature.STYLE_FONT, DocumentAnalysisFeature.OCR_HIGH_RESOLUTION ] ) -> DocIntelAnalysis:
        """
        Analyze a document using Azure Document Intelligence.
        :param file: The path to the document to analyze.
        :return: The analysis result.
        """
        with open(file, "rb") as fd:
            poller = self.client.begin_analyze_document(
                "prebuilt-layout",
                fd,  # File stream
                output_content_format=DocumentContentFormat.MARKDOWN,
                features=features,
                content_type="application/octet-stream"
            )
            analysis_result = poller.result()
            return DocIntelAnalysis.from_result(analysis_result)
