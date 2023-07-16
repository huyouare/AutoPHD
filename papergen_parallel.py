"""
Generates a research paper PDF via LaTeX using OpenAI or Anthropic.
"""

import anthropic
import concurrent
import json
import openai
import os
import re
import subprocess
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

openai.api_key = os.environ["OPENAI_API_KEY"]

SYSTEM_PROMPT = "You are a helpful research agent."

# Unused prompt
TOC_PROMPT = """
Write the table of contents as a parseable JSON array.
Your output should have the following format:

ABSTRACT:
<abstract>

SECTIONS:
[
  {
    "section": "Introduction",
    "subsections": [ ... ]
  },
  ...
  {
    "section": "Acklowledgements",
  },
  ...
]   
"""

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_completion(prompt, messages = [], max_tokens = 1000, model="gpt-3.5-turbo", temperature=0.0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

def generate_paper_skeleton(topic: str = ""):
    """
    Generates a paper using OpenAI.
    """
    print("Generating paper skeleton...")

    prompt = """
Generate the abstract and a section outline for a 20-page research paper.
Make it sound as close to a real paper as possible, such as one accepted to NeurIPS.
Write the table of contents as a parseable JSON list.
Your output should have the following format. Do not write anything else:

ABSTRACT:
<abstract>

SECTIONS:
[
  {
    "index": 0,
    "section": "Introduction"
  },
  ...
  {
    "index": ?,
    "section": "Acklowledgements"
  }
]   
    """
    if topic:
        prompt += f"\nWrite the paper about the following topic: {topic}"

    # Generate the skeleton
    paper_skeleton = generate_completion(prompt, temperature=0.3)

    print("Done.")

    return paper_skeleton

def generate_header(messages = []):
    """
    Generates the paper's title, authors, and abstract.
    """
    print("Generating paper header...")
    prompt = """
Generate the paper's header and abstract in LaTeX syntax using the above skeleton.
Make it sound as close to a real paper as possible, using specific facts, references, and formulas.
Use the NeurIPS paper format. Use real names and affiliations.
Do NOT use fake names such as John Smith or Jane Doe.
Start at the beginning, and ending at the abstract section.
Do NOT continue after the abstract section.

Use the following LaTeX code format:
\\documentclass{article}
\\usepackage[preprint]{neurips_2021}
\\usepackage{amsfonts}
\\usepackage{amsmath}
\\usepackage{booktabs}
\\usepackage{url}
\\usepackage{graphicx}
...
\\end{abstract}
"""
    # Generate the header
    paper_header = generate_completion(prompt, messages=messages, max_tokens=1000)

    print("Done.")

    return paper_header

def generate_paper_section(section_name = "Introduction", subsection = "", messages = [], figure_paths = []):
    print("Generating paper section...")
    print("figure_paths:", figure_paths)

    prompt = f"""
Write the {section_name} section of the paper in LaTeX syntax using the above skeleton.
If provided, only write the following subsection: {subsection}.
YOU MUST include (in Latex) one of the following figures (local files) into the section: {figure_paths}.
For example, \\includegraphics[width=0.8\\textwidth]{{figure_0.png}}.
Do not use LaTeX code that requres packages other than neurips_2021 and graphicx.
Make it sound as close to a real paper as possible, using specific facts, references, and formulas.
Make sure to liberally use \\cite to cite your sources.

Do not write more than one subsection or 1500 tokens at a time. Do not end in the middle of a sentence.
YOU MUST include one of the local figures as mentioned above.
    """
    print("PROMPT:", prompt)

    # Generate the section
    section = generate_completion(prompt, messages, max_tokens=1000)

    print("Done.")

    # If there are any lines containing \includegraphics, remove only that line.
    # section = "\n".join([line for line in section.split("\n") if "\\includegraphics" not in line])

    return section_name, section

def generate_references(citations = [], messages = []):
    print("Generating paper references...")

    print("Citations:", citations)

    prompt = f"""
Write the References section in LaTeX neurips_2021 style for the paper.
Make sure to use author-year format for citations.
You are using the following references in the paper:
{citations}

Make sure to cite ALL of the references mentioned above.
"""
    prompt += """
Use the following as a guide:
\\bibliographystyle{plain}
\\bibliography{references}

\\begin{thebibliography}{10}

\bibitem{vaswani2017attention}
Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin.
\newblock Attention is all you need.
\newblock {\em In Advances in Neural Information Processing Systems}, pages 5998--6008, 2017.
...

\\end{thebibliography}
"""

    # Generate the skeleton
    paper_skeleton = generate_completion(prompt, messages, max_tokens=2000)

    print("Done.")

    return paper_skeleton

def generate_paper(topic: str = "", skeleton: str = "", figure_paths = []):
    """
    Generates a paper using OpenAI.
    """
    print("Generating paper...")

    final_paper = ""

    messages = []
    messages.append({"role": "assistant", "content": skeleton})

    # Parse the TOC from skeleton
    toc = skeleton.split("SECTIONS:")[1]
    print("TOC:", toc)
    toc = json.loads(toc)

    citations = []

    header = generate_header(messages)
    print(header)
    if "\\end{document}" in header:
        header = header.split("\\end{document}")[0]
    # Remove everything after \end{abstract}
    header = header.split("\\end{abstract}")[0] + "\\end{abstract}\n"
    final_paper += header
    messages.append({"role": "assistant", "content": header})

    # Parse all of the citations found in the section
    for citation in re.findall(r"\\cite{(.+?)}", header):
        citations.append(citation)

    # Parse title from header
    paper_title = re.findall(r"\\title{(.+?)}", header)[0]

    sections = {}

    # Using the TOC, generate each section in parallel using multiple threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for section in toc:
            futures.append(executor.submit(generate_paper_section, section_name=section["section"], messages=messages, figure_paths=figure_paths))

        for future in concurrent.futures.as_completed(futures):
            section_name, section = future.result()
            print("Section:", section_name, "\n", section)
            sections[section_name] = section

            # Parse all of the citations found in the section
            for citation in re.findall(r"\\cite{(.+?)}", section):
                citations.append(citation)

    print("sections:", sections)

    # Add the sections to the final paper
    for section in toc:
        section_name = section["section"]
        final_paper += "\n"
        final_paper += sections[section_name]

    # Remove everything in final_paper after \biblio
    final_paper = final_paper.split("\\biblio")[0]

    # Generate references
    references = generate_references(citations, messages)
    print(references)
    final_paper += references

    if "\\end{document}" not in references:
        final_paper += "\n\n\\end{document}"

    # Make filename from paper title
    paper_title = paper_title.replace(":", "")
    filename = paper_title.lower().replace(" ", "_")[:20]
    
    with open(f"latex/{filename}-3p5-parallel.tex", "w") as f:
        f.write(final_paper)
    
    # Compile the paper and save to file using -interaction=nonstopmode

    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"latex/{filename}-3p5-parallel.tex"])

    # Move the pdf to the pdf folder
    subprocess.run(["mv", f"{filename}-3p5-parallel.pdf", f"pdf/{filename}-3p5-parallel.pdf"])

    print("Done.")


if __name__ == "__main__":
    generate_paper("Quantitative social studies analysis of jobs and skills that are most at risk of automation from generative AI")
