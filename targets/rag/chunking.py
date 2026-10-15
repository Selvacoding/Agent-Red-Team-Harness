def split_large_paragraph(
    paragraph: str,
    chunk_size: int,
) -> list[str]:

    words = paragraph.split()

    chunks = []
    current_words = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1

        if (
            current_words
            and current_length + word_length > chunk_size
        ):
            chunks.append(" ".join(current_words))

            current_words = []
            current_length = 0

        current_words.append(word)
        current_length += word_length

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> list[dict]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be between 0 and chunk_size - 1"
        )

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    sections = []
    current_section = None
    current_paragraphs = []

    for paragraph in paragraphs:

        if paragraph.startswith("#"):
            if current_section is not None:
                sections.append({
                    "section": current_section,
                    "paragraphs": current_paragraphs,
                })

            current_section = paragraph.lstrip("#").strip()
            current_paragraphs = []

        else:
            current_paragraphs.append(paragraph)

    if current_section is not None:
        sections.append({
            "section": current_section,
            "paragraphs": current_paragraphs,
        })

    if not sections and current_paragraphs:
        sections.append({
            "section": "Uncategorized",
            "paragraphs": current_paragraphs,
        })

    chunks = []

    for section in sections:

        current_chunk = []
        current_length = 0

        for paragraph in section["paragraphs"]:

            if len(paragraph) > chunk_size:
                paragraphs_to_process = split_large_paragraph(
                    paragraph,
                    chunk_size,
                )
            else:
                paragraphs_to_process = [paragraph]

            for paragraph in paragraphs_to_process:

                paragraph_length = len(paragraph) + 1

                if (
                    current_chunk
                    and current_length + paragraph_length > chunk_size
                ):
                    chunks.append({
                        "content": "\n\n".join(current_chunk),
                        "section": section["section"],
                    })

                    # Keep whole paragraphs as overlap.
                    overlap_paragraphs = []
                    overlap_length = 0

                    for previous in reversed(current_chunk):
                        previous_length = len(previous) + 1

                        if overlap_length + previous_length > overlap:
                            break

                        overlap_paragraphs.insert(0, previous)
                        overlap_length += previous_length

                    current_chunk = overlap_paragraphs
                    current_length = overlap_length

                current_chunk.append(paragraph)
                current_length += paragraph_length

        if current_chunk:
            chunks.append({
                "content": "\n\n".join(current_chunk),
                "section": section["section"],
            })

    return chunks
