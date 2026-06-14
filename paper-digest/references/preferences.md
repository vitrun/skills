# Paper Digest Preferences

Preference semantics live at the skill or agent layer, not inside the public
fetcher. The fetcher should return all new candidate papers after dedupe. The
agent then reads user preferences, curates the candidate list, and materializes
the final `preview.json` and `digest.md` that get published.

## Preference File

Store user preference text in JSON:

```bash
mkdir -p ~/.config/paper-digest
cp paper-digest/assets/preferences.example.json ~/.config/paper-digest/preferences.json
chmod 600 ~/.config/paper-digest/preferences.json
```

Suggested env:

```bash
PAPER_DIGEST_PREFERENCES_FILE="${PAPER_DIGEST_PREFERENCES_FILE:-$HOME/.config/paper-digest/preferences.json}"
```

Schema:

```json
{
  "interested": ["free-text interest 1", "free-text interest 2"],
  "excluded": ["free-text exclusion 1", "free-text exclusion 2"]
}
```

- `interested` and `excluded` are both free-text preference statements.
- A single string may be a keyword, a phrase, or a full sentence.
- Do not create separate `keywords` and `descriptions` fields.

## Curation Contract

The agent should:

1. Read the raw candidate preview produced by `fetch-alphaxiv-hot.py`.
2. Read `PAPER_DIGEST_PREFERENCES_FILE` if it exists.
3. Use the preference text semantically to:
   - exclude papers that clearly conflict with `excluded`
   - prioritize papers that strongly match `interested`
   - keep the final set concise and useful for the digest audience
4. Write a selection file shaped like [selection-template.json](../assets/selection-template.json).
5. Materialize the final curated `preview.json` and `digest.md` with `materialize-curated-digest.py`.

The final `preview.json` should represent the curated publish set, not the raw candidate pool.
