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


def _is_bump(title: str):
    return 'bump' in title.lower()


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

    openai.organization = "org-H7ABqZ7qmV9zSWibV2hCj3Am"
    openai.api_key = os.getenv("OPENAI_API_KEY", "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")
    openai.Model.list()

    print(openai.Model.list())

    pull_request = fetch_pull_request(
        access_token=env['access_token'],
        owner=env['owner'],
        repository=env['repository'],
        number=int(env['pull_request_number']),
    )

    print(pull_request)
    
    # pull_request.edit(
    #     title=(decorated_title or pull_request.title),
    #     body=(decorated_body or pull_request.body),
    # )


if __name__ == "__main__":
    main()
