import inspect
import keyword
import os
import re
from os import environ as env
from typing import (
    List,
    Set,
)

import openai
from inflection import (
    humanize,
    pluralize,
    singularize,
    underscore,
)

from main import fetch_pull_request
from main.constants import STOPWORDS

TAG = [
    'build',
    'chore',
    'ci',
    'docs',
    'feat',
    'fix',
    'perf',
    'refactor',
    'revert',
    'style',
    'test',
]


def _logging(level: str, title: str, message: str):
    frame: inspect.FrameInfo = inspect.stack()[2]
    print(f'::{level} title={title}::{message}, file={frame.filename}, line={frame.lineno}')


def _required(title: str):
    return 'fill me' in title.lower()


def __can_relocate_words(title: str):
    return ':' not in title


def _decorate_number(title: str):
    return re.sub(r'(([`]*)([0-9]+[0-9\.\-\%\$\,]*)([`]*))', r'`\3`', title)


def _decorate_bump(title: str, ref_name: str):
    decorated = _decorate_number(title)
    match = re.search(r'dependabot\/\w+\/([\w\-]+)\-[\.\d]+', ref_name)
    if match:
        dep_name = match[1]
        decorated = _highlight(decorated, {dep_name})
    return decorated


def _parse_title(title: str):
    if __can_relocate_words(title):
        p = re.search(r'(.*)[(\[](.*)[)\]](.*)', title)
        if not p:
            return ('misc', title)
        plain_title = f'{p[1]}{p[3]}'
        tag = p[2].lower().strip()
        return tag, plain_title

    p = re.search(r'(.*)[\:][ ]*(.*)', title)
    return (p[1].lower().strip(), p[2].lower().strip()) if p else (None, None)


def _highlight(text: str, keywords: Set[str]):
    highlighted = text
    for k in keywords:
        try:
            highlighted = re.sub(rf'\b(?<!`)({k})(?!`)\b', r'`\1`', highlighted)
        except re.error as ex:
            _logging('error', f'regex error during highlighting keyword {k}', str(ex))
            continue
        except Exception as ex:
            _logging('error', f'misc error during highlighting keyword {k}', str(ex))
            continue
    return highlighted


def _extend_singularize(symbols: List[str]):
    symbols.extend([singularize(symbol) for symbol in symbols])


def _extend_pluralize(symbols: List[str]):
    symbols.extend([pluralize(symbol) for symbol in symbols])


def _extend_files(symbols: List[str], src_path: str):
    files = []
    for root, _, f_names in os.walk(src_path):
        for f in f_names:
            file_path = os.path.join(root, f)
            if file_path.startswith('./.'):
                continue
            files.append(f)
    symbols.extend(files)


def _tokenize(symbol: str):
    stopwords = list(keyword.kwlist)
    stopwords.extend(STOPWORDS)
    return (re
            .sub(rf'\b({"|".join(stopwords)})\b', r'', humanize(underscore(symbol)).lower().strip())
            .lower().strip())


def _symbolize(raw_symbols: str):
    symbols = [_tokenize(symbol)for symbol in raw_symbols.split('\n') if len(_tokenize(symbol)) > 3]
    symbols.extend([symbol.replace(' ', '_') for symbol in symbols])
    return symbols


def main():

    openai.organization = "org-JAnMEEEFNvtPSGwRA1DVF3Yu"
    openai.api_key = os.getenv("OPENAI_API_KEY", "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")

    pull_request = fetch_pull_request(
        access_token=os.getenv("access_token", "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"),
        owner=os.getenv("owner", "chyccs"),
        repository=os.getenv("repository", "pull-request-generator"),
        number=int(os.getenv("pull_request_number", "4"),),
    )

    # if not _required(pull_request.title):
    #     return
    
    patches = ['Can you summarize the code changes I\'m about to enter in single lowercase Conventional Commits 1.0.0 format?']
    
    for f in pull_request.get_files():
        patches.append(f.patch)

    prompt = '\n'.join(patches)

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\"\"\""],
    )

    print(response)

    pull_request.edit(
        title=(response['choices'][0]['text']),
    )

if __name__ == "__main__":
    main()
