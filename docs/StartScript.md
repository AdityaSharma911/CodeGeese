curl 'https://leetcode.com/graphql/' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "query": "query getQuestionDetail($titleSlug: String!) { question(titleSlug: $titleSlug) { questionId title titleSlug difficulty content stats topicTags { name slug } codeSnippets { lang langSlug code } } }",
    "variables": {
      "titleSlug": "find-consistently-improving-employees"
    }
  }'

  