import panflute as pf

def simplify_cite(elem, doc):
    if isinstance(elem, pf.Para):
        new_inlines = []
        for inline in elem.content:
            if isinstance(inline, pf.Cite):
                if inline.citations[0].mode == 'AuthorInText':
                    text = pf.Str(inline.citations[0].id)
                else:
                    text = pf.Str(f"({inline.citations[0].id})")
                new_inlines.append(text)
            else:
                new_inlines.append(inline)
        return pf.Para(*new_inlines)

def main(doc=None):
    return pf.run_filter(simplify_cite, doc=doc)

if __name__ == "__main__":
    main()
