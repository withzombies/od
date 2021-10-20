#!/usr/bin/env python3

import os
import sys
import json
import os.path
import subprocess
import glob
import shlex
from collections import defaultdict

from pydub import AudioSegment

if len(sys.argv) != 2:
    print("Usage: python3 02_process.py directory_with_manifest_and_mp3s")
    sys.exit(1)

directory = sys.argv[1]
manifest_path = os.path.join(directory, "manifest.json")
manifest = json.load(open(manifest_path))


book_title = manifest["title"]
author = manifest["author"]
chapters = manifest["chapters"]

output_directory = os.path.join('output', f"{author} - {book_title}")
try:
    os.makedirs(output_directory)
except:
    pass

open(os.path.join(output_directory, "description.txt"), "w").write(manifest['description'])

paths = defaultdict(list)

print(f"[+] Found: {book_title} by {author}")
print("Chapters:")
for chapter in chapters:
    idx = chapter['chapter']
    ch_title = chapter['title']
    print(f"  #{idx} - {ch_title}")

    try:
        path, offset = chapter['path'].split('#')
    except:
        path = chapter['path']
        offset = 0

    paths[path].append({
        'title': ch_title,
        'idx': idx,
        'start': offset,
        'end': -1
        })

output_chapters = []

for path, chapters in paths.items():
    chapter_titles = [chapter['title'] for chapter in chapters]
    print(f"Splitting {path} into {chapter_titles}")
    if len(chapters) > 1:
        # Write the ending time for each chapter
        for i in range(len(chapters) - 1):
            chapters[i]['end'] = chapters[i + 1]['start']

        #sound = AudioSegment.from_mp3(os.path.join(directory, path))
        for chapter in chapters:
            start = int(chapter['start'])
            end = int(chapter['end'])
            idx = chapter['idx']
            ch_title = chapter['title']
            new_name = f"{idx:03d} - {ch_title}.mp3"

            output_chapters.append({
                    "chapter-title" : ch_title,
                    "filename" : new_name
            })

            if end != -1:
                chapter_audio = sound[start * 1000 : end * 1000]
            else:
                chapter_audio = sound[start:]

            chapter_audio.export(os.path.join(output_directory, new_name), format='mp3')

    else:
        # one chapter per file, rename file
        chapter = chapters[0]
        idx = chapter['idx']
        ch_title = chapter['title']
        new_name = f"{idx:03d} - {ch_title}.mp3"
        open(os.path.join(output_directory, new_name), "wb").write(open(os.path.join(directory, path), "rb").read())

        output_chapters.append({
            "chapter-title" : ch_title,
            "filename" : new_name
        })


cmd = ['/Applications/AudioBookBinder.app/Contents/MacOS/abbinder',
        '-a', author,
        '-t', book_title,
        '-C', os.path.join(directory, 'cover.jpg'),
        '-o', os.path.join(output_directory, f"{author} - {book_title}.m4b")]

for chapter in output_chapters:
    cmd += [f"@{chapter['chapter-title']}@", os.path.join(output_directory, chapter['filename'])]

subprocess.call(cmd)

print(f"[+] Done!")
