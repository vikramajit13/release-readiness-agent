class ExtractorFactory:
    def __init__(self, extractors: list):
        self.extractors = extractors

    def for_mime_type(self, mime_type: str):
        for extractor in self.extractors:
            if extractor.supports(mime_type):
                return extractor
        raise ValueError(f"No extractor found for mime type: {mime_type}")