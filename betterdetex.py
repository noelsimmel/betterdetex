"""Strips TeX commands from a file and saves as new .txt file.
Will print warnings if detexing seems to strip too much from the files.
Note that this sometimes destroys sentence structures and should not be 
performed prior to POS tagging etc.
WIP/Use at your own risk.
"""

import re

def main(paths, threshold=0.5):
    """
    Iterates over a list of files paths and detexes them.
    
    Args:
        paths (str|list): Single path or list of paths to TeX files.
        threshold (float): Percentage [0.0, 1.0] of the original text length that 
                           should remain after detexing. Defaults to 0.5.
    """
    
    if type(paths) != list: paths = [paths] 

    for fi in paths:
        with open(fi, encoding="utf-8", errors="replace") as f:
            text = f.read()
            
        detexed = detex(text)
        if len(detexed) < len(text)*threshold: 
            print(f"Warning: Less than {int(threshold*100)}% of the content remains for file {fi}")
            
        filename = fi[:-4] + "_betterdetex.txt"
        with open(filename, mode="w+") as f:
            f.write(detexed)
    
def _sort_chapters(files):
    """Sort tex files as well as possible,
    i.e. alphabetically, but starting with the introduction."""
    
    files = sorted(files)
    c = 0
    for f in files:
        if "intro" in f or "einleitung" in f or "1" in f:
            files.remove(f)
            files.insert(c, f)
            c += 1
        elif "conclusion" in f:
            files.remove(f)
            files.append(f)
    return files
 
def detex(text):
    """Strips string of (nearly) all TeX commands using regular expressions."""
    
    # Delete comments
    text = re.sub("%.*", "", text) # Delete comments
    # Replace/remove various characters
    text = re.sub(r"(\$)|(\|\()|(\|\))", "", text)
    text = re.sub(r"\\author\{.*?(\\affiliation\{.*?\}.*?)*\}", "", text, flags=re.DOTALL) 
    text = re.sub(r"\\IfFileExists\{.*?\}\{\}", "", text, flags=re.DOTALL) 
    text = re.sub(r"\\hyp\{\}", "-", text)
    text = re.sub(r"\\'e", "é", text)
    
    # Remove \begin{document} etc., otherwise environment-wise subs below would delete everything
    openers = ["document", "otherlanguage", "refcontext", "refsection"]
    for com in openers:
        text = re.sub(r"\\begin\{" + com + r"\}", "", text)
    
    # Preserve quotes
    to_preserve = ["quote", "quotation"]
    for env in to_preserve:
        text = re.sub(r"\\begin\{" + env + r"\}(.*?)\\end( )?\{" + env + r"\}", "\\1", text, flags=re.DOTALL)
    # Delete everything within an environment (between \begin{} and \end{})
    text = re.sub(r"\\begin\{(?P<env>[a-z]+)\}.*?\\end( )?\{(?P=env)\}", "", text, flags=re.DOTALL|re.IGNORECASE)
    # Delete linguistic examples that use langsci's gb4e
    text = re.sub(r"\\ea.*?\\z", "", text, flags=re.DOTALL)
    
    # Replace text within a command with just the text
    # e.g. \subsection*{title} becomes title
    # TODO: \emph and \textbf might mark keywords
    # Order is important! Smaller scope commands have to come first
    # \il and \is are not included since they would repeat the keywords
    to_replace = ["textbf", "textsc", "textit", "textrm", "ili", "isi", "emph", "enquote", "footnote"]
    for com in to_replace:
        text = re.sub(r"\\" + com + r"\{(.*?)\}", "\\1", text)
    # Here the whole line should be replaced
    # This avoids "stealing" closing braces from smaller scope commands
    to_replace_line = ["title", "abstract", "caption", "chapter"]
    for com in to_replace_line:
        text = re.sub(r"\\" + com + r"(\*)?\{(.*)\}(?!\})", "\\n\\2 ", text)
    text = re.sub(r"\\[sub]*section[\*]?\{(.*?)\}", "\\n\\n\\1\\n", text) # Also matches \subsection etc.
    text = re.sub(r"\\title\[(.*?)\]", "\\1", text, flags=re.DOTALL) # Short title
    
    # Delete crossreferences
    to_delete = ["section", "sections", "figure", "figures", "table", "tables"]
    for com in to_delete:
        text = re.sub(com + r"( |~)\\[a-z]*ref\{.*?\}", "", text, flags=re.IGNORECASE)
        
    # Delete all remaining commands with arguments: \command[something]{something1}{something2}
    text = re.sub(r"\\[a-z]+(\[.*?\])?(\{.*?\})+", "", text, flags=re.IGNORECASE) 
    # Delete all remaining commands without arguments: \command
    text = re.sub(r"\\[a-z]+", "", text, flags=re.IGNORECASE) 
    
    # Replace single braces/brackets with space
    text = re.sub(r"\n( |\t)*(\{|\}|\])|(\]|\}|\{)\n", " ", text)
    # Reduce whitespace for readability
    text = re.sub(r"\n\n\n", "\n", text)  
        
    return text


if __name__ == "__main__":
    paths = []
    main(paths, threshold=0.5)
