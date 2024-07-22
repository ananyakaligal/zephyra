import tiktoken
from .specialTokens import ZephyraTokens

class ZephyraTokenizer:
    def __init__(self, model_name="cl100k_base"):
        self.tokenizer = tiktoken.get_encoding(model_name)
        self.special_tokens = ZephyraTokens()
        self.addSpecialZephyraTokens()
        self.vocab_size = self.tokenizer.n_vocab


    def addSpecialZephyraTokens(self):
        for token in vars(self.special_tokens).values():
            if token not in self.tokenizer.encode(token):
                self.tokenizer.add_special_tokens([token])

    def encode(self, text, add_special_tokens=True):
        if add_special_tokens:
            text = f"{self.special_tokens.BOS} {text} {self.special_tokens.EOS}"
        return self.tokenizer.encode(text)

    def decode(self, tokens):
        return self.tokenizer.decode(tokens)

    def getVocabSize(self):
        return self.vocab_size

    def getPaddingTokenId(self):
        return self.tokenizer.encode(self.special_tokens.PAD)[0]

    def encodeCOQA_sample(self, context, questions, answers, rationales):
        """
        Encode a full CoQA example including context, questions, answers, and rationales.
        """
        encoded = self.encode(f"{self.special_tokens.CONTEXT} {context}")
        
        for q, a, r in zip(questions, answers, rationales):
            encoded += self.encode(f"{self.special_tokens.QUESTION} {q}")
            encoded += self.encode(f"{self.special_tokens.ANSWER} {a}")
            encoded += self.encode(f"{self.special_tokens.RATIONALE_START} {r} {self.special_tokens.RATIONALE_END}")
        
        return encoded

    def find_rationale_span(self, context_tokens, rationale_tokens):
        """
        Find the start and end indices of the rationale span in the context.
        """
        for i in range(len(context_tokens) - len(rationale_tokens) + 1):
            if context_tokens[i:i+len(rationale_tokens)] == rationale_tokens:
                return i, i + len(rationale_tokens)
        return -1, -1  # If not found

    def encode_with_rationale_positions(self, context, question, answer, rationale):
        """
        Encode a CoQA example and return token IDs along with rationale start and end positions.
        """
        context_tokens = self.encode(context)
        question_tokens = self.encode(question)
        answer_tokens = self.encode(answer)
        rationale_tokens = self.encode(rationale)

        rationale_start, rationale_end = self.find_rationale_span(context_tokens, rationale_tokens)

        full_encoding = (
            self.encode(self.special_tokens.CONTEXT) +
            context_tokens +
            self.encode(self.special_tokens.QUESTION) +
            question_tokens +
            self.encode(self.special_tokens.ANSWER) +
            answer_tokens
        )

        return full_encoding, rationale_start, rationale_end