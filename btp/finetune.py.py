from conllu import parse
from nltk import DependencyGraph
from difflib import ndiff
import graphviz

# ✅ Read CONLLU file
def read_conllu_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return parse(f.read())

# 🧠 Compute basic evaluation stats
def evaluate_projected(projected_sents, gold_sents):
    assert len(projected_sents) == len(gold_sents), "Mismatch in sentence count!"
    total_tokens, correct_upos, correct_heads, correct_labels = 0, 0, 0, 0

    for proj, gold in zip(projected_sents, gold_sents):
        for ptok, gtok in zip(proj, gold):
            if ptok["form"] != gtok["form"]:
                continue  # Alignment mismatch
            total_tokens += 1
            if ptok["upostag"] == gtok["upostag"]:
                correct_upos += 1
            if ptok["head"] == gtok["head"]:
                correct_heads += 1
            if ptok["deprel"] == gtok["deprel"]:
                correct_labels += 1

    print(f"\n📊 Evaluation on {len(projected_sents)} sentences:")
    print(f"🧩 Tokens compared: {total_tokens}")
    print(f"✅ UPOS Accuracy: {correct_upos/total_tokens:.2%}")
    print(f"🔁 Head Accuracy: {correct_heads/total_tokens:.2%}")
    print(f"🧠 DepRel Accuracy: {correct_labels/total_tokens:.2%}")

# 🌳 Visualize dependency tree using Graphviz
def visualize_sentence(sentence, title="Tree"):
    dot = graphviz.Digraph(format='png')
    for token in sentence:
        dot.node(str(token["id"]), f'{token["form"]} ({token["upostag"]})')
    for token in sentence:
        head = token["head"]
        if head != 0:
            dot.edge(str(head), str(token["id"]), label=token["deprel"])
        else:
            dot.edge("0", str(token["id"]), label="root")
    dot.render(title, view=True)

# 🧪 Compare tokens visually
def compare_sentences(proj_sent, gold_sent):
    print("\n🔍 Comparing Sentence:")
    for ptok, gtok in zip(proj_sent, gold_sent):
        print(f"{ptok['form']:10} | UD: {ptok['upostag']:10} vs GOLD: {gtok['upostag']:10} | Head: {ptok['head']} vs {gtok['head']} | DepRel: {ptok['deprel']} vs {gtok['deprel']}")

# 🚀 Main
if __name__ == "__main__":
    projected = read_conllu_file("bhojpuri_projected.conllu")
    gold = read_conllu_file(r"C:\Users\HP\Downloads\btp\bhojpuri_gold.conllu")

    evaluate_projected(projected, gold)

    # 📌 Visualize first sentence
    visualize_sentence(projected[0], "Projected_Tree")
    visualize_sentence(gold[0], "Gold_Tree")

    # 🧪 Compare first sentence
    compare_sentences(projected[0], gold[0])
