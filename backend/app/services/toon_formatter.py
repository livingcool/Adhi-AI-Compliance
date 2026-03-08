from typing import List
from app.api.schemas import SourceChunk

def format_to_toon(chunks: List[SourceChunk]) -> str:
    """
    Formats a list of SourceChunk objects into the TOON (Type Object Object Notation) format.
    Format: TYPE|ID|CONTENT
    
    Types:
    - TXT: Text chunk
    - IMG: Image description
    - TBL: Table (if we distinguish it, otherwise TXT)
    """
    toon_output = []
    
    for i, chunk in enumerate(chunks):
        # Determine Type
        # We can infer type from metadata or content. 
        # For now, if content starts with "[Visual Description", it's IMG.
        chunk_type = "TXT"
        if chunk.chunk_text.startswith("[Visual Description"):
            chunk_type = "IMG"
        
        # Create ID (using source file and index/time)
        # Shorten source file name for token efficiency
        short_name = chunk.source_file.split('.')[0][:10]
        chunk_id = f"{short_name}_{i}"
        
        # Clean content (remove newlines to keep it on one line per chunk if possible, or just standard)
        # TOON usually implies a structured format. Let's keep newlines but ensure the separator is clear.
        # Actually, pipe delimited might break if content has pipes. 
        # Let's escape pipes in content or just use it as a prefix.
        # "TYPE|ID|CONTENT"
        
        clean_content = chunk.chunk_text.replace("|", "\|").replace("\n", " ")
        
        line = f"{chunk_type}|{chunk_id}|{clean_content}"
        toon_output.append(line)
        
    return "\n".join(toon_output)
