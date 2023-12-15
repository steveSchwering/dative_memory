import spacy

from pathlib import Path


def get_words(words_file,
              delimiter = '\t'):
    """
    """
    with words_file.open() as f:
        words = [line.split(delimiter)[0] for line in f.readlines()]

    return words[1:]


def extract_embeddings(words):
    """
    """
    embeddings = []

    nlp_lg = spacy.load('en_core_web_lg')

    for word in words:
        embedding = nlp_lg(word)
        embeddings.append({'word': word,
                           'embedding': embedding.vector})

    return embeddings


def save_embeddings(embeddings,
                    embedding_file = 'all_noun_spacy_embeddings.tsv',
                    delimiter = '\t',
                    newline = '\n'):
    """
    """
    with open(embedding_file, 'w') as f:
        # Heading
        print(embeddings[0])
        embedding_example = embeddings[0]['embedding']
        embeddings_header = [f'embedding_{num}' for num in range(len(embedding_example))]
        embeddings_header = delimiter.join(embeddings_header)
        header = f'word{delimiter}' + embeddings_header + newline
        f.write(header)

        # Write embeddings
        for embedding in embeddings:
            embedding_string = delimiter.join([str(dim) for dim in embedding['embedding']])
            write_string = f'{embedding["word"]}{delimiter}' + embedding_string + newline
            f.write(write_string)


if __name__ == '__main__':
    nounfile = Path.cwd().joinpath('animacy_norms_vanarsdall.tsv')
    nouns = get_words(words_file = nounfile)
    embeddings = extract_embeddings(words = nouns)
    save_embeddings(embeddings = embeddings)