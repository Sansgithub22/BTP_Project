from conllu import parse

def read_conllu(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return parse(f.read())

def read_alignments(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip().split() for line in f]

def read_bhojpuri_cpg(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip().split() for line in f]

def project_cpg_to_ud(hindi_ud, bhojpuri_sents, alignments):
    all_projected = []

    for hin, bhoj, align_line in zip(hindi_ud, bhojpuri_sents, alignments):
        align_map = {}  # Hindi index -> Bhojpuri index
        rev_align_map = {}  # Bhojpuri index -> Hindi index
        for pair in align_line:
            h, b = map(int, pair.split("-"))
            align_map[h] = b
            rev_align_map[b] = h

        proj_sent = []
        for b_idx, word in enumerate(bhoj):
            token = {
                "id": b_idx + 1,
                "form": word,
                "lemma": "_",
                "upostag": "_",
                "xpostag": "_",
                "feats": "_",
                "head": 0,
                "deprel": "dep",
                "deps": "_",
                "misc": "_"
            }

            if b_idx in rev_align_map:
                h_idx = rev_align_map[b_idx]
                if h_idx < len(hin):
                    h_tok = hin[h_idx]
                    token["upostag"] = h_tok.get("upostag", "_")
                    token["xpostag"] = h_tok.get("xpostag", "_")
                    token["deprel"] = h_tok.get("deprel", "dep")
                    h_head = h_tok.get("head", 0)

                    if h_head == 0 or (h_head - 1) not in align_map:
                        token["head"] = 0
                    else:
                        token["head"] = align_map[h_head - 1] + 1  # 1-based
            proj_sent.append(token)

        conllu_lines = []
        for tok in proj_sent:
            conllu_line = f"{tok['id']}\t{tok['form']}\t{tok['lemma']}\t{tok['upostag']}\t{tok['xpostag']}\t{tok['feats']}\t{tok['head']}\t{tok['deprel']}\t{tok['deps']}\t{tok['misc']}"
            conllu_lines.append(conllu_line)
        all_projected.append("\n".join(conllu_lines) + "\n")

    return all_projected

if __name__ == "__main__":
    hindi_ud = read_conllu(r"C:\Users\HP\Downloads\btp\hindi.conllu")
    bhojpuri_sents = read_bhojpuri_cpg(r"C:\Users\HP\Downloads\btp\bhojpuri.cpg")

    alignments = read_alignments(r"C:\Users\HP\Downloads\btp\alignment.txt")

    output = project_cpg_to_ud(hindi_ud, bhojpuri_sents, alignments)

    with open("bhojpuri_projected.conllu", "w", encoding="utf-8") as f:
        for sent in output:
            f.write(sent + "\n")

    print("✅ Bhojpuri UD projection complete! Output written to 'bhojpuri_projected.conllu'")
